export const SITE='https://borinprojetos.com.br'
let n=0; const w=new Map(); let ws
export const cmd=(m,p={},s)=>new Promise((ok,no)=>{const i=++n;w.set(i,{ok,no})
  ws.send(JSON.stringify(s?{id:i,method:m,params:p,sessionId:s}:{id:i,method:m,params:p}))
  setTimeout(()=>{if(w.has(i)){w.delete(i);no(new Error('timeout '+m))}},60000)})
export async function conectar(){
  const v=await (await fetch('http://127.0.0.1:9333/json/version')).json()
  ws=new WebSocket(v.webSocketDebuggerUrl)
  await new Promise(ok=>ws.addEventListener('open',ok,{once:true}))
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data)
    if(m.id&&w.has(m.id)){const p=w.get(m.id);w.delete(m.id)
      if(m.error)p.no(new Error(m.error.message));else p.ok(m.result)}})}
export async function aba(url){const t=await cmd('Target.createTarget',{url})
  const{sessionId}=await cmd('Target.attachToTarget',{targetId:t.targetId,flatten:true})
  await cmd('Runtime.enable',{},sessionId); return sessionId}
export async function js(s,e){const r=await cmd('Runtime.evaluate',
  {expression:e,returnByValue:true,awaitPromise:true},s)
  if(r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text)
  return r.result.value}
export const pausa=ms=>new Promise(r=>setTimeout(r,ms))
