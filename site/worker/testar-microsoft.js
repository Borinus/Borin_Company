// Prova que o login com Microsoft recusa token forjado.
//
//     node site/worker/testar-microsoft.js
//
// Espelha o testar-google.js. validarTokenMicrosoft decide quem entra na conta
// de quem. O teste não é "o token bom passa" — é "TODOS os tokens maus batem na
// porta e ficam de fora".
//
// Como testa sem a Microsoft: gera um par de chaves RSA próprio e assina tokens
// aqui. O jwks entra por parâmetro (por isso a função é pura), então a "chave
// da Microsoft" do teste é a nossa. Um segundo par faz o papel do atacante.
//
// Regra #1 do AGENTS.md, embutida: no fim planta um defeito (apaga a checagem
// de assinatura numa CÓPIA do microsoft.js) e confere que o token do ladrão
// PASSARIA a entrar. Se essa prova falhar, o teste virou enfeite.

import { generateKeyPairSync, createSign } from "node:crypto";
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const FONTE = readFileSync(join(AQUI, "microsoft.js"), "utf8");

// o import de .js sem package.json cai em CommonJS; copiar pra .mjs resolve.
// A cópia é byte a byte: testa o arquivo real.
const TMP = mkdtempSync(join(tmpdir(), "borin-microsoft-"));
writeFileSync(join(TMP, "microsoft.mjs"), FONTE);
const m = await import(pathToFileURL(join(TMP, "microsoft.mjs")).href);

// ------------------------------------------------------------ ferramentas

const b64u = (buf) => Buffer.from(buf).toString("base64url");

function novoPar(kid) {
  const { publicKey, privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const jwk = publicKey.export({ format: "jwk" });
  return { privada: privateKey, jwk: { ...jwk, kid, alg: "RS256", use: "sig" } };
}

function assinar(privada, cabecalho, corpo) {
  const base = b64u(JSON.stringify(cabecalho)) + "." + b64u(JSON.stringify(corpo));
  const ass = createSign("RSA-SHA256").update(base).end().sign(privada);
  return base + "." + b64u(ass);
}

const AUD = "11111111-2222-3333-4444-555555555555";      // client_id de teste
const TID = "9188040d-6c67-4c5b-b112-36a304b66dad";      // tenant de conta pessoal
const AGORA = 1754500000;
const microsoft = novoPar("chave-ms");   // faz o papel da Microsoft
const ladrao = novoPar("chave-ms");      // MESMO kid, chave diferente
const jwks = { keys: [microsoft.jwk] };

const corpoBom = {
  ver: "2.0",
  iss: "https://login.microsoftonline.com/" + TID + "/v2.0",
  tid: TID,
  aud: AUD,
  exp: AGORA + 3600,
  preferred_username: "cliente@empresa.com",
  name: "Cliente Teste",
};
const cab = { alg: "RS256", kid: "chave-ms", typ: "JWT" };

const passos = [];
function P(nome, ok, detalhe = "") {
  passos.push([nome, ok]);
  console.log("  %s %s %s", ok ? "ok   " : "FALHA", nome.padEnd(52), detalhe);
}

async function valida(jwt, opts) {
  return m.validarTokenMicrosoft(jwt, jwks, { aud: AUD, agora: AGORA, ...opts });
}

console.log("\n  " + "=".repeat(66));
console.log("  LOGIN COM MICROSOFT — a porta so abre pra token verdadeiro");
console.log("  " + "=".repeat(66));

// ------------------------------------------------- o unico que pode entrar
let r = await valida(assinar(microsoft.privada, cab, corpoBom));
P("token legitimo ENTRA", r.ok === true && r.email === "cliente@empresa.com",
  r.ok ? r.email : r.motivo);

// aceita email tambem no claim `email` (conta pessoal costuma trazer os dois)
r = await valida(assinar(microsoft.privada, cab,
  { ...corpoBom, preferred_username: undefined, email: "pessoal@outlook.com" }));
P("pega o email do claim `email` quando nao ha preferred_username",
  r.ok === true && r.email === "pessoal@outlook.com", r.ok ? r.email : r.motivo);

// ------------------------------------------------------- todos os outros
r = await valida(assinar(ladrao.privada, cab, corpoBom));
P("assinatura de OUTRA chave, mesmo kid: fora", !r.ok, r.motivo || "ENTROU!");

const legit = assinar(microsoft.privada, cab, corpoBom);
const partes = legit.split(".");
const adulterado = partes[0] + "." +
  b64u(JSON.stringify({ ...corpoBom, preferred_username: "atacante@evil.com" })) + "." + partes[2];
P("corpo trocado depois de assinado: fora", !(await valida(adulterado)).ok,
  (await valida(adulterado)).motivo || "ENTROU!");

r = await valida(assinar(microsoft.privada, cab, { ...corpoBom, exp: AGORA - 60 }));
P("token vencido: fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(microsoft.privada, cab,
  { ...corpoBom, aud: "outro-app-qualquer" }));
P("token emitido pra OUTRO app (aud): fora", !r.ok, r.motivo || "ENTROU!");

// iss que nao casa com o tid do token — o ataque que a amarra iss/tid barra
r = await valida(assinar(microsoft.privada, cab,
  { ...corpoBom, iss: "https://login.microsoftonline.com/outro-tenant/v2.0" }));
P("iss que nao casa com o tid: fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(microsoft.privada, cab,
  { ...corpoBom, iss: "https://login.evil.com/" + TID + "/v2.0" }));
P("emissor que nao e a Microsoft: fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(microsoft.privada, cab, { ...corpoBom, ver: "1.0" }));
P("token v1.0 (nao v2.0): fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(microsoft.privada, cab,
  { ...corpoBom, email: undefined, preferred_username: "sem-arroba" }));
P("sem email valido no token: fora", !r.ok, r.motivo || "ENTROU!");

r = await m.validarTokenMicrosoft(
  b64u(JSON.stringify({ alg: "none", kid: "chave-ms" })) + "." + partes[1] + ".",
  jwks, { aud: AUD, agora: AGORA });
P('alg "none": fora', !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(microsoft.privada, { ...cab, kid: "kid-inventado" }, corpoBom));
P("kid que a Microsoft nao publica: fora", !r.ok, r.motivo || "ENTROU!");

for (const lixo of ["", "so.duas", null, 42, "a.b.c.d", "%%%.%%%.%%%"]) {
  const x = await m.validarTokenMicrosoft(lixo, jwks, { aud: AUD, agora: AGORA });
  if (x.ok) P("lixo " + JSON.stringify(lixo) + " ENTROU", false, "");
}
P("lixo malformado nunca entra nem estoura", true, "6 formas testadas");

r = await m.validarTokenMicrosoft(legit, jwks, { aud: null, agora: AGORA });
P("sem client_id configurado: fora", !r.ok, r.motivo || "ENTROU!");

// ---------------------------------------- a prova de que o teste tem dente
console.log("\n  [prova] plantando o defeito classico numa copia: sem conferir assinatura");
const sabotado = FONTE.replace(
  'if (!valida) return { ok: false, motivo: "assinatura nao confere" };', "");
if (sabotado === FONTE) {
  P("consegui plantar o defeito", false, "o texto da checagem mudou — ajustar o teste");
} else {
  writeFileSync(join(TMP, "sabotado.mjs"), sabotado);
  const s = await import(pathToFileURL(join(TMP, "sabotado.mjs")).href);
  const furada = await s.validarTokenMicrosoft(
    assinar(ladrao.privada, cab, corpoBom), jwks, { aud: AUD, agora: AGORA });
  P("sem a checagem, o token do ladrao ENTRARIA", furada.ok === true,
    "logo, e a checagem que segura a porta");
}

const bons = passos.filter(([, ok]) => ok).length;
console.log("\n  " + "=".repeat(66));
console.log("  %d/%d passos ok", bons, passos.length);
for (const [n, ok] of passos) if (!ok) console.log("    FALHOU:", n);
console.log("  " + "=".repeat(66) + "\n");
process.exit(bons === passos.length ? 0 : 1);
