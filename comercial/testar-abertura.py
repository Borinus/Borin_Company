# -*- coding: utf-8 -*-
"""Prova que a condição de abertura vai pra quem deve, e só pra quem deve.

POR QUE ESTE TESTE EXISTE: até 05/08/2026 o orcamento.py tinha uma constante
`TODOS_NOVOS = True` que dava o desconto de abertura pra TODO mundo, com um
comentário mandando trocar pra False quando o primeiro cliente entrasse. Num
Escopo B são R$ 6.700 por proposta — e a proteção era alguém lembrar.

Agora a regra é: novo é quem não está em clientes-atendidos.json. `--forcar-novo`
existe pra conferir formato e vale só naquela execução.

Regra #1 do AGENTS.md: os defeitos plantados estão no rodapé.

Roda com: python comercial/testar-abertura.py
"""

import importlib.util
import io
import json
import os
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AQUI = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("orc", os.path.join(AQUI, "orcamento.py"))
orc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(orc)

passos = []


def P(nome, ok, detalhe=""):
    passos.append((nome, ok, detalhe))
    print("  %s %-52s %s" % ("ok   " if ok else "FALHA", nome, detalhe))


def com_ficheiro(atendidos):
    """Aponta o módulo pra um cadastro temporário, longe do de verdade."""
    tmp = os.path.join(tempfile.mkdtemp(), "atendidos.json")
    io.open(tmp, "w", encoding="utf-8").write(json.dumps(atendidos, ensure_ascii=False))
    orc.ATENDIDOS = tmp
    return tmp


class Ped(object):
    def __init__(self, **kw):
        self.email = "cliente@empresa.com"
        self.abertura = False
        self.setup_padrao = False
        self.ja_e_cliente = False
        self.forcar_novo = False
        self.__dict__.update(kw)


import contextlib


def decidir(p):
    """Roda aplicar_primeira_vez sem poluir a saída, devolve (abertura, recado)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        orc.aplicar_primeira_vez(p)
    return p.abertura, p.setup_padrao, buf.getvalue().strip()


VELHO = {"cliente@empresa.com": {"primeira_proposta": "PROP-2026-001", "em": "2026-07-10"}}

print()
print("  " + "=" * 68)
print("  CONDIÇÃO DE ABERTURA — vai pra quem deve?")
print("  " + "=" * 68)
print()
print("  [a regra] quem já recebeu proposta NÃO leva o desconto de novo")

com_ficheiro({})
ab, st, recado = decidir(Ped())
P("cliente que nunca apareceu é NOVO", ab and st, recado[:52])

com_ficheiro(VELHO)
ab, st, recado = decidir(Ped())
P("cliente que já recebeu NÃO leva desconto", not ab and not st, recado[:52])
P("e o recado diz qual foi a primeira proposta", "PROP-2026-001" in recado, recado[:52])

com_ficheiro(VELHO)
ab, st, _ = decidir(Ped(email="  Cliente@Empresa.COM  "))
P("maiúscula e espaço não driblam a regra", not ab, "e-mail normalizado")

com_ficheiro(VELHO)
ab, st, _ = decidir(Ped(email="outro@empresa.com"))
P("colega do mesmo domínio ainda é cliente novo", ab and st, "regra é por e-mail")

print()
print("  [as forçadas] existem, e cada uma diz o que fez")

com_ficheiro(VELHO)
ab, st, recado = decidir(Ped(forcar_novo=True))
P("--forcar-novo devolve o desconto", ab and st, recado[:52])
P("e avisa que foi forçado", "forçado" in recado or "forcar" in recado, "")

com_ficheiro({})
ab, st, recado = decidir(Ped(ja_e_cliente=True))
P("--ja-e-cliente tira o desconto de quem seria novo", not ab and not st, recado[:52])

com_ficheiro({})
ab, st, _ = decidir(Ped(abertura=True, ja_e_cliente=True))
P("--abertura na mão sobrevive a --ja-e-cliente", ab, "o que foi digitado manda")

print()
print("  [desconto combinado] --desconto N substitui a abertura, sem empilhar")

com_ficheiro({})
ab, st, recado = decidir(Ped(desconto=20))
P("--desconto 20 desliga a abertura automática do novo", not ab and not st,
  recado[:52])
P("e diz em voz alta o que decidiu",
  "20" in recado and "abertura" in recado, recado[:52])

r20 = orc.calc.calcular(40, desconto_pct=20)
P("calcular põe a linha do desconto combinado",
  any("20%" in r for r, _ in r20["linhas"]) and r20["total"] < r20["valor_cheio"],
  "total %s, cheio %s" % (r20["total"], r20["valor_cheio"]))
# a sobra do arredondamento e absorvida na linha do projeto (como nos outros
# descontos), entao o cheio desce junto — o que tem que bater e a COLUNA
soma = round(sum(v for _, v in r20["linhas"]), 2)
P("a conta fecha: 40 páginas −20% = R$ 7.500 e a coluna soma exata",
  r20["total"] == 7500.0 and soma == r20["total"],
  "coluna %s, total %s, cheio %s" % (soma, r20["total"], r20["valor_cheio"]))

try:
    orc.calc.calcular(40, abertura=True, desconto_pct=20)
    P("abertura + desconto juntos LEVANTA erro", False,
      "aceitou os dois — seria 60% de desconto sem ninguém decidir")
except ValueError:
    P("abertura + desconto juntos LEVANTA erro", True, "nada de empilhar calado")

try:
    orc.calc.calcular(40, desconto_pct=120)
    P("desconto acima de 100% LEVANTA erro", False, "aceitou pagar o cliente")
except ValueError:
    P("desconto acima de 100% LEVANTA erro", True, "")

print()
print("  [nada calado] toda decisão de R$ 6.700 tem que aparecer na tela")
for rot, p, ficha in [("novo", Ped(), {}),
                      ("antigo", Ped(), VELHO),
                      ("forçado novo", Ped(forcar_novo=True), VELHO),
                      ("forçado antigo", Ped(ja_e_cliente=True), {})]:
    com_ficheiro(ficha)
    _, _, recado = decidir(p)
    P("caso '%s' imprime um recado" % rot, bool(recado), recado[:50])

print()
print("  [a bomba] a constante que dava desconto pra todo mundo sumiu")
fonte = io.open(os.path.join(AQUI, "orcamento.py"), encoding="utf-8").read()
# procura ATRIBUIÇÃO, não a string: o comentário que conta a história da bomba
# cita o nome dela de propósito, e apagar esse comentário pra agradar o teste
# seria trocar a memória do defeito por um check verde
atribui = [l for l in fonte.splitlines()
           if l.strip().startswith("TODOS_NOVOS") and "=" in l.split("#")[0]]
P("nenhuma atribuição a TODOS_NOVOS sobrou", not atribui,
  atribui[0][:44] if atribui else "só o comentário histórico")
# a regra tem que morar num lugar só, e esse lugar é aplicar_primeira_vez
corpo = fonte.split("def aplicar_primeira_vez")[1].split("\ndef ")[0]
P("a regra consulta o cadastro dentro de aplicar_primeira_vez",
  "_atendidos()" in corpo, "")
# checa DEFINIÇÃO, não menção. É a terceira vez hoje que um teste meu falha
# porque o comentário que explica o defeito cita o nome do defeito — o grep
# cru não distingue código de história, e a história é a parte que vale manter.
P("não voltou uma função ehClienteNovo sem uso",
  "def ehClienteNovo" not in fonte, "só a nota explicando por que saiu")

print()
print("  [cadastro ilegível] vira desconto — então tem que GRITAR antes")
tmp = com_ficheiro({})
io.open(tmp, "w", encoding="utf-8").write("{isso nao e json")
ab, _, recado = decidir(Ped())
P("cadastro corrompido: cliente vira NOVO", ab,
  "erra pro lado do cliente, que é o lado certo")
P("mas avisa na tela que não conseguiu ler", "NAO CONSEGUI LER" in recado,
  "" if "NAO CONSEGUI LER" in recado else "PASSOU CALADO — R$ 6.700 sem aviso")

tmp = com_ficheiro({})
io.open(tmp, "w", encoding="utf-8").write('["lista", "em vez de objeto"]')
_, _, recado = decidir(Ped())
P("arquivo com formato errado também avisa", "NAO CONSEGUI LER" in recado, "")

orc.ATENDIDOS = os.path.join(tempfile.mkdtemp(), "nao-existe.json")
_, _, recado = decidir(Ped())
P("arquivo que ainda NÃO existe não gera alarme falso",
  "NAO CONSEGUI LER" not in recado, "primeira execução é normal")

print()
bons = sum(1 for _, o, _ in passos if o)
print("  " + "=" * 68)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o, d in passos:
    if not o:
        print("    FALHOU: %s — %s" % (n, d))
print("  " + "=" * 68)
print()

# COMO ESTE ARQUIVO FOI PROVADO (05/08/2026) — defeitos plantados e efeito:
#   1. `ficha = None` (a bomba de volta)      -> 4 vermelhos
#   2. tirar o print do caso ANTIGO           -> 2 vermelhos (recado some)
#   3. tirar o .strip().lower() do e-mail     -> 1 vermelho (maiúscula dribla)
#   4. ja_e_cliente deixando de zerar abertura-> 1 vermelho
# Se algum dia esses quatro passarem verde, o teste virou enfeite.
#
# O QUE A PROVA DE FALHA ACHOU SOZINHA, e vale mais que os quatro: na primeira
# rodada o defeito 1 foi plantado em `ehClienteNovo`, e derrubou UM check — o de
# leitura do código — e nenhum de comportamento. Motivo: nada chamava aquela
# função. Ela tinha o nome da regra e não era a regra. Foi removida. Sem tentar
# quebrar o código de propósito, ela ficaria lá pra sempre parecendo importante.

raise SystemExit(0 if bons == len(passos) else 1)
