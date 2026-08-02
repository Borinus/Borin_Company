/* Enter tem que enviar, e email invalido tem que parar na porta.
   Usa Input.dispatchKeyEvent de verdade, nao um evento sintetico do JS:
   o objetivo e reproduzir o que o teclado faz, nao o que eu acho que faz. */
import { conectar, aba, js, pausa, cmd, SITE } from './base.mjs'

const P = (n, o, d = '') => console.log(`  ${o ? 'ok   ' : 'FALHA'} ${n.padEnd(48)} ${d}`)
let falhas = 0
const check = (n, o, d) => { if (!o) falhas++; P(n, o, d) }

async function tecla(s, id) {
  await js(s, `document.getElementById(${JSON.stringify(id)}).focus()`)
  for (const type of ['keyDown', 'char', 'keyUp']) {
    await cmd('Input.dispatchKeyEvent', {
      type, key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13, text: type === 'char' ? '\r' : undefined
    }, s)
  }
}

await conectar()

// ---------------------------------------------------- orcamento: email invalido
let s = await aba(`${SITE}/orcamento?cb=` + Date.now())
await pausa(11000)
check('orcamento tem form com submit',
  await js(s, `!!document.getElementById('formOrcamento') &&
    document.getElementById('btSolicitar').type === 'submit'`), '')

await js(s, `(() => { const p = (i, v) => { const e = document.getElementById(i);
  if (e) { e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); } };
  p('empresa','Teste Tecla'); p('contato','Joao'); p('email','joao@');
  p('equipamento','Painel'); p('ios','40'); p('acionamentos','4');
  return 1; })()`)
await tecla(s, 'empresa')
await pausa(4000)
let aviso = await js(s, `(document.getElementById('avisoFalta')||{}).textContent||''`)
let onde = await js(s, 'location.pathname')
check('Enter com email quebrado NAO envia', /enviado/.test(onde) === false, onde)
check('e explica o que esta errado', /email/i.test(aviso), aviso.slice(0, 56) || '(sem aviso)')

// ------------------------------------------------------ orcamento: email valido
await js(s, `(() => { const e = document.getElementById('email');
  e.value = 'joao@fabricateste.com.br'; e.dispatchEvent(new Event('input',{bubbles:true}));
  return 1; })()`)
await tecla(s, 'empresa')
await pausa(11000)
onde = await js(s, 'location.pathname')
check('Enter com email valido ENVIA', /enviado/.test(onde), onde)

// ------------------------------------------------------------ entrar: Enter loga
s = await aba(`${SITE}/entrar?cb=` + Date.now())
await pausa(10000)
check('entrar tem form com submit',
  await js(s, `!!document.getElementById('formEntrar') &&
    document.getElementById('btEntrar').type === 'submit'`), '')

await js(s, `(() => { const p = (i, v) => { const e = document.getElementById(i);
  if (e) { e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); } };
  p('email', ${JSON.stringify(process.env.CAIXA)});
  p('senha', ${JSON.stringify(process.env.SENHA)}); return 1; })()`)
await tecla(s, 'senha')
await pausa(11000)
const { quemEstaLogado } = await import('./base.mjs')
const eu = await quemEstaLogado(s)
check('Enter no campo de senha faz login',
  eu.toLowerCase() === (process.env.CAIXA || '').toLowerCase(), eu || 'ninguem logado')

console.log(`\n  ${falhas === 0 ? 'tudo ok' : falhas + ' falha(s)'}`)
process.exit(falhas === 0 ? 0 : 1)
