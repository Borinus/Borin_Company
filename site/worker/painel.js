/**
 * O painel do Mateus — o espelho do /conta, do lado de quem vende.
 *
 * Até aqui o negócio só existia espalhado no banco: 11 pedidos guardados que
 * ninguém tinha como ver sem consultar a API na mão. Um lead que chega e não é
 * respondido não dá erro em lugar nenhum — ele simplesmente não vira nada, e o
 * silêncio é indistinguível de "não chegou pedido nenhum".
 *
 * Por isso o painel não é uma lista: é a resposta a "o que precisa de mim
 * agora". A lista vem depois, pra quem quiser conferir.
 *
 * Tudo daqui exige o segredo de admin no cabeçalho. Não há sessão nem cookie:
 * é uma tela só, usada por uma pessoa só.
 */

const DIAS = 86400000;

/* Quanto tempo até virar cobrança. Os números saem do que o negócio promete:
   a proposta diz "respondo em até 24 horas", e a validade dela é de 3 dias. */
const PEDIDO_ATRASADO = 1;      // dia sem resposta
const PROPOSTA_ESFRIANDO = 3;   // dias sem virar projeto
const PROJETO_PARADO = 7;       // dias sem atualização

/** Lista uma prefixo inteiro, seguindo o cursor. */
async function tudoDe(env, prefixo) {
  const itens = [];
  let cursor;
  for (let volta = 0; volta < 20; volta++) {
    const r = await env.CLIENTES.list({ prefix: prefixo, cursor, limit: 1000 });
    for (const k of r.keys) {
      const cru = await env.CLIENTES.get(k.name);
      if (cru) {
        try {
          itens.push({ chave: k.name, dado: JSON.parse(cru) });
        } catch (e) { /* chave corrompida não derruba o painel inteiro */ }
      }
    }
    if (r.list_complete) break;
    cursor = r.cursor;
  }
  return itens;
}

/** A parte do meio da chave: pedido:<AQUI>:<data> */
function donoDaChave(chave, prefixo) {
  const resto = chave.slice(prefixo.length);
  const corte = resto.indexOf(":");
  return corte === -1 ? resto : resto.slice(0, corte);
}

function diasDesde(iso) {
  if (!iso) return null;
  const t = Date.parse(iso);
  if (isNaN(t)) return null;
  return Math.floor((Date.now() - t) / DIAS);
}

export async function montarPainel(env) {
  const empresas = await tudoDe(env, "empresa:");
  const clientes = await tudoDe(env, "cliente:");

  /* id da empresa -> como chamar ela na tela. O email do dono entra junto
     porque é por ele que todo comando é chamado depois. */
  const quem = {};
  for (const e of empresas) {
    quem[e.dado.id] = { nome: e.dado.nome || "", email: e.dado.dono || "" };
  }
  /* conta sem empresa ainda: a chave é o próprio email */
  for (const c of clientes) {
    const d = c.dado;
    const email = d.email || c.chave.slice("cliente:".length);
    if (!quem[email]) quem[email] = { nome: d.empresa || "", email };
    if (d.empresa_id && quem[d.empresa_id] && !quem[d.empresa_id].nome) {
      quem[d.empresa_id].nome = d.empresa || "";
    }
  }

  const nomear = (id) => quem[id] || { nome: "", email: id };

  const pedidos = (await tudoDe(env, "pedido:")).map((x) => {
    const id = donoDaChave(x.chave, "pedido:");
    const q = nomear(id);
    return { ...x.dado, empresa_id: id, cliente: q.email, empresa_nome: q.nome || x.dado.empresa,
             dias: diasDesde(x.dado.em) };
  }).sort((a, b) => String(b.em).localeCompare(String(a.em)));

  const propostas = (await tudoDe(env, "proposta:")).map((x) => {
    const id = donoDaChave(x.chave, "proposta:");
    const q = nomear(id);
    return { ...x.dado, empresa_id: id, cliente: q.email, empresa_nome: q.nome,
             dias: diasDesde(x.dado.em) };
  }).sort((a, b) => String(b.em).localeCompare(String(a.em)));

  const projetos = (await tudoDe(env, "projeto:")).map((x) => {
    const id = donoDaChave(x.chave, "projeto:");
    const q = nomear(id);
    const quando = x.dado.atualizado_em || x.dado.criado_em;
    return { ...x.dado, empresa_id: id, cliente: q.email, empresa_nome: q.nome,
             dias: diasDesde(quando) };
  }).sort((a, b) => (b.atualizado_em || "").localeCompare(a.atualizado_em || ""));

  /* --------------------------------------------------- o que precisa de mim
   *
   * A regra é sempre a mesma: alguém está esperando resposta minha e não sabe
   * disso. Ordenado pelo que espera há mais tempo — é o que corre mais risco
   * de já ter procurado outro.
   */
  const temProposta = new Set(propostas.map((p) => p.empresa_id));
  const temProjeto = new Set(projetos.map((p) => p.empresa_id));

  const cobrancas = [];

  for (const p of pedidos) {
    if (temProposta.has(p.empresa_id)) continue;
    if (p.dias === null || p.dias < PEDIDO_ATRASADO) continue;
    cobrancas.push({
      tipo: "pedido sem proposta",
      dias: p.dias,
      cliente: p.cliente,
      empresa: p.empresa_nome || p.empresa,
      sobre: p.equipamento,
      acao: "mandar a proposta",
    });
  }

  for (const p of propostas) {
    if (temProjeto.has(p.empresa_id)) continue;
    if (p.dias === null || p.dias < PROPOSTA_ESFRIANDO) continue;
    cobrancas.push({
      tipo: "proposta sem resposta",
      dias: p.dias,
      cliente: p.cliente,
      empresa: p.empresa_nome,
      sobre: p.numero + " · " + (p.equipamento || ""),
      acao: "ligar ou mandar um lembrete",
    });
  }

  for (const p of projetos) {
    if (p.dias === null || p.dias < PROJETO_PARADO) continue;
    cobrancas.push({
      tipo: "projeto parado",
      dias: p.dias,
      cliente: p.cliente,
      empresa: p.empresa_nome,
      sobre: p.codigo + " · " + (p.nome || ""),
      acao: "atualizar a etapa ou subir a entrega",
    });
  }

  cobrancas.sort((a, b) => b.dias - a.dias);

  /* Um pedido repetido do mesmo cliente não é um lead a mais: é a mesma pessoa
     insistindo. Contar por empresa evita o painel dizer "11 pedidos" quando são
     11 tentativas de um teste. */
  const empresasComPedido = new Set(pedidos.map((p) => p.empresa_id));

  return {
    ok: true,
    em: new Date().toISOString(),
    resumo: {
      clientes: clientes.length,
      pedidos: pedidos.length,
      empresas_com_pedido: empresasComPedido.size,
      propostas: propostas.length,
      projetos: projetos.length,
      valor_em_proposta: propostas
        .filter((p) => !temProjeto.has(p.empresa_id))
        .reduce((s, p) => s + (Number(p.total) || 0), 0),
    },
    cobrancas,
    pedidos,
    propostas,
    projetos,
  };
}
