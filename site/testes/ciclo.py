# -*- coding: utf-8 -*-
"""Um cliente inteiro, do primeiro clique ao contrato assinavel, numa corrida so.

Nada aqui le o banco nem endpoint de admin para descobrir senha: tudo que o
cliente precisa saber e lido da CAIXA DE ENTRADA dele, como ele leria. Se
passar, o caminho esta provado com o codigo que esta no ar.
"""

import base64
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
    print("  %s %-46s %s" % ("ok   " if ok else "FALHA", nome, det))
    sys.stdout.flush()


def req(url, metodo="GET", corpo=None, tok=None, cru=False):
    d = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(url, data=d, method=metodo)
    r.add_header("Content-Type", "application/json")
    r.add_header("Accept", "application/json")
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(r, timeout=40) as x:
            b = x.read()
            return x.status, (b if cru else json.loads(b.decode() or "{}"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


# ------------------------------------------------------------ caixa do cliente
def abrir_caixa():
    import random
    import string
    s, d = req("https://api.mail.tm/domains")
    itens = d if isinstance(d, list) else (d.get("hydra:member") or [])
    dom = itens[0]["domain"]
    user = "cli" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(9))
    addr, senha = user + "@" + dom, "Cx" + "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(12))
    req("https://api.mail.tm/accounts", "POST", {"address": addr, "password": senha})
    s, t = req("https://api.mail.tm/token", "POST", {"address": addr, "password": senha})
    return addr, t["token"]


def esperar_email(tok, contendo, ja_vistos, limite=20):
    """Devolve a mensagem inteira cujo assunto casa, ignorando as ja lidas."""
    for _ in range(limite):
        time.sleep(9)
        s, d = req("https://api.mail.tm/messages", tok=tok)
        itens = d if isinstance(d, list) else (d.get("hydra:member") or [])
        for m in itens:
            if m["id"] in ja_vistos:
                continue
            if contendo.lower() in (m.get("subject") or "").lower():
                s, full = req("https://api.mail.tm/messages/" + m["id"], tok=tok)
                ja_vistos.add(m["id"])
                return full
    return None


# ------------------------------------------------------------------- navegador
def navegador(script, **amb):
    e = dict(os.environ)
    e.update({k: str(v) for k, v in amb.items()})
    p = subprocess.run(["node", script], cwd=SP, capture_output=True, text=True,
                       env=e, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def comando(args):
    p = subprocess.run([sys.executable] + args, cwd=RAIZ, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    print()
    print("  " + "=" * 62)
    print("  UM CLIENTE INTEIRO, NUMA CORRIDA SO")
    print("  " + "=" * 62)

    caixa, tok = abrir_caixa()
    vistos = set()
    print("  caixa do cliente: %s\n" % caixa)

    # 1 -----------------------------------------------------------------------
    print("  [1] preenche o formulario no site")
    cod, saida = navegador("passo1.mjs", CAIXA=caixa)
    P("formulario enviado, foi pra confirmacao", cod == 0, saida.strip().splitlines()[-1] if saida.strip() else "")

    # 2 -----------------------------------------------------------------------
    print("\n  [2] recebe o acesso por email")
    m = esperar_email(tok, "Seu acesso", vistos)
    P("email de acesso chegou", bool(m), (m or {}).get("subject", "nao chegou"))
    if not m:
        return encerrar()
    de = (m.get("from") or {}).get("address", "")
    P("remetente e o dominio proprio", de.endswith("@borinprojetos.com.br"), de)
    html = " ".join(m.get("html") or []) or m.get("text") or ""
    achou = re.search(r">([A-HJ-NP-Za-hj-km-z2-9]{12})<", html)
    senha = achou.group(1) if achou else ""
    P("senha legivel no corpo", bool(senha), senha[:3] + "*" * 9 if senha else "nao achei")
    P("acentos intactos", "Elétricos" in (m.get("subject") or "") or "é" in html,
      (m.get("subject") or "")[:44])
    if not senha:
        return encerrar()

    # 3 e 4 -------------------------------------------------------------------
    print("\n  [3] entra com a senha e preenche os dados da empresa")
    cod, saida = navegador("passo34.mjs", CAIXA=caixa, SENHA=senha)
    for l in saida.strip().splitlines():
        if l.startswith("PASSO:"):
            n, o, d = l[6:].split("|", 2)
            P(n, o == "1", d)

    # 5 -----------------------------------------------------------------------
    print("\n  [5] recebe a proposta com o contrato anexo")
    cod, saida = comando(["comercial/orcamento.py", "--de", "exemplo", "--email", caixa,
                          "--empresa", "Verificacao Ciclo Ltda", "--enviar"])
    P("comando de proposta rodou", "enviado para" in saida, saida.strip().splitlines()[-1][:60])
    m = esperar_email(tok, "Proposta", vistos)
    P("proposta chegou na caixa", bool(m), (m or {}).get("subject", "")[:52])
    if m:
        anexos = m.get("attachments") or []
        pdf = [a for a in anexos if "pdf" in (a.get("contentType") or "").lower()]
        P("contrato em PDF veio anexo", bool(pdf),
          "%s (%s KB)" % (pdf[0].get("filename", "")[:34], round(pdf[0].get("size", 0) / 1024))
          if pdf else "sem anexo")

    # 6 -----------------------------------------------------------------------
    print("\n  [6] recebe o contrato preenchido pelo cadastro")
    cod, saida = comando(["comercial/reenviar-contrato.py", "--cliente", caixa, "--enviar"])
    P("comando de reenvio rodou", "enviado para" in saida,
      [l for l in saida.splitlines() if "CLIENTE" in l or "enviado" in l][-1].strip()[:56]
      if saida.strip() else "")
    P("contrato sem campo em branco", "AINDA EM BRANCO" not in saida,
      "nenhum [campo] sobrou" if "AINDA EM BRANCO" not in saida else "sobrou campo")
    m = esperar_email(tok, "Contrato", vistos)
    P("contrato chegou na caixa", bool(m), (m or {}).get("subject", "")[:52])
    if m:
        anexos = m.get("attachments") or []
        pdf = [a for a in anexos if "pdf" in (a.get("contentType") or "").lower()]
        P("PDF do contrato anexo", bool(pdf),
          "%s (%s KB)" % (pdf[0].get("filename", "")[:34], round(pdf[0].get("size", 0) / 1024))
          if pdf else "sem anexo")
        if pdf:
            s, b = req("https://api.mail.tm" + pdf[0]["downloadUrl"], tok=tok, cru=True)
            io.open(os.path.join(SP, "recebido.pdf"), "wb").write(b)
            P("PDF baixado da caixa do cliente", len(b) > 20000, "%d bytes" % len(b))

    io.open(os.path.join(SP, "caixa_final.json"), "w", encoding="utf-8").write(
        json.dumps({"caixa": caixa, "token": tok}))
    encerrar()


def encerrar():
    print()
    bons = sum(1 for _, o, _ in passos if o)
    print("  " + "=" * 62)
    print("  %d/%d passos ok" % (bons, len(passos)))
    for n, o, d in passos:
        if not o:
            print("    FALHOU: %s — %s" % (n, d))
    print("  " + "=" * 62)
    print()
    raise SystemExit(0 if bons == len(passos) else 1)


main()
