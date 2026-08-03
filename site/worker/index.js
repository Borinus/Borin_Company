/* Recebe o pedido de orcamento e responde ao cliente.
 *
 * Por que existe: antes, se o cliente preenchia o formulario e nao apertava
 * enviar no WhatsApp, o Mateus nunca ficava sabendo que ele existiu. Agora o
 * envio dispara junto com o clique e chega email em segundos.
 *
 * DOIS CAMINHOS, e eles nao se misturam:
 *
 *   /api/orcamento  — publico, e o formulario do site. So aceita campos
 *                     estruturados; o Worker monta o texto, sempre em texto
 *                     puro, sempre pro Mateus. Sem anexo, sem HTML, sem
 *                     escolher destinatario.
 *   /api/enviar     — os comandos do Mateus, com Authorization: Bearer. Ai sim
 *                     pode escrever pro cliente, em HTML e com PDF anexo.
 *
 * A separacao existe porque a versao anterior aceitava DO NAVEGADOR o corpo
 * pronto, o HTML, os anexos e o destinatario. Confirmado com teste em
 * 02/08/2026: um estranho, sem segredo nenhum, fez o site enviar email de
 * site@borinprojetos.com.br pra um endereco qualquer, com "Banco Falso S.A."
 * no assunto e assinado com o DKIM do dominio. O custo nao e o email em si: e
 * a reputacao queimar, e dominio queimado nao entrega mais proposta nenhuma.
 *
 * Quem decide PARA ONDE vai cada email e o correio.js.
 */

import { rotaAcesso, contaDoLead } from "./acesso.js";
import { enviarPara, limpo } from "./correio.js";
import { lerPedido, montarTexto, montarAssunto, podePedir, ehAdmin } from "./pedido.js";

const LIMITE = 24 * 1024;               // corpo de texto do caminho de admin
const LIMITE_PEDIDO = 6 * 1024 * 1024;  // com anexo, o PDF do contrato entra aqui
const LIMITE_PUBLICO = 24 * 1024;       // formulario nao precisa de mais que isso

const ok = (o, status = 200) => Response.json(o, {
  status,
  headers: {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
  },
});

async function corpo(request, limite) {
  const cru = await request.text();
  if (cru.length > limite) return { erro: "pedido grande demais", status: 413 };
  try {
    return { dados: JSON.parse(cru) };
  } catch (e) {
    return { erro: "corpo inválido", status: 400 };
  }
}

/* ------------------------------------------------------------- publico */

async function pedidoDoSite(request, env) {
  const r = await corpo(request, LIMITE_PUBLICO);
  if (r.erro) return ok({ erro: r.erro }, r.status);
  const dados = r.dados;

  /* campo escondido que humano nunca preenche: se veio cheio, e robo.
     Responde 200 de proposito, pra o robo achar que funcionou. */
  if (limpo(dados.website)) return ok({ ok: true });

  const { p, falta } = lerPedido(dados);
  if (falta.length) {
    return ok({ erro: "falta " + falta.join(", ") }, 400);
  }

  const ip = request.headers.get("cf-connecting-ip") || "";
  if (!(await podePedir(env, ip, p.email))) {
    return ok({ erro: "muitos pedidos seguidos. me chame no WhatsApp que eu respondo agora" }, 429);
  }

  let entrega;
  try {
    entrega = await enviarPara(env, {
      para: env.DESTINO,
      assunto: montarAssunto(p),
      corpo: montarTexto(p, ip),
      responder: p.email,
    });
  } catch (e) {
    /* O cliente nao pode ver erro: o pedido dele nao pode parecer perdido. */
    console.error("falha ao enviar:", e && e.message);
    return ok({ ok: false });
  }

  /* Pedido com email valido abre a conta do cliente na hora e manda a senha
     pra ele. Era o que faltava: ate entao a senha so existia se o Mateus
     rodasse um comando e copiasse na mao. */
  let conta = null;
  try {
    conta = await contaDoLead(env, p.email, p.empresa, p.contato);
  } catch (e) {
    console.error("nao criei a conta do lead:", e && e.message);
  }

  return ok({
    ok: true,
    entregue: entrega ? entrega.entregue : false,
    conta: conta ? conta.estado : null,
  });
}

/* --------------------------------------------------------------- admin */

async function envioDoMateus(request, env) {
  if (!ehAdmin(request, env)) {
    return ok({ erro: "nao autorizado" }, 401);
  }
  const r = await corpo(request, LIMITE_PEDIDO);
  if (r.erro) return ok({ erro: r.erro }, r.status);
  const dados = r.dados;

  const texto = typeof dados.texto === "string" ? dados.texto.slice(0, LIMITE) : "";
  if (!texto) return ok({ erro: "pedido vazio" }, 400);

  const email = limpo(dados.email, 160);
  const paraCliente = dados.para_cliente === true && email.includes("@");

  let entrega;
  try {
    entrega = await enviarPara(env, {
      para: paraCliente ? email : env.DESTINO,
      assunto: limpo(dados.assunto, 200) || "Borin Projetos Elétricos",
      corpo: texto,
      responder: email.includes("@") ? email : null,
      html: dados.html === true,
      anexos: Array.isArray(dados.anexos) ? dados.anexos.slice(0, 4) : null,
    });
  } catch (e) {
    console.error("falha ao enviar:", e && e.message);
    return ok({ ok: false, erro: String(e && e.message).slice(0, 200) }, 502);
  }
  return ok({ ok: true, entregue: entrega ? entrega.entregue : false });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    /* conta do cliente: entrar, trocar senha, guardar ficha, equipe */
    if (url.pathname.startsWith("/api/acesso")) {
      return rotaAcesso(request, env, url);
    }

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }
    if (request.method !== "POST") {
      return new Response("metodo nao permitido", { status: 405 });
    }

    if (url.pathname === "/api/enviar") return envioDoMateus(request, env);
    return pedidoDoSite(request, env);
  },
};
