"""
Atualiza o andamento de um projeto na conta do cliente.

    python comercial/projeto.py joao@empresa.com 04003478 --nome "Painel de estufa"
    python comercial/projeto.py joao@empresa.com 04003478 --status "Em execução"
    python comercial/projeto.py joao@empresa.com 04003478 --status "Entregue" \\
           --link "https://drive.google.com/..." --nota "Databook vai separado."

O cliente ve isso em borinprojetos.com.br/conta, com a trilha de etapas.
E a resposta pro "e o meu projeto?" que hoje chega por WhatsApp.

O arquivo entregue NAO sobe pra ca — entra o link da pasta compartilhada, que
e como a entrega ja e feita (ver padroes/padrao-entrega.md).

Etapas, na ordem:
  Orçamento enviado · Contrato assinado · Aguardando a ficha · Em execução ·
  Em conferência · Entregue · Aprovado
"""

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://borinprojetos.com.br/api/acesso/projeto"

ETAPAS = ["Orçamento enviado", "Contrato assinado", "Aguardando a ficha",
          "Em execução", "Em conferência", "Entregue", "Aprovado"]

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
    a = argparse.ArgumentParser(description="Andamento do projeto na conta do cliente")
    a.add_argument("email")
    a.add_argument("codigo")
    a.add_argument("--nome", help="nome do projeto, como o cliente chama")
    a.add_argument("--status", choices=ETAPAS, help="em que etapa esta")
    a.add_argument("--prazo", help="entrega prevista, texto livre: 15/09 ou 8 dias uteis")
    a.add_argument("--link", help="link da pasta com a entrega")
    a.add_argument("--nota", help="um recado curto que aparece no cartao")
    o = a.parse_args()

    corpo = {"segredo": segredo(), "email": o.email, "codigo": o.codigo}
    for campo in ("nome", "status", "prazo", "link", "nota"):
        if getattr(o, campo) is not None:
            corpo[campo] = getattr(o, campo)

    if len(corpo) == 3:
        print("\n  Nada pra mudar. Use --status, --nome, --prazo, --link ou --nota.")
        print("  Etapas: " + " · ".join(ETAPAS) + "\n")
        raise SystemExit(1)

    p = os.path.join(tempfile.gettempdir(), "borin-projeto.json")
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
        raise SystemExit("Resposta inesperada:\n" + (r.stdout or "")[:400])

    if not d.get("ok"):
        raise SystemExit("NAO ATUALIZOU: " + d.get("erro", "falhou"))

    pr = d["projeto"]
    print()
    print("  " + "-" * 56)
    print("  %-10s %s" % ("PROJETO", pr.get("nome") or pr["codigo"]))
    print("  %-10s #%s" % ("CÓDIGO", pr["codigo"]))
    print("  %-10s %s" % ("ETAPA", pr.get("status") or "—"))
    if pr.get("prazo"):
        print("  %-10s %s" % ("PRAZO", pr["prazo"]))
    if pr.get("link"):
        print("  %-10s %s" % ("ENTREGA", pr["link"]))
    if pr.get("nota"):
        print("  %-10s %s" % ("NOTA", pr["nota"]))
    print("  " + "-" * 56)
    print("  O cliente já vê em borinprojetos.com.br/conta\n")


if __name__ == "__main__":
    main()
