/* Entrar com o Google — a parte que decide se o token e VERDADEIRO.
 *
 * Como funciona o caminho inteiro: o botao do Google na pagina /entrar devolve
 * pro navegador um JWT assinado pelo Google dizendo "este navegador provou ser
 * fulano@gmail.com". O navegador manda esse JWT pro Worker, e ESTE arquivo
 * confere a assinatura contra as chaves publicas do Google. So depois disso o
 * email que esta dentro do token pode ser tratado como verdade.
 *
 * Por que a conferencia mora num arquivo separado do acesso.js: pra ser
 * testavel FORA do Worker. O teste (testar-google.js) gera um par de chaves
 * proprio, forja tokens — assinatura de outra chave, expirado, aud errado,
 * email nao verificado — e prova que cada um e RECUSADO. Se a conferencia
 * morasse dentro da rota, testar exigiria subir o Worker e um token real do
 * Google, e o teste nunca existiria.
 *
 * A regra de ouro: o "aud" do token TEM que ser o nosso client_id. Sem essa
 * checagem, um token emitido pra QUALQUER site (o cliente logou no
 * meujogo.com com Google) entraria aqui como se fosse nosso. E o erro mais
 * comum em login com Google, e e por isso que ele tem teste proprio.
 */

const EMISSORES = ["accounts.google.com", "https://accounts.google.com"];
const CERTS = "https://www.googleapis.com/oauth2/v3/certs";

/* base64url -> bytes. O JWT usa base64 SEM padding e com -_ no lugar de +/ */
function b64url(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

export function decodificarJwt(jwt) {
  if (typeof jwt !== "string") return null;
  const partes = jwt.split(".");
  if (partes.length !== 3) return null;
  try {
    const texto = new TextDecoder();
    return {
      cabecalho: JSON.parse(texto.decode(b64url(partes[0]))),
      corpo: JSON.parse(texto.decode(b64url(partes[1]))),
      assinatura: b64url(partes[2]),
      assinado: new TextEncoder().encode(partes[0] + "." + partes[1]),
    };
  } catch (e) {
    return null;
  }
}

/* Busca as chaves publicas do Google. O cache do fetch da Cloudflare respeita
   o Cache-Control que o Google manda (~5 h), entao isso nao vira uma chamada
   por login. */
export async function buscarJwks() {
  const r = await fetch(CERTS, { cf: { cacheTtl: 3600, cacheEverything: true } });
  if (!r.ok) throw new Error("certs do Google respondeu " + r.status);
  return r.json();
}

/**
 * Valida um credential do Google. Puro de proposito: jwks e relogio entram
 * por parametro, entao o teste injeta chave propria e hora falsa.
 *
 * Devolve { ok:true, email, nome } ou { ok:false, motivo }. Nunca lanca por
 * entrada malformada — token quebrado e recusa, nao erro 500.
 */
export async function validarTokenGoogle(jwt, jwks, opts) {
  const aud = opts && opts.aud;
  const agora = (opts && opts.agora) || Math.floor(Date.now() / 1000);
  if (!aud) return { ok: false, motivo: "sem client_id configurado" };

  const t = decodificarJwt(jwt);
  if (!t) return { ok: false, motivo: "token malformado" };

  /* o algoritmo vem do TOKEN, e token e palavra do atacante. Aceitar o que
     vier abriria o classico alg:"none". So RS256, que e o que o Google usa. */
  if (t.cabecalho.alg !== "RS256") {
    return { ok: false, motivo: "alg " + t.cabecalho.alg + " recusado" };
  }

  const chave = ((jwks && jwks.keys) || []).find((k) => k.kid === t.cabecalho.kid);
  if (!chave) return { ok: false, motivo: "kid desconhecido" };

  let valida = false;
  try {
    const pub = await crypto.subtle.importKey(
      "jwk", chave, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false, ["verify"]);
    valida = await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5", pub, t.assinatura, t.assinado);
  } catch (e) {
    return { ok: false, motivo: "chave publica ilegivel" };
  }
  if (!valida) return { ok: false, motivo: "assinatura nao confere" };

  const c = t.corpo;
  if (!EMISSORES.includes(c.iss)) return { ok: false, motivo: "iss estranho" };
  if (c.aud !== aud) return { ok: false, motivo: "aud de outro site" };
  if (!(typeof c.exp === "number" && c.exp > agora)) {
    return { ok: false, motivo: "token vencido" };
  }
  /* email_verified: o Google emite token ate pra email que o dono nunca
     confirmou. Aceitar esse seria deixar alguem entrar na conta de um email
     que talvez nem seja dele. */
  if (!c.email || c.email_verified !== true) {
    return { ok: false, motivo: "email nao verificado" };
  }
  return { ok: true, email: c.email, nome: c.name || "" };
}
