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
  return { email, token, conta: JSON.parse(cru) };
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
async function criar(request, env, dados) {
  if (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(dados.email);
  if (!email.includes("@")) return json({ erro: "email inválido" }, 400);

  const existente = await env.CLIENTES.get("cliente:" + email);
  if (existente && !dados.trocar) {
    return json({ erro: "ja existe. use trocar:true para gerar outra senha" }, 409);
  }

  /* sem I, l, O, 0 e 1: essa senha vai ser lida e digitada por uma pessoa */
  const letras = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  const senha = [...bytes].map((b) => letras[b % letras.length]).join("");

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

  await env.CLIENTES.put("ficha:" + s.email + ":" + tipo,
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
  const cru = await env.CLIENTES.get("ficha:" + s.email + ":" + tipo);
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

async function gravarProjeto(request, env, dados) {
  if (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(dados.email);
  const codigo = (dados.codigo || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 30);
  if (!email.includes("@") || !codigo) return json({ erro: "informe email e codigo" }, 400);

  const conta = await env.CLIENTES.get("cliente:" + email);
  if (!conta) return json({ erro: "esse email nao tem conta ainda" }, 404);

  const chave = "projeto:" + email + ":" + codigo;
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

  const lista = await env.CLIENTES.list({ prefix: "projeto:" + s.email + ":" });
  const projetos = [];
  for (const k of lista.keys) {
    const cru = await env.CLIENTES.get(k.name);
    if (cru) projetos.push(JSON.parse(cru));
  }
  projetos.sort((a, b) => (b.atualizado_em || "").localeCompare(a.atualizado_em || ""));

  /* as fichas ja preenchidas, pra ele saber o que falta */
  const fichas = await env.CLIENTES.list({ prefix: "ficha:" + s.email + ":" });
  const preenchidas = fichas.keys.map((k) => k.name.split(":").slice(2).join(":"));

  return json({
    entrou: true,
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
async function lerCliente(request, env, url) {
  if (!env.SEGREDO_ADMIN || url.searchParams.get("segredo") !== env.SEGREDO_ADMIN) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(url.searchParams.get("email"));
  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return json({ erro: "sem conta" }, 404);
  const conta = JSON.parse(cru);
  delete conta.hash; delete conta.salt;

  const fichas = {};
  const lista = await env.CLIENTES.list({ prefix: "ficha:" + email + ":" });
  for (const k of lista.keys) {
    const v = await env.CLIENTES.get(k.name);
    if (v) fichas[k.name.split(":").slice(2).join(":")] = JSON.parse(v).dados;
  }
  return json({ ok: true, conta, fichas });
}

/* Avisa o Mateus quando o cliente termina o cadastro — senao ele so descobre
   se ficar checando. E o gatilho pra reenviar o contrato preenchido. */
const NL = String.fromCharCode(10);
const CRLF = String.fromCharCode(13, 10);

function b64texto(t) {
  const b = new TextEncoder().encode(t);
  let bin = "";
  b.forEach((x) => { bin += String.fromCharCode(x); });
  return btoa(bin);
}

/* Avisa o Mateus quando o cliente termina o cadastro — senao ele so descobre
   se ficar checando. E o gatilho pra reenviar o contrato preenchido. */
async function avisarCadastro(env, email, dados) {
  if (!env.EMAIL) return;
  const linhas = Object.entries(dados || {})
    .filter(([, v]) => v)
    .map(([k, v]) => "  " + k + ": " + String(v).slice(0, 120))
    .join(NL);
  const corpo = "O cliente " + email + " completou o cadastro da empresa." + NL + NL
    + linhas + NL + NL + "Para reenviar o contrato preenchido:" + NL
    + "  python comercial/reenviar-contrato.py --cliente " + email + " --enviar" + NL;
  try {
    const { EmailMessage } = await import("cloudflare:email");
    const bruto = [
      "From: Borin Projetos <" + env.REMETENTE + ">",
      "To: <" + env.DESTINO + ">",
      "Subject: =?UTF-8?B?" + b64texto("Cadastro completo: "
        + (dados.razao_social || email)) + "?=",
      "Message-ID: <" + crypto.randomUUID() + "@borinprojetos.com.br>",
      "Date: " + new Date().toUTCString(),
      "MIME-Version: 1.0",
      'Content-Type: text/plain; charset="utf-8"',
      "Content-Transfer-Encoding: base64",
      "",
      b64texto(corpo).replace(/(.{76})/g, "$1" + CRLF),
    ].join(CRLF);
    await env.EMAIL.send(new EmailMessage(env.REMETENTE, env.DESTINO, bruto));
  } catch (e) {
    console.error("aviso de cadastro falhou:", e && e.message);
  }
}

export async function rotaAcesso(request, env, url) {
  const rota = url.pathname.replace(/^\/api\/acesso\/?/, "");

  if (request.method === "GET") {
    if (rota === "eu") return eu(request, env);
    if (rota === "ficha") return lerFicha(request, env, url);
    if (rota === "projetos") return listarProjetos(request, env);
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
  return json({ erro: "rota desconhecida" }, 404);
}
