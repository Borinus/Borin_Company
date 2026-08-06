/**
 * Empresa e equipe.
 *
 * O modelo original prendia tudo ao email de uma pessoa: projeto:<email>:<cod>,
 * ficha:<email>:<tipo>. Funciona pra um cliente sozinho e quebra no primeiro
 * pedido real — o dono quer que o pessoal do campo abra o diagrama no celular
 * sem ele repassar arquivo por WhatsApp.
 *
 * Agora existe a EMPRESA. Projeto e ficha pertencem a ela, e as pessoas são
 * membros:
 *
 *   empresa:<id>          { id, nome, cnpj, dono, criada_em }
 *   cliente:<email>       { ..., empresa_id: <id>, empresa: "<nome>", papel }
 *   projeto:<id>:<codigo> { ... }
 *   ficha:<id>:<tipo>     { ... }
 *
 * O id fica em `empresa_id`, NUNCA em `empresa`. O campo `empresa` ja existia
 * e guarda o NOME que o cliente digitou — é ele que aparece na tela e no
 * email. Guardar o id ali faria a conta do cliente exibir "aB3xK9mQ2pLt" no
 * lugar de "Metalúrgica Serra Ltda", e perderia o nome pra sempre.
 *
 * Papéis, de propósito só dois:
 *   dono   — quem pediu o orçamento. Convida, remove, preenche ficha.
 *   membro — lê projeto e baixa arquivo. Não convida, não preenche, não paga.
 *
 * Não há convite com token e link de aceite. O dono digita o email, a conta
 * nasce com senha gerada e a senha vai por email — o mesmo caminho que já
 * funciona pro lead. Um passo a menos pra errar, e o membro entra do celular
 * sem clicar em link que expira.
 */

import { enviarPara } from "./correio.js";

const ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";

export function novoId() {
  const b = crypto.getRandomValues(new Uint8Array(12));
  return [...b].map((x) => ALFABETO[x % ALFABETO.length]).join("");
}

/**
 * A senha que vai por email.
 *
 * Era `HUzpXs5RTaab`: doze caracteres misturando maiúscula, minúscula e
 * número. Ninguém digita isso do celular sem errar, e ninguém dita isso por
 * telefone. Agora é uma palavra que a pessoa já conhece mais um número:
 *
 *     BORIN482913
 *
 * Seis dígitos, e não quatro, por conta única e exclusivamente da conta:
 * quatro dígitos são 10 mil combinações e o freio de login solta 8 tentativas
 * a cada 15 minutos — daria pra abrir a conta de alguém em menos de uma
 * semana de tentativa automática. Seis dígitos são um milhão, o que leva a
 * mesma tentativa pra casa dos anos. O prefixo é fixo de propósito: ele não
 * conta como segredo (quem ataca sabe qual é), serve pra pessoa reconhecer de
 * onde veio e pra ficar fácil de ler em voz alta.
 */
const PREFIXO_SENHA = "BORIN";

export function gerarSenha() {
  const b = crypto.getRandomValues(new Uint32Array(1));
  /* módulo direto em 32 bits enviesaria os primeiros números; descartar o
     resto que não fecha um milhão redondo mantém os dígitos parelhos */
  let n = b[0];
  while (n >= 4294000000) {
    n = crypto.getRandomValues(new Uint32Array(1))[0];
  }
  return PREFIXO_SENHA + String(n % 1000000).padStart(6, "0");
}

/** A senha gerada aqui é sempre em caixa alta — quem digitou em minúscula não
 *  errou a senha, errou o shift. Vale só pra senha provisória: a que o cliente
 *  escolhe continua diferenciando maiúscula de minúscula. */
export function ehSenhaGerada(v) {
  return new RegExp("^" + PREFIXO_SENHA + "[0-9]{6}$", "i").test(String(v || "").trim());
}

/**
 * Toda conta precisa pertencer a uma empresa. As que existem desde antes deste
 * arquivo não pertencem, então a empresa nasce na primeira vez que a conta é
 * usada — com o titular como dono. Migração sem janela de manutenção e sem
 * script separado que alguém esquece de rodar.
 */
export async function garantirEmpresa(env, email, conta) {
  if (conta && conta.empresa_id) return conta;

  const id = novoId();
  await env.CLIENTES.put("empresa:" + id, JSON.stringify({
    id,
    nome: conta.empresa || "",
    dono: email,
    criada_em: conta.criado_em || new Date().toISOString(),
  }));

  const nova = { ...conta, empresa_id: id, papel: "dono" };
  await env.CLIENTES.put("cliente:" + email, JSON.stringify(nova));

  /* o que era da pessoa passa a ser da empresa. `pedido:` entra aqui porque o
     orçamento é registrado no instante em que o site recebe o formulário — a
     conta ainda é pendente e não tem empresa nenhuma. Sem esta linha, o
     histórico do cliente ficaria preso na chave antiga e a conta dele abriria
     vazia justamente no primeiro pedido, que é o único que ele já fez. */
  for (const prefixo of ["projeto:", "ficha:", "pedido:", "proposta:"]) {
    const lista = await env.CLIENTES.list({ prefix: prefixo + email + ":" });
    for (const k of lista.keys) {
      const v = await env.CLIENTES.get(k.name);
      if (v === null) continue;
      const resto = k.name.slice((prefixo + email + ":").length);
      await env.CLIENTES.put(prefixo + id + ":" + resto, v);
      await env.CLIENTES.delete(k.name);
    }
  }
  return nova;
}

/* ------------------------------------------------------------------ papéis
 *
 * Três, e a diferença que importa é o que cada um VÊ, não só o que faz.
 *
 * Antes existiam dois — dono e membro — e o membro via a conta inteira:
 * proposta, valor fechado, contrato. O eletricista que abre o diagrama no chão
 * de fábrica enxergava quanto o patrão dele pagou. O comentário deste arquivo
 * sempre disse "membro lê projeto e baixa arquivo", mas nada no código
 * restringia a visão — era vazamento, não permissão concedida.
 *
 *   dono     Contratante. Vê tudo, libera acesso, preenche ficha.
 *   compras  Vê tudo e preenche ficha. NÃO libera acesso.
 *   campo    Vê só projeto e arquivo. Nada de proposta, valor ou orçamento.
 */
export const PAPEIS = {
  dono: { nome: "Contratante", ve_dinheiro: true, preenche: true, libera: true },
  compras: { nome: "Compras", ve_dinheiro: true, preenche: true, libera: false },
  campo: { nome: "Campo", ve_dinheiro: false, preenche: false, libera: false },
};

/** Conta antiga sem papel é dono. `membro` legado vira `campo`: era a intenção
 *  escrita desde sempre, e apertar isso fecha o vazamento em vez de tirar um
 *  direito que alguém tinha de propósito. */
export function papelDe(conta) {
  if (!conta || !conta.papel) return "dono";
  if (conta.papel === "membro") return "campo";
  return PAPEIS[conta.papel] ? conta.papel : "campo";
}

export function podeLiberar(conta) {
  return PAPEIS[papelDe(conta)].libera;
}

export function veDinheiro(conta) {
  return PAPEIS[papelDe(conta)].ve_dinheiro;
}

export function ehDono(conta) {
  return papelDe(conta) === "dono";
}

/** Quem preenche ficha: dono e compras. Campo não. */
export function podePreencher(conta) {
  return PAPEIS[papelDe(conta)].preenche;
}

/* ------------------------------------------------------- pedidos de orçamento
 *
 * O pedido virava email e desaparecia. O cliente que preencheu o formulário há
 * duas semanas não tinha como saber se chegou, o que ele pediu, nem em que pé
 * está — só restava perguntar no WhatsApp, que é exatamente o que a conta
 * existe pra evitar. Agora fica registrado:
 *
 *   pedido:<empresa|email>:<iso>  { em, equipamento, codigo, ... }
 *
 * A chave carrega a data em ISO porque o KV lista em ordem alfabética: assim a
 * ordem da lista já sai certa sem carregar tudo pra ordenar.
 */

const ESTADO_INICIAL = "Recebido";

export async function guardarPedido(env, email, p) {
  /* a conta pode ainda nem ter empresa: o pedido é o que a CRIA. Enquanto não
     tem, a chave é o email, e o garantirEmpresa move quando ela nascer. */
  const cru = await env.CLIENTES.get("cliente:" + email);
  const conta = cru ? JSON.parse(cru) : null;
  const chave = (conta && conta.empresa_id) || email;
  const em = new Date().toISOString();

  const registro = {
    em,
    empresa: p.empresa || "",
    contato: p.contato || "",
    equipamento: p.equipamento || "",
    codigo: p.codigo || "",
    escopo: p.escopo || "",
    nr12: p.nr12 || "",
    ios: p.ios || 0,
    acionamentos: p.acionamentos || 0,
    seg_qtd: p.seg_qtd || 0,
    prazo: p.prazo || "",
    observacao: p.observacao || "",
    canal: p.canal || "email",
    fone: p.fone || "",
    /* true = avisado no celular; false = pediu WhatsApp e não saiu;
       null = escolheu só email. Sem isto o painel não distingue "o cliente já
       sabe que chegou" de "ele está esperando sem sinal nenhum". */
    zap: p.zap === undefined ? null : p.zap,
    estado: ESTADO_INICIAL,
  };

  /* Sem empresa ainda, o registro segue a validade da conta pendente: se
     ninguém nunca usar aquele email, não fica lixo pra sempre no banco. Ao
     migrar pra empresa, o put do garantirEmpresa grava sem validade. */
  const opcoes = conta && conta.empresa_id ? {} : { expirationTtl: 400 * 86400 };
  await env.CLIENTES.put("pedido:" + chave + ":" + em, JSON.stringify(registro), opcoes);
  return registro;
}

/* ------------------------------------------------------------- propostas
 *
 * A proposta existia só no email. Quem apagou sem querer, ou procurou seis
 * semanas depois, não tinha onde olhar — e valor e prazo de um projeto são
 * exatamente o que se procura depois. Agora ficam na conta:
 *
 *   proposta:<empresa>:<numero>  { numero, total, prazo, equipamento, ... }
 *
 * O contrato em PDF vai pro R2 pelo mesmo caminho dos outros arquivos, com o
 * número da proposta no lugar do código do projeto.
 */
export async function guardarProposta(env, empresa, p) {
  const numero = String(p.numero || "").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 40);
  if (!numero) return null;

  const registro = {
    numero,
    em: new Date().toISOString(),
    equipamento: String(p.equipamento || "").slice(0, 140),
    codigo: String(p.codigo || "").slice(0, 30),
    escopo: String(p.escopo || "").slice(0, 60),
    paginas: Number(p.paginas) || 0,
    total: Number(p.total) || 0,
    prazo: String(p.prazo || "").slice(0, 60),
    validade: String(p.validade || "").slice(0, 40),
    estado: String(p.estado || "Enviada").slice(0, 40),
  };
  await env.CLIENTES.put("proposta:" + empresa + ":" + numero, JSON.stringify(registro));
  return registro;
}

export async function listarPropostas(env, chave) {
  if (!chave) return [];
  const lista = await env.CLIENTES.list({ prefix: "proposta:" + chave + ":" });
  const props = [];
  for (const k of lista.keys) {
    const cru = await env.CLIENTES.get(k.name);
    if (cru) props.push(JSON.parse(cru));
  }
  props.sort((a, b) => (b.em || "").localeCompare(a.em || ""));
  return props;
}

export async function listarPedidos(env, chave) {
  if (!chave) return [];
  const lista = await env.CLIENTES.list({ prefix: "pedido:" + chave + ":" });
  const pedidos = [];
  for (const k of lista.keys) {
    const cru = await env.CLIENTES.get(k.name);
    if (cru) pedidos.push(JSON.parse(cru));
  }
  /* mais novo primeiro: é o que ele quer ver ao abrir */
  pedidos.sort((a, b) => (b.em || "").localeCompare(a.em || ""));
  return pedidos;
}

/** Quem pode ver a empresa, e em que papel. */
export async function listarEquipe(env, conta) {
  const empresa = conta.empresa_id;
  if (!empresa) return { dono: null, membros: [] };

  const cru = await env.CLIENTES.get("empresa:" + empresa);
  const e = cru ? JSON.parse(cru) : {};
  const idx = await env.CLIENTES.get("equipe:" + empresa);
  const emails = idx ? JSON.parse(idx) : [];

  const membros = [];
  for (const em of emails) {
    const c = await env.CLIENTES.get("cliente:" + em);
    if (!c) continue;
    const d = JSON.parse(c);
    membros.push({
      email: em,
      contato: d.contato || "",
      papel: papelDe(d),
      papel_nome: PAPEIS[papelDe(d)].nome,
      criado_em: d.criado_em,
      entrou_alguma_vez: !d.senha_provisoria,
    });
  }
  return { dono: e.dono || null, empresa: e.nome || "", membros };
}

async function guardarIndice(env, empresa, emails) {
  await env.CLIENTES.put("equipe:" + empresa, JSON.stringify([...new Set(emails)]));
}

/**
 * O dono libera acesso pra alguém. Se a pessoa já tem conta em OUTRA empresa,
 * recusa: uma conta não pode ver dois clientes, e mover ela por engano daria
 * a um terceiro o acervo inteiro de outra empresa.
 */
export async function adicionarMembro(env, conta, email, dados) {
  if (!podeLiberar(conta)) return { erro: "só quem contratou pode liberar acesso", status: 403 };

  const alvo = (dados.email || "").trim().toLowerCase();
  if (!alvo.includes("@") || alvo.length > 160) return { erro: "email inválido", status: 400 };

  const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
  const emails = idx ? JSON.parse(idx) : [];
  if (emails.includes(alvo)) return { erro: "essa pessoa já tem acesso", status: 409 };
  if (emails.length >= 25) return { erro: "limite de 25 pessoas por empresa", status: 409 };

  const existente = await env.CLIENTES.get("cliente:" + alvo);
  if (existente) {
    const d = JSON.parse(existente);
    if (d.empresa_id && d.empresa_id !== conta.empresa_id) {
      return { erro: "esse email já tem conta em outra empresa", status: 409 };
    }
  }

  const senha = gerarSenha();
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const saltHex = [...salt].map((b) => b.toString(16).padStart(2, "0")).join("");

  return {
    ok: true,
    alvo,
    senha,
    saltHex,
    emails: emails.concat([alvo]),
    nome: (dados.nome || "").slice(0, 120),
    /* papel escolhido na tela; qualquer coisa fora da lista cai no mais
       restrito, nunca no mais permissivo */
    papel: (dados.papel === "compras" || dados.papel === "campo")
      ? dados.papel : "campo",
  };
}

/** Troca o papel de quem já tem acesso. Só o contratante mexe. */
export async function trocarPapel(env, conta, email, papel) {
  if (!podeLiberar(conta)) return { erro: "só quem contratou muda o acesso", status: 403 };

  const alvo = (email || "").trim().toLowerCase();
  if (papel !== "compras" && papel !== "campo") {
    return { erro: "papel inválido", status: 400 };
  }
  const cru = await env.CLIENTES.get("cliente:" + alvo);
  if (!cru) return { erro: "essa pessoa não tem acesso", status: 404 };

  const d = JSON.parse(cru);
  if (d.empresa_id !== conta.empresa_id) {
    return { erro: "essa pessoa não é da sua empresa", status: 403 };
  }
  /* o contratante não pode se rebaixar: a empresa ficaria sem ninguém pra
     liberar acesso e não existe tela pra desfazer */
  if (papelDe(d) === "dono") {
    return { erro: "o contratante não muda de papel", status: 409 };
  }

  await env.CLIENTES.put("cliente:" + alvo, JSON.stringify({ ...d, papel }));
  return { ok: true, email: alvo, papel };
}

export async function gravarMembro(env, conta, r, hash) {
  await env.CLIENTES.put("cliente:" + r.alvo, JSON.stringify({
    email: r.alvo,
    /* o id manda no acesso; o nome existe só pra tela dele nao ficar vazia */
    empresa_id: conta.empresa_id,
    empresa: conta.empresa || "",
    papel: r.papel || "campo",
    contato: r.nome,
    salt: r.saltHex,
    hash,
    criado_em: new Date().toISOString(),
    senha_provisoria: true,
    /* quem responde por esse endereco e o dono da empresa, que digitou ele:
       nasce ativa e nao expira */
    estado: "ativa",
    origem: "liberado por " + (conta.email || "dono da conta"),
  }));
  await guardarIndice(env, conta.empresa_id, r.emails);
}

export async function removerMembro(env, conta, email) {
  if (!ehDono(conta)) return { erro: "só quem contratou pode remover acesso", status: 403 };
  const alvo = (email || "").trim().toLowerCase();

  const c = await env.CLIENTES.get("cliente:" + alvo);
  if (!c) return { erro: "sem conta", status: 404 };
  const d = JSON.parse(c);
  if (d.empresa_id !== conta.empresa_id) {
    return { erro: "essa pessoa não é da sua empresa", status: 403 };
  }
  if (d.papel === "dono") return { erro: "não dá para remover quem contratou", status: 400 };

  await env.CLIENTES.delete("cliente:" + alvo);
  await env.CLIENTES.delete("freio:" + alvo);
  /* a sessao aberta dele morre junto: sem isso, quem foi removido continua
     dentro ate o cookie expirar, com o acervo da empresa na mao */
  const sessoes = await env.CLIENTES.list({ prefix: "sessao:" });
  for (const k of sessoes.keys) {
    if ((await env.CLIENTES.get(k.name)) === alvo) {
      await env.CLIENTES.delete(k.name);
    }
  }

  const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
  const emails = (idx ? JSON.parse(idx) : []).filter((x) => x !== alvo);
  await guardarIndice(env, conta.empresa_id, emails);
  return { ok: true, removido: alvo };
}

/** O email que o funcionário recebe. Curto: ele vai ler no celular, no chão de fábrica. */
export function avisoDeAcesso(empresa, quem, email, senha) {
  const nome = (quem || "").split(" ")[0];
  return [
    '<div style="margin:0;padding:24px 16px;background:#F4F4F4;',
    "font-family:'Segoe UI',Arial,Helvetica,sans-serif\">",
    '<div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #111111">',
    '<div style="padding:24px 26px 18px;border-bottom:1px solid #111111">',
    '<div style="font-size:26px;font-weight:700;letter-spacing:4px;color:#111111">BORIN</div>',
    '<div style="height:3px;background:#111111;width:148px;margin:5px 0 0"></div>',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-top:5px">projetos elétricos industriais</div>',
    "</div>",
    '<div style="padding:22px 26px 0">',
    '<h1 style="font-size:20px;font-weight:700;margin:0 0 10px;color:#111111">',
    (nome ? nome + ", você tem acesso" : "Você tem acesso"), "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    empresa ? ("A " + empresa + " liberou seu acesso") : "Liberaram seu acesso",
    " aos projetos elétricos feitos pela Borin. Dá para abrir do celular, no campo.",
    "</p></div>",
    '<div style="padding:0 26px">',
    '<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;',
    'border:1px solid #DCDCDC">',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;width:32%;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;",
    'color:#6B6B6B">Endereço</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;color:#111111">',
    "borinprojetos.com.br/entrar</td></tr>",
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;",
    'color:#6B6B6B">Email</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;color:#111111">',
    email, "</td></tr>",
    '<tr><td style="padding:10px 12px;font-family:Consolas,monospace;font-size:10px;',
    'letter-spacing:.08em;text-transform:uppercase;color:#6B6B6B">Senha</td>',
    '<td style="padding:10px 12px;font-family:Consolas,monospace;font-size:18px;',
    'font-weight:700;letter-spacing:1px;color:#111111">', senha, "</td></tr>",
    "</table></div>",
    '<div style="padding:18px 26px 22px">',
    '<p style="font-size:13px;line-height:1.6;color:#6B6B6B;margin:0">',
    "Na primeira entrada o site pede para você trocar essa senha. Você vê e baixa os documentos; ",
    "quem contratou é quem preenche as fichas e libera acesso.",
    "</p></div>",
    '<div style="padding:13px 26px;border-top:1px solid #DCDCDC;',
    'font-family:Consolas,monospace;font-size:10px;color:#6B6B6B">',
    "Borin Projetos Elétricos &middot; Caxias do Sul / RS &middot; contato@borinprojetos.com.br",
    "</div></div></div>",
  ].join("");
}

export async function avisarNovoMembro(env, empresa, r) {
  try {
    await enviarPara(env, {
      para: r.alvo,
      assunto: "Seu acesso aos projetos — Borin Projetos Elétricos",
      corpo: avisoDeAcesso(empresa, r.nome, r.alvo, r.senha),
      html: true,
    });
    return true;
  } catch (e) {
    console.error("aviso de acesso falhou:", e && e.message);
    return false;
  }
}
