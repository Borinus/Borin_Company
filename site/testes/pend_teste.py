# -*- coding: utf-8 -*-
"""A conta so vale depois que a pessoa troca a senha.

O ataque que isto precisa impedir: um estranho digita o email de um prospecto
do Mateus. Antes, isso criava a conta e, quando o prospecto de verdade
pedisse orcamento, o sistema dizia "ja tinha" e ele nunca recebia a senha —
lead queimado por alguem de fora.
"""
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
SP = os.environ["SP"]
SITE = "https://borinprojetos.com.br"
passos = []


def P(n, o, d=""):
    passos.append((n, o, d))
    print("  %s %-50s %s" % ("ok   " if o else "FALHA", n, d))
    sys.stdout.flush()


def req(u, m="GET", c=None, t=None):
    d = json.dumps(c).encode() if c is not None else None
    r = urllib.request.Request(u, data=d, method=m)
    r.add_header("Content-Type", "application/json")
    r.add_header("Accept", "application/json")
    if t:
        r.add_header("Authorization", "Bearer " + t)
    for _ in range(3):
        try:
            with urllib.request.urlopen(r, timeout=40) as x:
                return x.status, json.loads(x.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:
                return e.code, {}
        except Exception:
            time.sleep(4)
    return 0, {}


def caixa():
    import random
    import string
    s, d = req("https://api.mail.tm/domains")
    dom = (d if isinstance(d, list) else d.get("hydra:member"))[0]["domain"]
    u = "pd" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    addr = u + "@" + dom
    pw = "Pd12345678ab"
    req("https://api.mail.tm/accounts", "POST", {"address": addr, "password": pw})
    s, t = req("https://api.mail.tm/token", "POST", {"address": addr, "password": pw})
    return addr, t.get("token", "")


def senhas(tok, quantas=1, limite=50):
    """Todas as senhas que chegaram, na ordem."""
    vistas = []
    for _ in range(limite):
        time.sleep(6)
        s, d = req("https://api.mail.tm/messages", t=tok)
        itens = d if isinstance(d, list) else (d.get("hydra:member") or [])
        for m in reversed(itens):
            if m["id"] in [v[0] for v in vistas]:
                continue
            s, full = req("https://api.mail.tm/messages/" + m["id"], t=tok)
            html = " ".join(full.get("html") or [])
            a = re.search(r">([A-HJ-NP-Za-hj-km-z2-9]{12})<", html)
            if a:
                vistas.append((m["id"], a.group(1)))
        if len(vistas) >= quantas:
            break
    return [v[1] for v in vistas]


def curl(metodo, rota, corpo=None, cookie=None, salvar=None, seg=None):
    args = ["curl", "-s", "-X", metodo, SITE + rota, "-H", "Content-Type: application/json"]
    if seg:
        args += ["-H", "Authorization: Bearer " + seg]
    if corpo is not None:
        f = os.path.join(SP, "pc.json")
        io.open(f, "w", encoding="utf-8").write(json.dumps(corpo, ensure_ascii=False))
        args += ["--data-binary", "@" + f]
    if cookie:
        args += ["-b", cookie]
    if salvar:
        args += ["-c", salvar]
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads(p.stdout or "{}")
    except ValueError:
        return {"cru": (p.stdout or "")[:160]}


seg = ""
for l in io.open(r"c:/Users/Borin/Desktop/Borin Company/ccos-ratos/.env", encoding="utf-8"):
    k, _, v = l.partition("=")
    if k.strip() == "BORIN_SEGREDO_ADMIN":
        seg = v.strip().strip("'\"")

print()
print("  " + "=" * 66)
print("  CONTA PENDENTE — O LEAD DE OUTRA PESSOA NAO PODE SER QUEIMADO")
print("  " + "=" * 66)

alvo, tok = caixa()
print("  email do 'prospecto':", alvo)

# 1. um estranho digita o email dele
r = curl("POST", "/api/orcamento", {
    "contato": "Estranho", "email": alvo, "equipamento": "Painel",
    "empresa": "Empresa Inventada"})
P("estranho consegue disparar o pedido", r.get("ok") is True, "conta=%s" % r.get("conta"))
P("a conta nasce PENDENTE, nao criada de vez", r.get("conta") == "criada", "")

d = curl("GET", "/api/acesso/cliente?email=" + alvo, seg=seg)
P("estado no banco e pendente", (d.get("conta") or {}).get("estado") == "pendente",
  str((d.get("conta") or {}).get("estado")))

# 2. o dono de verdade pede orcamento depois
time.sleep(3)
r = curl("POST", "/api/orcamento", {
    "contato": "Dono de Verdade", "email": alvo, "equipamento": "Painel de pintura",
    "empresa": "Metalúrgica Real Ltda"})
P("o dono de verdade NAO e barrado", r.get("ok") is True and r.get("conta") != "ja_tinha",
  "conta=%s" % r.get("conta"))
P("e a senha e REENVIADA pra ele", r.get("conta") == "reenviada", "")

lidas = senhas(tok, quantas=2)
P("chegaram as duas senhas na caixa", len(lidas) >= 2, "%d email(s)" % len(lidas))
if len(lidas) < 2:
    raise SystemExit(1)
velha, nova = lidas[0], lidas[1]
P("a segunda senha e diferente da primeira", velha != nova, "")

# 3. a senha antiga do estranho nao vale mais
r = curl("POST", "/api/acesso/entrar", {"email": alvo, "senha": velha})
P("a senha da primeira tentativa deixou de valer", r.get("ok") is not True,
  r.get("erro", "")[:40])

# 4. o dono entra com a senha nova e troca
ck = os.path.join(SP, "ck-pend.txt")
r = curl("POST", "/api/acesso/entrar", {"email": alvo, "senha": nova}, salvar=ck)
P("o dono entra com a senha que recebeu", r.get("ok") is True, r.get("erro", ""))

r = curl("POST", "/api/acesso/trocar", {"atual": nova, "nova": "MinhaSenhaBoa2026"}, cookie=ck)
P("o dono troca a senha", r.get("ok") is True, r.get("erro", ""))

d = curl("GET", "/api/acesso/cliente?email=" + alvo, seg=seg)
P("agora a conta esta ATIVA", (d.get("conta") or {}).get("estado") == "ativa",
  str((d.get("conta") or {}).get("estado")))

# 5. depois de ativa, novo pedido nao mexe mais na senha
time.sleep(3)
r = curl("POST", "/api/orcamento", {
    "contato": "Estranho de novo", "email": alvo, "equipamento": "Painel"})
P("com a conta ativa, pedido novo NAO troca a senha", r.get("conta") == "ja_tinha",
  "conta=%s" % r.get("conta"))

r = curl("POST", "/api/acesso/entrar", {"email": alvo, "senha": "MinhaSenhaBoa2026"})
P("a senha escolhida pelo dono continua valendo", r.get("ok") is True, r.get("erro", ""))

io.open(os.path.join(SP, "pend.json"), "w", encoding="utf-8").write(json.dumps({"alvo": alvo}))
print()
bons = sum(1 for _, o, _ in passos if o)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o, d in passos:
    if not o:
        print("    FALHOU: %s — %s" % (n, d))
raise SystemExit(0 if bons == len(passos) else 1)
