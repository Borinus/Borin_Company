# -*- coding: utf-8 -*-
"""Gera a proposta em PDF, com a identidade aplicada.

    python comercial/proposta.py --de exemplo

POR QUE EXISTE: até 05/08/2026 a proposta só existia como HTML de email. Isso
resolve o caso comum — o cliente abre e lê sem baixar nada — e falha nos dois
casos que fecham negócio:

  - o contato repassa a proposta pro chefe ou pro comprador. Email encaminhado
    chega desmontado, e o que era um documento vira um bloco de texto
  - alguém imprime pra levar pra reunião. O HTML de email imprime mal por
    construção: ele é tabela dentro de tabela com largura fixa de 640 px

O contrato já saía em PDF desde o começo. A proposta é o documento que o cliente
vê ANTES de decidir — era o que não podia estar sem.

Mesmo motor do contrato.py (HTML impresso pelo Chrome) e mesmo cabeçalho de
marca, de propósito: proposta e contrato chegam na mesma caixa, e se
divergirem parecem duas empresas.
"""

import argparse
import importlib.util
import io
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.join(RAIZ, "comercial")
# mesma chave do orcamento.py: teste escreve longe da pasta real
PASTA = os.environ.get("BORIN_PROPOSTAS") or os.path.join(AQUI, "propostas")

_s = importlib.util.spec_from_file_location("calc", os.path.join(AQUI, "calcular.py"))
calc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(calc)

# a marca (cabeçalho + carimbo) mora num módulo só, compartilhado com o
# contrato — ver o porquê em identidade.py
_i = importlib.util.spec_from_file_location("ident", os.path.join(AQUI, "identidade.py"))
ident = importlib.util.module_from_spec(_i)
_i.loader.exec_module(ident)

CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
           shutil.which("chrome") or ""]


def chrome():
    for c in CHROMES:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chrome nao encontrado — e ele que imprime o PDF.")


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# O cabeçalho de marca e o carimbo vêm de identidade.py — o mesmo do contrato.
# O fio acompanha a largura do NOME (regra dos três elementos, 05/08/2026): o
# bloco é inline-block e o fio é flex dentro dele, então nunca sobra do N.
CSS = """
/* Tudo aqui está calibrado pra proposta caber em UMA folha, inclusive no caso
   maior (Escopo B, 51 páginas, com desconto de abertura). Proposta que vira
   duas folhas chega grampeada, e a segunda folha é onde moram as condições de
   pagamento — a parte que o cliente precisa ler. Ao mexer em corpo, entrelinha
   ou espaçamento, rodar `python comercial/testar-proposta.py`, que falha se
   passar de uma página.

   Escala tipográfica (guia: no máximo três tamanhos por página):
   7.5pt rótulo/mono · 9.5pt corpo · 17pt título e total — mais os 7/9pt que a
   seção "O carimbo" do guia fixa pro rodapé.

   Margens: 25mm de lateral, como o guia pede. Coube com a folga vinda de dois
   lugares: espaçamentos apertados (respiro, nunca corpo de letra) e o carimbo
   de geometria fixa, que não cresce com nome comprido. */
@page { size: A4; margin: 13mm 25mm 10mm; }
body { font: 9.5pt/1.42 'Inter', Arial, Helvetica, sans-serif; color: #111111;
       margin: 0; }

.rotulo { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 7.5pt;
          letter-spacing: .12em; text-transform: uppercase; color: #6B6B6B; }
h1 { font-size: 17pt; font-weight: 700; letter-spacing: -.02em; margin: 3pt 0 1pt;
     line-height: 1.18; }
.cliente { font-size: 9.5pt; color: #6B6B6B; margin-bottom: 6pt; }

.chapeu { display: flex; gap: 20pt; margin: 0 0 8pt; }
.chapeu .cel .v { font-size: 9.5pt; margin-top: 1pt; white-space: nowrap; }

.secao { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 7.5pt;
         letter-spacing: .12em; text-transform: uppercase; color: #6B6B6B;
         border-bottom: 1px solid #DCDCDC; padding-bottom: 3.5pt; margin: 0 0 5pt;
         page-break-after: avoid; }
.bloco { margin-bottom: 4pt; page-break-inside: avoid; }

/* Duas colunas: são itens curtos, e em coluna única viravam uma lista magra de
   dez linhas que sozinha empurrava as condições de pagamento pra folha 2. */
ul.inclui { margin: 0; padding: 0; list-style: none; columns: 2; column-gap: 18pt; }
ul.inclui li { font-size: 9.5pt; color: #111111; padding: 1pt 0;
               border-bottom: 1px solid #F4F4F4; break-inside: avoid; }

table.val { width: 100%; border-collapse: collapse; }
table.val td { padding: 2.3pt 0; border-bottom: 1px solid #DCDCDC; font-size: 9.5pt;
               vertical-align: top; }
table.val td.r { text-align: right; white-space: nowrap; }
table.val td.rot { color: #6B6B6B; }
table.val tr.cheio td { color: #6B6B6B; text-decoration: line-through; }
table.val tr.total td { border-bottom: 0; padding-top: 6pt; font-weight: 700; }
table.val tr.total td.r { font-size: 17pt; letter-spacing: -.02em; }

.obs { font-size: 7.5pt; color: #6B6B6B; margin-top: 3pt; line-height: 1.45; }
.passo { border: 1px solid #DCDCDC; padding: 6pt 8pt; margin-top: 2pt;
         page-break-inside: avoid; }
.passo .t { font-weight: 600; font-size: 9.5pt; margin-bottom: 2pt; }
.passo .d { font-size: 9.5pt; color: #6B6B6B; }
.passo .link { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 9pt;
               margin-top: 5pt; }
.rodape { margin-top: 6pt; }
""" + ident.CSS_MARCA + ident.CSS_CARIMBO


def documento(p):
    """Monta o HTML de impressão a partir do mesmo dicionário do orcamento.py."""
    chapeu = "".join(
        '<div class="cel"><div class="rotulo">%s</div><div class="v">%s</div></div>'
        % (esc(r), esc(v))
        for r, v in [("Escopo", p["escopo_txt"]),
                     ("Páginas estimadas", str(p["paginas"])),
                     ("Prazo", p["prazo"]),
                     ("Validade", p.get("validade", ""))])

    inclui = "".join("<li>%s</li>" % esc(x) for x in p["entrega"])
    # a linha de normas é argumento de venda (modelo-proposta.md) — o rigor de
    # documentação é o que diferencia; o PDF tinha perdido isso
    normas = ('<div class="obs">Projeto desenvolvido em CAD elétrico, conforme '
              'IEC 81346, IEC 61082, NFPA 79 e IEC 60204-1.</div>')

    # o desconto vem DEPOIS do valor cheio: "-50%" antes do número que ele
    # desconta não se lê. Mesma ordem do email, de propósito.
    somas = [(r, v) for r, v in p["linhas"] if v >= 0]
    abates = [(r, v) for r, v in p["linhas"] if v < 0]
    linhas = "".join('<tr><td class="rot">%s</td><td class="r">%s</td></tr>'
                     % (esc(r), calc.brl(v)) for r, v in somas)
    if abates:
        # com UMA soma só, a linha riscada repetia o mesmo número da linha de
        # cima (R$ 7.500 duas vezes) — o "cheio" só informa quando é uma SOMA
        if len(somas) >= 2:
            linhas += ('<tr class="cheio"><td class="rot">Valor cheio</td>'
                       '<td class="r">%s</td></tr>' % calc.brl(p["valor_cheio"]))
        linhas += "".join('<tr><td class="rot">%s</td><td class="r">%s</td></tr>'
                          % (esc(r), calc.brl(v)) for r, v in abates)
    linhas += ('<tr class="total"><td>Total</td><td class="r">%s</td></tr>'
               % calc.brl(p["total"]))

    # protege o escopo: sem esta linha, "projeto elétrico" parece incluir ART,
    # programação e obra — e a conversa difícil fica pra depois do aceite
    nao_incluso = ('<div class="obs">Não inclusos: responsabilidade técnica (ART), '
                   'programação de CLP, IHM ou supervisório, montagem e comissionamento, '
                   'compra ou intermediação de material, arquivo-fonte do CAD e '
                   'acompanhamento em obra.</div>')

    cond = "".join('<tr><td class="rot">%s</td><td class="r">%s</td></tr>'
                   % (esc(r), esc(v)) for r, v in p["condicoes"])

    obs = ('<div class="obs">A condição de início vale uma vez por cliente. Você não me '
           'conhece, e eu preciso do primeiro projeto pra mostrar o padrão.</div>'
           ) if p.get("abertura") else ""

    # A linha de suporte veio pra cá junto com as outras condições, por
    # p["condicoes"] (orcamento.py). Ela morava só aqui e o email saía sem —
    # dois documentos da mesma mensagem com condições diferentes.

    # Negócio conduzido na mão (--direto, ex.: proposta que vai por WhatsApp)
    # não passa pelo /cadastro — mas precisa de UMA instrução de aceite, senão
    # a proposta termina sem dizer o que fazer pra fechar.
    if p.get("direto"):
        passo = """
<div class="bloco">
  <div class="secao">Para fechar</div>
  <div class="passo">
    <div class="d">Responda esta mensagem que eu devolvo o contrato preenchido
    no mesmo dia, faltando só a assinatura.</div>
  </div>
</div>"""
    else:
        passo = """
<div class="bloco">
  <div class="secao">Próximo passo</div>
  <div class="passo">
    <div class="t">Preencher os dados e gerar o contrato</div>
    <div class="d">São nove campos: dados da empresa e quem assina. Devolvo o contrato
    preenchido, faltando só a assinatura. Se preferir, responda o email desta proposta.</div>
    <div class="link">borinprojetos.com.br/cadastro</div>
  </div>
</div>"""

    # o carimbo de folha — a assinatura estrutural da marca ("peça sem carimbo"
    # está na lista do que nunca fazer). Campo sem valor sai sozinho.
    carimbo = ident.carimbo([
        ("Documento", "Proposta " + p["numero"]),
        ("Cliente", p["empresa"] or p["contato"]),
        ("Rev", "00"),
        ("Data", p.get("data_curta", "")),
    ])

    return """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Proposta %(num)s</title>
<style>%(css)s</style>
</head>
<body>
%(cabeca)s
<div class="rotulo">Proposta %(num)s</div>
<h1>%(equip)s</h1>
<div class="cliente">%(empresa)s%(contato)s</div>

<div class="chapeu">%(chapeu)s</div>

<div class="bloco">
  <div class="secao">O que está incluso</div>
  <ul class="inclui">%(inclui)s</ul>
  %(normas)s
</div>

<div class="bloco">
  <div class="secao">Valor</div>
  <table class="val">%(linhas)s</table>
  %(nao_incluso)s
  %(obs)s
</div>

<div class="bloco">
  <div class="secao">Condições</div>
  <table class="val">%(cond)s</table>
</div>
%(passo)s
<div class="rodape">%(carimbo)s</div>
</body>
</html>""" % {
        "css": CSS, "cabeca": ident.CABECA, "num": esc(p["numero"]),
        "equip": esc(p["equipamento"]), "empresa": esc(p["empresa"]),
        "contato": (" &middot; " + esc(p["contato"])) if p.get("contato") else "",
        "chapeu": chapeu, "inclui": inclui, "normas": normas, "linhas": linhas,
        "nao_incluso": nao_incluso, "cond": cond, "obs": obs, "passo": passo,
        "carimbo": carimbo,
    }


def gerar(p, saida=None):
    """Escreve o PDF e devolve o caminho. Levanta se o Chrome não produzir nada.

    Falhar aqui tem que ser barulhento: um `return None` calado faria o
    orcamento.py mandar a proposta SEM o anexo, e ninguém repara na ausência de
    um arquivo que deveria estar lá.
    """
    doc = documento(p)
    os.makedirs(PASTA, exist_ok=True)
    nome = saida or os.path.join(
        PASTA, "Proposta %s - %s" % (p["numero"], (p["empresa"] or "cliente")[:40]))
    io.open(nome + ".html", "w", encoding="utf-8").write(doc)

    # Chrome nao aceita acento no caminho de --print-to-pdf de forma confiavel
    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "borin-proposta")
    io.open(tmp + ".html", "w", encoding="utf-8").write(doc)
    if os.path.exists(tmp + ".pdf"):
        os.remove(tmp + ".pdf")          # senao um PDF velho passa por novo
    subprocess.run([chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + tmp + ".pdf", "--virtual-time-budget=6000",
                    "file:///" + tmp.replace("\\", "/") + ".html"],
                   capture_output=True, timeout=120)
    if not os.path.exists(tmp + ".pdf"):
        raise SystemExit("Chrome nao gerou o PDF da proposta")
    shutil.copy2(tmp + ".pdf", nome + ".pdf")
    os.remove(tmp + ".pdf")
    os.remove(tmp + ".html")
    return nome + ".pdf"


def main():
    ap = argparse.ArgumentParser(description="Gera a proposta em PDF.")
    ap.add_argument("--de", help="'exemplo' monta um pedido de teste")
    o = ap.parse_args()

    if o.de != "exemplo":
        raise SystemExit("Use --de exemplo, ou importe gerar(p) do orcamento.py.")

    _o = importlib.util.spec_from_file_location("orc", os.path.join(AQUI, "orcamento.py"))
    orc = importlib.util.module_from_spec(_o)
    _o.loader.exec_module(orc)

    # mesmo EXEMPLO do orcamento.py, pra proposta impressa e email de teste
    # saírem do mesmo pedido — se divergirem, comparar os dois não prova nada
    class Pedido(object):
        pass
    ped = Pedido()
    for k, v in dict(numero=None, paginas=None, io=0, acionamentos=0, seguranca=0,
                     escopo="A", itens_manuais=0, setup_padrao=False, urgencia=False,
                     arquivo_fonte=False, abertura=False, empresa="", contato="",
                     equipamento="Projeto elétrico", codigo="", email="").items():
        setattr(ped, k, v)
    for k, v in orc.EXEMPLO.items():
        setattr(ped, k, v)

    print("  " + gerar(orc.montar(ped)))


if __name__ == "__main__":
    main()
