/* Entrar com a Microsoft — a parte que decide se o token e VERDADEIRO.
 *
 * Espelha o google.js. O botao "Entrar com a Microsoft" na /entrar leva o
 * navegador ao login da Microsoft, que redireciona de volta com um id_token
 * (JWT) assinado dizendo "este navegador provou ser fulano@empresa.com". O
 * navegador manda esse JWT pro Worker e ESTE arquivo confere a assinatura
 * contra as chaves publicas da Microsoft. So depois disso o email do token
 * pode ser tratado como verdade.
 *
 * Fica separado do acesso.js pelo mesmo motivo do google.js: pra ser testavel
 * FORA do Worker. testar-microsoft.js gera um par de chaves proprio, forja
 * tokens (assinatura de outra chave, aud errado, iss estranho, expirado,
 * alg:"none", kid desconhecido) e prova que cada um e RECUSADO.
 *
 * Diferencas pra Microsoft (doc: learn.microsoft.com/entra/identity-platform/id-tokens):
 *   - o emissor NAO e fixo: varia por tenant. O token v2.0 traz o tenant em
 *     `tid`, e o `iss` tem que ser exatamente
 *     https://login.microsoftonline.com/<tid>/v2.0 — cobre conta de empresa e
 *     conta pessoal (tenant 9188040d-...). A assinatura ja garante que veio da
 *     Microsoft; essa checagem garante que veio do endpoint v2.0.
 *   - o email vem em `email` OU em `preferred_username` (conta de empresa
 *     costuma trazer so o segundo). Nao ha `email_verified`.
 *   - a regra de ouro continua: `aud` TEM que ser o nosso client_id, senao um
 *     token emitido pra outro app entraria como se fosse nosso.
 */

const JWKS_MS = "https://login.microsoftonline.com/common/discovery/v2.0/keys";
const ISS_BASE = "https://login.microsoftonline.com/";

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

/* Chaves publicas da Microsoft. O fetch da Cloudflare respeita o Cache-Control
   que a Microsoft manda, entao nao vira uma chamada por login. */
export async function buscarJwksMicrosoft() {
  const r = await fetch(JWKS_MS, { cf: { cacheTtl: 3600, cacheEverything: true } });
  if (!r.ok) throw new Error("certs da Microsoft respondeu " + r.status);
  return r.json();
}

function pareceEmail(v) {
  return typeof v === "string" && /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/.test(v);
}

/**
 * Valida um id_token da Microsoft. Puro de proposito: jwks e relogio entram por
 * parametro, entao o teste injeta chave propria e hora falsa.
 *
 * Devolve { ok:true, email, nome } ou { ok:false, motivo }. Nunca lanca por
 * entrada malformada — token quebrado e recusa, nao erro 500.
 */
export async function validarTokenMicrosoft(jwt, jwks, opts) {
  const aud = opts && opts.aud;
  const agora = (opts && opts.agora) || Math.floor(Date.now() / 1000);
  if (!aud) return { ok: false, motivo: "sem client_id configurado" };

  const t = decodificarJwt(jwt);
  if (!t) return { ok: false, motivo: "token malformado" };

  /* o algoritmo vem do TOKEN, e token e palavra do atacante. So RS256, que e
     o que a Microsoft usa — aceitar o que vier abriria o classico alg:"none". */
  if (t.cabecalho.alg !== "RS256") {
    return { ok: false, motivo: "alg " + t.cabecalho.alg + " recusado" };
  }

  const chave = ((jwks && jwks.keys) || []).find((k) => k.kid === t.cabecalho.kid);
  if (!chave) return { ok: false, motivo: "kid desconhecido" };

  let valida = false;
  try {
    const pub = await crypto.subtle.importKey(
      "jwk",
      { kty: chave.kty, n: chave.n, e: chave.e },
      { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false, ["verify"]);
    valida = await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5", pub, t.assinatura, t.assinado);
  } catch (e) {
    return { ok: false, motivo: "chave publica ilegivel" };
  }
  if (!valida) return { ok: false, motivo: "assinatura nao confere" };

  const c = t.corpo;
  if (c.ver !== "2.0") return { ok: false, motivo: "token nao e v2.0" };
  if (c.aud !== aud) return { ok: false, motivo: "aud de outro app" };
  /* o emissor tem que casar com o tenant DENTRO do token: so a Microsoft
     assina um token cujo iss = base + tid + /v2.0 (a assinatura ja provou que
     e ela). Sem essa amarra, um token de outro emissor com aud copiado passaria. */
  if (!c.tid || c.iss !== ISS_BASE + c.tid + "/v2.0") {
    return { ok: false, motivo: "iss/tid inconsistente" };
  }
  if (!(typeof c.exp === "number" && c.exp > agora)) {
    return { ok: false, motivo: "token vencido" };
  }

  const email = c.email || c.preferred_username || "";
  if (!pareceEmail(email)) return { ok: false, motivo: "sem email no token" };

  return { ok: true, email, nome: c.name || "" };
}
