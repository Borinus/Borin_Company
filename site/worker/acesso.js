/* Conta do cliente: entrar, trocar senha, guardar e ler as fichas.
 *
 * O desenho e deliberado e vale entender antes de mexer:
 *
 *   Nao existe cadastro aberto. O cliente pede orcamento sem conta nenhuma.
 *   Quem cria a conta e o Mateus, quando responde o orcamento — e a senha vai
 *   dentro daquela resposta. Isso dispensa verificacao de email: se a mensagem
 *   chegou naquele endereco, a posse ja esta provada.
 *
 *   Sem "esqueci minha senha" automatico. Numa base de dezenas de clientes,
 *   fluxo de recuperacao e mais superficie de ataque do que utilidade — o
 *   Mateus gera outra senha e manda. Um cliente por ano vai precisar.
 *
 * Guarda em KV, nao em banco: sao poucos registros, nenhuma consulta por
 * campo, e KV nao tem esquema pra migrar.
 */

import { enviarPara, podeEscreverAoCliente } from "./correio.js";
import { garantirEmpresa, ehDono, listarEquipe, adicionarMembro, gravarMembro,
         removerMembro, avisarNovoMembro, listarPedidos, gerarSenha,
         ehSenhaGerada, guardarProposta, listarPropostas, veDinheiro,
         podePreencher, podeLiberar, trocarPapel, papelDe, PAPEIS } from "./equipe.js";
import { guardarArquivo, listarArquivos, lerArquivo, apagarArquivo,
         limparCodigo, LIMITE_ARQUIVO } from "./arquivos.js";
import { montarPainel } from "./painel.js";
import { validarTokenGoogle, buscarJwks } from "./google.js";
import { validarTokenMicrosoft, buscarJwksMicrosoft } from "./microsoft.js";

const SESSAO_HORAS = 12;
const TENTATIVAS_MAX = 8;      // por email, antes de travar
const TRAVA_MINUTOS = 15;
/* O Workers limita o CPU por requisicao, e PBKDF2 com as 210 mil voltas que a
   OWASP recomenda estoura e derruba o pedido inteiro (erro 1101). O que
   compensa a conta menor e o PIMENTA: um segredo que so existe no Worker e
   entra no calculo. Sem ele, uma copia do KV nao permite testar senha nenhuma
   fora daqui — que e justamente o ataque que a conta alta evitaria. */
const PBKDF2_VOLTAS = 50000;

/* ---------- utilidades ---------- */

const enc = new TextEncoder();

function hex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function aleatorio(bytes) {
  return hex(crypto.getRandomValues(new Uint8Array(bytes)));
}

async function derivar(senha, salt, pimenta) {
  const chave = await crypto.subtle.importKey(
    "raw", enc.encode(senha + "|" + (pimenta || "")), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash: "SHA-256", salt: enc.encode(salt), iterations: PBKDF2_VOLTAS },
    chave, 256);
  return hex(bits);
}

/* comparacao em tempo constante: sair no primeiro byte diferente conta quanto
   do hash o atacante acertou */
function igual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

function normalizarEmail(v) {
  return typeof v === "string" ? v.trim().toLowerCase().slice(0, 160) : "";
}

const json = (o, status = 200, extra = {}) =>
  new Response(JSON.stringify(o), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...extra },
  });

/* ---------- sessao ---------- */

async function abrirSessao(env, email) {
  const token = aleatorio(32);
  await env.CLIENTES.put("sessao:" + token, email,
    { expirationTtl: SESSAO_HORAS * 3600 });
  const cookie = [
    "borin_sessao=" + token,
    "Path=/",
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    "Max-Age=" + SESSAO_HORAS * 3600,
  ].join("; ");
  return cookie;
}

function lerCookie(request, nome) {
  const cru = request.headers.get("Cookie") || "";
  for (const parte of cru.split(";")) {
    const [k, ...v] = parte.trim().split("=");
    if (k === nome) return v.join("=");
  }
  return "";
}

async function quemE(request, env) {
  const token = lerCookie(request, "borin_sessao");
  if (!token) return null;
  const email = await env.CLIENTES.get("sessao:" + token);
  if (!email) return null;
  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return null;
  /* conta criada antes da empresa existir ganha a dela aqui, na primeira vez
     que e usada. Migracao sem script separado e sem janela de manutencao. */
  const conta = await garantirEmpresa(env, email, JSON.parse(cru));
  /* `empresa` aqui e o ID, usado como prefixo das chaves. O NOME fica em
     conta.empresa e e o que aparece na tela. Trocar os dois faria a conta do
     cliente exibir o id no lugar do nome da empresa dele. */
  return { email, token, conta, empresa: conta.empresa_id, dono: ehDono(conta) };
}

/* ---------- freio de forca bruta ---------- */

async function travado(env, email) {
  const cru = await env.CLIENTES.get("freio:" + email);
  if (!cru) return 0;
  const f = JSON.parse(cru);
  if (f.n < TENTATIVAS_MAX) return 0;
  const falta = Math.ceil((f.ate - Date.now()) / 60000);
  return falta > 0 ? falta : 0;
}

async function contarErro(env, email) {
  const cru = await env.CLIENTES.get("freio:" + email);
  const f = cru ? JSON.parse(cru) : { n: 0, ate: 0 };
  f.n += 1;
  f.ate = Date.now() + TRAVA_MINUTOS * 60000;
  await env.CLIENTES.put("freio:" + email, JSON.stringify(f),
    { expirationTtl: TRAVA_MINUTOS * 60 });
}

/* ---------- rotas ---------- */

/* Criar conta. So o Mateus chama, com o segredo do Worker.
   Devolve a senha em claro UMA vez — e para ele colar na resposta do
   orcamento. Depois disso so existe o hash.

   O gerador vive no equipe.js. Antes existia uma copia aqui com alfabeto
   proprio: as duas geravam senhas de formato diferente e mudar uma nao mudava
   a outra, entao a senha do lead e a do funcionario nunca eram iguais. */

async function criar(request, env, dados) {
  if (!ehAdmin(request, env) && (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN)) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(dados.email);
  if (!email.includes("@")) return json({ erro: "email inválido" }, 400);

  const existente = await env.CLIENTES.get("cliente:" + email);
  if (existente && !dados.trocar) {
    return json({ erro: "ja existe. use trocar:true para gerar outra senha" }, 409);
  }

  const senha = gerarSenha();

  const salt = aleatorio(16);

  /* Conta que ja existe: PRESERVAR tudo e trocar so a senha.
     Antes montava um objeto novo do zero e copiava tres campos na mao, o que
     apagava `empresa_id` e `papel`. Gerar senha nova pra um funcionario que
     perdeu a dele desligava ele da empresa e o transformava em dono de uma
     empresa vazia — perdia projeto, arquivo e acesso, sem erro nenhum. */
  const velho = existente ? JSON.parse(existente) : null;
  const conta = {
    ...(velho || {}),
    email,
    empresa: (dados.empresa || "").slice(0, 120) || (velho && velho.empresa) || "",
    contato: (dados.contato || "").slice(0, 120) || (velho && velho.contato) || "",
    salt,
    hash: await derivar(senha, salt, env.PIMENTA),
    criado_em: (velho && velho.criado_em) || new Date().toISOString(),
    senha_provisoria: true,
    /* criada pelo Mateus: ele mesmo entrega a senha, entao ja nasce ativa e
       nao expira */
    estado: "ativa",
  };
  /* senha nova invalida as antigas: elas so serviam pra explicar o erro
     enquanto a conta era pendente */
  delete conta.provisorias_antigas;
  await env.CLIENTES.put("cliente:" + email, JSON.stringify(conta));
  await env.CLIENTES.delete("freio:" + email);

  return json({ ok: true, email, senha, trocada: !!existente });
}

async function entrar(request, env, dados) {
  const email = normalizarEmail(dados.email);
  const senha = typeof dados.senha === "string" ? dados.senha : "";
  if (!email || !senha) return json({ erro: "informe o email e a senha" }, 400);

  const preso = await travado(env, email);
  if (preso) {
    return json({ erro: "muitas tentativas. tente de novo em " + preso + " min" }, 429);
  }

  const cru = await env.CLIENTES.get("cliente:" + email);
  /* mesmo tempo e mesma resposta para conta inexistente e senha errada:
     senao da pra descobrir quem e cliente so pelo tempo de resposta */
  const conta = cru ? JSON.parse(cru) : { salt: "vazio", hash: "-" };
  let tentativa = await derivar(senha, conta.salt, env.PIMENTA);

  /* A senha gerada por mim é sempre em caixa alta. Quem digitou BORIN482913 em
     minúscula não errou a senha, errou o shift — e num campo de senha o
     celular não corrige sozinho. Só vale pra senha que EU gerei; a que o
     cliente escolhe continua diferenciando maiúscula de minúscula. */
  if (!igual(tentativa, conta.hash) && conta.senha_provisoria && ehSenhaGerada(senha)) {
    tentativa = await derivar(senha.trim().toUpperCase(), conta.salt, env.PIMENTA);
  }

  if (!cru || !igual(tentativa, conta.hash)) {
    /* Senha de um email anterior não é chute: prova que a pessoa recebeu um
       email meu. Dizer o que houve e NÃO contar como tentativa — era isso que
       travava o cliente por 15 minutos com a senha certa na caixa. */
    for (const v of (conta.provisorias_antigas || [])) {
      let velha = await derivar(senha, v.salt, env.PIMENTA);
      if (!igual(velha, v.hash) && ehSenhaGerada(senha)) {
        velha = await derivar(senha.trim().toUpperCase(), v.salt, env.PIMENTA);
      }
      if (igual(velha, v.hash)) {
        return json({
          erro: "essa senha era de um pedido anterior e já não vale. "
              + "use a do email mais recente, com o assunto “Sua senha nova”",
        }, 401);
      }
    }
    await contarErro(env, email);
    return json({ erro: "email ou senha não conferem" }, 401);
  }

  await env.CLIENTES.delete("freio:" + email);
  const cookie = await abrirSessao(env, email);
  return json({
    ok: true,
    empresa: conta.empresa,
    contato: conta.contato,
    senha_provisoria: !!conta.senha_provisoria,
  }, 200, { "Set-Cookie": cookie });
}

/**
 * Entrar com o Google. O botao na pagina devolve um JWT do Google; o google.js
 * confere a assinatura e so entao o email do token vira verdade.
 *
 * Por que existe: a senha por email e o maior atrito do funil — ela se perde,
 * vai pro spam, chega em caixa alta errada. Quem usa Gmail (a maioria aqui)
 * entra com dois cliques e nunca mais precisa da BORIN######.
 *
 * Duas decisoes de projeto, e o porque:
 *
 * - Conta NAO nasce aqui. Ela nasce com o pedido de orcamento, que e o que
 *   amarra a conta a uma empresa e a um projeto. Login de estranho criaria
 *   uma conta vazia orfa. Como o Google ja provou que o email e da pessoa,
 *   dizer "nao achei conta pra este email" nao vaza nada — so o proprio dono
 *   do email recebe essa resposta.
 *
 * - Falha aqui NAO conta pro freio de senha. O freio protege contra chute de
 *   senha; token invalido nao e chute de senha, e travar a conta de alguem
 *   por token vencido puniria a pessoa errada.
 */
async function entrarComGoogle(request, env, dados) {
  if (!env.GOOGLE_CLIENT_ID) {
    return json({ erro: "a entrada com Google ainda não está ligada" }, 503);
  }
  let jwks;
  try {
    jwks = await buscarJwks();
  } catch (e) {
    console.error("certs do Google fora do ar:", e && e.message);
    return json({ erro: "não consegui falar com o Google agora. use a senha" }, 502);
  }
  const r = await validarTokenGoogle(dados.credential, jwks,
                                     { aud: env.GOOGLE_CLIENT_ID });
  if (!r.ok) {
    /* o motivo exato vai pro log, nao pro navegador: "aud de outro site" e
       detalhe de implementacao que so interessa a quem esta atacando */
    console.error("token Google recusado:", r.motivo);
    return json({ erro: "não consegui confirmar sua conta Google. tente de novo" }, 401);
  }

  const { conta, criada, cookie } = await entrarOuCriarPorEmail(
    env, r.email, r.nome, "entrar com o Google");
  return json({
    ok: true,
    empresa: conta.empresa,
    contato: conta.contato,
    senha_provisoria: false,
    google: true,
    criada,
  }, 200, { "Set-Cookie": cookie });
}

/**
 * Login social (Google/Microsoft): o provedor JÁ PROVOU que o email é da
 * pessoa, então a conta entra direto — e nasce na hora se ainda não existe.
 *
 * A conta criada aqui NÃO tem senha usável: o cliente entra só pela conexão da
 * conta. Guarda-se um hash de uma senha aleatória que ninguém conhece só pra
 * manter o mesmo formato das outras contas; ele nunca é usado pra login.
 *
 * empresa_id e papel NÃO nascem aqui: o primeiro quemE() resolve via
 * garantirEmpresa (é assim que toda conta funciona, inclusive a do pedido).
 * Por isso conta sem empresa vinculada é válida — o cliente preenche a empresa
 * quando pedir um orçamento, e o vínculo é sempre o email.
 */
async function entrarOuCriarPorEmail(env, emailCru, nome, origem) {
  const email = normalizarEmail(emailCru);
  let cru = await env.CLIENTES.get("cliente:" + email);
  let criada = false;

  if (!cru) {
    const salt = aleatorio(16);
    const senha = gerarSenha();          // aleatória, nunca usada pra entrar
    const nova = {
      email,
      empresa: "",
      contato: (nome || "").slice(0, 120),
      salt,
      hash: await derivar(senha, salt, env.PIMENTA),
      provisorias_antigas: [],
      criado_em: new Date().toISOString(),
      senha_provisoria: false,
      estado: "ativa",
      origem,
    };
    await env.CLIENTES.put("cliente:" + email, JSON.stringify(nova));
    cru = JSON.stringify(nova);
    criada = true;
  }

  const conta = JSON.parse(cru);
  /* entrou por provedor social = dono do email confirmado. A trava de
     tentativas de senha perde o motivo de existir pra essa conta agora. */
  await env.CLIENTES.delete("freio:" + email);
  const cookie = await abrirSessao(env, email);
  return { conta, criada, cookie };
}

/**
 * Entrar com a Microsoft. Espelha entrarComGoogle: o botão devolve um id_token
 * da Microsoft, o microsoft.js confere a assinatura contra o JWKS da Microsoft,
 * e só então o email do token vira verdade. Cria a conta se não existir.
 */
async function entrarComMicrosoft(request, env, dados) {
  if (!env.MICROSOFT_CLIENT_ID) {
    return json({ erro: "a entrada com Microsoft ainda não está ligada" }, 503);
  }
  let jwks;
  try {
    jwks = await buscarJwksMicrosoft();
  } catch (e) {
    console.error("certs da Microsoft fora do ar:", e && e.message);
    return json({ erro: "não consegui falar com a Microsoft agora. use a senha" }, 502);
  }
  const r = await validarTokenMicrosoft(dados.credential, jwks,
                                        { aud: env.MICROSOFT_CLIENT_ID });
  if (!r.ok) {
    console.error("token Microsoft recusado:", r.motivo);
    return json({ erro: "não consegui confirmar sua conta Microsoft. tente de novo" }, 401);
  }

  const { conta, criada, cookie } = await entrarOuCriarPorEmail(
    env, r.email, r.nome, "entrar com a Microsoft");
  return json({
    ok: true,
    empresa: conta.empresa,
    contato: conta.contato,
    senha_provisoria: false,
    microsoft: true,
    criada,
  }, 200, { "Set-Cookie": cookie });
}

/**
 * "Não recebi a senha" — o cliente pede outra, sem depender do Mateus.
 *
 * Existe porque o pedido repetido deixou de mandar senha nova (era o que
 * confundia o cliente com três emails diferentes). Sem este caminho, quem
 * perdeu o primeiro email ficava esperando alguém responder na mão.
 *
 * O endereço de email é a prova de identidade — é a mesma premissa em que o
 * sistema inteiro já se apoia: se a mensagem chegou naquela caixa, quem abre é
 * o dono. Não há pergunta secreta nem link com token que expira.
 */
async function reenviarSenha(request, env, dados) {
  const email = normalizarEmail(dados.email);
  if (!email.includes("@")) return json({ erro: "informe um email válido" }, 400);

  /* A resposta é IGUAL exista ou não a conta. Responder "não achei esse email"
     transformaria esta rota numa lista de clientes: bastaria testar endereços
     até um deles confirmar. */
  const resposta = json({
    ok: true,
    recado: "Se esse email tiver conta aqui, a senha nova chega em instantes.",
  });

  /* Freio próprio: sem ele, qualquer um enche a caixa de um cliente com
     senha nova a cada segundo — e ainda invalida a que ele estava usando. */
  const trava = "reenvio:" + email;
  try {
    const cru = await env.CLIENTES.get(trava);
    const n = cru ? JSON.parse(cru).n : 0;
    if (n >= 3) return resposta;
    await env.CLIENTES.put(trava, JSON.stringify({ n: n + 1 }),
      { expirationTtl: 86400 });
  } catch (e) {
    console.error("freio de reenvio falhou:", e && e.message);
  }

  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return resposta;

  const conta = JSON.parse(cru);
  const senha = gerarSenha();
  const salt = aleatorio(16);

  await env.CLIENTES.put("cliente:" + email, JSON.stringify({
    ...conta,
    salt,
    hash: await derivar(senha, salt, env.PIMENTA),
    senha_provisoria: true,
  }), conta.estado === "ativa" ? {} : { expirationTtl: 30 * 86400 });

  /* a trava de tentativas some junto: quem pediu senha nova não pode continuar
     preso pelos erros que cometeu tentando lembrar a antiga */
  await env.CLIENTES.delete("freio:" + email);

  try {
    await enviarPara(env, {
      para: email,
      assunto: "Sua senha nova — Borin Projetos Elétricos",
      corpo: boasVindas(conta.contato, email, senha, true),
      html: true,
    });
  } catch (e) {
    console.error("reenvio de senha falhou:", e && e.message);
  }
  return resposta;
}

async function trocarSenha(request, env, dados) {
  const eu = await quemE(request, env);
  if (!eu) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const nova = typeof dados.nova === "string" ? dados.nova : "";
  if (nova.length < 8) return json({ erro: "a senha precisa de 8 caracteres ou mais" }, 400);

  const atual = await derivar(dados.atual || "", eu.conta.salt, env.PIMENTA);
  if (!igual(atual, eu.conta.hash)) return json({ erro: "senha atual não confere" }, 401);

  const salt = aleatorio(16);
  /* Aqui a conta deixa de ser pendente: quem trocou a senha leu o email, e
     isso e a prova de que o endereco e dele. Some tambem o prazo de validade —
     conta pendente expira em 30 dias, conta ativa nao expira. */
  const conta = {
    ...eu.conta, salt,
    hash: await derivar(nova, salt, env.PIMENTA),
    senha_provisoria: false,
    estado: "ativa",
    ativada_em: new Date().toISOString(),
  };
  /* As senhas provisórias antigas só serviam pra explicar o erro enquanto a
     conta era pendente. Com a conta ativa elas viram peso morto guardado —
     hash de credencial não fica no banco depois de deixar de ter uso. */
  delete conta.provisorias_antigas;
  await env.CLIENTES.put("cliente:" + eu.email, JSON.stringify(conta));
  return json({ ok: true });
}

async function sair(request, env) {
  const token = lerCookie(request, "borin_sessao");
  if (token) await env.CLIENTES.delete("sessao:" + token);
  return json({ ok: true }, 200, {
    "Set-Cookie": "borin_sessao=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0",
  });
}

async function eu(request, env) {
  const s = await quemE(request, env);
  if (!s) return json({ entrou: false });
  return json({
    entrou: true,
    email: s.email,
    empresa: s.conta.empresa,
    contato: s.conta.contato,
    senha_provisoria: !!s.conta.senha_provisoria,
  });
}

/* As fichas ficam na conta pra o cliente continuar de outra maquina.
   tipo e 'padrao' ou 'projeto:<codigo>'. */
async function guardarFicha(request, env, dados) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const tipo = (dados.tipo || "").replace(/[^a-zA-Z0-9:_-]/g, "").slice(0, 60);
  if (!tipo) return json({ erro: "tipo inválido" }, 400);
  const corpo = JSON.stringify(dados.dados || {});
  if (corpo.length > 64 * 1024) return json({ erro: "ficha grande demais" }, 413);

  if (!podePreencher(s.conta)) {
    return json({ erro: "só quem contratou ou compras preenche as fichas" }, 403);
  }

  await env.CLIENTES.put("ficha:" + s.empresa + ":" + tipo,
    JSON.stringify({ dados: dados.dados, em: new Date().toISOString() }));
  if (tipo === "cadastro" && dados.avisar) {
    await avisarCadastro(env, s.email, dados.dados);
  }
  return json({ ok: true });
}

async function lerFicha(request, env, url) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);
  const tipo = (url.searchParams.get("tipo") || "").replace(/[^a-zA-Z0-9:_-]/g, "").slice(0, 60);
  const cru = await env.CLIENTES.get("ficha:" + s.empresa + ":" + tipo);
  return json(cru ? JSON.parse(cru) : { dados: null });
}

/* ---------- projetos do cliente ---------- */

/* O andamento e escrito pelo Mateus, nao pelo cliente. Um projeto por codigo.
   O arquivo entregue nao fica aqui: entra o link da pasta compartilhada, que
   e como a entrega ja e feita hoje (ver padroes/padrao-entrega.md). */
const ETAPAS = [
  "Orçamento enviado",
  "Contrato assinado",
  "Aguardando a ficha",
  "Em execução",
  "Em conferência",
  "Entregue",
  "Aprovado",
];

/* A empresa a que um email pertence. Admin nao tem sessao, entao migra
   aqui tambem — senao a primeira chamada de admin numa conta antiga
   escreveria com chave de empresa que ainda nao existe. */
async function empresaDe(env, email) {
  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return null;
  const conta = await garantirEmpresa(env, email, JSON.parse(cru));
  return conta.empresa_id;
}

async function gravarProjeto(request, env, dados) {
  /* Aceita o segredo no cabeçalho, como as outras rotas de admin. Esta era a
     única que exigia ele no CORPO — quem chamasse do jeito certo levava 401 e
     ia procurar defeito na autenticação, que estava funcionando. */
  if (!ehAdmin(request, env)
      && (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN)) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(dados.email);
  const codigo = (dados.codigo || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 30);
  if (!email.includes("@") || !codigo) return json({ erro: "informe email e codigo" }, 400);

  const empresa = await empresaDe(env, email);
  if (!empresa) return json({ erro: "esse email nao tem conta ainda" }, 404);

  const chave = "projeto:" + empresa + ":" + codigo;
  const antes = await env.CLIENTES.get(chave);
  const p = antes ? JSON.parse(antes) : { codigo, criado_em: new Date().toISOString() };

  if (dados.nome !== undefined) p.nome = String(dados.nome).slice(0, 140);
  if (dados.status !== undefined) p.status = String(dados.status).slice(0, 60);
  if (dados.prazo !== undefined) p.prazo = String(dados.prazo).slice(0, 40);
  if (dados.link !== undefined) p.link = String(dados.link).slice(0, 500);
  if (dados.nota !== undefined) p.nota = String(dados.nota).slice(0, 400);
  p.atualizado_em = new Date().toISOString();

  await env.CLIENTES.put(chave, JSON.stringify(p));
  return json({ ok: true, projeto: p });
}

async function listarProjetos(request, env) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const lista = await env.CLIENTES.list({ prefix: "projeto:" + s.empresa + ":" });
  const projetos = [];
  for (const k of lista.keys) {
    const cru = await env.CLIENTES.get(k.name);
    if (cru) projetos.push(JSON.parse(cru));
  }
  projetos.sort((a, b) => (b.atualizado_em || "").localeCompare(a.atualizado_em || ""));

  /* as fichas ja preenchidas, pra ele saber o que falta */
  const fichas = await env.CLIENTES.list({ prefix: "ficha:" + s.empresa + ":" });
  const preenchidas = fichas.keys.map((k) => k.name.split(":").slice(2).join(":"));

  /* Tudo que ele já pediu pelo site. Vem junto porque a conta é a resposta ao
     "e o meu orçamento?" — sem isso ele abre a conta, vê "nenhum projeto" e
     continua sem saber se o pedido dele chegou. */
  /* Quem é do campo NÃO recebe proposta nem orçamento. E a filtragem é aqui,
     no servidor — esconder na tela deixaria o valor viajando na resposta, a um
     F12 de distância de quem não devia ver. */
  const dinheiro = veDinheiro(s.conta);
  const pedidos = dinheiro ? await listarPedidos(env, s.empresa) : [];
  const propostas = dinheiro ? await listarPropostas(env, s.empresa) : [];

  /* O nome vinha do formulário rápido de orçamento, onde a pessoa digita com
     pressa: "Mateu, seus projetos" era um "s" que faltou ali. O cadastro é o
     formulário que ela preenche com calma, conferindo, pra ir no contrato —
     quando existe, é ele que vale. Mesma coisa pra razão social da empresa. */
  let contato = s.conta.contato;
  let empresa = s.conta.empresa;
  try {
    const cru = await env.CLIENTES.get("ficha:" + s.empresa + ":cadastro");
    const cad = cru ? (JSON.parse(cru).dados || {}) : {};
    if (cad.rep_nome) contato = cad.rep_nome;
    if (cad.nome_fantasia) empresa = cad.nome_fantasia;
  } catch (e) {
    /* cadastro ilegível não pode derrubar a conta inteira */
    console.error("cadastro nao lido:", e && e.message);
  }

  /* quantas pessoas têm acesso: a conta mostra o número sem o cliente
     precisar abrir outra tela pra descobrir que liberou alguém e esqueceu */
  let equipe = 0;
  if (s.empresa) {
    const idx = await env.CLIENTES.get("equipe:" + s.empresa);
    equipe = (idx ? JSON.parse(idx) : []).length + 1;
  }

  return json({
    entrou: true,
    papel: papelDe(s.conta),
    papel_nome: PAPEIS[papelDe(s.conta)].nome,
    empresa,
    contato,
    email: s.email,
    etapas: ETAPAS,
    projetos,
    pedidos,
    propostas,
    equipe,
    fichas: preenchidas,
  });
}

/* Le a conta e as fichas de um cliente. So o Mateus chama, com o segredo:
   e o que permite o contrato ser gerado ja preenchido a partir do cadastro
   que o cliente fez, em vez de ele editar campo por campo no PDF. */
/* O segredo vem no cabecalho Authorization, nunca na URL: query string entra
   em log da Cloudflare, no historico do navegador e no Referer que vaza pra
   qualquer recurso que a pagina carregue. Cabecalho nao entra em nenhum. */
function ehAdmin(request, env) {
  if (!env.SEGREDO_ADMIN) return false;
  const cab = request.headers.get("Authorization") || "";
  const dado = cab.startsWith("Bearer ") ? cab.slice(7) : "";
  return dado.length === env.SEGREDO_ADMIN.length && igual(dado, env.SEGREDO_ADMIN);
}

async function lerCliente(request, env, url) {
  if (!ehAdmin(request, env)) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(url.searchParams.get("email"));
  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return json({ erro: "sem conta" }, 404);
  const conta = await garantirEmpresa(env, email, JSON.parse(cru));
  delete conta.hash; delete conta.salt;

  const fichas = {};
  const lista = await env.CLIENTES.list({ prefix: "ficha:" + conta.empresa_id + ":" });
  for (const k of lista.keys) {
    const v = await env.CLIENTES.get(k.name);
    if (v) fichas[k.name.split(":").slice(2).join(":")] = JSON.parse(v).dados;
  }
  const projetos = [];
  const pl = await env.CLIENTES.list({ prefix: "projeto:" + conta.empresa_id + ":" });
  for (const k of pl.keys) {
    const v = await env.CLIENTES.get(k.name);
    if (v) projetos.push(JSON.parse(v));
  }
  return json({ ok: true, conta, fichas, projetos });
}

/* Avisa o Mateus quando o cliente termina o cadastro — senao ele so descobre
   se ficar checando. E o gatilho pra reenviar o contrato preenchido. */
/* Avisa o Mateus quando o cliente termina o cadastro — senao ele so descobre
   se ficar checando. E o gatilho pra reenviar o contrato preenchido. */
async function avisarCadastro(env, email, dados) {
  const linhas = Object.entries(dados || {})
    .filter(([, v]) => v)
    .map(([k, v]) => "  " + k + ": " + String(v).slice(0, 120))
    .join("\n");
  const corpo = "O cliente " + email + " completou o cadastro da empresa.\n\n"
    + linhas + "\n\nPara reenviar o contrato preenchido:\n"
    + "  python comercial/reenviar-contrato.py --cliente " + email + " --enviar\n";
  try {
    await enviarPara(env, {
      para: env.DESTINO,
      assunto: "Cadastro completo: " + (dados.razao_social || email),
      corpo: corpo,
    });
  } catch (e) {
    console.error("aviso de cadastro falhou:", e && e.message);
  }
}

/* O email que abre a porta pro cliente. E o primeiro texto que ele recebe de
   nos, entao nao pode parecer aviso de sistema: diz o que aconteceu, da a
   senha e explica pra que serve. */
/**
 * Confirmação para quem JÁ tem conta.
 *
 * O cliente que volta era o único que não recebia nada. O `contaDoLead` via
 * conta ativa, devolvia "ja_tinha" e saía — sem senha pra mandar, mandava
 * silêncio. Quem pediu orçamento pela segunda vez via a tela de "recebido" e
 * depois mais nada, sem saber se o pedido tinha chegado. E é justamente o
 * cliente que volta que mais merece resposta.
 */
/**
 * Pedido repetido de quem ainda não entrou.
 *
 * Não leva senha: a que eu mandei antes continua valendo. Mandar outra criava
 * o problema que este email existe pra evitar — vários emails iguais na caixa,
 * só o último funcionando, e a pessoa travando a conta ao tentar os anteriores.
 */
/* Um rodape so pros tres emails do cliente.

   Estava escrito tres vezes, identico. Rodape repetido e rodape que diverge: no
   dia em que um dado mudar, dois ficam velhos e o cliente recebe documentos da
   mesma empresa com informacao diferente.

   E agora leva o TELEFONE. O email fica guardado na caixa do cliente por meses
   e era o unico canal sem jeito de falar comigo agora — a pagina /enviado tinha
   o numero, o email nao. Importa mais desde que se sabe que o numero do
   WhatsApp automatico nao recebe resposta: quem responder por la fala sozinho,
   entao o numero de verdade precisa estar onde ele procurar. */
const RODAPE = [
  '<div style="padding:14px 28px;border-top:1px solid #DCDCDC;',
  'font-family:Consolas,monospace;font-size:10px;color:#6B6B6B;line-height:1.7">',
  "Borin Projetos El\u00e9tricos &middot; CNPJ 65.749.097/0001-85 &middot; Caxias do Sul / RS<br>",
  'WhatsApp <a href="https://wa.me/5554996642003" style="color:#111111">',
  "(54) 99664-2003</a> &middot; contato@borinprojetos.com.br &middot; ",
  "borinprojetos.com.br",
  "</div></div></div>",
].join("");

function senhaJaFoi(contato, email) {
  const nome = (contato || "").split(" ")[0];
  return [
    '<div style="margin:0;padding:24px 16px;background:#F4F4F4;',
    "font-family:'Segoe UI',Arial,Helvetica,sans-serif\">",
    '<div style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #111111">',
    '<div style="padding:26px 28px 20px;border-bottom:1px solid #111111">',
    '<div style="font-size:30px;font-weight:700;letter-spacing:4px;color:#111111">BORIN</div>',
    '<div style="height:3px;background:#111111;width:170px;margin:5px 0 0"></div>',
    '<div style="display:inline-block;width:8px;height:8px;background:#C1121F;',
    'margin:0 0 0 174px;position:relative;top:-9px"></div>',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-top:-4px">projetos elétricos industriais</div>',
    "</div>",
    '<div style="padding:22px 28px 24px">',
    '<h1 style="font-size:22px;font-weight:700;margin:0 0 10px;letter-spacing:-.02em;color:#111111">',
    (nome ? nome + ", recebi seu pedido" : "Recebi seu pedido"),
    "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "Respondo com valor e prazo fechados em até 24 horas.",
    "</p>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "<b>Sua senha continua a mesma</b> — a que eu mandei no primeiro email, com o ",
    "assunto “Seu acesso”. Procure por ele na sua caixa; eu não mando senha nova ",
    "a cada pedido, justamente pra você não ficar sem saber qual vale.",
    "</p>",
    '<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;',
    'border:1px solid #DCDCDC;margin:0 0 16px">',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;width:34%;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;",
    'text-transform:uppercase;color:#6B6B6B">Endereço</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;',
    'color:#111111">borinprojetos.com.br/entrar</td></tr>',
    '<tr><td style="padding:10px 12px;font-family:Consolas,monospace;font-size:10px;',
    'letter-spacing:.08em;text-transform:uppercase;color:#6B6B6B">Email</td>',
    '<td style="padding:10px 12px;font-size:14px;color:#111111">', email, "</td></tr>",
    "</table>",
    '<p style="font-size:13px;line-height:1.6;color:#6B6B6B;margin:0">',
    "Não achou o email da senha? Responda este que eu mando outra na hora.",
    "</p></div>",
    RODAPE,
  ].join("");
}

function pedidoRecebido(contato, email) {
  const nome = (contato || "").split(" ")[0];
  return [
    '<div style="margin:0;padding:24px 16px;background:#F4F4F4;',
    "font-family:'Segoe UI',Arial,Helvetica,sans-serif\">",
    '<div style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #111111">',
    '<div style="padding:26px 28px 20px;border-bottom:1px solid #111111">',
    '<div style="font-size:30px;font-weight:700;letter-spacing:4px;color:#111111">BORIN</div>',
    '<div style="height:3px;background:#111111;width:170px;margin:5px 0 0"></div>',
    '<div style="display:inline-block;width:8px;height:8px;background:#C1121F;',
    'margin:0 0 0 174px;position:relative;top:-9px"></div>',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-top:-4px">projetos elétricos industriais</div>',
    "</div>",
    '<div style="padding:22px 28px 24px">',
    '<h1 style="font-size:22px;font-weight:700;margin:0 0 10px;letter-spacing:-.02em;color:#111111">',
    (nome ? nome + ", recebi seu pedido" : "Recebi seu pedido"),
    "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "Respondo com valor e prazo fechados em até 24 horas.",
    "</p>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "Ele já está na sua conta, em <b>borinprojetos.com.br/conta</b>, junto com os ",
    "outros que você pediu. Entre com <b>", email, "</b> e a senha que você mesmo ",
    "escolheu — esta continua valendo, eu não mando senha nova pra quem já tem conta.",
    "</p>",
    '<p style="font-size:13px;line-height:1.6;color:#6B6B6B;margin:0">',
    "Se esqueceu a senha, responda este email que eu mando outra.",
    "</p></div>",
    RODAPE,
  ].join("");
}

function boasVindas(contato, email, senha, repetido) {
  const nome = (contato || "").split(" ")[0];
  /* Pedido repetido gera senha nova e mata a anterior. Sem este aviso, o
     cliente fica com dois ou três emails IDÊNTICOS na caixa, tenta a senha do
     primeiro, erra, tenta a do segundo, erra, e no oitavo erro o freio trava
     por 15 minutos — nem a senha certa passa. Foi exatamente assim que o
     cliente ficou de fora da própria conta. */
  const aviso = repetido
    ? ['<div style="padding:0 28px 0"><p style="font-size:13px;line-height:1.6;',
       'margin:0 0 16px;padding:11px 13px;border:1px solid #C1121F;color:#111111">',
       "<b>Esta senha substitui a anterior.</b> Você pediu mais de um orçamento, ",
       "então eu mandei mais de um email. Vale a senha <b>deste</b> aqui, o mais ",
       "recente — as que eu mandei antes deixaram de funcionar.",
       "</p></div>"].join("")
    : "";
  return [
    '<div style="margin:0;padding:24px 16px;background:#F4F4F4;',
    "font-family:'Segoe UI',Arial,Helvetica,sans-serif\">",
    '<div style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #111111">',
    '<div style="padding:26px 28px 20px;border-bottom:1px solid #111111">',
    '<div style="font-size:30px;font-weight:700;letter-spacing:4px;color:#111111">BORIN</div>',
    '<div style="height:3px;background:#111111;width:170px;margin:5px 0 0"></div>',
    '<div style="display:inline-block;width:8px;height:8px;background:#C1121F;',
    'margin:0 0 0 174px;position:relative;top:-9px"></div>',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-top:-4px">projetos elétricos industriais</div>',
    "</div>",
    '<div style="padding:22px 28px 0">',
    '<h1 style="font-size:22px;font-weight:700;margin:0 0 10px;letter-spacing:-.02em;color:#111111">',
    (nome ? nome + ", recebi seu pedido" : "Recebi seu pedido"),
    "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "Respondo com valor e prazo fechados em até 24 horas. Enquanto isso, criei um acesso ",
    "para você acompanhar o projeto e preencher a parte técnica sem precisar repetir dado.",
    "</p></div>",
    aviso,
    '<div style="padding:0 28px">',
    '<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;',
    'border:1px solid #DCDCDC">',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;width:34%;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;",
    'text-transform:uppercase;color:#6B6B6B">Endereço</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;',
    'color:#111111">borinprojetos.com.br/entrar</td></tr>',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;",
    'text-transform:uppercase;color:#6B6B6B">Email</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;',
    'color:#111111">', email, "</td></tr>",
    '<tr><td style="padding:10px 12px;font-family:Consolas,monospace;font-size:10px;',
    'letter-spacing:.08em;text-transform:uppercase;color:#6B6B6B">Senha</td>',
    '<td style="padding:10px 12px;font-family:Consolas,monospace;font-size:18px;',
    'font-weight:700;letter-spacing:1px;color:#111111">', senha, "</td></tr>",
    "</table></div>",
    '<div style="padding:20px 28px 24px">',
    '<p style="font-size:13px;line-height:1.6;color:#111111;margin:0 0 12px">',
    "Na primeira entrada o site pede para você trocar essa senha por uma sua. ",
    "Ela foi gerada agora e ninguém mais tem cópia.",
    "</p>",
    '<p style="font-size:13px;line-height:1.6;color:#6B6B6B;margin:0">',
    "Não precisa entrar agora. Se preferir esperar minha resposta, este email fica guardado ",
    "e o acesso continua valendo.",
    "</p></div>",
    RODAPE,
  ].join("");
}

/**
 * Abre a conta do lead que acabou de pedir orcamento e manda a senha pra ele.
 *
 * Silencioso de proposito: se a conta ja existe, nao gera senha nova nem
 * reenvia nada — o cliente que pede dois orcamentos nao pode receber duas
 * senhas diferentes e ficar sem saber qual vale.
 */
export async function contaDoLead(env, email, empresa, contato) {
  const chave = normalizarEmail(email);
  if (!chave.includes("@")) return { estado: "email_invalido" };

  const cru = await env.CLIENTES.get("cliente:" + chave);
  const antes = cru ? JSON.parse(cru) : null;

  /* Conta ATIVA e de gente que ja provou ser dona do email: nao mexe. Conta
     PENDENTE nunca foi usada por ninguem, entao um pedido novo refaz a senha e
     manda de novo — senao um estranho que digitou o email de um prospecto teu
     bloquearia o acesso dele pra sempre. */
  if (antes && antes.estado === "ativa") {
    /* Conta ativa não ganha senha nova — a senha é dele. Mas ganha resposta:
       sem isto o cliente que volta recebe silêncio absoluto. */
    try {
      const r = await enviarPara(env, {
        para: chave,
        assunto: "Recebi seu pedido — Borin Projetos Elétricos",
        corpo: pedidoRecebido(contato || antes.contato, chave),
        html: true,
      });
      return { estado: r.entregue ? "ja_tinha" : "ja_tinha_sem_entregar" };
    } catch (e) {
      console.error("conta ja existia e o aviso falhou:", e && e.message);
      return { estado: "ja_tinha_sem_email" };
    }
  }

  /* Conta PENDENTE que já existe: a senha que eu mandei antes CONTINUA
     valendo. Antes eu gerava uma nova a cada pedido, e o cliente ficava com
     três emails iguais na caixa onde só o último funcionava — foi assim que o
     Mateus se trancou pra fora da própria conta.
     Agora o pedido repetido só lembra dela: "sua senha é a que eu já mandei". */
  if (antes && antes.hash && antes.salt) {
    try {
      const r = await enviarPara(env, {
        para: chave,
        assunto: "Recebi seu pedido — Borin Projetos Elétricos",
        corpo: senhaJaFoi(contato || antes.contato, chave),
        html: true,
      });
      return { estado: r.entregue ? "reenviada" : "reenviada_sem_entregar" };
    } catch (e) {
      console.error("lembrete de senha falhou:", e && e.message);
      return { estado: "reenviada_sem_email" };
    }
  }

  const senha = gerarSenha();
  const salt = aleatorio(16);
  const velhas = [];

  await env.CLIENTES.put("cliente:" + chave, JSON.stringify({
    email: chave,
    empresa: (empresa || "").slice(0, 120) || (antes && antes.empresa) || "",
    contato: (contato || "").slice(0, 120) || (antes && antes.contato) || "",
    salt,
    hash: await derivar(senha, salt, env.PIMENTA),
    provisorias_antigas: velhas,
    criado_em: (antes && antes.criado_em) || new Date().toISOString(),
    senha_provisoria: true,
    estado: "pendente",
    origem: "pedido de orcamento pelo site",
  }), { expirationTtl: 30 * 86400 });

  try {
    const r = await enviarPara(env, {
      para: chave,
      /* assunto diferente no reenvio: na lista da caixa de entrada, dois
         emails com o mesmo assunto são indistinguíveis, e o cliente não tem
         como saber qual é o mais novo sem abrir os dois */
      assunto: antes ? "Sua senha nova — Borin Projetos Elétricos"
                     : "Seu acesso — Borin Projetos Elétricos",
      corpo: boasVindas(contato, chave, senha, !!antes),
      html: true,
    });
    return { estado: r.entregue ? (antes ? "reenviada" : "criada")
                                : "criada_sem_entregar" };
  } catch (e) {
    console.error("conta criada mas email falhou:", e && e.message);
    return { estado: "criada_sem_email" };
  }
}

/* Apaga uma conta e tudo que pende dela. Existe porque teste deixa lixo no
   banco de producao, e conta falsa misturada com cliente de verdade e pior
   que nao ter testado. So admin, e exige o email escrito por extenso. */
async function apagarConta(request, env, dados) {
  if (!ehAdmin(request, env) && (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN)) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(dados.email);
  if (!email.includes("@")) return json({ erro: "email inválido" }, 400);
  if (!(await env.CLIENTES.get("cliente:" + email))) {
    return json({ erro: "sem conta" }, 404);
  }

  const conta = JSON.parse(await env.CLIENTES.get("cliente:" + email));
  const apagados = ["cliente:" + email, "freio:" + email];

  /* Membro some sozinho. Dono leva a empresa junto: ficha, projeto, o
     registro da empresa, o indice de equipe e as contas de quem ele tinha
     liberado — senao sobra gente com login valido apontando pra uma empresa
     que nao existe mais. */
  const dono = !conta.papel || conta.papel === "dono";
  if (dono && conta.empresa_id) {
    /* `pedido:` e `proposta:` entram aqui porque sem eles a conta some e o
       histórico fica órfão: o painel passou a mostrar 38 pedidos com 2
       clientes, todos sem nome, e não havia como saber de quem eram. */
    for (const prefixo of ["ficha:", "projeto:", "pedido:", "proposta:"]) {
      const l = await env.CLIENTES.list({ prefix: prefixo + conta.empresa_id + ":" });
      for (const k of l.keys) { apagados.push(k.name); }
    }
    const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
    for (const em of (idx ? JSON.parse(idx) : [])) {
      apagados.push("cliente:" + em, "freio:" + em);
    }
    apagados.push("empresa:" + conta.empresa_id, "equipe:" + conta.empresa_id);

    /* O acervo do R2 morre junto. Sem isto, apagar a conta deixava os PDFs
       da empresa orfaos no bucket — em 05/08/2026 havia 6 contratos de conta
       de teste apagada acumulados la, cada um com nome e dados de "cliente".
       Arquivo orfao e o pior tipo de lixo: nenhuma tela lista, nenhum dono
       reclama, e o dado pessoal fica pra sempre. */
    try {
      let cursor;
      do {
        const acervo = await env.ARQUIVOS.list(
          { prefix: conta.empresa_id + "/", cursor });
        for (const o of acervo.objects) { await env.ARQUIVOS.delete(o.key); }
        cursor = acervo.truncated ? acervo.cursor : null;
      } while (cursor);
    } catch (e) {
      /* nao derruba a exclusao da conta, mas nao pode ser silencioso */
      console.error("acervo R2 nao apagado de " + conta.empresa_id + ":",
                    e && e.message);
    }
  } else if (conta.empresa_id) {
    const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
    const resto = (idx ? JSON.parse(idx) : []).filter((x) => x !== email);
    await env.CLIENTES.put("equipe:" + conta.empresa_id, JSON.stringify(resto));
  }

  /* a sessao morre junto, senao quem foi apagado segue dentro */
  const sessoes = await env.CLIENTES.list({ prefix: "sessao:" });
  for (const k of sessoes.keys) {
    const dono_da_sessao = await env.CLIENTES.get(k.name);
    if (apagados.includes("cliente:" + dono_da_sessao)) { apagados.push(k.name); }
  }

  for (const chave of apagados) { await env.CLIENTES.delete(chave); }
  return json({ ok: true, email, apagados: apagados.length });
}

/* ---------------------------------------------------------------- equipe */

async function verEquipe(request, env) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);
  const e = await listarEquipe(env, s.conta);
  return json({ ok: true, papel: papelDe(s.conta),
                papel_nome: PAPEIS[papelDe(s.conta)].nome,
                pode_liberar: podeLiberar(s.conta), eu: s.email, ...e });
}

/**
 * O dono libera acesso pra alguem da equipe dele. A conta nasce com senha
 * gerada e a senha vai por email — mesmo caminho do lead, um passo a menos
 * pra errar, e o funcionario entra do celular sem clicar em link que expira.
 */
async function liberarAcesso(request, env, dados) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const r = await adicionarMembro(env, s.conta, s.email, dados);
  if (r.erro) return json({ erro: r.erro }, r.status || 400);

  const hash = await derivar(r.senha, r.saltHex, env.PIMENTA);
  await gravarMembro(env, { ...s.conta, email: s.email }, r, hash);

  const entregue = await avisarNovoMembro(env, s.conta.empresa || "", r);
  return json({ ok: true, email: r.alvo, entregue,
                senha: entregue ? undefined : r.senha });
}

async function tirarAcesso(request, env, dados) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);
  const r = await removerMembro(env, s.conta, dados.email);
  if (r.erro) return json({ erro: r.erro }, r.status || 400);
  return json(r);
}

export async function rotaAcesso(request, env, url) {
  const rota = url.pathname.replace(/^\/api\/acesso\/?/, "");

  if (request.method === "GET") {
    if (rota === "eu") return eu(request, env);
    /* o front pergunta se o login com Google esta ligado. client_id e
       informacao publica (vai dentro da propria pagina em qualquer site que
       use Google); null = botao nao aparece, em vez de um botao morto */
    if (rota === "google") return json({ client_id: env.GOOGLE_CLIENT_ID || null });
    if (rota === "microsoft") return json({ client_id: env.MICROSOFT_CLIENT_ID || null });
    if (rota === "ficha") return lerFicha(request, env, url);
    if (rota === "projetos") return listarProjetos(request, env);
    if (rota === "equipe") return verEquipe(request, env);
    if (rota === "cliente") return lerCliente(request, env, url);
    if (rota === "arquivos") return verArquivos(request, env, url);
    if (rota === "arquivo") return baixarArquivo(request, env, url);
    if (rota === "arquivos-admin") return listarComoAdmin(request, env, url);
    if (rota === "painel") return verPainel(request, env);
    return json({ erro: "rota desconhecida" }, 404);
  }

  /* O upload vem com o arquivo CRU no corpo, e tem que ser tratado antes do
     JSON.parse lá embaixo — passar um PDF por JSON.parse estoura, e passar por
     base64 inflaria 33% um arquivo que já pode ter 60 MB. */
  if (request.method === "PUT" && rota === "arquivo") {
    return subirArquivo(request, env, url);
  }

  if (request.method !== "POST") return json({ erro: "metodo nao permitido" }, 405);

  let dados;
  try {
    dados = JSON.parse(await request.text());
  } catch (e) {
    return json({ erro: "pedido inválido" }, 400);
  }

  if (rota === "criar") return criar(request, env, dados);
  if (rota === "entrar") return entrar(request, env, dados);
  if (rota === "google") return entrarComGoogle(request, env, dados);
  if (rota === "microsoft") return entrarComMicrosoft(request, env, dados);
  if (rota === "trocar") return trocarSenha(request, env, dados);
  if (rota === "reenviar") return reenviarSenha(request, env, dados);
  if (rota === "sair") return sair(request, env);
  if (rota === "ficha") return guardarFicha(request, env, dados);
  if (rota === "projeto") return gravarProjeto(request, env, dados);
  if (rota === "apagar") return apagarConta(request, env, dados);
  if (rota === "equipe") return liberarAcesso(request, env, dados);
  if (rota === "equipe-remover") return tirarAcesso(request, env, dados);
  if (rota === "equipe-papel") return mudarPapel(request, env, dados);
  if (rota === "arquivo-apagar") return apagarDoProjeto(request, env, dados);
  if (rota === "proposta") return gravarProposta(request, env, dados);
  return json({ erro: "rota desconhecida" }, 404);
}

/** Registra a proposta na conta do cliente. Chamado pelo orcamento.py. */
async function gravarProposta(request, env, dados) {
  if (!ehAdmin(request, env)) return json({ erro: "nao autorizado" }, 401);

  const email = normalizarEmail(dados.email || "");
  const cru = email ? await env.CLIENTES.get("cliente:" + email) : null;
  if (!cru) return json({ erro: "sem conta para esse email" }, 404);

  const conta = await garantirEmpresa(env, email, JSON.parse(cru));
  if (!conta.empresa_id) return json({ erro: "conta sem empresa" }, 409);

  const r = await guardarProposta(env, conta.empresa_id, dados);
  if (!r) return json({ erro: "informe o numero da proposta" }, 400);
  return json({ ok: true, proposta: r });
}

async function mudarPapel(request, env, dados) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);
  const r = await trocarPapel(env, s.conta, dados.email, dados.papel);
  if (r.erro) return json({ erro: r.erro }, r.status || 400);
  return json(r);
}

/* --------------------------------------------------------------- arquivos */

/**
 * Os arquivos de um projeto.
 *
 * A empresa vem SEMPRE da sessão, nunca do pedido. Se viesse de um parâmetro,
 * trocar um id na URL entregaria o acervo do vizinho — e acervo de projeto
 * elétrico é justamente o que o cliente não quer que circule.
 *
 * De propósito NÃO exijo que exista o registro `projeto:` pra listar. O Mateus
 * sobe arquivo no ritmo dele; exigir o registro faria a pasta aparecer vazia
 * sem ninguém entender por quê, que é o pior tipo de defeito.
 */
async function verArquivos(request, env, url) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const codigo = limparCodigo(url.searchParams.get("codigo") || "");
  if (!codigo) return json({ erro: "informe o projeto" }, 400);

  const arquivos = await listarArquivos(env, s.empresa, codigo);
  return json({ ok: true, codigo, arquivos });
}

async function baixarArquivo(request, env, url) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const codigo = limparCodigo(url.searchParams.get("codigo") || "");
  const nome = url.searchParams.get("nome") || "";
  if (!codigo || !nome) return json({ erro: "informe o projeto e o arquivo" }, 400);

  const r = await lerArquivo(env, s.empresa, codigo, nome);
  if (!r) return json({ erro: "arquivo não encontrado" }, 404);
  return r;
}

/**
 * A mesma lista, do lado do Mateus.
 *
 * Existe pra ele conferir o que o cliente vê sem precisar entrar na conta do
 * cliente. Usa a MESMA função de listagem que a tela usa, de propósito: uma
 * segunda implementação divergiria com o tempo e ele confiaria numa lista que
 * não é a que o cliente abre.
 */
async function listarComoAdmin(request, env, url) {
  if (!ehAdmin(request, env)) return json({ erro: "nao autorizado" }, 401);

  const email = normalizarEmail(url.searchParams.get("email") || "");
  const codigo = limparCodigo(url.searchParams.get("codigo") || "");
  if (!email || !codigo) return json({ erro: "informe email e codigo" }, 400);

  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return json({ erro: "sem conta para esse email" }, 404);
  const conta = JSON.parse(cru);
  if (!conta.empresa_id) return json({ ok: true, codigo, arquivos: [] });

  const arquivos = await listarArquivos(env, conta.empresa_id, codigo);
  return json({ ok: true, codigo, arquivos });
}

/** O painel. Só o Mateus, e o segredo vai no cabeçalho — nunca na URL. */
async function verPainel(request, env) {
  if (!ehAdmin(request, env)) return json({ erro: "nao autorizado" }, 401);
  return json(await montarPainel(env));
}

/** Sobe. Só o Mateus, com o segredo — o cliente nunca escreve no acervo. */
async function subirArquivo(request, env, url) {
  if (!ehAdmin(request, env)) return json({ erro: "nao autorizado" }, 401);

  const email = normalizarEmail(url.searchParams.get("email") || "");
  const codigo = limparCodigo(url.searchParams.get("codigo") || "");
  const nome = url.searchParams.get("nome") || "";
  if (!email || !codigo || !nome) {
    return json({ erro: "informe email, codigo e nome" }, 400);
  }

  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return json({ erro: "sem conta para esse email" }, 404);
  const conta = await garantirEmpresa(env, email, JSON.parse(cru));
  if (!conta.empresa_id) return json({ erro: "conta sem empresa" }, 409);

  /* O limite é conferido pelo cabeçalho ANTES de ler o corpo: descobrir que
     passou depois de puxar 200 MB já custou a memória do Worker. */
  const tamanho = Number(request.headers.get("content-length") || 0);
  if (tamanho > LIMITE_ARQUIVO) {
    return json({ erro: "arquivo maior que o limite de 60 MB" }, 413);
  }

  const bytes = await request.arrayBuffer();
  if (!bytes.byteLength) return json({ erro: "arquivo vazio" }, 400);
  if (bytes.byteLength > LIMITE_ARQUIVO) {
    return json({ erro: "arquivo maior que o limite de 60 MB" }, 413);
  }

  const chave = await guardarArquivo(env, conta.empresa_id, codigo, nome, bytes, {
    titulo: url.searchParams.get("titulo") || "",
    etapa: url.searchParams.get("etapa") || "",
  });
  return json({ ok: true, chave, bytes: bytes.byteLength });
}

async function apagarDoProjeto(request, env, dados) {
  if (!ehAdmin(request, env)) return json({ erro: "nao autorizado" }, 401);
  const email = normalizarEmail(dados.email || "");
  const cru = email ? await env.CLIENTES.get("cliente:" + email) : null;
  if (!cru) return json({ erro: "sem conta para esse email" }, 404);
  const conta = JSON.parse(cru);
  if (!conta.empresa_id) return json({ erro: "conta sem empresa" }, 409);
  await apagarArquivo(env, conta.empresa_id, dados.codigo || "", dados.nome || "");
  return json({ ok: true });
}
