/**
 * Os arquivos do projeto.
 *
 * Ficam no R2, sob a chave <empresa>/<codigo>/<nome>. Nunca sao publicos: o
 * download passa pelo Worker, que confere a sessao e a empresa antes de
 * devolver o byte. E por isso que nao serve link de Drive — la o arquivo ou e
 * publico pra quem tiver o link, ou exige conta Google, e nenhum dos dois e o
 * que o cliente quer pro pessoal do campo.
 *
 * Quem sobe e o Mateus, pelo comando. Quem baixa e qualquer pessoa da empresa
 * dona do projeto, dono ou membro — o funcionario no chao de fabrica abre o
 * diagrama no celular com o login dele.
 */

const LIMITE = 60 * 1024 * 1024;   // um PDF de projeto grande cabe folgado

/* Nome de arquivo que o cliente ve. Tira caminho, acento perigoso e barra:
   a chave do R2 nao pode virar diretorio inventado por quem sobe. */
export function limparNome(v) {
  return String(v || "")
    /* barra vira hifen: o nome nao pode inventar pasta dentro do bucket */
    .replace(/[\\/]/g, "-")
    /* caractere de controle sai. Espaco e hifen FICAM: com eles removidos,
       "Contrato PROP-2026-001.pdf" chegaria no cliente como
       "ContratoPROP2026001.pdf" */
    .replace(/[\u0000-\u001f\u007f]/g, "")
    /* ponto no inicio nao escapa da pasta */
    .replace(/^\.+/, "")
    .trim()
    .slice(0, 140) || "arquivo";
}


export function limparCodigo(v) {
  return String(v || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 30);
}

function tipoPor(nome) {
  const e = (nome.split(".").pop() || "").toLowerCase();
  const m = {
    pdf: "application/pdf", zip: "application/zip", png: "image/png",
    jpg: "image/jpeg", jpeg: "image/jpeg", dwg: "image/vnd.dwg",
    xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    csv: "text/csv", txt: "text/plain",
  };
  return m[e] || "application/octet-stream";
}

/** Sobe um arquivo. So o Mateus, com o segredo de admin. */
export async function guardarArquivo(env, empresa, codigo, nome, bytes, extra) {
  const chave = empresa + "/" + limparCodigo(codigo) + "/" + limparNome(nome);
  await env.ARQUIVOS.put(chave, bytes, {
    httpMetadata: { contentType: tipoPor(nome) },
    customMetadata: {
      titulo: String((extra && extra.titulo) || "").slice(0, 140),
      etapa: String((extra && extra.etapa) || "").slice(0, 60),
      em: new Date().toISOString(),
    },
  });
  return chave;
}

/** O que existe naquele projeto. Nao devolve a chave crua pra fora. */
export async function listarArquivos(env, empresa, codigo) {
  const prefixo = empresa + "/" + limparCodigo(codigo) + "/";
  const r = await env.ARQUIVOS.list({ prefix: prefixo, include: ["customMetadata"] });
  return r.objects.map((o) => ({
    nome: o.key.slice(prefixo.length),
    tamanho: o.size,
    em: (o.customMetadata && o.customMetadata.em) || o.uploaded,
    titulo: (o.customMetadata && o.customMetadata.titulo) || "",
    etapa: (o.customMetadata && o.customMetadata.etapa) || "",
  })).sort((a, b) => String(b.em).localeCompare(String(a.em)));
}

/**
 * Devolve o arquivo, ja com a sessao conferida por quem chamou.
 *
 * A empresa vem da SESSAO, nunca do pedido: se viesse do parametro, trocar um
 * id na URL daria o acervo do vizinho. E a mesma razao de o nome ser limpo de
 * novo aqui — "../" na URL nao pode escapar da pasta da empresa.
 */
export async function lerArquivo(env, empresa, codigo, nome) {
  const chave = empresa + "/" + limparCodigo(codigo) + "/" + limparNome(nome);
  const obj = await env.ARQUIVOS.get(chave);
  if (!obj) return null;
  const h = new Headers();
  obj.writeHttpMetadata(h);
  h.set("etag", obj.httpEtag);
  h.set("Cache-Control", "private, max-age=0, must-revalidate");
  /* inline: o cliente abre o PDF no navegador do celular em vez de baixar um
     arquivo que ele nao vai achar depois */
  h.set("Content-Disposition",
    'inline; filename="' + limparNome(nome).replace(/"/g, "") + '"');
  return new Response(obj.body, { headers: h });
}

export async function apagarArquivo(env, empresa, codigo, nome) {
  await env.ARQUIVOS.delete(
    empresa + "/" + limparCodigo(codigo) + "/" + limparNome(nome));
}

export const LIMITE_ARQUIVO = LIMITE;
