# -*- coding: utf-8 -*-
"""O ciclo da equipe, do jeito que o cliente vai usar.

O dono pede orcamento, entra, libera acesso pro funcionario. O funcionario
recebe a senha NA CAIXA DELE, entra, ve os mesmos projetos e NAO consegue
mexer nas fichas. No fim o dono tira o acesso e o funcionario para de entrar.
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
RAIZ = r"c:/Users/Borin/Desktop/Borin Company/ccos-ratos"
SITE = "https://borinprojetos.com.br"

passos = []


def P(nome, ok, det=""):
    passos.append((nome, ok, det))
    print("  %s %-48s %s" % ("ok   " if ok else "FALHA", nome, det))
    sys.stdout.flush()


def req(url, metodo="GET", corpo=None, tok=None):
    d = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(url, data=d, method=metodo)
    r.add_header("Content-Type", "application/json")
    r.add_header("Accept", "application/json")
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=40) as x:
            return x.status, json.loads(x.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def caixa():
    """Uma caixa de entrada de verdade, que eu consigo ler."""
    import random
    import string
    s, d = req("https://api.mail.tm/domains")
    dom = (d if isinstance(d, list) else d.get("hydra:member"))[0]["domain"]
    u = "eq" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    addr = u + "@" + dom
    pw = "Ex" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
    req("https://api.mail.tm/accounts", "POST", {"address": addr, "password": pw})
    s, t = req("https://api.mail.tm/token", "POST", {"address": addr, "password": pw})
    return addr, t["token"]


def senha_do_email(tok, contendo="acesso", limite=50):
    for _ in range(limite):
        time.sleep(6)
        s, d = req("https://api.mail.tm/messages", tok=tok)
        itens = d if isinstance(d, list) else (d.get("hydra:member") or [])
        for m in itens:
            if contendo.lower() in (m.get("subject") or "").lower():
                s, full = req("https://api.mail.tm/messages/" + m["id"], tok=tok)
                html = " ".join(full.get("html") or [])
                achou = re.search(r">([A-HJ-NP-Za-hj-km-z2-9]{12})<", html)
                if achou:
                    return achou.group(1), (m.get("subject") or "")
    return None, None


def curl(metodo, rota, corpo=None, cookie=None, salvar=None):
    args = ["curl", "-s", "-X", metodo, SITE + rota,
            "-H", "Content-Type: application/json"]
    if corpo is not None:
        f = os.path.join(SP, "c.json")
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
        return {"cru": (p.stdout or "")[:200]}


print()
print("  " + "=" * 64)
print("  EMPRESA E EQUIPE")
print("  " + "=" * 64)

# 1 ------------------------------------------------------------- o dono
dono, tokDono = caixa()
print("  dono:     %s" % dono)
curl("POST", "/api/orcamento", {
    "intencao": "site", "doc": "Pedido de orçamento", "empresa": "Metalúrgica Equipe Ltda",
    "contato": "Carla Dias", "email": dono, "fone": "+55 54 99988-7766", "website": "",
    "equipamento": "Painel", "codigo": "EQ-01", "texto": "PEDIDO\nEscopo: B\n"})
sd, _ = senha_do_email(tokDono)
P("dono recebeu a senha", bool(sd), dono)
if not sd:
    raise SystemExit(1)

ck = os.path.join(SP, "ck-dono.txt")
r = curl("POST", "/api/acesso/entrar", {"email": dono, "senha": sd}, salvar=ck)
P("dono entrou", r.get("ok") is True, r.get("empresa", ""))

r = curl("GET", "/api/acesso/equipe", cookie=ck)
P("dono e reconhecido como dono", r.get("papel") == "dono", "papel=%s" % r.get("papel"))

# 2 -------------------------------------------------- libera o funcionario
func, tokFunc = caixa()
print("  funcionário: %s" % func)
r = curl("POST", "/api/acesso/equipe", {"email": func, "nome": "Jorge Campo"}, cookie=ck)
P("dono liberou acesso", r.get("ok") is True, r.get("erro", "") or ("entregue=%s" % r.get("entregue")))

sf, assunto = senha_do_email(tokFunc)
P("funcionario recebeu a senha na caixa dele", bool(sf), (assunto or "")[:46])
if not sf:
    raise SystemExit(1)

# 3 ------------------------------------------------ o funcionario entra
ckf = os.path.join(SP, "ck-func.txt")
r = curl("POST", "/api/acesso/entrar", {"email": func, "senha": sf}, salvar=ckf)
P("funcionario entrou com a senha do email", r.get("ok") is True, r.get("erro", ""))

r = curl("GET", "/api/acesso/projetos", cookie=ckf)
P("funcionario ve a area da empresa", r.get("entrou") is True,
  "papel=%s empresa=%s" % (r.get("papel"), r.get("empresa")))

r = curl("GET", "/api/acesso/equipe", cookie=ckf)
P("funcionario ve quem tem acesso", r.get("ok") is True,
  "%d pessoa(s)" % len(r.get("membros") or []))

# 4 ------------------------------------------- o que o membro NAO pode
r = curl("POST", "/api/acesso/ficha", {"tipo": "cadastro", "dados": {"razao_social": "X"}}, cookie=ckf)
P("funcionario NAO preenche ficha", r.get("ok") is not True, r.get("erro", "")[:44])

# nao precisa de caixa real: o pedido tem que ser recusado antes de qualquer envio
outro = "terceiro.sem.acesso@exemplo-teste.com"
r = curl("POST", "/api/acesso/equipe", {"email": outro, "nome": "Terceiro"}, cookie=ckf)
P("funcionario NAO libera acesso", r.get("ok") is not True, r.get("erro", "")[:44])

# 5 ----------------------------------- o dono ve a ficha e o membro tambem
r = curl("POST", "/api/acesso/ficha",
         {"tipo": "padrao", "dados": {"empresa": "Metalúrgica Equipe Ltda", "tensao": "380V"}},
         cookie=ck)
P("dono preenche ficha", r.get("ok") is True, r.get("erro", ""))

# o endpoint devolve {dados: ...}; e o _form.js que renomeia pra "ficha" na tela
r = curl("GET", "/api/acesso/ficha?tipo=padrao", cookie=ckf)
P("funcionario LE a ficha da empresa", (r.get("dados") or {}).get("tensao") == "380V",
  json.dumps(r.get("dados") or {}, ensure_ascii=False)[:44])

# 6 ------------------------------------------------ o dono tira o acesso
r = curl("POST", "/api/acesso/equipe-remover", {"email": func}, cookie=ck)
P("dono removeu o acesso", r.get("ok") is True, r.get("erro", ""))

r = curl("POST", "/api/acesso/entrar", {"email": func, "senha": sf})
P("funcionario removido nao entra mais", r.get("ok") is not True, r.get("erro", "")[:40])

io.open(os.path.join(SP, "eq.json"), "w", encoding="utf-8").write(
    json.dumps({"dono": dono, "func": func, "outro": outro}))

print()
bons = sum(1 for _, o, _ in passos if o)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o, d in passos:
    if not o:
        print("    FALHOU: %s — %s" % (n, d))
raise SystemExit(0 if bons == len(passos) else 1)
