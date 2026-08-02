import {conectar,aba,js,pausa,SITE} from './base.mjs'
await conectar()
const s=await aba(`${SITE}/orcamento?t=`+Date.now())
await pausa(10000)
await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
  if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}}
  p('empresa','Verificacao Ciclo Ltda');p('contato','Sandra Reis')
  p('email',${JSON.stringify(process.env.CAIXA)})
  p('equipamento','Painel de cabine de pintura');p('codigo','CICLO-FIM')
  p('acionamentos','8');p('ios','96');p('seg_qtd','6')
  const f=document.getElementById('fone')
  for(const d of '54999887766'){f.value+=d;f.dispatchEvent(new Event('input',{bubbles:true}))}
  const b=document.querySelector('input[type=radio][value="B"]');if(b){b.checked=true;b.dispatchEvent(new Event('change',{bubbles:true}))}
  const nr=document.querySelector('input[type=radio][value="sim"]');if(nr){nr.checked=true;nr.dispatchEvent(new Event('change',{bubbles:true}))}
  return 1})()`)
await js(s,`Array.from(document.querySelectorAll('button')).find(x=>/solicitar/i.test(x.textContent)).click()`)
await pausa(11000)
const p=await js(s,'location.pathname')
console.log(p)
process.exit(/enviado/.test(p)?0:1)
