# -*- coding: utf-8 -*-
"""Controle do faturamento acumulado — uma linha por nota emitida.

POR QUE ISSO EXISTE, E POR QUE E DE VERDADE IMPORTANTE

O teto do MEI nao e um numero redondo de R$ 81 mil. No ano em que o CNPJ abre,
a lei manda proporcionalizar: R$ 6.750 por mes, contando o mes de abertura
inteiro (LC 123/2006, art. 18-A, paragrafo 2). O CNPJ abriu em 18/03/2026, entao
o teto de 2026 e R$ 67.500 — e nao os R$ 81 mil que todo mundo repete.

Passar disso tem dois precos muito diferentes:

  ate 20% acima (ate R$ 81.000 em 2026)  ->  DAS complementar, sai do MEI em
                                             01/01 do ano seguinte
  mais de 20% acima (acima de R$ 81.000) ->  desenquadramento DE OFICIO
                                             RETROATIVO a 18/03/2026, com todo
                                             o faturamento recalculado como ME

O segundo patamar e a conta mais cara documentada em toda a pasta comercial. E
ele chega de surpresa, porque um unico Escopo B grande (R$ 11.700) mexe 17% do
teto de uma vez. Sem controle escrito, a linha se cruza sem ninguem perceber.

Por isso o gatilho aqui e R$ 55 mil, nao o teto: sobra um projeto grande inteiro
de folga pra abrir o Simples sem pressa. Abrir empresa depois de cruzar a linha
nao adianta — o retroativo ja foi gerado.

O QUE MAIS ESTA AQUI: O QUE AINDA NAO ENTROU

Contrato assinado gera duas parcelas — 40% na assinatura e 60% em 15 dias
(comercial/fluxo-comercial.md). Ate 05/08/2026 nada guardava isso: o sistema ia
ate o contrato assinado e parava. Quem trabalha sozinho perde dinheiro
exatamente ai, no saldo que ninguem lembrou de cobrar, porque o projeto ja foi
entregue e a atencao ja foi pro proximo.

Entao o mesmo comando cuida das duas metades: o que ENTROU (nota emitida, que
conta pro teto do MEI) e o que FALTA ENTRAR (parcela em aberto, com vencimento).

USO

    python comercial/faturar.py                          # situacao de hoje
    python comercial/faturar.py cobrar --proposta PROP-2026-082 \\
        --cliente "Metalurgica X" --total 6700 --assinado 2026-08-14
    python comercial/faturar.py add --data 2026-08-14 \\
        --cliente "Metalurgica X" --nota 1 --valor 2680 \\
        --proposta PROP-2026-082 --descricao "Entrada 40%"
    python comercial/faturar.py --ano 2027               # olhar outro ano

Detalhe da regra #3 do AGENTS.md: nada aqui pode falhar calado. Arquivo corrompido,
numero de nota repetido, valor que nao e numero — tudo isso para o programa com
mensagem, em vez de gravar errado e deixar a conta mentir depois.
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
LIVRO = AQUI / "faturamento.json"
RECEBER = AQUI / "receber.json"

# fluxo-comercial.md: 40% na assinatura, 60% em 15 dias apos a aprovacao
PARCELAS = [("Entrada, na assinatura", 0.40, 0),
            ("Saldo", 0.60, 15)]

# LC 123/2006, art. 18-A, par. 1 e 2. Confirmado em fonte oficial — ver
# comercial/enquadramento.md. Os R$ 110 mil do PLP 186/2026 NAO viraram lei.
TETO_MENSAL = 6750.00
MARGEM_RETROATIVO = 1.20          # acima disso o desenquadramento retroage
ABERTURA = date(2026, 3, 18)      # CNPJ 65.749.097/0001-85
GATILHO = 55000.00                # comercial/formalizacao.md, 29/07/2026


# --------------------------------------------------------------- as contas

def meses_no_ano(ano):
    """Quantos meses do ano o CNPJ existiu. O mes de abertura conta inteiro."""
    if ano < ABERTURA.year:
        return 0
    if ano > ABERTURA.year:
        return 12
    return 12 - ABERTURA.month + 1


def teto_do_ano(ano):
    return TETO_MENSAL * meses_no_ano(ano)


def dinheiro(v):
    """R$ 67.500,00 — ponto de milhar e virgula de decimal, como se le aqui."""
    s = "%.2f" % v
    inteiro, dec = s.split(".")
    negativo = inteiro.startswith("-")
    inteiro = inteiro.lstrip("-")
    partes = []
    while len(inteiro) > 3:
        partes.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    partes.insert(0, inteiro)
    return ("-" if negativo else "") + "R$ " + ".".join(partes) + "," + dec


# ------------------------------------------------------------- o arquivo

def ler():
    if not LIVRO.exists():
        return []
    try:
        dados = json.loads(LIVRO.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(
            "ERRO: %s esta corrompido (%s).\n"
            "Nao vou continuar: um livro de faturamento pela metade daria um\n"
            "acumulado menor que o real, e e exatamente esse numero que decide\n"
            "se voce ainda esta dentro do teto." % (LIVRO.name, e))
    if not isinstance(dados, list):
        raise SystemExit("ERRO: %s deveria ser uma lista de notas." % LIVRO.name)
    return dados


def gravar(notas):
    notas = sorted(notas, key=lambda n: (n["data"], str(n["nota"])))
    LIVRO.write_text(
        json.dumps(notas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ler_receber():
    """Parcelas combinadas e ainda nao recebidas.

    Mesmo cuidado do livro: arquivo que existe e nao abre PARA o programa. Aqui
    o silencio custa ainda mais caro que no faturamento — uma lista de cobranca
    que volta vazia por erro de leitura parece 'esta tudo recebido'.
    """
    if not RECEBER.exists():
        return []
    try:
        d = json.loads(RECEBER.read_text(encoding="utf-8"))
        if not isinstance(d, list):
            raise ValueError("deveria ser uma lista de parcelas")
        return d
    except Exception as e:
        raise SystemExit(
            "ERRO: %s existe e nao abre (%s).\n"
            "Nao vou seguir: lista de cobranca ilegivel lida como vazia vira\n"
            "'nao tem nada a receber', que e a mentira mais cara deste arquivo."
            % (RECEBER.name, e))


def gravar_receber(itens):
    itens = sorted(itens, key=lambda p: (p["vence"], p["proposta"]))
    RECEBER.write_text(
        json.dumps(itens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# -------------------------------------------------------------- comandos

def cobrar(args):
    """Contrato assinado: registra as duas parcelas que passam a ser devidas."""
    try:
        assinado = date.fromisoformat(args.assinado)
    except ValueError:
        raise SystemExit("ERRO: data '%s' nao e AAAA-MM-DD." % args.assinado)
    if args.total <= 0:
        raise SystemExit("ERRO: total tem que ser maior que zero.")

    itens = ler_receber()
    if any(p["proposta"] == args.proposta for p in itens):
        raise SystemExit(
            "ERRO: a proposta %s ja tem parcela em aberto.\n"
            "Lancar de novo dobraria o valor a receber e faria voce cobrar\n"
            "duas vezes o mesmo contrato." % args.proposta)

    novas = []
    for nome, fracao, dias in PARCELAS:
        novas.append({
            "proposta": args.proposta,
            "cliente": args.cliente,
            "parcela": nome,
            "valor": round(args.total * fracao, 2),
            "vence": (assinado + timedelta(days=dias)).isoformat(),
        })
    gravar_receber(itens + novas)
    print()
    print("  contrato %s — %s" % (args.proposta, args.cliente))
    for p in novas:
        print("    %-24s %14s   vence %s"
              % (p["parcela"], dinheiro(p["valor"]), p["vence"]))
    print()
    situacao(assinado.year)


def adicionar(args):
    notas = ler()

    try:
        d = date.fromisoformat(args.data)
    except ValueError:
        raise SystemExit("ERRO: data '%s' nao e AAAA-MM-DD." % args.data)
    if d < ABERTURA:
        raise SystemExit(
            "ERRO: %s e anterior a abertura do CNPJ (%s). Nota antes da empresa\n"
            "existir nao entra em teto nenhum — confira a data."
            % (args.data, ABERTURA.isoformat()))

    if args.valor <= 0:
        raise SystemExit("ERRO: valor tem que ser maior que zero.")

    chave = (str(args.nota), d.year)
    for n in notas:
        if (str(n["nota"]), date.fromisoformat(n["data"]).year) == chave:
            raise SystemExit(
                "ERRO: a nota %s de %d ja esta lancada (%s, %s).\n"
                "Lancar duas vezes inflaria o acumulado e faria voce abrir o\n"
                "Simples antes da hora; apagar a linha certa e pior ainda."
                % (args.nota, d.year, n["cliente"], dinheiro(n["valor"])))

    notas.append({
        "data": d.isoformat(),
        "nota": str(args.nota),
        "cliente": args.cliente,
        "descricao": args.descricao or "",
        "proposta": getattr(args, "proposta", "") or "",
        "valor": round(float(args.valor), 2),
    })
    gravar(notas)
    print("\n  lancado: nota %s  %s  %s  %s"
          % (args.nota, d.isoformat(), args.cliente, dinheiro(args.valor)))

    # Baixa a parcela em aberto. Sem isto ele teria que lembrar de dar baixa
    # num segundo lugar — e a regra #3 do AGENTS.md ja custou caro aqui: coisa
    # que depende de lembrar nao acontece.
    if getattr(args, "proposta", ""):
        abertos = ler_receber()
        alvo = [p for p in abertos if p["proposta"] == args.proposta]
        if not alvo:
            print("  aviso:   a proposta %s nao tem parcela em aberto. A nota foi"
                  % args.proposta)
            print("           lancada, mas nao deu baixa em nada — confira o numero.")
        else:
            # a mais antiga primeiro: entrada antes do saldo
            p = sorted(alvo, key=lambda x: x["vence"])[0]
            abertos.remove(p)
            gravar_receber(abertos)
            print("  baixa:   %s de %s — %s"
                  % (p["parcela"], args.proposta, dinheiro(p["valor"])))
            if abs(p["valor"] - float(args.valor)) > 0.01:
                print("  ATENCAO: a parcela era %s e a nota saiu %s. Diferenca de %s."
                      % (dinheiro(p["valor"]), dinheiro(args.valor),
                         dinheiro(abs(p["valor"] - float(args.valor)))))
    print()
    situacao(d.year)


def situacao(ano):
    notas = [n for n in ler() if date.fromisoformat(n["data"]).year == ano]
    acumulado = sum(n["valor"] for n in notas)
    teto = teto_do_ano(ano)
    retro = teto * MARGEM_RETROATIVO
    meses = meses_no_ano(ano)

    print("  " + "=" * 68)
    print("  FATURAMENTO %d — MEI 65.749.097/0001-85" % ano)
    print("  " + "=" * 68)

    if not notas:
        print("  nenhuma nota lancada em %d." % ano)
    else:
        print("  %-11s %-6s %-26s %14s" % ("data", "nota", "cliente", "valor"))
        print("  " + "-" * 68)
        for n in notas:
            print("  %-11s %-6s %-26s %14s"
                  % (n["data"], n["nota"], n["cliente"][:26], dinheiro(n["valor"])))
        print("  " + "-" * 68)

    print("  %-45s %20s" % ("acumulado no ano", dinheiro(acumulado)))
    print()

    if teto <= 0:
        print("  o CNPJ nao existia em %d — nao ha teto a comparar." % ano)
        return acumulado

    if meses < 12:
        print("  teto de %d: %s  (proporcional, %d meses desde a abertura)"
              % (ano, dinheiro(teto), meses))
    else:
        print("  teto de %d: %s  (ano cheio)" % (ano, dinheiro(teto)))
    print("  desenquadramento retroativo a partir de: %s" % dinheiro(retro))
    print()

    pct = acumulado / teto * 100
    barra = int(min(pct, 100) / 2.5)
    print("  [%s%s] %.1f%% do teto" % ("#" * barra, "." * (40 - barra), pct))
    print()

    # --- o veredito. Nada de "voce esta em 82%" e o usuario que interprete ---
    if acumulado >= retro:
        print("  !! PASSOU DA LINHA DO RETROATIVO.")
        print("     O desenquadramento retroage a %s e todo o faturamento do"
              % ABERTURA.strftime("%d/%m/%Y"))
        print("     periodo e recalculado como ME. Falar com contador HOJE —")
        print("     isso so se desfaz por processo administrativo.")
    elif acumulado > teto:
        print("  !! PASSOU DO TETO, mas ainda abaixo da linha do retroativo.")
        print("     Paga DAS complementar e sai do MEI em 01/01/%d." % (ano + 1))
        print("     Falta %s pro retroativo — nao emita mais nada sem falar"
              % dinheiro(retro - acumulado))
        print("     com o contador.")
    elif acumulado >= GATILHO:
        print("  >  GATILHO ATINGIDO (%s). Hora de procurar o contador e" % dinheiro(GATILHO))
        print("     comecar a abrir o Simples. Ainda cabe %s ate o teto —"
              % dinheiro(teto - acumulado))
        print("     e um projeto grande de folga, que e exatamente o tempo que")
        print("     a abertura leva.")
    else:
        falta = GATILHO - acumulado
        print("  -  dentro do MEI. Faltam %s pro gatilho de %s."
              % (dinheiro(falta), dinheiro(GATILHO)))
        # o aviso que muda decisao: quantos projetos grandes ainda cabem
        cabe = int((teto - acumulado) // 11700)
        print("     Do teto ainda cabem %d Escopo B grande (R$ 11.700) — "
              "depois disso" % cabe)
        print("     o proximo projeto sozinho ja encosta na linha.")
    mostrar_receber()
    return acumulado


def mostrar_receber(hoje=None):
    """O que foi combinado e ainda nao entrou. Vencido primeiro, em destaque."""
    hoje = hoje or date.today()
    itens = ler_receber()
    if not itens:
        print()
        return 0.0

    vencidos = [p for p in itens if date.fromisoformat(p["vence"]) < hoje]
    aVencer = [p for p in itens if date.fromisoformat(p["vence"]) >= hoje]

    print("  " + "=" * 68)
    print("  A RECEBER")
    print("  " + "=" * 68)
    for p in vencidos:
        atraso = (hoje - date.fromisoformat(p["vence"])).days
        print("  !! %-15s %-20s %13s  VENCIDA ha %d dia(s)"
              % (p["proposta"][:15], p["cliente"][:20], dinheiro(p["valor"]), atraso))
    for p in aVencer:
        faltam = (date.fromisoformat(p["vence"]) - hoje).days
        print("     %-15s %-20s %13s  vence em %d dia(s)"
              % (p["proposta"][:15], p["cliente"][:20], dinheiro(p["valor"]), faltam))

    total = sum(p["valor"] for p in itens)
    print("  " + "-" * 68)
    print("  %-45s %20s" % ("total a receber", dinheiro(total)))
    if vencidos:
        print()
        print("  %d parcela(s) vencida(s), somando %s."
              % (len(vencidos), dinheiro(sum(p["valor"] for p in vencidos))))
        print("  Isso nao se cobra sozinho.")
    print()
    return total


def main():
    p = argparse.ArgumentParser(
        description="Controle do faturamento acumulado do MEI.")
    p.add_argument("--ano", type=int, default=date.today().year,
                   help="ano a conferir (padrao: o atual)")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("add", help="lancar uma nota emitida")
    a.add_argument("--data", required=True, help="AAAA-MM-DD da emissao")
    a.add_argument("--nota", required=True, help="numero da nota")
    a.add_argument("--cliente", required=True)
    a.add_argument("--valor", required=True, type=float, help="valor bruto")
    a.add_argument("--proposta", default="", help="da baixa na parcela em aberto")
    a.add_argument("--descricao", default="")

    c = sub.add_parser("cobrar", help="contrato assinado: abre as duas parcelas")
    c.add_argument("--proposta", required=True, help="numero da proposta")
    c.add_argument("--cliente", required=True)
    c.add_argument("--total", required=True, type=float, help="valor fechado")
    c.add_argument("--assinado", required=True, help="AAAA-MM-DD da assinatura")

    args = p.parse_args()
    if args.cmd == "add":
        adicionar(args)
    elif args.cmd == "cobrar":
        cobrar(args)
    else:
        situacao(args.ano)


if __name__ == "__main__":
    main()
