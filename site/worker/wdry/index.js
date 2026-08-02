var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// correio.js
import { EmailMessage } from "cloudflare:email";
function base64(bytes) {
  let bin = "";
  bytes.forEach((b) => {
    bin += String.fromCharCode(b);
  });
  return btoa(bin);
}
__name(base64, "base64");
function assuntoCodificado(texto) {
  const bytes = new TextEncoder().encode(texto);
  const partes = [];
  let i = 0;
  while (i < bytes.length) {
    let fim = Math.min(i + 15, bytes.length);
    while (fim > i && fim < bytes.length && (bytes[fim] & 192) === 128) {
      fim--;
    }
    partes.push("=?UTF-8?B?" + base64(bytes.slice(i, fim)) + "?=");
    i = fim;
  }
  return partes.join("\r\n ");
}
__name(assuntoCodificado, "assuntoCodificado");
function corpoBase64(texto) {
  return base64(new TextEncoder().encode(texto)).replace(/(.{76})/g, "$1\r\n");
}
__name(corpoBase64, "corpoBase64");
function limpo(v, max) {
  if (typeof v !== "string") {
    return "";
  }
  return v.replace(/[\r\n]+/g, " ").trim().slice(0, max || 120);
}
__name(limpo, "limpo");
function paraTexto(html) {
  return html.replace(/<style[\s\S]*?<\/style>/gi, "").replace(/<\/(div|tr|h1|h2|p)>/gi, "\n").replace(/<[^>]+>/g, "").replace(/&middot;/g, "\xB7").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ").replace(/[ \t]+/g, " ").replace(/\n\s*\n\s*\n+/g, "\n\n").trim();
}
__name(paraTexto, "paraTexto");
function montarEmail(de, para, assunto, corpo, responder, html, anexos) {
  const cab = [
    "From: Borin Projetos <" + de + ">",
    "To: <" + para + ">",
    responder ? "Reply-To: <" + responder + ">" : null,
    "Subject: " + assuntoCodificado(assunto),
    "Message-ID: <" + crypto.randomUUID() + "@borinprojetos.com.br>",
    "Date: " + (/* @__PURE__ */ new Date()).toUTCString(),
    "MIME-Version: 1.0"
  ].filter(Boolean);
  if (!html) {
    return cab.concat([
      'Content-Type: text/plain; charset="utf-8"',
      "Content-Transfer-Encoding: base64",
      "",
      corpoBase64(corpo)
    ]).join("\r\n");
  }
  const alt = "alt" + crypto.randomUUID().replace(/-/g, "");
  const corpoAlt = [
    'Content-Type: multipart/alternative; boundary="' + alt + '"',
    "",
    "--" + alt,
    'Content-Type: text/plain; charset="utf-8"',
    "Content-Transfer-Encoding: base64",
    "",
    corpoBase64(paraTexto(corpo)),
    "--" + alt,
    'Content-Type: text/html; charset="utf-8"',
    "Content-Transfer-Encoding: base64",
    "",
    corpoBase64(corpo),
    "--" + alt + "--"
  ];
  if (!anexos || !anexos.length) {
    return cab.concat(corpoAlt).join("\r\n");
  }
  const mix = "mix" + crypto.randomUUID().replace(/-/g, "");
  const partes = [
    'Content-Type: multipart/mixed; boundary="' + mix + '"',
    "",
    "--" + mix
  ].concat(corpoAlt);
  for (const a of anexos) {
    partes.push(
      "--" + mix,
      "Content-Type: " + (a.tipo || "application/octet-stream") + '; name="' + (a.nome || "anexo") + '"',
      "Content-Transfer-Encoding: base64",
      'Content-Disposition: attachment; filename="' + (a.nome || "anexo") + '"',
      "",
      String(a.base64 || "").replace(/\s+/g, "").replace(/(.{76})/g, "$1\r\n")
    );
  }
  partes.push("--" + mix + "--", "");
  return cab.concat(partes).join("\r\n");
}
__name(montarEmail, "montarEmail");
function podeEscreverAoCliente(env) {
  return !!env.RESEND_API_KEY || env.ENVIO_ABERTO === "1";
}
__name(podeEscreverAoCliente, "podeEscreverAoCliente");
function ehODono(env, endereco) {
  const meu = (env.DESTINO || "").trim().toLowerCase();
  return !endereco || endereco.trim().toLowerCase() === meu;
}
__name(ehODono, "ehODono");
async function porBinding(env, para, bruto) {
  await env.EMAIL.send(new EmailMessage(env.REMETENTE, para, bruto));
}
__name(porBinding, "porBinding");
async function porResend(env, o, para) {
  const corpo = {
    from: "Borin Projetos <" + env.REMETENTE + ">",
    to: [para],
    subject: o.assunto
  };
  if (o.responder) {
    corpo.reply_to = o.responder;
  }
  if (o.html) {
    corpo.html = o.corpo;
    corpo.text = paraTexto(o.corpo);
  } else {
    corpo.text = o.corpo;
  }
  if (o.anexos && o.anexos.length) {
    corpo.attachments = o.anexos.map((a) => ({
      filename: a.nome || "anexo",
      content: String(a.base64 || "").replace(/\s+/g, "")
    }));
  }
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + env.RESEND_API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(corpo)
  });
  if (!r.ok) {
    const detalhe = await r.text();
    throw new Error("resend " + r.status + ": " + detalhe.slice(0, 300));
  }
}
__name(porResend, "porResend");
async function entregarAoDono(env, o, queriaIr) {
  const aviso = "ESTE EMAIL ERA PARA O CLIENTE E NAO PUDE ENTREGAR.\nDestinatario pretendido: " + queriaIr + "\nMotivo: o site ainda nao tem transporte de email para terceiros.\nRepasse este conteudo na mao, ou ligue o envio (ver site/worker/correio.js).\n\n" + "-".repeat(58) + "\n\n";
  const corpo = o.html ? '<div style="background:#FFF4F4;border:2px solid #C1121F;padding:14px;font-family:monospace;font-size:12px;color:#C1121F;white-space:pre-wrap">' + aviso.replace(/</g, "&lt;") + "</div>" + o.corpo : aviso + o.corpo;
  const bruto = montarEmail(
    env.REMETENTE,
    env.DESTINO,
    "[NAO ENTREGUE] " + o.assunto,
    corpo,
    queriaIr,
    o.html,
    o.anexos
  );
  await porBinding(env, env.DESTINO, bruto);
  return { entregue: false, para: env.DESTINO, pretendido: queriaIr };
}
__name(entregarAoDono, "entregarAoDono");
async function enviarPara(env, o) {
  const para = limpo(o.para, 160);
  const meu = ehODono(env, para);
  if (!meu && !podeEscreverAoCliente(env)) {
    return entregarAoDono(env, o, para);
  }
  const destino = meu ? env.DESTINO : para;
  if (env.RESEND_API_KEY) {
    await porResend(env, o, destino);
  } else {
    const bruto = montarEmail(
      env.REMETENTE,
      destino,
      o.assunto,
      o.corpo,
      o.responder,
      o.html,
      o.anexos
    );
    await porBinding(env, destino, bruto);
  }
  return { entregue: true, para: destino };
}
__name(enviarPara, "enviarPara");

// acesso.js
var SESSAO_HORAS = 12;
var TENTATIVAS_MAX = 8;
var TRAVA_MINUTOS = 15;
var PBKDF2_VOLTAS = 5e4;
var enc = new TextEncoder();
function hex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
__name(hex, "hex");
function aleatorio(bytes) {
  return hex(crypto.getRandomValues(new Uint8Array(bytes)));
}
__name(aleatorio, "aleatorio");
async function derivar(senha, salt, pimenta) {
  const chave = await crypto.subtle.importKey(
    "raw",
    enc.encode(senha + "|" + (pimenta || "")),
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash: "SHA-256", salt: enc.encode(salt), iterations: PBKDF2_VOLTAS },
    chave,
    256
  );
  return hex(bits);
}
__name(derivar, "derivar");
function igual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
__name(igual, "igual");
function normalizarEmail(v) {
  return typeof v === "string" ? v.trim().toLowerCase().slice(0, 160) : "";
}
__name(normalizarEmail, "normalizarEmail");
var json = /* @__PURE__ */ __name((o, status = 200, extra = {}) => new Response(JSON.stringify(o), {
  status,
  headers: { "Content-Type": "application/json; charset=utf-8", ...extra }
}), "json");
async function abrirSessao(env, email) {
  const token = aleatorio(32);
  await env.CLIENTES.put(
    "sessao:" + token,
    email,
    { expirationTtl: SESSAO_HORAS * 3600 }
  );
  const cookie = [
    "borin_sessao=" + token,
    "Path=/",
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    "Max-Age=" + SESSAO_HORAS * 3600
  ].join("; ");
  return cookie;
}
__name(abrirSessao, "abrirSessao");
function lerCookie(request, nome) {
  const cru = request.headers.get("Cookie") || "";
  for (const parte of cru.split(";")) {
    const [k, ...v] = parte.trim().split("=");
    if (k === nome) return v.join("=");
  }
  return "";
}
__name(lerCookie, "lerCookie");
async function quemE(request, env) {
  const token = lerCookie(request, "borin_sessao");
  if (!token) return null;
  const email = await env.CLIENTES.get("sessao:" + token);
  if (!email) return null;
  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return null;
  return { email, token, conta: JSON.parse(cru) };
}
__name(quemE, "quemE");
async function travado(env, email) {
  const cru = await env.CLIENTES.get("freio:" + email);
  if (!cru) return 0;
  const f = JSON.parse(cru);
  if (f.n < TENTATIVAS_MAX) return 0;
  const falta = Math.ceil((f.ate - Date.now()) / 6e4);
  return falta > 0 ? falta : 0;
}
__name(travado, "travado");
async function contarErro(env, email) {
  const cru = await env.CLIENTES.get("freio:" + email);
  const f = cru ? JSON.parse(cru) : { n: 0, ate: 0 };
  f.n += 1;
  f.ate = Date.now() + TRAVA_MINUTOS * 6e4;
  await env.CLIENTES.put(
    "freio:" + email,
    JSON.stringify(f),
    { expirationTtl: TRAVA_MINUTOS * 60 }
  );
}
__name(contarErro, "contarErro");
function gerarSenha() {
  const letras = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  return [...bytes].map((b) => letras[b % letras.length]).join("");
}
__name(gerarSenha, "gerarSenha");
async function criar(request, env, dados) {
  if (!env.SEGREDO_ADMIN || dados.segredo !== env.SEGREDO_ADMIN) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(dados.email);
  if (!email.includes("@")) return json({ erro: "email inv\xE1lido" }, 400);
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
    criado_em: (/* @__PURE__ */ new Date()).toISOString(),
    senha_provisoria: true
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
__name(criar, "criar");
async function entrar(request, env, dados) {
  const email = normalizarEmail(dados.email);
  const senha = typeof dados.senha === "string" ? dados.senha : "";
  if (!email || !senha) return json({ erro: "informe o email e a senha" }, 400);
  const preso = await travado(env, email);
  if (preso) {
    return json({ erro: "muitas tentativas. tente de novo em " + preso + " min" }, 429);
  }
  const cru = await env.CLIENTES.get("cliente:" + email);
  const conta = cru ? JSON.parse(cru) : { salt: "vazio", hash: "-" };
  const tentativa = await derivar(senha, conta.salt, env.PIMENTA);
  if (!cru || !igual(tentativa, conta.hash)) {
    await contarErro(env, email);
    return json({ erro: "email ou senha n\xE3o conferem" }, 401);
  }
  await env.CLIENTES.delete("freio:" + email);
  const cookie = await abrirSessao(env, email);
  return json({
    ok: true,
    empresa: conta.empresa,
    contato: conta.contato,
    senha_provisoria: !!conta.senha_provisoria
  }, 200, { "Set-Cookie": cookie });
}
__name(entrar, "entrar");
async function trocarSenha(request, env, dados) {
  const eu2 = await quemE(request, env);
  if (!eu2) return json({ erro: "sua sess\xE3o expirou. entre de novo" }, 401);
  const nova = typeof dados.nova === "string" ? dados.nova : "";
  if (nova.length < 8) return json({ erro: "a senha precisa de 8 caracteres ou mais" }, 400);
  const atual = await derivar(dados.atual || "", eu2.conta.salt, env.PIMENTA);
  if (!igual(atual, eu2.conta.hash)) return json({ erro: "senha atual n\xE3o confere" }, 401);
  const salt = aleatorio(16);
  const conta = { ...eu2.conta, salt, hash: await derivar(nova, salt, env.PIMENTA), senha_provisoria: false };
  await env.CLIENTES.put("cliente:" + eu2.email, JSON.stringify(conta));
  return json({ ok: true });
}
__name(trocarSenha, "trocarSenha");
async function sair(request, env) {
  const token = lerCookie(request, "borin_sessao");
  if (token) await env.CLIENTES.delete("sessao:" + token);
  return json({ ok: true }, 200, {
    "Set-Cookie": "borin_sessao=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0"
  });
}
__name(sair, "sair");
async function eu(request, env) {
  const s = await quemE(request, env);
  if (!s) return json({ entrou: false });
  return json({
    entrou: true,
    email: s.email,
    empresa: s.conta.empresa,
    contato: s.conta.contato,
    senha_provisoria: !!s.conta.senha_provisoria
  });
}
__name(eu, "eu");
async function guardarFicha(request, env, dados) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sess\xE3o expirou. entre de novo" }, 401);
  const tipo = (dados.tipo || "").replace(/[^a-zA-Z0-9:_-]/g, "").slice(0, 60);
  if (!tipo) return json({ erro: "tipo inv\xE1lido" }, 400);
  const corpo = JSON.stringify(dados.dados || {});
  if (corpo.length > 64 * 1024) return json({ erro: "ficha grande demais" }, 413);
  await env.CLIENTES.put(
    "ficha:" + s.email + ":" + tipo,
    JSON.stringify({ dados: dados.dados, em: (/* @__PURE__ */ new Date()).toISOString() })
  );
  if (tipo === "cadastro" && dados.avisar) {
    await avisarCadastro(env, s.email, dados.dados);
  }
  return json({ ok: true });
}
__name(guardarFicha, "guardarFicha");
async function lerFicha(request, env, url) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sess\xE3o expirou. entre de novo" }, 401);
  const tipo = (url.searchParams.get("tipo") || "").replace(/[^a-zA-Z0-9:_-]/g, "").slice(0, 60);
  const cru = await env.CLIENTES.get("ficha:" + s.email + ":" + tipo);
  return json(cru ? JSON.parse(cru) : { dados: null });
}
__name(lerFicha, "lerFicha");
var ETAPAS = [
  "Or\xE7amento enviado",
  "Contrato assinado",
  "Aguardando a ficha",
  "Em execu\xE7\xE3o",
  "Em confer\xEAncia",
  "Entregue",
  "Aprovado"
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
  const p = antes ? JSON.parse(antes) : { codigo, criado_em: (/* @__PURE__ */ new Date()).toISOString() };
  if (dados.nome !== void 0) p.nome = String(dados.nome).slice(0, 140);
  if (dados.status !== void 0) p.status = String(dados.status).slice(0, 60);
  if (dados.prazo !== void 0) p.prazo = String(dados.prazo).slice(0, 40);
  if (dados.link !== void 0) p.link = String(dados.link).slice(0, 500);
  if (dados.nota !== void 0) p.nota = String(dados.nota).slice(0, 400);
  p.atualizado_em = (/* @__PURE__ */ new Date()).toISOString();
  await env.CLIENTES.put(chave, JSON.stringify(p));
  return json({ ok: true, projeto: p });
}
__name(gravarProjeto, "gravarProjeto");
async function listarProjetos(request, env) {
  const s = await quemE(request, env);
  if (!s) return json({ erro: "sua sess\xE3o expirou. entre de novo" }, 401);
  const lista = await env.CLIENTES.list({ prefix: "projeto:" + s.email + ":" });
  const projetos = [];
  for (const k of lista.keys) {
    const cru = await env.CLIENTES.get(k.name);
    if (cru) projetos.push(JSON.parse(cru));
  }
  projetos.sort((a, b) => (b.atualizado_em || "").localeCompare(a.atualizado_em || ""));
  const fichas = await env.CLIENTES.list({ prefix: "ficha:" + s.email + ":" });
  const preenchidas = fichas.keys.map((k) => k.name.split(":").slice(2).join(":"));
  return json({
    entrou: true,
    empresa: s.conta.empresa,
    contato: s.conta.contato,
    email: s.email,
    etapas: ETAPAS,
    projetos,
    fichas: preenchidas
  });
}
__name(listarProjetos, "listarProjetos");
async function lerCliente(request, env, url) {
  if (!env.SEGREDO_ADMIN || url.searchParams.get("segredo") !== env.SEGREDO_ADMIN) {
    return json({ erro: "nao autorizado" }, 401);
  }
  const email = normalizarEmail(url.searchParams.get("email"));
  const cru = await env.CLIENTES.get("cliente:" + email);
  if (!cru) return json({ erro: "sem conta" }, 404);
  const conta = JSON.parse(cru);
  delete conta.hash;
  delete conta.salt;
  const fichas = {};
  const lista = await env.CLIENTES.list({ prefix: "ficha:" + email + ":" });
  for (const k of lista.keys) {
    const v = await env.CLIENTES.get(k.name);
    if (v) fichas[k.name.split(":").slice(2).join(":")] = JSON.parse(v).dados;
  }
  return json({ ok: true, conta, fichas });
}
__name(lerCliente, "lerCliente");
var NL = String.fromCharCode(10);
var CRLF = String.fromCharCode(13, 10);
async function avisarCadastro(env, email, dados) {
  const linhas = Object.entries(dados || {}).filter(([, v]) => v).map(([k, v]) => "  " + k + ": " + String(v).slice(0, 120)).join("\n");
  const corpo = "O cliente " + email + " completou o cadastro da empresa.\n\n" + linhas + "\n\nPara reenviar o contrato preenchido:\n  python comercial/reenviar-contrato.py --cliente " + email + " --enviar\n";
  try {
    await enviarPara(env, {
      para: env.DESTINO,
      assunto: "Cadastro completo: " + (dados.razao_social || email),
      corpo
    });
  } catch (e) {
    console.error("aviso de cadastro falhou:", e && e.message);
  }
}
__name(avisarCadastro, "avisarCadastro");
function boasVindas(contato, email, senha) {
  const nome = (contato || "").split(" ")[0];
  return [
    '<div style="margin:0;padding:24px 16px;background:#F4F4F4;',
    `font-family:'Segoe UI',Arial,Helvetica,sans-serif">`,
    '<div style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #111111">',
    '<div style="padding:26px 28px 20px;border-bottom:1px solid #111111">',
    '<div style="font-size:30px;font-weight:700;letter-spacing:4px;color:#111111">BORIN</div>',
    '<div style="height:3px;background:#111111;width:170px;margin:5px 0 0"></div>',
    '<div style="display:inline-block;width:8px;height:8px;background:#C1121F;',
    'margin:0 0 0 174px;position:relative;top:-9px"></div>',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-top:-4px">projetos el\xE9tricos industriais</div>',
    "</div>",
    '<div style="padding:22px 28px 0">',
    '<h1 style="font-size:22px;font-weight:700;margin:0 0 10px;letter-spacing:-.02em;color:#111111">',
    nome ? nome + ", recebi seu pedido" : "Recebi seu pedido",
    "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    "Respondo com valor e prazo fechados em at\xE9 24 horas. Enquanto isso, criei um acesso ",
    "para voc\xEA acompanhar o projeto e preencher a parte t\xE9cnica sem precisar repetir dado.",
    "</p></div>",
    '<div style="padding:0 28px">',
    '<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;',
    'border:1px solid #DCDCDC">',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;width:34%;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;",
    'text-transform:uppercase;color:#6B6B6B">Endere\xE7o</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;',
    'color:#111111">borinprojetos.com.br/entrar</td></tr>',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;",
    'text-transform:uppercase;color:#6B6B6B">Email</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;',
    'color:#111111">',
    email,
    "</td></tr>",
    '<tr><td style="padding:10px 12px;font-family:Consolas,monospace;font-size:10px;',
    'letter-spacing:.08em;text-transform:uppercase;color:#6B6B6B">Senha</td>',
    '<td style="padding:10px 12px;font-family:Consolas,monospace;font-size:18px;',
    'font-weight:700;letter-spacing:1px;color:#111111">',
    senha,
    "</td></tr>",
    "</table></div>",
    '<div style="padding:20px 28px 24px">',
    '<p style="font-size:13px;line-height:1.6;color:#111111;margin:0 0 12px">',
    "Na primeira entrada o site pede para voc\xEA trocar essa senha por uma sua. ",
    "Ela foi gerada agora e ningu\xE9m mais tem c\xF3pia.",
    "</p>",
    '<p style="font-size:13px;line-height:1.6;color:#6B6B6B;margin:0">',
    "N\xE3o precisa entrar agora. Se preferir esperar minha resposta, este email fica guardado ",
    "e o acesso continua valendo.",
    "</p></div>",
    '<div style="padding:14px 28px;border-top:1px solid #DCDCDC;',
    'font-family:Consolas,monospace;font-size:10px;color:#6B6B6B">',
    "Borin Projetos El\xE9tricos &middot; CNPJ 65.749.097/0001-85 &middot; Caxias do Sul / RS<br>",
    "contato@borinprojetos.com.br &middot; borinprojetos.com.br",
    "</div></div></div>"
  ].join("");
}
__name(boasVindas, "boasVindas");
async function contaDoLead(env, email, empresa, contato) {
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
    criado_em: (/* @__PURE__ */ new Date()).toISOString(),
    senha_provisoria: true,
    origem: "pedido de orcamento pelo site"
  }));
  try {
    const r = await enviarPara(env, {
      para: chave,
      assunto: "Seu acesso \u2014 Borin Projetos El\xE9tricos",
      corpo: boasVindas(contato, chave, senha),
      html: true
    });
    return { estado: r.entregue ? "criada" : "criada_sem_entregar" };
  } catch (e) {
    console.error("conta criada mas email falhou:", e && e.message);
    return { estado: "criada_sem_email" };
  }
}
__name(contaDoLead, "contaDoLead");
async function rotaAcesso(request, env, url) {
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
    return json({ erro: "pedido inv\xE1lido" }, 400);
  }
  if (rota === "criar") return criar(request, env, dados);
  if (rota === "entrar") return entrar(request, env, dados);
  if (rota === "trocar") return trocarSenha(request, env, dados);
  if (rota === "sair") return sair(request, env);
  if (rota === "ficha") return guardarFicha(request, env, dados);
  if (rota === "projeto") return gravarProjeto(request, env, dados);
  return json({ erro: "rota desconhecida" }, 404);
}
__name(rotaAcesso, "rotaAcesso");

// index.js
var LIMITE = 24 * 1024;
var LIMITE_PEDIDO = 6 * 1024 * 1024;
var index_default = {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/acesso")) {
      return rotaAcesso(request, env, url);
    }
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }
    if (request.method !== "POST") {
      return new Response("metodo nao permitido", { status: 405 });
    }
    let dados;
    try {
      const cru = await request.text();
      if (cru.length > LIMITE_PEDIDO) {
        return new Response("pedido grande demais", { status: 413 });
      }
      dados = JSON.parse(cru);
    } catch (e) {
      return new Response("corpo invalido", { status: 400 });
    }
    if (limpo(dados.website)) {
      return Response.json({ ok: true });
    }
    const empresa = limpo(dados.empresa) || "sem empresa";
    const contato = limpo(dados.contato);
    const email = limpo(dados.email, 160);
    const texto = typeof dados.texto === "string" ? dados.texto.slice(0, LIMITE) : "";
    if (!texto) {
      return new Response("pedido vazio", { status: 400 });
    }
    const cabecalho = dados.html === true ? "" : "Pedido recebido pelo site.\nOrigem: " + limpo(dados.intencao) + "\n" + (request.headers.get("cf-connecting-ip") ? "IP: " + request.headers.get("cf-connecting-ip") + "\n" : "") + "\n" + "-".repeat(50) + "\n\n";
    const codigo = limpo(dados.codigo, 30);
    const equip = limpo(dados.equipamento, 60);
    const doc = limpo(dados.doc, 40) || "Pedido de or\xE7amento";
    let assunto = codigo ? "#" + codigo + " \xB7 " + empresa : empresa;
    assunto += " \u2014 " + (equip || doc);
    if (equip && doc && doc !== "Pedido de or\xE7amento") {
      assunto += " \xB7 " + doc;
    }
    const paraCliente = dados.para_cliente === true && email.includes("@");
    let entrega;
    try {
      entrega = await enviarPara(env, {
        para: paraCliente ? email : env.DESTINO,
        assunto,
        corpo: cabecalho + texto,
        responder: email.includes("@") ? email : null,
        /* proposta vai como HTML pra o cliente ver o documento, nao um txt */
        html: dados.html === true,
        anexos: Array.isArray(dados.anexos) ? dados.anexos.slice(0, 4) : null
      });
    } catch (e) {
      console.error("falha ao enviar:", e && e.message);
      return Response.json({ ok: false }, { status: 200 });
    }
    let conta = null;
    if (!paraCliente && email.includes("@") && limpo(dados.intencao) === "site") {
      try {
        conta = await contaDoLead(env, email, empresa, contato);
      } catch (e) {
        console.error("nao criei a conta do lead:", e && e.message);
      }
    }
    return Response.json({
      ok: true,
      entregue: entrega ? entrega.entregue : false,
      conta: conta ? conta.estado : null
    });
  }
};
export {
  index_default as default
};
//# sourceMappingURL=index.js.map
