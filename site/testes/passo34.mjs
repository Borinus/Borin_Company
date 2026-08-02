import {conectar,aba,js,pausa,cmd,SITE} from './base.mjs'
const P=(n,o,d='')=>console.log(`PASSO:${n}|${o?1:0}|${d}`)
await conectar()
const s=await aba(`${SITE}/entrar?t=`+Date.now())
await pausa(9000)
await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
  if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}}
  p('email',${JSON.stringify(process.env.CAIXA)});p('senha',${JSON.stringify(process.env.SENHA)})
  Array.from(document.querySelectorAll('button')).find(x=>/entrar/i.test(x.textContent)).click();return 1})()`)
await pausa(10000)
const txt=await js(s,'document.body.innerText||""')
const erro=await js(s,`(document.getElementById('erro')||{}).textContent||''`)
P('login com a senha do email', !/não conferem|invalid/i.test(erro), await js(s,'location.pathname'))
await cmd('Page.navigate',{url:`${SITE}/cadastro`},s); await pausa(10000)
const tem=await js(s,"!!document.getElementById('razao_social')")
P('cadastro abriu logado', tem, tem?'':'nao logou')
if(tem){
  await js(s,`(()=>{const p=(i,v)=>{const e=document.getElementById(i)
    if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}}
    p('razao_social','Verificacao Ciclo Ltda');p('cnpj','44.555.666/0001-77')
    p('cep','95044-080');p('logradouro','Rua Os Dezoito do Forte');p('numero_end','2366')
    p('bairro','Sao Pelegrino');p('cidade','Caxias do Sul');p('uf','RS')
    p('rep_nome','Sandra Reis');p('rep_cargo','Diretora de Operacoes')
    p('rep_cpf','321.654.987-00');p('rep_email',${JSON.stringify(process.env.CAIXA)});return 1})()`)
  await js(s,`document.getElementById('btSalvar').click()`); await pausa(11000)
  const r=await js(s,`(document.getElementById('ok')||{}).textContent||(document.getElementById('erro')||{}).textContent||''`)
  P('cadastro salvo', /recebido|reenvio/i.test(r), r.slice(0,46))
}
process.exit(0)
