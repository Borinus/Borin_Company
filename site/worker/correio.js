/**
 * Correio — a única porta de saída de email do site.
 *
 * Antes deste arquivo, o destinatário estava escrito na mão em dois lugares
 * (index.js e acesso.js), sempre como env.DESTINO. Resultado: TODO email que o
 * site produzia chegava no Mateus, inclusive os que eram escritos para o
 * cliente. O endereço do cliente ia só no Reply-To. Ninguém percebia, porque
 * o email chegava — só que sempre na mesma caixa.
 *
 * Agora existe um lugar só que decide para onde vai, e ele conhece dois
 * transportes:
 *
 *   1. binding nativo do Cloudflare (`env.EMAIL`)
 *      Grátis, mas no plano Workers Free só alcança o endereço verificado em
 *      Email Routing — ou seja, só o próprio Mateus. Depois de assinar o
 *      Workers Paid e onboardar o domínio em Email Sending, ele passa a
 *      alcançar qualquer um: é aí que se liga ENVIO_ABERTO = "1".
 *
 *   2. API HTTP de um serviço de envio (`env.RESEND_API_KEY`)
 *      Alcança qualquer destinatário sem depender do plano do Worker.
 *
 * Enquanto nenhum dos dois estiver ligado, email destinado ao cliente NÃO
 * some calado: ele é entregue ao Mateus com um aviso no topo dizendo quem
 * deveria ter recebido. Perder proposta em silêncio é pior que entregar no
 * lugar errado com etiqueta.
 */

import { EmailMessage } from "cloudflare:email";

export function base64(bytes) {
  let bin = "";
  bytes.forEach((b) => { bin += String.fromCharCode(b); });
  return btoa(bin);
}

/* Assunto com acento precisa de RFC 2047. A regra que faltava: cada palavra
 * codificada tem limite de 75 caracteres, e o assunto inteiro não pode sair
 * numa linha só. Estourando isso, o cliente de email mostra o "=?UTF-8?B?..."
 * cru ou embaralha o texto.
 *
 * Então: fatia em pedaços de 15 bytes (20 chars de base64, folgado dentro do
 * limite) e dobra com CRLF + espaço. Corta em limite de byte UTF-8 válido pra
 * não partir acento no meio.
 */
export function assuntoCodificado(texto) {
  const bytes = new TextEncoder().encode(texto);
  const partes = [];
  let i = 0;
  while (i < bytes.length) {
    let fim = Math.min(i + 15, bytes.length);
    while (fim > i && fim < bytes.length && (bytes[fim] & 0xc0) === 0x80) { fim--; }
    partes.push("=?UTF-8?B?" + base64(bytes.slice(i, fim)) + "?=");
    i = fim;
  }
  return partes.join("\r\n ");
}

export function corpoBase64(texto) {
  /* base64 de email quebra em linha de 76 colunas */
  return base64(new TextEncoder().encode(texto)).replace(/(.{76})/g, "$1\r\n");
}

export function limpo(v, max) {
  if (typeof v !== "string") { return ""; }
  /* corta CR/LF pra ninguém injetar cabeçalho pelo nome da empresa */
  return v.replace(/[\r\n]+/g, " ").trim().slice(0, max || 120);
}

/* Tira as marcas do HTML pra fazer a versão em texto. Não é conversão
   bonita — é a alternativa que o filtro de spam espera encontrar. */
export function paraTexto(html) {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<\/(div|tr|h1|h2|p)>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&middot;/g, "·").replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s*\n\s*\n+/g, "\n\n")
    .trim();
}

export function montarEmail(de, para, assunto, corpo, responder, html, anexos) {
  const cab = [
    "From: Borin Projetos <" + de + ">",
    "To: <" + para + ">",
    responder ? "Reply-To: <" + responder + ">" : null,
    "Subject: " + assuntoCodificado(assunto),
    "Message-ID: <" + crypto.randomUUID() + "@borinprojetos.com.br>",
    "Date: " + new Date().toUTCString(),
    "MIME-Version: 1.0",
  ].filter(Boolean);

  if (!html) {
    return cab.concat([
      'Content-Type: text/plain; charset="utf-8"',
      "Content-Transfer-Encoding: base64",
      "",
      corpoBase64(corpo),
    ]).join("\r\n");
  }

  /* multipart/alternative: HTML sozinho é um dos sinais de spam mais fortes
     que existem. Email transacional de verdade manda as duas versões, e o
     cliente escolhe qual mostra. */
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
    "--" + alt + "--",
  ];

  if (!anexos || !anexos.length) {
    return cab.concat(corpoAlt).join("\r\n");
  }

  /* Com anexo, a estrutura ganha um nível: mixed por fora com o corpo e os
     arquivos, alternative por dentro com as duas versões do corpo. */
  const mix = "mix" + crypto.randomUUID().replace(/-/g, "");
  const partes = [
    'Content-Type: multipart/mixed; boundary="' + mix + '"',
    "",
    "--" + mix,
  ].concat(corpoAlt);

  for (const a of anexos) {
    partes.push(
      "--" + mix,
      'Content-Type: ' + (a.tipo || "application/octet-stream")
        + '; name="' + (a.nome || "anexo") + '"',
      "Content-Transfer-Encoding: base64",
      'Content-Disposition: attachment; filename="' + (a.nome || "anexo") + '"',
      "",
      String(a.base64 || "").replace(/\s+/g, "").replace(/(.{76})/g, "$1\r\n"));
  }
  partes.push("--" + mix + "--", "");
  return cab.concat(partes).join("\r\n");
}

/** O site consegue escrever para alguém que não seja o próprio Mateus? */
export function podeEscreverAoCliente(env) {
  return !!env.RESEND_API_KEY || env.ENVIO_ABERTO === "1";
}

function ehODono(env, endereco) {
  const meu = (env.DESTINO || "").trim().toLowerCase();
  return !endereco || endereco.trim().toLowerCase() === meu;
}

async function porBinding(env, para, bruto) {
  await env.EMAIL.send(new EmailMessage(env.REMETENTE, para, bruto));
}

async function porResend(env, o, para) {
  const corpo = {
    from: "Borin Projetos <" + env.REMETENTE + ">",
    to: [para],
    subject: o.assunto,
  };
  if (o.responder) { corpo.reply_to = o.responder; }
  if (o.html) {
    corpo.html = o.corpo;
    corpo.text = paraTexto(o.corpo);
  } else {
    corpo.text = o.corpo;
  }
  if (o.anexos && o.anexos.length) {
    corpo.attachments = o.anexos.map((a) => ({
      filename: a.nome || "anexo",
      content: String(a.base64 || "").replace(/\s+/g, ""),
    }));
  }
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + env.RESEND_API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(corpo),
  });
  if (!r.ok) {
    const detalhe = await r.text();
    throw new Error("resend " + r.status + ": " + detalhe.slice(0, 300));
  }
}

/* O email era pro cliente e não dá pra alcançá-lo. Vai pro Mateus, com
   etiqueta, pra ele repassar na mão — e pra ele SABER que precisa repassar. */
async function entregarAoDono(env, o, queriaIr) {
  const aviso =
    "ESTE EMAIL ERA PARA O CLIENTE E NAO PUDE ENTREGAR.\n" +
    "Destinatario pretendido: " + queriaIr + "\n" +
    "Motivo: o site ainda nao tem transporte de email para terceiros.\n" +
    "Repasse este conteudo na mao, ou ligue o envio (ver site/worker/correio.js).\n" +
    "\n" + "-".repeat(58) + "\n\n";

  const corpo = o.html
    ? '<div style="background:#FFF4F4;border:2px solid #C1121F;padding:14px;'
      + 'font-family:monospace;font-size:12px;color:#C1121F;white-space:pre-wrap">'
      + aviso.replace(/</g, "&lt;") + "</div>" + o.corpo
    : aviso + o.corpo;

  const bruto = montarEmail(env.REMETENTE, env.DESTINO,
    "[NAO ENTREGUE] " + o.assunto, corpo, queriaIr, o.html, o.anexos);
  await porBinding(env, env.DESTINO, bruto);
  return { entregue: false, para: env.DESTINO, pretendido: queriaIr };
}

/**
 * A única função que manda email neste site.
 *
 * o = { para, assunto, corpo, html, anexos, responder }
 * Se `para` for vazio ou for o próprio Mateus, vai direto pra ele.
 */
export async function enviarPara(env, o) {
  const para = limpo(o.para, 160);
  const meu = ehODono(env, para);

  if (!meu && !podeEscreverAoCliente(env)) {
    return entregarAoDono(env, o, para);
  }

  const destino = meu ? env.DESTINO : para;

  if (env.RESEND_API_KEY) {
    await porResend(env, o, destino);
  } else {
    const bruto = montarEmail(env.REMETENTE, destino, o.assunto, o.corpo,
      o.responder, o.html, o.anexos);
    await porBinding(env, destino, bruto);
  }
  return { entregue: true, para: destino };
}
