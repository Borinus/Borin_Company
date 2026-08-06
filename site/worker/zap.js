/**
 * WhatsApp pelo Cloud API da Meta.
 *
 * Fica DESLIGADO enquanto os segredos não existirem — mesmo padrão do
 * `correio.js` com o Resend. Sem `ZAP_TOKEN` e `ZAP_NUMERO_ID`, `avisarNoZap`
 * devolve `{ligado:false}` e ninguém percebe. Assim o site sobe igual antes,
 * durante e depois da aprovação da Meta, sem release coordenado.
 *
 * Uma regra da plataforma manda no desenho todo: mensagem que o NEGÓCIO
 * começa (é o caso — o cliente preencheu um formulário no site, não mandou
 * WhatsApp) só pode sair como MODELO aprovado. Texto livre só funciona dentro
 * de 24 horas depois de o cliente escrever primeiro. Por isso aqui não existe
 * "mandar uma mensagem qualquer": existe mandar UM modelo com os campos dele.
 *
 * O modelo (a cadastrar em Meta Business → WhatsApp → Modelos):
 *
 *   nome      pedido_recebido
 *   categoria UTILITY          (UTILITY aprova rápido; MARKETING não)
 *   idioma    pt_BR
 *   corpo     Olá {{1}}, recebi seu pedido de orçamento para {{2}}.
 *             Respondo com valor e prazo em até 24 horas.
 *             Você acompanha em borinprojetos.com.br/conta.
 *
 * O passo a passo da configuração está em `site/whatsapp.md`.
 */

import { enviarPara } from "./correio.js";

const API = "https://graph.facebook.com/v21.0";

export function zapLigado(env) {
  return !!(env.ZAP_TOKEN && env.ZAP_NUMERO_ID);
}

/**
 * O número como a Meta quer: só dígitos, com o país na frente.
 *
 * O formulário aceita "+55 (54) 99664-2003", "54996642003", "5554996642003".
 * Mandar qualquer uma dessas cruas devolve erro 131026 e a mensagem some sem
 * ninguém ficar sabendo, então a normalização é feita aqui e testada.
 */
export function numeroE164(v) {
  let d = String(v || "").replace(/\D/g, "");
  if (!d) return "";
  /* 55 na frente só conta como país se o que sobra tiver cara de número
     brasileiro (10 ou 11 dígitos). "5511" sozinho é DDD 55 + prefixo, não
     Brasil + DDD 11. */
  if (d.length >= 12 && d.startsWith("55")) {
    const resto = d.slice(2);
    if (resto.length === 10 || resto.length === 11) return d;
  }
  if (d.length === 10 || d.length === 11) return "55" + d;
  return d.length >= 12 ? d : "";
}

/**
 * Manda o modelo. Nunca lança: WhatsApp é um extra em cima do email, e o
 * pedido do cliente não pode cair porque a Meta ficou fora do ar.
 */
export async function avisarNoZap(env, { fone, contato, equipamento }) {
  if (!zapLigado(env)) return { ligado: false };

  const para = numeroE164(fone);
  if (!para) return { ligado: true, enviado: false, erro: "numero invalido" };

  const nome = (String(contato || "").split(" ")[0] || "tudo bem").slice(0, 60);
  const oque = String(equipamento || "seu projeto").slice(0, 90);

  const corpo = {
    messaging_product: "whatsapp",
    to: para,
    type: "template",
    template: {
      name: env.ZAP_TEMPLATE || "pedido_recebido",
      language: { code: env.ZAP_IDIOMA || "pt_BR" },
      components: [{
        type: "body",
        parameters: [
          { type: "text", text: nome },
          { type: "text", text: oque },
        ],
      }],
    },
  };

  try {
    const r = await fetch(API + "/" + env.ZAP_NUMERO_ID + "/messages", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + env.ZAP_TOKEN,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(corpo),
    });
    const t = await r.text();
    if (!r.ok) {
      /* o motivo vai pro log inteiro: os erros da Meta (131026 número não
         existe no WhatsApp, 132001 modelo não aprovado) só se distinguem pelo
         código, e sem ele a investigação vira adivinhação */
      console.error("zap recusou:", r.status, t.slice(0, 300));
      return { ligado: true, enviado: false, erro: "http " + r.status };
    }
    return { ligado: true, enviado: true };
  } catch (e) {
    console.error("zap falhou:", e && e.message);
    return { ligado: true, enviado: false, erro: String(e && e.message).slice(0, 120) };
  }
}

/* ------------------------------------------------------ resposta do cliente
 *
 * O cliente que responde a confirmação escreve pra um número que não está em
 * celular nenhum: a mensagem chega na API e morre ali. Ele fica falando
 * sozinho e o Mateus nunca fica sabendo — pior que não ter mandado nada.
 *
 * Esta rota é o webhook da Meta. Toda resposta vira email na hora.
 */
export async function rotaZap(request, env, url) {
  /* Aperto de mão: a Meta chama com GET uma vez, no cadastro do webhook, e
     espera o desafio de volta em texto puro. Errar isso não dá erro visível —
     o webhook simplesmente nunca é ativado. */
  if (request.method === "GET") {
    const modo = url.searchParams.get("hub.mode");
    const token = url.searchParams.get("hub.verify_token");
    const desafio = url.searchParams.get("hub.challenge");
    if (modo === "subscribe" && env.ZAP_VERIFY && token === env.ZAP_VERIFY) {
      return new Response(desafio || "", { status: 200 });
    }
    return new Response("nao autorizado", { status: 403 });
  }

  if (request.method !== "POST") {
    return new Response("metodo nao permitido", { status: 405 });
  }

  /* Responder 200 SEMPRE, mesmo com corpo estranho. A Meta repete o que dá
     erro e, se insistir errando, desliga o webhook — perder uma resposta é
     ruim, ficar sem canal nenhum é pior. */
  let dados = {};
  try {
    dados = JSON.parse(await request.text());
  } catch (e) {
    return new Response("ok", { status: 200 });
  }

  try {
    for (const entrada of (dados.entry || [])) {
      for (const m of (entrada.changes || [])) {
        const v = (m && m.value) || {};

        /* Status do que EU mandei. A resposta da Meta ao enviar diz só
           "accepted", que significa "recebi o pedido" e nada mais — entregue,
           lida ou falhada só chega aqui. Sem isto, mensagem que não chega vira
           mistério: o envio parece ter dado certo dos dois lados. */
        for (const s of (v.statuses || [])) {
          const erros = (s.errors || []).map((e) =>
            e.code + " " + (e.title || e.message || "")).join(" · ");
          const linha = [s.status, s.recipient_id, erros].filter(Boolean).join(" | ");
          console.log("zap status:", linha);
          await env.CLIENTES.put(
            "zapstatus:" + (s.timestamp || Date.now()) + ":" + (s.id || "").slice(-8),
            JSON.stringify({ em: new Date().toISOString(), status: s.status,
                             para: s.recipient_id, erros: s.errors || [] }),
            { expirationTtl: 3 * 86400 });

          /* falha é o único status que precisa chegar em alguém */
          if (s.status === "failed") {
            await enviarPara(env, {
              para: env.DESTINO,
              assunto: "WhatsApp NAO entregue — " + (s.recipient_id || ""),
              corpo: ["A mensagem de WhatsApp não foi entregue.", "",
                      "Destinatário: +" + (s.recipient_id || "?"),
                      "Motivo: " + (erros || "não informado"), "",
                      JSON.stringify(s.errors || [], null, 2)].join("\n"),
            });
          }
        }

        const contatos = v.contacts || [];
        for (const msg of (v.messages || [])) {
          const quem = contatos[0] || {};
          const nome = (quem.profile && quem.profile.name) || "";
          const fone = msg.from || quem.wa_id || "";
          const texto = (msg.text && msg.text.body)
            || "[" + (msg.type || "mensagem") + " — abra no WhatsApp]";

          await enviarPara(env, {
            para: env.DESTINO,
            assunto: "WhatsApp de " + (nome || fone),
            corpo: [
              "RESPOSTA NO WHATSAPP DO SITE",
              "=".repeat(46),
              "",
              "De:      " + (nome || "(sem nome)"),
              "Número:  +" + fone,
              "",
              texto,
              "",
              "-".repeat(46),
              "Responda direto no WhatsApp: https://wa.me/" + fone,
            ].join("\n"),
          });
        }
      }
    }
  } catch (e) {
    console.error("nao repassei a resposta do zap:", e && e.message);
  }

  return new Response("ok", { status: 200 });
}
