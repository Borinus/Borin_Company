import { conectar, aba, js, pausa, cmd, SITE } from './base.mjs'

const IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ' +
  'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'

await conectar()
const s = await aba('about:blank')
await cmd('Emulation.setDeviceMetricsOverride',
  { width: 390, height: 844, deviceScaleFactor: 3, mobile: true }, s)
await cmd('Emulation.setUserAgentOverride', { userAgent: IPHONE }, s)
await cmd('Page.navigate', { url: `${SITE}/orcamento?cb=` + Date.now() }, s)
await pausa(12000)

const r = await js(s, `(() => {
  const cs = Array.from(document.querySelectorAll('input,select,textarea'))
    .filter(e => e.offsetParent !== null);
  const tam = {}, ruins = [];
  cs.forEach(e => {
    const f = parseFloat(getComputedStyle(e).fontSize);
    tam[f] = (tam[f] || 0) + 1;
    if (f < 16) { ruins.push((e.id || e.type) + ':' + f + 'px'); }
  });
  const alturas = [...new Set(cs.map(e => Math.round(e.getBoundingClientRect().height)))]
    .sort((a, b) => a - b);
  return JSON.stringify({
    campos: cs.length,
    fontes: tam,
    abaixoDe16: ruins.length ? ruins : 'NENHUM',
    alturas: alturas,
    rolaNaHorizontal: document.documentElement.scrollWidth > window.innerWidth,
    largura: window.innerWidth
  });
})()`)

const d = JSON.parse(r)
console.log('  campos visiveis:      ' + d.campos)
console.log('  tamanhos de fonte:    ' + JSON.stringify(d.fontes))
console.log('  abaixo de 16px:       ' +
  (Array.isArray(d.abaixoDe16) ? d.abaixoDe16.join(', ') : d.abaixoDe16))
console.log('  alturas dos campos:   ' + JSON.stringify(d.alturas) + ' px')
console.log('  rola na horizontal:   ' + d.rolaNaHorizontal)
console.log('  largura da janela:    ' + d.largura)

const foto = await cmd('Page.captureScreenshot', { format: 'png' }, s)
const fs = await import('node:fs')
fs.writeFileSync(process.env.FOTO, Buffer.from(foto.data, 'base64'))
process.exit(Array.isArray(d.abaixoDe16) ? 1 : 0)
