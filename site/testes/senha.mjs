import {conectar,aba,js,pausa,cmd,SITE,quemEstaLogado} from './base.mjs'
const P=(n,o,d='')=>console.log(`${o?'  ok   ':'  FALHA'} ${n.padEnd(44)} ${d}`)
const CAIXA=process.env.CAIXA, VELHA=process.env.SENHA, NOVA='SenhaNova2026x'
await conectar()
const s=await aba(`${SITE}/entrar?t=`+Date.now()); await pausa(9000)
await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
  if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}}
  p('email',${JSON.stringify(CAIXA)});p('senha',${JSON.stringify(VELHA)})
  document.getElementById('btEntrar').click();return 1})()`)
await pausa(10000)
const pediu=await js(s,`(()=>{const e=document.getElementById('cxTrocar');
  return !!e && !e.classList.contains('oculto') && e.offsetParent!==null})()`)
P('site pediu pra trocar a senha provisoria', pediu, pediu?'':'caixa de troca nao apareceu')
if(!pediu){process.exit(1)}
const campos=await js(s,`JSON.stringify(Array.from(document.querySelectorAll('#cxTrocar input')).map(e=>e.id))`)
P('campos da troca', true, campos)
await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
  if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}}
  p('nova',${JSON.stringify(NOVA)});p('nova2',${JSON.stringify(NOVA)})
  document.getElementById('btTrocar').click();return 1})()`)
await pausa(10000)
const erro=await js(s,`(document.getElementById('erroTrocar')||{}).textContent||''`)
const onde=await js(s,'location.pathname')
P('troca aceita', !erro.trim(), erro.trim()? erro.slice(0,60) : 'foi pra '+onde)
// SAI de verdade: com a sessao viva, /entrar redireciona e o teste passa em falso
await js(s,`fetch('/api/acesso/sair',{method:'POST',credentials:'same-origin'}).then(()=>1)`)
await cmd('Page.navigate',{url:`${SITE}/entrar?t=`+Date.now()},s); await pausa(9000)
await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
  if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}}
  p('email',${JSON.stringify(CAIXA)});p('senha',${JSON.stringify(NOVA)})
  document.getElementById('btEntrar').click();return 1})()`)
await pausa(10000)
const e2=await js(s,`(document.getElementById('erro')||{}).textContent||''`)
const p2=await js(s,'location.pathname')
const eu2=await quemEstaLogado(s)
P('entra com a senha nova', eu2.toLowerCase()===CAIXA.toLowerCase(), eu2||'ninguem logado')
// e a velha tem que falhar
await js(s,`fetch('/api/acesso/sair',{method:'POST',credentials:'same-origin'}).then(()=>1)`)
await cmd('Page.navigate',{url:`${SITE}/entrar?t=`+Date.now()},s); await pausa(9000)
await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
  if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}}
  p('email',${JSON.stringify(CAIXA)});p('senha',${JSON.stringify(VELHA)})
  document.getElementById('btEntrar').click();return 1})()`)
await pausa(10000)
const e3=await js(s,`(document.getElementById('erro')||{}).textContent||''`)
P('senha velha deixou de valer', /conferem|inval/i.test(e3), e3.slice(0,50)||'NAO RECUSOU')
process.exit(0)
