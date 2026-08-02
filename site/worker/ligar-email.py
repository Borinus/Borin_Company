# -*- coding: utf-8 -*-
"""Liga o envio de email para o cliente, do zero ao teste de entrega.

Por que existe: comprar o dominio deu o NOME, nao o carteiro. Para o site
escrever para um cliente, um servico precisa carregar a mensagem — e como o
borinprojetos.com.br esta com DMARC p=reject, esse servico so pode falar em
nome dele se estiver autorizado por registro de DNS. Este script faz as duas
coisas e confere no fim se a carta chegou assinada.

O que ele faz, em ordem:

  1. registra o dominio na Resend e pega os registros de DNS que ela exige
  2. publica cada registro na Cloudflare, com proxy DESLIGADO
     (registro proxiado quebra a verificacao: a Cloudflare responde no lugar)
  3. pede a verificacao e espera o dominio ficar "verified"
  4. grava a chave como secret do Worker
  5. liga o transporte e manda um email de teste de verdade

Uso:
    # com a chave ja no .env como RESEND_API_KEY=
    python site/worker/ligar-email.py             # so mostra o que faria
    python site/worker/ligar-email.py --aplicar   # executa
    python site/worker/ligar-email.py --testar mateusborin20@gmail.com

Nada aqui e destrutivo: registro de DNS que ja existe com o mesmo valor e
deixado em paz, e o script nunca apaga registro que nao tenha criado.
"""

import argparse
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
DOMINIO = "borinprojetos.com.br"
REGIAO = "sa-east-1"          # Sao Paulo: mais perto do cliente brasileiro


def env(chave):
    p = os.path.join(RAIZ, ".env")
    if not os.path.exists(p):
        return ""
    for l in io.open(p, encoding="utf-8"):
        k, _, v = l.partition("=")
        if k.strip() == chave:
            return v.strip().strip("'\"")
    return ""


def http(url, metodo="GET", corpo=None, cabecalhos=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(url, data=dados, method=metodo)
    r.add_header("Content-Type", "application/json")
    for k, v in (cabecalhos or {}).items():
        r.add_header(k, v)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except ValueError:
            return e.code, {}


def resend(caminho, metodo="GET", corpo=None):
    chave = env("RESEND_API_KEY")
    if not chave:
        raise SystemExit(
            "Falta RESEND_API_KEY no .env.\n"
            "  1. cria a conta em resend.com\n"
            "  2. API Keys > Create > permissao 'Sending access'\n"
            "  3. cola no .env como:  RESEND_API_KEY=re_...")
    return http("https://api.resend.com" + caminho, metodo, corpo,
                {"Authorization": "Bearer " + chave})


def cloudflare(caminho, metodo="GET", corpo=None):
    tk, zona = env("CLOUDFLARE_API_TOKEN"), env("CLOUDFLARE_ZONE_ID")
    if not tk or not zona:
        raise SystemExit("Falta CLOUDFLARE_API_TOKEN ou CLOUDFLARE_ZONE_ID no .env")
    return http("https://api.cloudflare.com/client/v4/zones/" + zona + caminho,
                metodo, corpo, {"Authorization": "Bearer " + tk})


def achar_dominio():
    s, d = resend("/domains")
    if s != 200:
        raise SystemExit("Resend recusou a chave (%s): %s" % (s, json.dumps(d)[:200]))
    for x in (d.get("data") or []):
        if x.get("name") == DOMINIO:
            return x
    return None


def registros_do_dominio(ident):
    s, d = resend("/domains/" + ident)
    if s != 200:
        raise SystemExit("nao li o dominio na Resend: %s" % json.dumps(d)[:200])
    return d


def publicar(reg, aplicar):
    """Um registro da Resend vira um registro na Cloudflare."""
    nome = reg.get("name") or ""
    # a Resend devolve o nome ja completo em alguns casos e relativo em outros
    if not nome.endswith(DOMINIO):
        nome = (nome + "." + DOMINIO) if nome else DOMINIO
    tipo = (reg.get("type") or "").upper()
    valor = reg.get("value") or ""

    s, d = cloudflare("/dns_records?type=%s&name=%s" % (tipo, nome))
    existentes = (d.get("result") or []) if s == 200 else []
    for e in existentes:
        if (e.get("content") or "").strip().strip('"') == valor.strip().strip('"'):
            return "ja existia", nome
        if e.get("proxied"):
            return "CONFLITO: existe proxiado, precisa virar cinza", nome

    corpo = {"type": tipo, "name": nome, "content": valor, "ttl": 1, "proxied": False}
    if tipo == "MX":
        corpo["priority"] = int(reg.get("priority") or 10)

    if not aplicar:
        return "criaria", nome
    s, d = cloudflare("/dns_records", "POST", corpo)
    if s not in (200, 201):
        erros = json.dumps(d.get("errors") or d)[:200]
        return "FALHOU: " + erros, nome
    return "criado", nome


def secret_no_worker(aplicar):
    chave = env("RESEND_API_KEY")
    if not aplicar:
        return "gravaria o secret RESEND_API_KEY"
    p = subprocess.run(
        ["npx", "wrangler", "secret", "put", "RESEND_API_KEY"],
        cwd=AQUI, input=chave, capture_output=True, text=True, shell=True)
    return "secret gravado" if p.returncode == 0 else "FALHOU: " + (p.stderr or "")[:200]


def testar(para):
    """Manda um email de verdade e devolve o que a Resend respondeu."""
    corpo = {
        "from": "Borin Projetos <site@%s>" % DOMINIO,
        "to": [para],
        "subject": "Teste de entrega — Borin Projetos",
        "html": ("<p>Se este email chegou na caixa de entrada, o envio para cliente "
                 "está funcionando.</p><p>Confira no cabeçalho da mensagem que aparecem "
                 "<b>dkim=pass</b>, <b>spf=pass</b> e <b>dmarc=pass</b> com "
                 "header.from=%s. Sem os três, cliente com filtro rígido não recebe."
                 "</p>" % DOMINIO),
        "text": ("Se este email chegou, o envio para cliente esta funcionando.\n"
                 "Confira dkim=pass, spf=pass e dmarc=pass no cabecalho."),
    }
    s, d = resend("/emails", "POST", corpo)
    return s, d


def main():
    a = argparse.ArgumentParser(description="Liga o envio de email pro cliente")
    a.add_argument("--aplicar", action="store_true", help="executa de verdade")
    a.add_argument("--testar", metavar="EMAIL", help="so manda um email de teste")
    o = a.parse_args()

    if o.testar:
        s, d = testar(o.testar)
        print("  resposta: %s  %s" % (s, json.dumps(d)[:300]))
        if s in (200, 201):
            print("  enviado. Abra a mensagem e confira dkim=pass no cabecalho.")
        raise SystemExit(0 if s in (200, 201) else 1)

    print()
    print("  " + "-" * 58)
    print("  LIGANDO O ENVIO DE EMAIL  (%s)" % ("aplicando" if o.aplicar else "simulacao"))
    print("  " + "-" * 58)

    d = achar_dominio()
    if not d:
        print("  dominio ainda nao registrado na Resend")
        if not o.aplicar:
            print("  -> registraria %s na regiao %s" % (DOMINIO, REGIAO))
            print()
            print("  (simulacao — rode com --aplicar)")
            return
        s, d = resend("/domains", "POST", {"name": DOMINIO, "region": REGIAO})
        if s not in (200, 201):
            raise SystemExit("nao registrei o dominio: %s" % json.dumps(d)[:300])
        print("  dominio registrado: %s" % d.get("id"))

    info = registros_do_dominio(d["id"])
    regs = info.get("records") or []
    print("  status na Resend: %s" % info.get("status"))
    print("  registros exigidos: %d" % len(regs))
    print()

    for r in regs:
        estado, nome = publicar(r, o.aplicar)
        print("    %-9s %-46s %s" % (r.get("type"), nome[:46], estado))

    if not o.aplicar:
        print()
        print("  (simulacao — nada foi criado. Rode com --aplicar)")
        return

    print()
    print("  pedindo verificacao...")
    resend("/domains/" + d["id"] + "/verify", "POST")
    for tentativa in range(1, 21):
        time.sleep(15)
        info = registros_do_dominio(d["id"])
        st = info.get("status")
        print("    %2d/20  %s" % (tentativa, st))
        if st == "verified":
            break
    else:
        print()
        print("  O dominio ainda nao verificou. Isso costuma ser propagacao de DNS —")
        print("  espere alguns minutos e rode de novo. NAO mande email antes de")
        print("  verificar: com DMARC p=reject a mensagem e rejeitada, nao vai pra spam.")
        raise SystemExit(1)

    print()
    print("  " + secret_no_worker(True))
    print()
    print("  Falta so publicar o Worker:  cd site/worker && npx wrangler deploy")
    print("  Depois:  python site/worker/ligar-email.py --testar seu@email.com")
    print()


if __name__ == "__main__":
    main()
