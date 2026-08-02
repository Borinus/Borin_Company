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
         removerMembro, avisarNovoMembro } from "./equipe.js";

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
   orcamento. Depois disso so existe o hash. */
/* sem I, l, O, 0 e 1: essa senha vai ser lida em voz alta e digitada
   por uma pessoa, provavelmente do celular */
function gerarSenha() {
  const letras = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  return [...bytes].map((b) => letras[b % letras.length]).join("");
}

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
  const conta = {
    email,
    empresa: (dados.empresa || "").slice(0, 120),
    contato: (dados.contato || "").slice(0, 120),
    salt,
    hash: await derivar(senha, salt, env.PIMENTA),
    criado_em: new Date().toISOString(),
    senha_provisoria: true,
  };
  if (existente) {
    const velho = JSON.parse(existente);
    conta.criado_em = velho.criado_em;
    conta.empresa = conta.empresa || velho.empresa;
    conta.contato = conta.contato || velho.contato;
  }
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
  const tentativa = await derivar(senha, conta.salt, env.PIMENTA);

  if (!cru || !igual(tentativa, conta.hash)) {
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

async function trocarSenha(request, env, dados) {
  const eu = await quemE(request, env);
  if (!eu) return json({ erro: "sua sessão expirou. entre de novo" }, 401);

  const nova = typeof dados.nova === "string" ? dados.nova : "";
  if (nova.length < 8) return json({ erro: "a senha precisa de 8 caracteres ou mais" }, 400);

  const atual = await derivar(dados.atual || "", eu.conta.salt, env.PIMENTA);
  if (!igual(atual, eu.conta.hash)) return json({ erro: "senha atual não confere" }, 401);

  const salt = aleatorio(16);
  const conta = { ...eu.conta, salt, hash: await derivar(nova, salt, env.PIMENTA), senha_provisoria: false };
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

  if (!s.dono) return json({ erro: "só quem contratou preenche as fichas" }, 403);

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
  if (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN) {
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

  return json({
    entrou: true,
    papel: s.dono ? "dono" : "membro",
    empresa: s.conta.empresa,
    contato: s.conta.contato,
    email: s.email,
    etapas: ETAPAS,
    projetos,
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
function boasVindas(contato, email, senha) {
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
    '<div style="padding:22px 28px 0">',
    '<h1 style="font-size:22px;font-weight:700;margin:0 0 10px;letter-spacing:-.02em;color:#111111">',
    (nome ? nome + ", recebi seu pedido" : "Recebi seu pedido"),
    "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "Respondo com valor e prazo fechados em até 24 horas. Enquanto isso, criei um acesso ",
    "para você acompanhar o projeto e preencher a parte técnica sem precisar repetir dado.",
    "</p></div>",
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
    '<div style="padding:14px 28px;border-top:1px solid #DCDCDC;',
    'font-family:Consolas,monospace;font-size:10px;color:#6B6B6B">',
    "Borin Projetos Elétricos &middot; CNPJ 65.749.097/0001-85 &middot; Caxias do Sul / RS<br>",
    "contato@borinprojetos.com.br &middot; borinprojetos.com.br",
    "</div></div></div>",
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

  const existente = await env.CLIENTES.get("cliente:" + chave);
  if (existente) return { estado: "ja_tinha" };

  const senha = gerarSenha();
  const salt = aleatorio(16);
  await env.CLIENTES.put("cliente:" + chave, JSON.stringify({
    email: chave,
    empresa: (empresa || "").slice(0, 120),
    contato: (contato || "").slice(0, 120),
    salt,
    hash: await derivar(senha, salt, env.PIMENTA),
    criado_em: new Date().toISOString(),
    senha_provisoria: true,
    origem: "pedido de orcamento pelo site",
  }));

  try {
    const r = await enviarPara(env, {
      para: chave,
      assunto: "Seu acesso — Borin Projetos Elétricos",
      corpo: boasVindas(contato, chave, senha),
      html: true,
    });
    return { estado: r.entregue ? "criada" : "criada_sem_entregar" };
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
    for (const prefixo of ["ficha:", "projeto:"]) {
      const l = await env.CLIENTES.list({ prefix: prefixo + conta.empresa_id + ":" });
      for (const k of l.keys) { apagados.push(k.name); }
    }
    const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
    for (const em of (idx ? JSON.parse(idx) : [])) {
      apagados.push("cliente:" + em, "freio:" + em);
    }
    apagados.push("empresa:" + conta.empresa_id, "equipe:" + conta.empresa_id);
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
  return json({ ok: true, papel: s.dono ? "dono" : "membro", eu: s.email, ...e });
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
    if (rota === "ficha") return lerFicha(request, env, url);
    if (rota === "projetos") return listarProjetos(request, env);
    if (rota === "equipe") return verEquipe(request, env);
    if (rota === "cliente") return lerCliente(request, env, url);
    return json({ erro: "rota desconhecida" }, 404);
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
  if (rota === "trocar") return trocarSenha(request, env, dados);
  if (rota === "sair") return sair(request, env);
  if (rota === "ficha") return guardarFicha(request, env, dados);
  if (rota === "projeto") return gravarProjeto(request, env, dados);
  if (rota === "apagar") return apagarConta(request, env, dados);
  if (rota === "equipe") return liberarAcesso(request, env, dados);
  if (rota === "equipe-remover") return tirarAcesso(request, env, dados);
  return json({ erro: "rota desconhecida" }, 404);
}
