/**
 * O pedido de orçamento — regra no servidor, não no navegador.
 *
 * Como estava, o Worker aceitava do navegador: o corpo da mensagem já pronto
 * (`texto`), a decisão de mandar em HTML (`html`), anexos (`anexos`) e, o pior
 * de todos, PARA QUEM enviar (`para_cliente` + `email`).
 *
 * Isso é um relay aberto, e foi confirmado com teste: um estranho, sem segredo
 * nenhum, fez o site enviar um email de site@borinprojetos.com.br para um
 * endereço qualquer, com HTML escolhido por ele e "Banco Falso S.A." no
 * assunto. Assinado com o DKIM do domínio, ou seja, passando por todos os
 * filtros. O custo não é o email em si: é a reputação do domínio queimar e as
 * propostas de verdade pararem de ser entregues.
 *
 * Agora existem dois caminhos, e eles não se misturam:
 *
 *   PÚBLICO   — o formulário do site. Só campos estruturados. O Worker monta o
 *               texto, sempre em texto puro, sempre para o Mateus. Sem anexo,
 *               sem HTML, sem escolher destinatário.
 *   ADMIN     — os comandos do Mateus, com Authorization: Bearer. Aí sim pode
 *               escrever para o cliente, em HTML e com o PDF anexo.
 *
 * O navegador nunca mais decide nada disso.
 */

import { enviarPara, limpo } from "./correio.js";

const LIMITE_CAMPO = 400;
const LIMITE_TEXTO = 4000;
/* O limite é anti-enxurrada, não anti-abuso. Estava apertado demais e barrou
   gente de verdade: 3 pedidos por dia por email derruba um integrador que
   manda quatro máquinas na mesma tarde, e 12 por hora por IP derruba o
   escritório inteiro que sai por um IP só. Um lead perdido custa mais que dez
   emails a mais na caixa.

   Quem já tem CONTA não passa por freio nenhum: provou que é dono do email
   quando entrou, e um cliente pedindo o quinto orçamento é o melhor tipo de
   cliente que existe — não é ele que a trava existe pra parar. */
const POR_HORA = 40;          // pedidos por IP, para quem ainda não tem conta
const POR_DIA_EMAIL = 12;     // pedidos por endereço de email sem conta
const POR_DIA_CLIENTE = 40;   // teto de segurança para quem já tem conta

/* ------------------------------------------------------------ validação */

export function emailValido(v) {
  return /^[^\s@]{1,64}@[^\s@.]{1,63}(\.[^\s@.]{2,63})+$/.test(String(v || "").trim());
}

/* Campo de contagem opcional. VAZIO e ok (vale 0). Texto nao-numerico e
   RECUSADO — nao coagido.
   Antes isto era `inteiro()`, que fazia replace(/\D/g,"") e parseInt: "10 a 15"
   virava 1015 e "abc" virava 0, os dois em silencio. Coacao calada e o padrao
   que a regra #3 do AGENTS.md manda cacar — o dado do cliente sumia ou se
   deformava sem ninguem ver. Agora o servidor devolve o erro, o front mostra,
   e o mascara do site ja impede o cliente de digitar letra em primeiro lugar. */
function numero(v, max) {
  const s = String(v || "").trim();
  if (!s) return { n: 0 };
  if (!/^\d+$/.test(s)) return { erro: true };
  return { n: Math.min(parseInt(s, 10), max) };
}

function daLista(v, lista) {
  const s = String(v || "").trim();
  return lista.includes(s) ? s : "";
}

/**
 * O pedido, campo a campo. O que não está aqui não entra — e o que está vem
 * limpo, com tamanho e formato conferidos no servidor.
 */
export function lerPedido(dados) {
  const nIos = numero(dados.ios, 100000);
  const nAcio = numero(dados.acionamentos, 10000);
  const nSeg = numero(dados.seg_qtd, 10000);

  const p = {
    empresa: limpo(dados.empresa, 120),
    contato: limpo(dados.contato, 120),
    email: limpo(dados.email, 160).toLowerCase(),
    fone: limpo(dados.fone, 40),
    equipamento: limpo(dados.equipamento, 120),
    codigo: limpo(dados.codigo, 30),
    escopo: daLista(dados.escopo, ["A", "B", "?"]),
    nr12: daLista(dados.nr12, ["sim", "nao", "?"]),
    canal: daLista(dados.canal, ["email", "email+whats"]) || "email",
    ios: nIos.n || 0,
    acionamentos: nAcio.n || 0,
    seg_qtd: nSeg.n || 0,
    prazo: limpo(dados.prazo, 40),
    observacao: limpo(dados.observacao, LIMITE_TEXTO),
  };

  const falta = [];
  if (!p.contato) falta.push("seu nome");
  if (!p.email) falta.push("seu email");
  else if (!emailValido(p.email)) falta.push("um email válido");
  if (!p.equipamento) falta.push("a máquina ou o processo");
  if (p.canal === "email+whats" && p.fone.replace(/\D/g, "").length < 12) {
    falta.push("o WhatsApp completo, com DDD");
  }
  /* contagens: opcionais, mas se vieram tem que ser numero. So o site ja
     impede letra pela mascara; isto pega o pedido montado na mao ou por robo. */
  if (nIos.erro) falta.push("os pontos de I/O só em número");
  if (nAcio.erro) falta.push("os acionamentos só em número");
  if (nSeg.erro) falta.push("os dispositivos de segurança só em número");
  return { p, falta };
}

/**
 * O texto do email é montado AQUI, não no navegador. Antes o corpo vinha
 * pronto do cliente, então qualquer um mandava o que quisesse pra caixa do
 * Mateus — inclusive HTML se pedisse.
 */
export function montarTexto(p, ip) {
  const l = [];
  const linha = (r, v) => { if (v) l.push(r + ": " + v); };

  l.push("PEDIDO DE ORÇAMENTO — BORIN PROJETOS ELÉTRICOS");
  l.push("=".repeat(46));
  l.push("");
  l.push("QUEM ESTÁ PEDINDO");
  linha("Empresa", p.empresa);
  linha("Contato", p.contato);
  linha("Email", p.email);
  linha("WhatsApp", p.fone);
  l.push("");
  l.push("O PROJETO");
  linha("Máquina ou processo", p.equipamento);
  linha("Código", p.codigo);
  linha("Escopo", p.escopo === "A" ? "A — só o painel"
    : p.escopo === "B" ? "B — painel e instalação em campo" : "não sabe ainda");
  l.push("");
  l.push("DADOS MÍNIMOS");
  linha("Acionamentos", p.acionamentos || "");
  linha("Pontos de I/O", p.ios || "");
  linha("NR-12", p.nr12 === "sim" ? "sim" : p.nr12 === "nao" ? "não" : "não sabe");
  linha("Dispositivos de segurança", p.seg_qtd || "");
  linha("Prazo desejado", p.prazo);
  if (p.observacao) {
    l.push("");
    l.push("OBSERVAÇÃO DO CLIENTE");
    l.push(p.observacao);
  }
  l.push("");
  l.push("COMO RESPONDER");
  l.push("Responder por: " + (p.canal === "email+whats" ? "email e WhatsApp" : "só email"));
  l.push("");
  l.push("-".repeat(46));
  l.push("Recebido pelo site" + (ip ? " · IP " + ip : ""));
  return l.join("\n");
}

export function montarAssunto(p) {
  const base = p.codigo ? "#" + p.codigo + " · " + (p.empresa || p.contato)
    : (p.empresa || p.contato);
  return base + " — " + (p.equipamento || "Pedido de orçamento");
}

/* ------------------------------------------------------------ freio */

/**
 * Freio por IP e por email. Sem isso qualquer um afoga a caixa do Mateus, e
 * com o email saindo do domínio dele isso também custa reputação.
 * Falha ABERTO de propósito: se o KV estiver fora, o pedido do cliente passa —
 * perder um lead real é pior que aceitar um a mais de um abusador.
 */
export async function podePedir(env, ip, email) {
  try {
    const agora = Date.now();

    /* Cliente conhecido: só o teto de segurança, e o IP não entra na conta.
       Sem isto, o cliente que pede o quarto orçamento leva "muitos pedidos
       seguidos" na cara — foi exatamente o que aconteceu no teste real. */
    const cru = await env.CLIENTES.get("cliente:" + email);
    const conhecido = !!cru;

    const chaves = conhecido
      ? [{ k: "freio-mail:" + email, max: POR_DIA_CLIENTE, ttl: 86400 }]
      : [
          { k: "freio-ip:" + ip, max: POR_HORA, ttl: 3600 },
          { k: "freio-mail:" + email, max: POR_DIA_EMAIL, ttl: 86400 },
        ];
    for (const c of chaves) {
      if (!c.k.split(":")[1]) continue;
      const cru = await env.CLIENTES.get(c.k);
      const n = cru ? JSON.parse(cru).n : 0;
      if (n >= c.max) return false;
    }
    for (const c of chaves) {
      if (!c.k.split(":")[1]) continue;
      const cru = await env.CLIENTES.get(c.k);
      const n = cru ? JSON.parse(cru).n : 0;
      await env.CLIENTES.put(c.k, JSON.stringify({ n: n + 1, em: agora }),
        { expirationTtl: c.ttl });
    }
    return true;
  } catch (e) {
    console.error("freio falhou, deixando passar:", e && e.message);
    return true;
  }
}

/** Quem chama com o segredo de admin pode o que o navegador não pode. */
export function ehAdmin(request, env) {
  if (!env.SEGREDO_ADMIN) return false;
  const cab = request.headers.get("Authorization") || "";
  const dado = cab.startsWith("Bearer ") ? cab.slice(7) : "";
  if (dado.length !== env.SEGREDO_ADMIN.length) return false;
  let d = 0;
  for (let i = 0; i < dado.length; i++) {
    d |= dado.charCodeAt(i) ^ env.SEGREDO_ADMIN.charCodeAt(i);
  }
  return d === 0;
}

export { enviarPara };
