"""
Calcula o valor de um projeto. Implementa comercial/calculo-preco.md.

    python comercial/calcular.py --io 96 --acionamentos 8 --seguranca 6 --escopo B
    python comercial/calcular.py --paginas 51 --itens-manuais 2 --abertura
    python comercial/calcular.py --io 40 --acionamentos 6 --json

As constantes de estimativa ficam todas no topo de proposito: elas sao derivadas
de UM projeto medido (04003478, 51 folhas). Depois de cada entrega, comparar
pagina estimada com pagina real e corrigir aqui.
"""

import argparse
import json
import math
import sys

# o console do Windows abre em cp1252 e quebra em acento e em sinal de menos
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------- preco ----------

POR_PAGINA = 235        # hora de mercado, 1h por folha de diagrama
POR_ITEM_MANUAL = 250   # hora avulsa: peca de marca pequena, cadastro 100% manual
SETUP_PADRAO = 1000     # padrao proprio do cliente, uma vez por cliente
PISO = 2400             # abaixo disto o trabalho humano domina e nao encolhe
ARREDONDA = 100         # o total sai redondo: 6.742,50 vira 6.700

ACRESCIMO_URGENCIA = 0.30
ACRESCIMO_FONTE = 0.50
DESCONTO_ABERTURA = 0.50

# ---------- estimativa de paginas ----------
# calibrado contra 04003478: 96 I/O, 8 acionamentos, 6 disp. seguranca,
# escopo B -> 50,1 -> 51 paginas. O projeto real tem 51 folhas.

PAGINAS_FIXAS = 14      # capa, indice, potencia, arquitetura CLP, layout, memorial, ref. cruzada
IO_POR_PAGINA = 4.5     # multifilar de comando
ACION_POR_PAGINA = 2.5  # partidas, inversores, valvulas, resistencias
SEG_POR_PAGINA = 2.0    # dispositivos de NR-12
PONTOS_POR_REGUA = 35.0
CABOS_POR_PAGINA = 6.0
IO_POR_CABO = 3.0       # quantos pontos, em media, cada cabo de campo carrega


def estimar_paginas(io=0, acionamentos=0, seguranca=0, escopo="A"):
    """Estima folhas de diagrama a partir do que a ficha pergunta."""
    p = PAGINAS_FIXAS
    p += io / IO_POR_PAGINA
    p += acionamentos / ACION_POR_PAGINA
    p += seguranca / SEG_POR_PAGINA
    p += io / PONTOS_POR_REGUA
    if escopo.upper() == "B":
        cabos = (io + acionamentos) / IO_POR_CABO
        p += cabos / CABOS_POR_PAGINA
    return math.ceil(p)


def _fechar(base, itens, setup, urgencia, arquivo_fonte, abertura):
    """O total exatamente como a coluna mostra: cada parcela arredondada em
    centavos, na mesma ordem. E esse numero que precisa cair redondo, nao o
    calculo continuo."""
    subtotal = base + itens + setup
    total = subtotal
    if urgencia:
        total += round(subtotal * ACRESCIMO_URGENCIA, 2)
    if arquivo_fonte:
        total += round(subtotal * ACRESCIMO_FONTE, 2)
    if abertura:
        total -= round(total * DESCONTO_ABERTURA, 2)
    return round(total, 2)


def calcular(paginas, itens_manuais=0, setup_padrao=False,
             urgencia=False, arquivo_fonte=False, abertura=False):
    """Monta o valor. Ordem importa: acrescimo antes do desconto, senao o
    desconto tambem reduz o que nao deveria ser descontado.

    O total sai sempre num multiplo de ARREDONDA, pra baixo. A sobra e
    descontada da linha do projeto — a unica que e estimativa. Os precos de
    tabela (cadastro de item, setup) ficam intactos, e a coluna continua
    fechando na conta do cliente."""
    itens = itens_manuais * POR_ITEM_MANUAL
    setup = SETUP_PADRAO if setup_padrao else 0
    base = paginas * POR_PAGINA

    # o piso e do projeto todo. Antes ele entrava no subtotal mas a linha do
    # projeto continuava mostrando o valor velho: a coluna nao somava.
    piso_aplicado = base + itens + setup < PISO
    if piso_aplicado:
        base = max(0.0, PISO - itens - setup)

    fator = 1.0
    if urgencia:
        fator += ACRESCIMO_URGENCIA
    if arquivo_fonte:
        fator += ACRESCIMO_FONTE
    if abertura:
        fator *= (1 - DESCONTO_ABERTURA)

    total = (base + itens + setup) * fator

    # Arredonda o total pra baixo e devolve a sobra pra linha do projeto.
    # Repete tres vezes porque cada linha e arredondada em centavos na hora de
    # montar a coluna, e essa sobra de centavo desloca o total: sem repetir,
    # um caso com acrescimo caia em 8.499,99 em vez de 8.500,00.
    alvo = int(total / ARREDONDA) * ARREDONDA
    if alvo >= ARREDONDA:
        arg = (itens, setup, urgencia, arquivo_fonte, abertura)
        # 1. aproxima: o quanto a base precisa mudar pra o total virar o alvo
        for _ in range(3):
            novo = base + (alvo - _fechar(base, *arg)) / fator
            if novo <= 0:
                break
            base = novo
        # 2. fecha o centavo. Cada parcela e arredondada na hora de montar a
        #    coluna, entao o total anda em degraus e o passo linear acima erra
        #    por um centavo em quem tem os dois acrescimos. Varre a vizinhanca
        #    e fica com o valor de base que bate exato.
        passo = 0.01 / fator
        for k in range(0, 400):
            for lado in ((0,) if k == 0 else (k, -k)):
                tent = base + lado * passo
                if tent > 0 and abs(_fechar(tent, *arg) - alvo) < 0.005:
                    base = tent
                    k = -1
                    break
            if k == -1:
                break

    subtotal = base + itens + setup

    linhas = [("Projeto — %d páginas de diagrama" % paginas, round(base, 2))]
    if itens:
        linhas.append(("Cadastro de %d %s fora do banco"
                       % (itens_manuais, "item" if itens_manuais == 1 else "itens"), itens))
    if setup:
        linhas.append(("Setup do padrão do cliente (uma vez)", setup))

    total = subtotal
    if urgencia:
        v = round(subtotal * ACRESCIMO_URGENCIA, 2)
        linhas.append(("Urgência (+30%)", v)); total += v
    if arquivo_fonte:
        v = round(subtotal * ACRESCIMO_FONTE, 2)
        linhas.append(("Arquivo-fonte do CAD (+50%)", v)); total += v

    cheio = total
    if abertura:
        v = -round(total * DESCONTO_ABERTURA, 2)
        linhas.append(("Condição de abertura (-50%)", v)); total += v

    total = round(total, 2)
    cheio = round(cheio, 2)

    # O ultimo centavo. Com desconto de 50% sobre um valor cheio impar em
    # centavos, o total NUNCA cai redondo por ajuste de base: 16.999,98 menos
    # metade da 8.499,99. Entao a sobra e absorvida pela ultima linha, que e o
    # desconto — o unico lugar onde um centavo nao muda nada que o cliente
    # confira. A coluna continua somando exatamente o total.
    alvo = int(total / ARREDONDA) * ARREDONDA
    if alvo >= ARREDONDA and abs(total - alvo) > 0.0001 and linhas:
        rotulo, valor = linhas[-1]
        linhas[-1] = (rotulo, round(valor + (alvo - total), 2))
        if valor >= 0:
            cheio = round(cheio + (alvo - total), 2)
        total = float(alvo)

    return {
        "paginas": paginas,
        "linhas": linhas,
        "valor_cheio": round(cheio, 2),
        "total": round(total, 2),
        "piso_aplicado": piso_aplicado,
    }


def brl(v):
    s = format(abs(v), ",.2f")
    s = s.replace(",", "#").replace(".", ",").replace("#", ".")
    return ("-R$ " if v < 0 else "R$ ") + s


def imprimir(r, hora_sua=None):
    print()
    print("  " + "-" * 58)
    for rotulo, valor in r["linhas"]:
        print("  %-40s %16s" % (rotulo, brl(valor)))
    print("  " + "-" * 58)
    if r["total"] != r["valor_cheio"]:
        print("  %-40s %16s" % ("Valor cheio", brl(r["valor_cheio"])))
    print("  %-40s %16s" % ("TOTAL", brl(r["total"])))
    print("  " + "-" * 58)
    if r["piso_aplicado"]:
        print("  aviso: caiu no piso de %s — confira se os dados de entrada" % brl(PISO))
        print("         estao certos, projeto assim pequeno quase nao existe")
    if hora_sua:
        print("  rende %s/h sobre %g h suas (piso: %s/h)"
              % (brl(r["total"] / hora_sua), hora_sua, brl(POR_PAGINA)))
    print()


def main():
    a = argparse.ArgumentParser(description="Valor de um projeto elétrico")
    a.add_argument("--paginas", type=int, help="se ja souber; senao use --io e --acionamentos")
    a.add_argument("--io", type=int, default=0, help="pontos de I/O somados")
    a.add_argument("--acionamentos", type=int, default=0, help="partidas, inversores, valvulas")
    a.add_argument("--seguranca", type=int, default=0, help="dispositivos de NR-12")
    a.add_argument("--escopo", default="A", choices=["A", "B", "a", "b"])
    a.add_argument("--itens-manuais", type=int, default=0,
                   help="pecas de marca pequena que nao estao no banco")
    a.add_argument("--setup-padrao", action="store_true", help="cliente impoe o padrao dele")
    a.add_argument("--urgencia", action="store_true")
    a.add_argument("--arquivo-fonte", action="store_true")
    a.add_argument("--abertura", action="store_true", help="primeiro projeto do cliente, -50%%")
    a.add_argument("--hora-sua", type=float, help="pra ver quanto rende por hora")
    a.add_argument("--json", action="store_true")
    o = a.parse_args()

    paginas = o.paginas or estimar_paginas(o.io, o.acionamentos, o.seguranca, o.escopo)
    r = calcular(paginas, o.itens_manuais, o.setup_padrao,
                 o.urgencia, o.arquivo_fonte, o.abertura)

    if o.json:
        print(json.dumps({k: v for k, v in r.items() if k != "linhas"}
                         | {"linhas": [[x, y] for x, y in r["linhas"]]},
                         ensure_ascii=False, indent=2))
    else:
        if not o.paginas:
            print("\n  páginas estimadas: %d  (I/O %d · acionamentos %d · segurança %d · escopo %s)"
                  % (paginas, o.io, o.acionamentos, o.seguranca, o.escopo.upper()))
        imprimir(r, o.hora_sua)


if __name__ == "__main__":
    main()
