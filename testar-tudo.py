# -*- coding: utf-8 -*-
"""Roda todas as suítes e dá UM veredito.

    python testar-tudo.py            # só as que rodam offline, de graça
    python testar-tudo.py --tudo     # inclui a travessia, que fala com produção

POR QUE UM COMANDO SÓ

São quatro suítes hoje, e vão ser mais. Suíte que precisa ser lembrada uma por
uma não é rodada — e suíte que não roda apodrece calada, que é o pior estado
possível: parece proteção e não é. Um comando, uma linha de resposta.

POR QUE A TRAVESSIA FICA DE FORA POR PADRÃO

Ela fala com o site de verdade: gasta 1 dos 40 pedidos/hora do freio por IP,
manda 2 emails pela Resend e cria uma conta temporária (que ela mesma apaga).
Isso é barato pra rodar antes de publicar, e caro pra rodar sem pensar num
laço. Então entra só com `--tudo`.

QUANDO RODAR
  - antes de publicar qualquer coisa: `--tudo`
  - depois de mexer em preço, proposta, contrato ou faturamento: sem argumento
"""

import argparse
import os
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.abspath(__file__))

# (arquivo, o que protege, fala com producao?)
SUITES = [
    ("comercial/testar-abertura.py",
     "quem leva a condição de abertura de R$ 6.700", False),
    ("comercial/testar-faturar.py",
     "o teto do MEI e o saldo a receber", False),
    ("comercial/testar-proposta.py",
     "a proposta em PDF cabendo numa folha", False),
    ("site/testar-travessia.py",
     "o caminho inteiro do cliente, do pedido à entrega", True),
]


def rodar(caminho):
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(RAIZ, caminho)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=RAIZ)
    saida = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"(\d+)/(\d+) passos ok", saida)
    falhas = re.findall(r"FALHOU: (.+?) —", saida)
    return {
        "codigo": r.returncode,
        "placar": m.group(0) if m else "sem placar",
        "falhas": falhas,
        "segundos": time.time() - t0,
        "saida": saida,
    }


def main():
    a = argparse.ArgumentParser(description="Roda as suítes e dá um veredito.")
    a.add_argument("--tudo", action="store_true",
                   help="inclui a travessia, que fala com o site de verdade")
    o = a.parse_args()

    escolhidas = [s for s in SUITES if o.tudo or not s[2]]
    puladas = [s for s in SUITES if not o.tudo and s[2]]

    print()
    print("  " + "=" * 72)
    print("  CONFERINDO %d SUÍTE(S)%s" % (len(escolhidas),
                                          "" if o.tudo else "  (offline)"))
    print("  " + "=" * 72)
    print()

    resultados = []
    for caminho, protege, _ in escolhidas:
        print("  %-32s %s" % (os.path.basename(caminho), protege))
        r = rodar(caminho)
        resultados.append((caminho, protege, r))
        print("      %-9s %-18s %5.0fs"
              % ("ok" if r["codigo"] == 0 else "FALHOU", r["placar"], r["segundos"]))
        for f in r["falhas"][:6]:
            print("      vermelho: %s" % f[:62])
        print()

    # nada calado: o que foi PULADO tem que aparecer, senão "tudo verde" mente
    for caminho, protege, _ in puladas:
        print("  %-32s PULADA — use --tudo" % os.path.basename(caminho))
        print("      (%s)" % protege)
        print()

    ruins = [x for x in resultados if x[2]["codigo"] != 0]
    total_passos = sum(int(x[2]["placar"].split("/")[1].split()[0])
                       for x in resultados if "/" in x[2]["placar"])
    bons_passos = sum(int(x[2]["placar"].split("/")[0])
                      for x in resultados if "/" in x[2]["placar"])

    print("  " + "=" * 72)
    if ruins:
        print("  VERMELHO — %d suíte(s) com falha, %d/%d passos"
              % (len(ruins), bons_passos, total_passos))
        for caminho, protege, r in ruins:
            print("    %s  (protege: %s)" % (os.path.basename(caminho), protege))
    else:
        print("  VERDE — %d/%d passos, %d suíte(s)"
              % (bons_passos, total_passos, len(resultados)))
        if puladas:
            print("  Mas %d suíte(s) nem rodaram. Antes de publicar, rode com --tudo."
                  % len(puladas))
    print("  " + "=" * 72)
    print()
    raise SystemExit(1 if ruins else 0)


if __name__ == "__main__":
    main()
