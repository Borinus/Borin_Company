/* /padrao e /projeto: logado, salvando na conta, e chegando na confirmacao
   mesmo quando o sessionStorage esta bloqueado — que e o caso do navegador
   embutido do Instagram e do WhatsApp, de onde vem parte do trafego. */
import { conectar, aba, js, pausa, cmd, SITE, quemEstaLogado } from './base.mjs'

const CAIXA = process.env.CAIXA, SENHA = process.env.SENHA
const P = (n, o, d = '') => console.log(`  ${o ? 'ok   ' : 'FALHA'} ${n.padEnd(46)} ${d}`)
let falhas = 0
const check = (n, o, d) => { if (!o) falhas++; P(n, o, d) }

await conectar()
const s = await aba(`${SITE}/entrar?t=` + Date.now())
await pausa(9000)
await js(s, `(() => { const p = (i, v) => { const e = document.getElementById(i);
  if (e) { e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); } };
  p('email', ${JSON.stringify(CAIXA)}); p('senha', ${JSON.stringify(SENHA)});
  document.getElementById('btEntrar').click(); return 1; })()`)
await pausa(10000)
/* Sem login confirmado NAO adianta seguir: /padrao e /projeto funcionam
   anonimos por design, entao os passos seguintes passariam em falso — o
   campo volta do armazenamento local e parece que veio da conta. */
const eu = await quemEstaLogado(s)
check('logou', eu.toLowerCase() === CAIXA.toLowerCase(), eu || 'ninguem logado')
if (eu.toLowerCase() !== CAIXA.toLowerCase()) {
  console.log('  parei aqui: sem sessao, o resto do teste nao prova nada')
  process.exit(1)
}

for (const pag of ['padrao', 'projeto']) {
  console.log(`\n  --- /${pag} ---`)
  await cmd('Page.navigate', { url: `${SITE}/${pag}?cb=` + Date.now() }, s)
  await pausa(11000)

  const est = JSON.parse(await js(s, `(() => {
    const cs = Array.from(document.querySelectorAll('input,select,textarea'));
    return JSON.stringify({
      titulo: (document.querySelector('h1') || {}).textContent || '',
      campos: cs.length,
      preenchidos: cs.filter(e => e.value && e.type !== 'radio').length,
      temEnviar: !!Array.from(document.querySelectorAll('button'))
        .find(b => /enviar|whats|email/i.test(b.textContent))
    });
  })()`))
  check(`/${pag} abriu logado`, est.campos > 0, `${est.campos} campos · ${est.titulo.slice(0, 34)}`)
  check(`/${pag} tem botao de enviar`, est.temEnviar, '')

  /* preenche o primeiro campo de texto e confere que a conta guarda sozinha */
  const marca = 'MARCA' + Date.now()
  const id = await js(s, `(() => {
    const e = Array.from(document.querySelectorAll('input[type=text]'))
      .find(x => x.offsetParent !== null);
    if (!e) return '';
    e.value = ${JSON.stringify(marca)};
    e.dispatchEvent(new Event('input', { bubbles: true }));
    e.dispatchEvent(new Event('change', { bubbles: true }));
    return e.id || '';
  })()`)
  await pausa(4000)

  /* bloqueia o sessionStorage: e assim que o navegador do Instagram se comporta */
  await js(s, `(() => { try {
    Object.defineProperty(window, 'sessionStorage', {
      get() { throw new Error('bloqueado'); }, configurable: true });
  } catch (e) {} return 1; })()`)

  const antes = await js(s, 'location.pathname')
  /* /projeto nao tem "Enviar por email" — so WhatsApp. Os dois caminhos passam
     pelo mesmo enviar(), entao qualquer um serve pra provar o redirect. */
  const clicou = await js(s, `(() => { const bs = Array.from(document.querySelectorAll('button'));
    const b = bs.find(x => /por email/i.test(x.textContent))
           || bs.find(x => /whats/i.test(x.textContent));
    if (b) { b.click(); return b.textContent.trim(); } return ''; })()`)
  check(`/${pag} tem caminho de envio clicavel`, !!clicou, clicou || 'nenhum botao de envio')
  await pausa(9000)
  const depois = await js(s, 'location.pathname')
  check(`/${pag} chega na confirmacao sem sessionStorage`, /enviado/.test(depois),
    `${antes} -> ${depois}`)

  /* volta e confere se a conta guardou o que foi digitado */
  if (id) {
    await cmd('Page.navigate', { url: `${SITE}/${pag}?cb=` + Date.now() }, s)
    await pausa(11000)
    const voltou = await js(s, `(document.getElementById(${JSON.stringify(id)}) || {}).value || ''`)
    check(`/${pag} guardou na conta e voltou preenchido`, voltou === marca,
      voltou ? 'campo ' + id + ' voltou' : 'campo ' + id + ' voltou vazio')
  }
}

console.log(`\n  ${falhas === 0 ? 'tudo ok' : falhas + ' falha(s)'}`)
process.exit(falhas === 0 ? 0 : 1)
