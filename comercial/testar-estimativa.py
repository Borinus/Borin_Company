# -*- coding: utf-8 -*-
"""Prova que a estimativa do site bate com o preco de verdade do Python.

O RISCO QUE ESTE TESTE MATA: estimar_paginas e as constantes de preco vivem em
DOIS arquivos — comercial/calcular.py (onde o Mateus fecha o valor) e
site/worker/estimativa.js (o que o cliente ve na hora do pedido). Se um mudar e
o outro nao, a estimativa que o cliente recebe passa a mentir sobre a proposta
que vem depois. Este teste roda os DOIS e cobra:

  1. as PAGINAS estimadas sao IDENTICAS nos dois (mesma formula)
  2. o TOTAL fechado do Python cai DENTRO da faixa [min, max] que o site mostra

Regra #2 do AGENTS.md (preco nao sai de memoria) aplicada a codigo duplicado:
os dois lados tem que concordar, e a maquina verifica.

Roda com: python comercial/testar-estimativa.py   (precisa do node no PATH)
"""

import importlib.util
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAIZ, "site", "worker", "estimativa.js")

_s = importlib.util.spec_from_file_location(
    "calc", os.path.join(RAIZ, "comercial", "calcular.py"))
calc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(calc)

# casos: (io, acionamentos, seguranca, escopo)
CASOS = [
    (96, 8, 6, "B"),    # o 04003478 real: 51 folhas
    (96, 8, 6, "A"),
    (40, 6, 0, "A"),
    (48, 6, 4, "B"),
    (12, 2, 0, "A"),    # pequeno: deve cair no piso
    (200, 20, 12, "B"), # grande
    (0, 10, 0, "A"),    # so acionamentos
    (60, 0, 0, "B"),    # so I/O
]


def estimativa_js(io, acion, seg, escopo):
    """Chama o estimativa.js pelo node e devolve {paginas, min, max} ou None."""
    expr = (
        "import('file://%s').then(m=>{"
        "const e=m.estimativaDoPedido({ios:%d,acionamentos:%d,seg_qtd:%d,escopo:'%s'});"
        "process.stdout.write(JSON.stringify(e));})"
        % (JS.replace("\\", "/"), io, acion, seg, escopo)
    )
    r = subprocess.run(["node", "--input-type=module", "-e", expr],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise SystemExit("node falhou: " + (r.stderr or "")[:300])
    return json.loads(r.stdout or "null")


passos = []


def P(nome, ok, detalhe=""):
    passos.append((nome, ok, detalhe))
    print("  %s %-46s %s" % ("ok   " if ok else "FALHA", nome, detalhe))


print()
print("  " + "=" * 68)
print("  ESTIMATIVA DO SITE  x  PRECO DO PYTHON")
print("  " + "=" * 68)

for io, acion, seg, escopo in CASOS:
    tag = "I/O %d · acion %d · seg %d · %s" % (io, acion, seg, escopo)
    js = estimativa_js(io, acion, seg, escopo)

    # paginas do Python
    pag_py = calc.estimar_paginas(io, acion, seg, escopo)

    if js is None:
        P("%-34s (sem estimativa)" % tag, True, "js=None")
        continue

    # 1. paginas identicas
    P("%-34s paginas iguais" % tag, js["paginas"] == pag_py,
      "js=%d py=%d" % (js["paginas"], pag_py))

    # 2. o total fechado do Python (sem acrescimo, sem desconto) dentro da faixa
    total = calc.calcular(pag_py)["total"]
    dentro = js["min"] <= total <= js["max"]
    P("%-34s total na faixa" % tag, dentro,
      "R$ %d ∈ [%d, %d]" % (total, js["min"], js["max"]))


# o "sem dados" tem que devolver None (nao inventar numero)
for io, acion, seg, escopo in [(0, 0, 0, "A"), (96, 8, 6, "?"), (0, 0, 5, "B")]:
    js = estimativa_js(io, acion, seg, escopo)
    P("sem escopo/tamanho -> None (%s)" % escopo, js is None,
      "js=%s" % (js if js is None else "estimou!"))


print()
bons = sum(1 for _, o, _ in passos if o)
print("  " + "=" * 68)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o, d in passos:
    if not o:
        print("    FALHOU: %s — %s" % (n, d))
print("  " + "=" * 68)
print()
raise SystemExit(0 if bons == len(passos) else 1)
