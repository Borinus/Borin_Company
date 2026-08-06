// Prova que o login com Google recusa token forjado.
//
//     node site/worker/testar-google.js
//
// O que esta em jogo: validarTokenGoogle decide quem entra na conta de quem.
// Se ela aceitar um token que nao devia, qualquer um entra como qualquer
// cliente. Entao o teste nao e "o token bom passa" — e "TODOS os tokens maus
// batem na porta e ficam de fora".
//
// Como testa sem o Google: gera um par de chaves RSA proprio e assina tokens
// aqui mesmo. O jwks entra por parametro (por isso a funcao e pura), entao a
// "chave do Google" do teste e a nossa. Um segundo par de chaves faz o papel
// do atacante.
//
// Regra #1 do AGENTS.md, embutida no proprio arquivo: no fim, o teste planta
// um defeito (apaga a checagem de assinatura numa COPIA do google.js) e
// confere que o caso "assinatura de outra chave" passaria a ENTRAR. Se um dia
// essa prova falhar, o teste virou enfeite.

import { generateKeyPairSync, createSign } from "node:crypto";
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const FONTE = readFileSync(join(AQUI, "google.js"), "utf8");

// o import de .js sem package.json cai em CommonJS; copiar pra .mjs resolve
// sem mexer no build do wrangler. A copia e byte a byte: testa o arquivo real.
const TMP = mkdtempSync(join(tmpdir(), "borin-google-"));
writeFileSync(join(TMP, "google.mjs"), FONTE);
const g = await import(pathToFileURL(join(TMP, "google.mjs")).href);

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

const AUD = "111111-teste.apps.googleusercontent.com";
const AGORA = 1754500000;
const google = novoPar("chave-google");   // faz o papel do Google
const ladrao = novoPar("chave-google");   // MESMO kid, chave diferente
const jwks = { keys: [google.jwk] };

const corpoBom = {
  iss: "https://accounts.google.com", aud: AUD, exp: AGORA + 3600,
  email: "cliente@gmail.com", email_verified: true, name: "Cliente Teste",
};
const cab = { alg: "RS256", kid: "chave-google", typ: "JWT" };

const passos = [];
function P(nome, ok, detalhe = "") {
  passos.push([nome, ok]);
  console.log("  %s %s %s", ok ? "ok   " : "FALHA", nome.padEnd(52), detalhe);
}

async function valida(jwt, opts) {
  return g.validarTokenGoogle(jwt, jwks, { aud: AUD, agora: AGORA, ...opts });
}

console.log("\n  " + "=".repeat(66));
console.log("  LOGIN COM GOOGLE — a porta so abre pra token verdadeiro");
console.log("  " + "=".repeat(66));

// ------------------------------------------------- o unico que pode entrar
let r = await valida(assinar(google.privada, cab, corpoBom));
P("token legitimo ENTRA", r.ok === true && r.email === "cliente@gmail.com",
  r.ok ? r.email : r.motivo);

// ------------------------------------------------------- todos os outros
r = await valida(assinar(ladrao.privada, cab, corpoBom));
P("assinatura de OUTRA chave, mesmo kid: fora", !r.ok, r.motivo || "ENTROU!");

const legit = assinar(google.privada, cab, corpoBom);
const partes = legit.split(".");
const adulterado = partes[0] + "." +
  b64u(JSON.stringify({ ...corpoBom, email: "atacante@gmail.com" })) + "." + partes[2];
P("corpo trocado depois de assinado: fora", !(await valida(adulterado)).ok,
  (await valida(adulterado)).motivo || "ENTROU!");

r = await valida(assinar(google.privada, cab, { ...corpoBom, exp: AGORA - 60 }));
P("token vencido: fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(google.privada, cab,
  { ...corpoBom, aud: "site-de-jogos.apps.googleusercontent.com" }));
P("token emitido pra OUTRO site (aud): fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(google.privada, cab, { ...corpoBom, email_verified: false }));
P("email que o dono nunca confirmou: fora", !r.ok, r.motivo || "ENTROU!");

r = await valida(assinar(google.privada, cab, { ...corpoBom, iss: "accounts.evil.com" }));
P("emissor que nao e o Google: fora", !r.ok, r.motivo || "ENTROU!");

const semAss = partes[0] + "." + partes[1] + ".";
r = await g.validarTokenGoogle(
  b64u(JSON.stringify({ alg: "none", kid: "chave-google" })) + "." + partes[1] + ".",
  jwks, { aud: AUD, agora: AGORA });
P('alg "none": fora', !r.ok, r.motivo || "ENTROU!");
P("assinatura vazia: fora", !(await valida(semAss)).ok, "");

r = await valida(assinar(google.privada, { ...cab, kid: "kid-inventado" }, corpoBom));
P("kid que o Google nao publica: fora", !r.ok, r.motivo || "ENTROU!");

for (const lixo of ["", "so.duas", null, 42, "a.b.c.d", "%%%.%%%.%%%"]) {
  const x = await g.validarTokenGoogle(lixo, jwks, { aud: AUD, agora: AGORA });
  if (x.ok) P("lixo " + JSON.stringify(lixo) + " ENTROU", false, "");
}
P("lixo malformado nunca entra nem estoura", true, "6 formas testadas");

r = await g.validarTokenGoogle(legit, jwks, { aud: null, agora: AGORA });
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
  const furada = await s.validarTokenGoogle(
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
