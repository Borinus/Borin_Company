# -*- coding: utf-8 -*-
"""Prova que o faturar.py sabe contar — e que sabe recusar.

Regra #1 do AGENTS.md: teste so passa se eu provar que ele sabe falhar. Este
arquivo foi rodado com tres defeitos plantados de proposito antes de entrar no
repositorio (ver o rodape do arquivo), e cada um deles deixou o teste vermelho.

Roda com: python comercial/testar-faturar.py
"""

import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("faturar", AQUI / "faturar.py")
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)

passos = []


def P(nome, ok, detalhe=""):
    passos.append((nome, ok, detalhe))
    print("  %s %-52s %s" % ("ok   " if ok else "FALHA", nome, detalhe))


def com_livro(notas):
    """Aponta o modulo pra um livro temporario, pra nao encostar no de verdade."""
    tmp = Path(tempfile.mkdtemp()) / "faturamento.json"
    tmp.write_text(json.dumps(notas, ensure_ascii=False), encoding="utf-8")
    f.LIVRO = tmp
    return tmp


def situacao_texto(ano):
    buf = io.StringIO()
    with redirect_stdout(buf):
        total = f.situacao(ano)
    return total, buf.getvalue()


print()
print("  " + "=" * 66)
print("  CONTROLE DE FATURAMENTO")
print("  " + "=" * 66)
print()
print("  [teto proporcional] o ano de abertura nao tem teto cheio")

# 18/03/2026 -> marco a dezembro = 10 meses. 10 x 6750 = 67.500
P("2026 conta 10 meses", f.meses_no_ano(2026) == 10, "%d meses" % f.meses_no_ano(2026))
P("teto de 2026 = R$ 67.500", f.teto_do_ano(2026) == 67500.0, f.dinheiro(f.teto_do_ano(2026)))
P("teto de 2027 = R$ 81.000 (ano cheio)", f.teto_do_ano(2027) == 81000.0,
  f.dinheiro(f.teto_do_ano(2027)))
P("2025 nao tem teto (CNPJ nao existia)", f.teto_do_ano(2025) == 0.0, "")
P("a linha do retroativo de 2026 e R$ 81.000",
  f.teto_do_ano(2026) * f.MARGEM_RETROATIVO == 81000.0,
  f.dinheiro(f.teto_do_ano(2026) * f.MARGEM_RETROATIVO))

print()
print("  [formato] o numero tem que ser legivel de relance")
P("67500 vira 'R$ 67.500,00'", f.dinheiro(67500) == "R$ 67.500,00", f.dinheiro(67500))
P("8940.5 vira 'R$ 8.940,50'", f.dinheiro(8940.5) == "R$ 8.940,50", f.dinheiro(8940.5))
P("1234567.89 com dois pontos de milhar",
  f.dinheiro(1234567.89) == "R$ 1.234.567,89", f.dinheiro(1234567.89))

print()
print("  [veredito] cada faixa tem que dizer coisa DIFERENTE")

com_livro([])
total, txt = situacao_texto(2026)
P("livro vazio: acumulado zero", total == 0, f.dinheiro(total))
P("livro vazio: nao dispara aviso nenhum",
  "GATILHO ATINGIDO" not in txt and "PASSOU" not in txt, "")

com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 30000.0}])
total, txt = situacao_texto(2026)
P("R$ 30 mil: dentro, sem aviso", total == 30000.0 and "dentro do MEI" in txt,
  f.dinheiro(total))
P("R$ 30 mil: diz quanto falta pro gatilho", "Faltam R$ 25.000,00" in txt, "")

com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 30000.0},
           {"data": "2026-06-02", "nota": "2", "cliente": "B", "descricao": "",
            "valor": 25100.0}])
total, txt = situacao_texto(2026)
P("R$ 55.100: dispara o gatilho", "GATILHO ATINGIDO" in txt, f.dinheiro(total))
P("R$ 55.100: NAO diz que passou do teto", "PASSOU" not in txt, "")

com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 70000.0}])
total, txt = situacao_texto(2026)
P("R$ 70 mil: passou do teto de 2026", "PASSOU DO TETO" in txt, f.dinheiro(total))
P("R$ 70 mil: ainda NAO e o retroativo", "PASSOU DA LINHA" not in txt, "")
P("R$ 70 mil: diz quanto falta pro retroativo", "Falta R$ 11.000,00" in txt, "")

com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 82000.0}])
total, txt = situacao_texto(2026)
P("R$ 82 mil: e retroativo", "PASSOU DA LINHA DO RETROATIVO" in txt, f.dinheiro(total))
P("R$ 82 mil: cita a data de abertura", "18/03/2026" in txt, "")

print()
print("  [fronteiras] o valor exato da linha, nao um perto dela")
com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 67500.0}])
_, txt = situacao_texto(2026)
P("exatamente no teto ainda NAO estourou", "PASSOU DO TETO" not in txt, "R$ 67.500,00")
com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 67500.01}])
_, txt = situacao_texto(2026)
P("um centavo acima do teto ja estoura", "PASSOU DO TETO" in txt, "R$ 67.500,01")
com_livro([{"data": "2026-05-02", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 81000.0}])
_, txt = situacao_texto(2026)
P("exatamente na linha ja e retroativo", "PASSOU DA LINHA" in txt, "R$ 81.000,00")

print()
print("  [ano errado] nota de 2027 nao pode contar no teto de 2026")
com_livro([{"data": "2026-12-30", "nota": "1", "cliente": "A", "descricao": "",
            "valor": 60000.0},
           {"data": "2027-01-02", "nota": "2", "cliente": "B", "descricao": "",
            "valor": 60000.0}])
t26, _ = situacao_texto(2026)
t27, _ = situacao_texto(2027)
P("cada ano conta so o seu", t26 == 60000.0 and t27 == 60000.0,
  "2026=%s 2027=%s" % (f.dinheiro(t26), f.dinheiro(t27)))


# --- as recusas. Regra #3: nada pode falhar calado ---------------------------

class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def tenta_add(**kw):
    """Devolve (deu_erro, mensagem). Silencia o print do sucesso."""
    base = dict(data="2026-08-14", nota="9", cliente="X", valor=1000.0,
                descricao="")
    base.update(kw)
    try:
        with redirect_stdout(io.StringIO()):
            f.adicionar(Args(**base))
        return False, ""
    except SystemExit as e:
        return True, str(e)


print()
print("  [recusas] lancamento errado tem que PARAR, nao gravar torto")

com_livro([])
erro, msg = tenta_add(data="2026-13-40")
P("data impossivel e recusada", erro, msg.splitlines()[0][:44] if erro else "gravou!")

com_livro([])
erro, msg = tenta_add(data="2026-03-17")
P("data anterior a abertura do CNPJ e recusada", erro,
  msg.splitlines()[0][:44] if erro else "gravou!")

com_livro([])
erro, msg = tenta_add(valor=0)
P("valor zero e recusado", erro, msg.splitlines()[0][:44] if erro else "gravou!")

com_livro([])
erro, msg = tenta_add(valor=-500)
P("valor negativo e recusado", erro, msg.splitlines()[0][:44] if erro else "gravou!")

com_livro([{"data": "2026-08-01", "nota": "9", "cliente": "Ja Existe",
            "descricao": "", "valor": 5000.0}])
erro, msg = tenta_add(nota="9", data="2026-08-14")
P("nota repetida no mesmo ano e recusada", erro,
  msg.splitlines()[0][:44] if erro else "gravou duas vezes!")

com_livro([{"data": "2026-08-01", "nota": "9", "cliente": "Ano Passado",
            "descricao": "", "valor": 5000.0}])
erro, _ = tenta_add(nota="9", data="2027-02-10")
P("mesmo numero em ANO diferente e aceito", not erro, "numeracao reinicia por ano")

tmp = com_livro([])
tmp.write_text("{isso nao e json", encoding="utf-8")
try:
    with redirect_stdout(io.StringIO()):
        f.ler()
    quebrou = False
    msg = ""
except SystemExit as e:
    quebrou, msg = True, str(e)
P("livro corrompido para o programa, nao devolve zero", quebrou,
  msg.splitlines()[0][:44] if quebrou else "devolveu lista vazia!")

tmp = com_livro([])
tmp.write_text('{"nota": 1}', encoding="utf-8")
try:
    with redirect_stdout(io.StringIO()):
        f.ler()
    quebrou = False
except SystemExit:
    quebrou = True
P("livro que nao e lista tambem para", quebrou, "")

# --- ida e volta pelo disco --------------------------------------------------
print()
print("  [gravacao] o que entra tem que sair igual")
com_livro([])
with redirect_stdout(io.StringIO()):
    f.adicionar(Args(data="2026-09-01", nota="3", cliente="Metalurgica Z",
                     valor=6700.0, descricao="Escopo A"))
    f.adicionar(Args(data="2026-08-15", nota="2", cliente="Fabrica Y",
                     valor=3500.0, descricao=""))
lido = f.ler()
P("as duas notas persistiram", len(lido) == 2, "%d no arquivo" % len(lido))
P("ficaram em ordem de data", [n["nota"] for n in lido] == ["2", "3"],
  " -> ".join(n["data"] for n in lido))
total, _ = situacao_texto(2026)
P("o acumulado soma as duas", total == 10200.0, f.dinheiro(total))

# ============================================================ o que falta entrar
print()
print("  " + "=" * 66)
print("  A RECEBER — o saldo que ninguem lembra de cobrar")
print("  " + "=" * 66)
print()


def com_receber(itens):
    tmp = Path(tempfile.mkdtemp()) / "receber.json"
    tmp.write_text(json.dumps(itens, ensure_ascii=False), encoding="utf-8")
    f.RECEBER = tmp
    return tmp


def cobrar_texto(**kw):
    base = dict(proposta="PROP-2026-001", cliente="Metalurgica Serra",
                total=6700.0, assinado="2026-07-20")
    base.update(kw)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            f.cobrar(Args(**base))
        return False, buf.getvalue()
    except SystemExit as e:
        return True, str(e)


print("  [as duas parcelas] 40 na assinatura, 60 em 15 dias")
com_livro([])
com_receber([])
erro, txt = cobrar_texto()
itens = f.ler_receber()
P("o contrato abriu duas parcelas", not erro and len(itens) == 2, "%d parcela(s)" % len(itens))
P("a entrada e 40% do total", any(abs(p["valor"] - 2680.0) < 0.01 for p in itens),
  f.dinheiro(itens[0]["valor"]) if itens else "")
P("o saldo e 60% do total", any(abs(p["valor"] - 4020.0) < 0.01 for p in itens), "")
P("as duas somam o total exato", abs(sum(p["valor"] for p in itens) - 6700.0) < 0.01,
  f.dinheiro(sum(p["valor"] for p in itens)))
P("a entrada vence no dia da assinatura",
  any(p["vence"] == "2026-07-20" for p in itens), "2026-07-20")
P("o saldo vence 15 dias depois",
  any(p["vence"] == "2026-08-04" for p in itens), "2026-08-04")

erro, msg = cobrar_texto()
P("cobrar a mesma proposta de novo e recusado", erro,
  msg.splitlines()[0][:44] if erro else "DOBROU O VALOR A RECEBER")

erro, _ = cobrar_texto(proposta="PROP-2026-002", total=0)
P("total zero e recusado", erro, "")
erro, _ = cobrar_texto(proposta="PROP-2026-003", assinado="20/07/2026")
P("data fora do formato e recusada", erro, "")

print()
print("  [baixa] a nota emitida derruba a parcela, sem eu lembrar")
com_livro([])
com_receber([])
cobrar_texto()
buf = io.StringIO()
with redirect_stdout(buf):
    f.adicionar(Args(data="2026-07-21", nota="1", cliente="Metalurgica Serra",
                     valor=2680.0, descricao="", proposta="PROP-2026-001"))
saida = buf.getvalue()
resta = f.ler_receber()
P("a entrada foi baixada", len(resta) == 1, "%d parcela(s) restante(s)" % len(resta))
P("quem sobrou e o SALDO, nao a entrada", resta and resta[0]["parcela"] == "Saldo",
  resta[0]["parcela"] if resta else "")
P("a baixa aparece na tela", "baixa:" in saida, "")

buf = io.StringIO()
with redirect_stdout(buf):
    f.adicionar(Args(data="2026-08-06", nota="2", cliente="Metalurgica Serra",
                     valor=4000.0, descricao="", proposta="PROP-2026-001"))
saida = buf.getvalue()
P("nota menor que a parcela dispara ATENCAO", "ATENCAO" in saida,
  "diferenca de R$ 20,00")
P("depois das duas, nao sobra nada a receber", f.ler_receber() == [], "")

com_livro([])
com_receber([])
buf = io.StringIO()
with redirect_stdout(buf):
    f.adicionar(Args(data="2026-08-06", nota="9", cliente="X", valor=100.0,
                     descricao="", proposta="PROP-QUE-NAO-EXISTE"))
saida = buf.getvalue()
P("proposta desconhecida avisa em vez de sumir", "nao tem parcela em aberto" in saida,
  "")
P("mas a nota foi lancada mesmo assim", len(f.ler()) == 1, "faturamento nao se perde")

buf = io.StringIO()
with redirect_stdout(buf):
    f.adicionar(Args(data="2026-08-07", nota="10", cliente="X", valor=100.0,
                     descricao="", proposta=""))
P("nota sem proposta nao tenta dar baixa", "baixa:" not in buf.getvalue(), "")

print()
print("  [vencida] o atraso tem que gritar, nao ficar numa lista")
com_receber([{"proposta": "PROP-2026-001", "cliente": "Atrasada Ltda",
              "parcela": "Saldo", "valor": 4020.0, "vence": "2026-07-01"},
             {"proposta": "PROP-2026-002", "cliente": "Em Dia Ltda",
              "parcela": "Saldo", "valor": 1000.0, "vence": "2026-12-01"}])
buf = io.StringIO()
with redirect_stdout(buf):
    f.mostrar_receber(hoje=date(2026, 8, 5))
saida = buf.getvalue()
P("a vencida sai marcada com !!", "!! PROP-2026-001" in saida, "")
P("e diz ha quantos dias", "VENCIDA ha 35 dia(s)" in saida, "35 dias")
P("a que esta em dia NAO e marcada", "!! PROP-2026-002" not in saida, "")
P("soma o total a receber", "R$ 5.020,00" in saida, "R$ 5.020,00")

tmp = com_receber([])
tmp.write_text("{nao e json", encoding="utf-8")
try:
    with redirect_stdout(io.StringIO()):
        f.ler_receber()
    parou = False
except SystemExit:
    parou = True
P("lista de cobranca ilegivel PARA o programa", parou,
  "vazia por erro pareceria 'esta tudo recebido'")

print()
bons = sum(1 for _, o, _ in passos if o)
print("  " + "=" * 66)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o, d in passos:
    if not o:
        print("    FALHOU: %s — %s" % (n, d))
print("  " + "=" * 66)
print()

# COMO ESTE ARQUIVO FOI PROVADO (05/08/2026) — os defeitos plantados e o efeito:
#   1. meses_no_ano() devolvendo sempre 12  -> 4 passos vermelhos (teto de 2026,
#      linha do retroativo, e as duas fronteiras de valor exato)
#   2. tirar a checagem de nota repetida    -> 1 passo vermelho ("gravou duas vezes!")
#   3. ler() devolvendo [] no JSONDecodeError -> 1 passo vermelho ("devolveu lista vazia!")
# Se algum dia esses tres defeitos passarem verde, o teste virou enfeite.

raise SystemExit(0 if bons == len(passos) else 1)
