/* O formulario nao pode mandar o cliente pra tela de "recebido" quando o
   servidor recusou. Antes ele mandava, e o cliente ia embora achando que
   pediu — pedido que nao existe em lugar nenhum. */
import { conectar, aba, js, pausa, cmd, SITE } from './base.mjs'

const P = (n, o, d = '') => console.log(`  ${o ? 'ok   ' : 'FALHA'} ${n.padEnd(50)} ${d}`)
let falhas = 0
const check = (n, o, d) => { if (!o) falhas++; P(n, o, d) }

await conectar()
const s = await aba(`${SITE}/orcamento?cb=` + Date.now())
await pausa(11000)

/* faz o servidor recusar de um jeito que o navegador nao pega sozinho:
   o campo do WhatsApp fica curto e o canal pede resposta por WhatsApp.
   A validacao do navegador aceita — a do servidor nao. */
await js(s, `(() => {
  const p = (i, v) => { const e = document.getElementById(i);
    if (e) { e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); } };
  p('empresa','Teste Recusa'); p('contato','Joao');
  p('email','joao@fabricateste.com.br'); p('equipamento','Painel');
  /* o servidor exige 12 digitos quando o canal e email+whats */
  p('fone','+55 54 9');
  const c = document.querySelector('input[type=radio][value="email+whats"]');
  if (c) { c.checked = true; c.dispatchEvent(new Event('change',{bubbles:true})); }
  return 1;
})()`)

/* desliga a validacao do navegador pra o pedido chegar mesmo no servidor:
   e assim que um cliente com JS antigo ou um robo chegaria */
await js(s, `window.validar = function () { return true; }; 1`)
await js(s, `document.getElementById('btSolicitar').click(); 1`)
await pausa(11000)

const onde = await js(s, 'location.pathname')
check('recusado pelo servidor NAO vai pra /enviado', !/enviado/.test(onde), onde)

const aviso = await js(s, `(document.getElementById('avisoFalta')||{}).textContent||''`)
check('e a pagina explica o motivo', aviso.trim().length > 0, aviso.slice(0, 62))

const botao = await js(s, `(() => { const b = document.getElementById('btSolicitar');
  return JSON.stringify({ texto: b.textContent.trim(), travado: b.disabled }); })()`)
const b = JSON.parse(botao)
check('o botao volta a funcionar', !b.travado, b.texto)

console.log(`\n  ${falhas === 0 ? 'tudo ok' : falhas + ' falha(s)'}`)
process.exit(falhas === 0 ? 0 : 1)
