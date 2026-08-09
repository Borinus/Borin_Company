/* Estimativa automatica pro cliente, na hora do pedido.
 *
 * POR QUE EXISTE: ate 09/08/2026 o cliente pedia e recebia so "conta criada".
 * Nenhum numero. A ideia sempre foi o orcamento ja chegar quando ele pede.
 *
 * O QUE ESTE MODULO NAO E: nao e o preco fechado. E ESTIMATIVA, faixa, marcada
 * como tal — a proposta fechada continua saindo do Mateus, conferida. Isso
 * respeita a regra do negocio ("preco conferido antes de sair"): o cliente
 * digita os numeros sozinho, e numero de cliente nao vira compromisso de preco.
 *
 * SINCRONIA COM O PYTHON: estimar_paginas e as constantes de preco vivem
 * TAMBEM em comercial/calcular.py, que e onde o Mateus fecha o valor de verdade.
 * Se eles divergirem, a estimativa do cliente mente sobre o que vem depois. Por
 * isso comercial/testar-estimativa.py roda os DOIS e prova que as paginas batem
 * e que o total do Python cai DENTRO da faixa que este arquivo mostra. Mexeu num
 * lado, o teste cobra o outro.
 */

// ---------- preco (espelha calcular.py) ----------
const POR_PAGINA = 235;   // hora de mercado, 1h por folha de diagrama
const PISO = 2400;        // abaixo disto o trabalho humano domina

// ---------- estimativa de paginas (espelha calcular.py) ----------
const PAGINAS_FIXAS = 14;
const IO_POR_PAGINA = 4.5;
const ACION_POR_PAGINA = 2.5;
const SEG_POR_PAGINA = 2.0;
const PONTOS_POR_REGUA = 35.0;
const CABOS_POR_PAGINA = 6.0;
const IO_POR_CABO = 3.0;

export function estimarPaginas(io, acionamentos, seguranca, escopo) {
  io = io || 0; acionamentos = acionamentos || 0; seguranca = seguranca || 0;
  let p = PAGINAS_FIXAS;
  p += io / IO_POR_PAGINA;
  p += acionamentos / ACION_POR_PAGINA;
  p += seguranca / SEG_POR_PAGINA;
  p += io / PONTOS_POR_REGUA;
  if (String(escopo).toUpperCase() === "B") {
    const cabos = (io + acionamentos) / IO_POR_CABO;
    p += cabos / CABOS_POR_PAGINA;
  }
  return Math.ceil(p);
}

// prazo por faixa de paginas — espelha PRAZOS em comercial/orcamento.py
const PRAZOS = [[15, "5 dias úteis"], [25, "8 dias úteis"], [40, "10 dias úteis"],
                [80, "12 dias úteis"]];

export function prazoDe(paginas) {
  for (const [teto, txt] of PRAZOS) { if (paginas <= teto) return txt; }
  return "a combinar";
}

function reais(v) {
  const s = Math.round(v).toLocaleString("pt-BR");
  return "R$ " + s;
}

/**
 * Decide se da pra estimar e devolve { paginas, prazo, min, max, faixa } ou null.
 *
 * So estima com escopo definido (A ou B — o "?" muda a conta pelos cabos de
 * campo) E com algum tamanho (I/O ou acionamentos). Sem isso, devolve null e o
 * email cai no texto de "estou preparando" — em vez de inventar um numero.
 */
export function estimativaDoPedido(p) {
  const escopo = String((p && p.escopo) || "").toUpperCase();
  if (escopo !== "A" && escopo !== "B") return null;
  const io = Number(p.ios) || 0;
  const acion = Number(p.acionamentos) || 0;
  const seg = Number(p.seg_qtd) || 0;
  if (io <= 0 && acion <= 0) return null;

  const paginas = estimarPaginas(io, acion, seg, escopo);
  const base = Math.max(paginas * POR_PAGINA, PISO);

  /* faixa larga o suficiente pra conter o valor que o Mateus vai fechar. O
     total do calcular.py, sem acrescimo e sem desconto, cai perto de base
     arredondado pra 100; a margem cobre a incerteza da estimativa de paginas. */
  const min = Math.floor((base * 0.9) / 100) * 100;
  const max = Math.ceil((base * 1.1) / 100) * 100;

  return {
    paginas,
    prazo: prazoDe(paginas),
    escopo,
    min,
    max,
    faixa: reais(min) + " a " + reais(max),
  };
}

/**
 * Bloco HTML da estimativa pro email do cliente. Devolve "" quando nao ha
 * estimativa — o email segue com o texto de "preparando", sem buraco.
 */
export function blocoEstimativaHtml(est) {
  if (!est) return "";
  const esc = est.escopo === "B" ? "painel e instalação em campo" : "só o painel";
  /* sem padding horizontal proprio: entra dentro de um container que ja tem os
     28px de margem do email (senao dobra a margem). */
  return [
    '<div style="border:1px solid #111111;padding:16px 18px;margin:0 0 16px">',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-bottom:8px">Estimativa — sujeita a confirmação</div>',
    '<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse">',
    '<tr><td style="padding:3px 0;font-size:13px;color:#6B6B6B;width:42%">Escopo</td>',
    '<td style="padding:3px 0;font-size:13px;color:#111111">', esc, "</td></tr>",
    '<tr><td style="padding:3px 0;font-size:13px;color:#6B6B6B">Páginas estimadas</td>',
    '<td style="padding:3px 0;font-size:13px;color:#111111">~', String(est.paginas), " páginas</td></tr>",
    '<tr><td style="padding:3px 0;font-size:13px;color:#6B6B6B">Prazo estimado</td>',
    '<td style="padding:3px 0;font-size:13px;color:#111111">', est.prazo, "</td></tr>",
    '<tr><td style="padding:6px 0 0;font-size:13px;color:#6B6B6B">Investimento estimado</td>',
    '<td style="padding:6px 0 0;font-size:16px;font-weight:700;color:#111111">', est.faixa, "</td></tr>",
    "</table>",
    '<p style="font-size:12px;line-height:1.5;color:#6B6B6B;margin:12px 0 0">',
    "É uma estimativa a partir do que você informou — o valor e o prazo <b>fechados</b> ",
    "eu confirmo em até 24 horas, depois de conferir. O primeiro projeto tem 50% de desconto.",
    "</p>",
    "</div>",
  ].join("");
}
