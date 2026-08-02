/* Recebe o pedido de orcamento e responde ao cliente.
 *
 * Por que existe: antes, se o cliente preenchia o formulario e nao apertava
 * enviar no WhatsApp, o Mateus nunca ficava sabendo que ele existiu. Agora o
 * envio dispara junto com o clique e chega email em segundos.
 *
 * Quem decide PARA ONDE vai cada email e o correio.js — este arquivo so diz
 * o que mandar e para quem. Ate 01/08/2026 o destinatario estava escrito na
 * mao aqui como env.DESTINO, e por isso o cliente nunca recebia nada.
 *
 * So o /orcamento usa isso. O /padrao e o /projeto continuam sem servidor,
 * porque carregam o padrao interno e o desenho da maquina do cliente.
 */

import { rotaAcesso, contaDoLead } from "./acesso.js";
import { enviarPara, limpo, podeEscreverAoCliente } from "./correio.js";

const LIMITE = 24 * 1024;        // corpo de texto: maior que isso e abuso
const LIMITE_PEDIDO = 6 * 1024 * 1024;  // com anexo, o PDF do contrato entra aqui

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    /* conta do cliente: entrar, trocar senha, guardar ficha */
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

    /* campo escondido que humano nunca preenche: se veio cheio, e robo.
       Responde 200 de proposito, pra o robo achar que funcionou. */
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

    /* proposta em HTML e um documento pro cliente: cabecalho tecnico com IP
       so faz sentido no pedido que chega pro Mateus */
    const cabecalho = dados.html === true ? "" :
      "Pedido recebido pelo site.\n" +
      "Origem: " + limpo(dados.intencao) + "\n" +
      (request.headers.get("cf-connecting-ip")
        ? "IP: " + request.headers.get("cf-connecting-ip") + "\n"
        : "") +
      "\n" + "-".repeat(50) + "\n\n";

    /* O assunto precisa ser diferente por projeto, senao o Gmail junta tudo
       numa conversa so e nao da pra achar nada. O codigo vai na frente porque
       e o que o Mateus procura: "cade o 04003478?" */
    const codigo = limpo(dados.codigo, 30);
    const equip = limpo(dados.equipamento, 60);
    const doc = limpo(dados.doc, 40) || "Pedido de orçamento";

    let assunto = codigo ? "#" + codigo + " · " + empresa : empresa;
    assunto += " — " + (equip || doc);
    if (equip && doc && doc !== "Pedido de orçamento") {
      assunto += " · " + doc;
    }

    /* Duas coisas diferentes passam por aqui:
       - pedido vindo do formulario do site: quem le e o Mateus, e o email do
         cliente vira Reply-To pra ele responder com um toque
       - proposta e contrato disparados pelo comando: esses SAO para o cliente,
         e vem marcados com para_cliente = true */
    const paraCliente = dados.para_cliente === true && email.includes("@");

    let entrega;
    try {
      entrega = await enviarPara(env, {
        para: paraCliente ? email : env.DESTINO,
        assunto: assunto,
        corpo: cabecalho + texto,
        responder: email.includes("@") ? email : null,
        /* proposta vai como HTML pra o cliente ver o documento, nao um txt */
        html: dados.html === true,
        anexos: Array.isArray(dados.anexos) ? dados.anexos.slice(0, 4) : null,
      });
    } catch (e) {
      /* O cliente nao pode ver erro: o pedido dele nao pode parecer perdido.
         Loga e devolve 200. */
      console.error("falha ao enviar:", e && e.message);
      return Response.json({ ok: false }, { status: 200 });
    }

    /* Pedido do site com email valido abre a conta do cliente na hora e manda
       a senha pra ele. Era o que faltava: ate agora a senha so existia se o
       Mateus rodasse um comando e copiasse na mao. */
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
      conta: conta ? conta.estado : null,
    });
  },
};
