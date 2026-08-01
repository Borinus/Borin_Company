"""
Cria o acesso do cliente e devolve a senha, pra colar na resposta do orcamento.

    python comercial/criar-acesso.py joao@metalurgica.com.br
    python comercial/criar-acesso.py joao@metalurgica.com.br --empresa "Metalurgica Serra" --contato "Joao Vieira"
    python comercial/criar-acesso.py joao@metalurgica.com.br --trocar

Quando usar: ao responder o orcamento. O cliente pede sem conta nenhuma; a
conta nasce junto com a proposta e a senha vai no mesmo email. Isso dispensa
verificacao de email — se a mensagem chegou naquele endereco, a posse ja esta
provada.

A senha aparece UMA vez. Depois disso o servidor so guarda o hash, e nem eu
consigo recuperar. Se o cliente perder, rode de novo com --trocar.

O segredo vem de BORIN_SEGREDO_ADMIN no .env. Ele nao esta no git.
"""

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://borinprojetos.com.br/api/acesso/criar"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def segredo():
    caminho = os.path.join(RAIZ, ".env")
    if os.path.exists(caminho):
        for linha in io.open(caminho, encoding="utf-8"):
            k, _, v = linha.partition("=")
            if k.strip() == "BORIN_SEGREDO_ADMIN":
                return v.strip().strip("'\"")
    raise SystemExit("Falta BORIN_SEGREDO_ADMIN no .env")


def main():
    a = argparse.ArgumentParser(description="Cria o acesso do cliente")
    a.add_argument("email")
    a.add_argument("--empresa", default="")
    a.add_argument("--contato", default="")
    a.add_argument("--trocar", action="store_true",
                   help="gera outra senha para quem ja tem conta")
    o = a.parse_args()

    corpo = {
        "segredo": segredo(),
        "email": o.email,
        "empresa": o.empresa,
        "contato": o.contato,
        "trocar": o.trocar,
    }

    # por arquivo em UTF-8: o shell do Windows corrompe acento em argumento
    p = os.path.join(tempfile.gettempdir(), "borin-acesso.json")
    io.open(p, "w", encoding="utf-8").write(json.dumps(corpo, ensure_ascii=False))
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", API,
             "-H", "Content-Type: application/json", "--data-binary", "@" + p],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(p)

    try:
        d = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        raise SystemExit("Resposta inesperada do servidor:\n" + (r.stdout or "")[:400])

    if not d.get("ok"):
        erro = d.get("erro", "falhou")
        if "ja existe" in erro:
            erro += "\n  (rode de novo com --trocar se for pra gerar outra senha)"
        raise SystemExit("NAO CRIOU: " + erro)

    senha = d["senha"]
    print()
    print("  " + "-" * 58)
    print("  %-12s %s" % ("EMAIL", d["email"]))
    print("  %-12s %s" % ("SENHA", senha))
    print("  " + "-" * 58)
    print("  %s" % ("senha trocada — a anterior parou de valer"
                    if d.get("trocada") else "conta nova"))
    print()
    print("  Cole no email do orçamento:")
    print()
    print("  ---------------------------------------------------------")
    print("  Para preencher o padrão da sua empresa e a ficha do projeto,")
    print("  entre em borinprojetos.com.br/entrar")
    print()
    print("      Email: %s" % d["email"])
    print("      Senha: %s" % senha)
    print()
    print("  Troque a senha no primeiro acesso — essa passou por email.")
    print("  ---------------------------------------------------------")
    print()
    print("  A senha não aparece de novo. Se perder, rode com --trocar.")
    print()


if __name__ == "__main__":
    main()
