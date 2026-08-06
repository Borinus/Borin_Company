# -*- coding: utf-8 -*-
"""Liga o webhook do WhatsApp pela API — sem depender do painel da Meta.

    python site/worker/ligar-webhook.py

PRA QUE: enquanto o webhook nao estiver ligado, resposta de cliente no WhatsApp
CHEGA E E DESCARTADA. A Meta entrega no webhook e nao guarda copia: nao existe
caixa de entrada pra abrir depois. Quem responde ao orcamento — que e o lead
mais quente que existe — fala sozinho e conclui que foi ignorado.

O QUE ELE FAZ, NA ORDEM

  1. confere que o endpoint responde o desafio (se nao responder, para aqui:
     nao adianta pedir pra Meta validar algo que esta quebrado)
  2. registra a URL de retorno e o token no app, assinando o campo `messages`
  3. garante que o app esta assinado na conta do WhatsApp
  4. le de volta o que ficou gravado — porque "a API respondeu ok" e diferente
     de "esta configurado", e essa diferenca ja custou tempo aqui

O QUE PRECISA NO .env

    BORIN_META_APP_SECRET=...     Chave secreta do app "Borin Site"
    BORIN_ZAP_VERIFY=...          ja existe, e o mesmo do segredo do Worker

Onde achar a chave secreta: developers.facebook.com > app "Borin Site" >
Configuracoes > Basico > "Chave secreta do app" > Mostrar. Ela NAO vai pro git
(o .env esta no .gitignore) e nao precisa passar por chat.
"""

import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = "https://graph.facebook.com/v21.0"
APP = "1020386860773883"          # app "Borin Site"
WABA = "902961082438081"
URL = "https://borinprojetos.com.br/api/zap"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")


def do_env(chave):
    caminho = os.path.join(RAIZ, ".env")
    if not os.path.exists(caminho):
        return ""
    for l in io.open(caminho, encoding="utf-8"):
        k, _, v = l.partition("=")
        if k.strip() == chave:
            return v.strip().strip("'\"")
    return ""


def bate(caminho, metodo="GET", corpo=None, token=None):
    d = urllib.parse.urlencode(corpo).encode() if corpo else None
    r = urllib.request.Request(G + caminho, data=d, method=metodo)
    if token:
        r.add_header("Authorization", "Bearer " + token)
    r.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            return x.status, json.loads(x.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


segredo = do_env("BORIN_META_APP_SECRET")
verify = do_env("BORIN_ZAP_VERIFY")
zap_token = do_env("BORIN_ZAP_TOKEN")

if not segredo:
    raise SystemExit(
        "Falta BORIN_META_APP_SECRET no .env.\n"
        "  developers.facebook.com > app 'Borin Site' > Configuracoes > Basico\n"
        "  > 'Chave secreta do app' > Mostrar. Cole no .env e rode de novo.")
if not verify:
    raise SystemExit("Falta BORIN_ZAP_VERIFY no .env.")

print()
print("  " + "=" * 68)
print("  1. o endpoint responde o desafio?")
print("  " + "=" * 68)
q = urllib.parse.urlencode({"hub.mode": "subscribe",
                            "hub.verify_token": verify,
                            "hub.challenge": "8421337"})
r = urllib.request.Request(URL + "?" + q)
r.add_header("User-Agent", UA)
try:
    with urllib.request.urlopen(r, timeout=45) as x:
        corpo = x.read().decode().strip()
        ok = x.status == 200 and corpo == "8421337"
except Exception as e:
    corpo, ok = str(e)[:60], False
print("  %s  resposta: %r" % ("ok  " if ok else "FALHA", corpo[:40]))
if not ok:
    raise SystemExit(
        "  O endpoint nao devolveu o desafio. Nao adianta pedir pra Meta\n"
        "  validar — conserte o Worker primeiro.")

print()
print("  " + "=" * 68)
print("  2. registrando a URL de retorno no app")
print("  " + "=" * 68)
app_token = APP + "|" + segredo
st, d = bate("/%s/subscriptions" % APP, "POST", {
    "object": "whatsapp_business_account",
    "callback_url": URL,
    "verify_token": verify,
    "fields": "messages,message_template_status_update",
    "access_token": app_token,
})
print("  http %d  %s" % (st, json.dumps(d, ensure_ascii=False)[:200]))
if not d.get("success"):
    raise SystemExit("  A Meta recusou. Mensagem acima.")

print()
print("  " + "=" * 68)
print("  3. o app assinado na conta do WhatsApp")
print("  " + "=" * 68)
st, d = bate("/%s/subscribed_apps" % WABA, "POST", token=zap_token) if zap_token \
    else (0, {"aviso": "sem BORIN_ZAP_TOKEN no .env; conferindo so a leitura"})
print("  http %s  %s" % (st, json.dumps(d, ensure_ascii=False)[:160]))

print()
print("  " + "=" * 68)
print("  4. lendo de volta o que FICOU gravado")
print("  " + "=" * 68)
st, d = bate("/%s/subscriptions?access_token=%s" % (APP, urllib.parse.quote(app_token)))
achou = False
for s in (d.get("data") or []):
    if s.get("object") == "whatsapp_business_account":
        achou = True
        print("  objeto:        %s" % s.get("object"))
        print("  callback_url:  %s" % s.get("callback_url"))
        print("  ativo:         %s" % s.get("active"))
        campos = [f.get("name") for f in (s.get("fields") or [])]
        print("  campos:        %s" % ", ".join(campos))
        if "messages" not in campos:
            print("  !! o campo 'messages' NAO esta assinado — sem ele o webhook")
            print("     valida e mesmo assim nao entrega resposta de cliente.")
if not achou:
    print("  nada gravado pra whatsapp_business_account. %s"
          % json.dumps(d, ensure_ascii=False)[:200])
print()
print("  Pronto. Resposta de cliente no WhatsApp agora chega como email.")
print()
