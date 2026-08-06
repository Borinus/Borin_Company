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
PASTA = os.path.join(AQUI, "propostas")

_s = importlib.util.spec_from_file_location("calc", os.path.join(AQUI, "calcular.py"))
calc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(calc)

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


# O fio acompanha a largura do NOME, não a do descritor — regra revisada no
# design-guide em 05/08/2026. Em CSS isso sai de graça: o bloco da marca é
# inline-block (encolhe até o texto) e o fio é flex dentro dele. Assim o fio
# nunca sobra pra fora do N, mesmo se a fonte do sistema mudar de métrica.
CSS = """
/* Tudo aqui está calibrado pra proposta caber em UMA folha, inclusive no caso
   maior (Escopo B, 51 páginas, com desconto de abertura). Proposta que vira
   duas folhas chega grampeada, e a segunda folha é onde moram as condições de
   pagamento — a parte que o cliente precisa ler. Ao mexer em corpo, entrelinha
   ou espaçamento, rodar `python comercial/testar-proposta.py`, que falha se
   passar de uma página. */
@page { size: A4; margin: 13mm 14mm 9mm; }
body { font: 9.5pt/1.42 'Segoe UI', Arial, sans-serif; color: #111; margin: 0; }

.marcabloco { display: inline-block; }
.marca { font-size: 19pt; font-weight: 700; letter-spacing: .16em; line-height: 1; }
.fio { display: flex; align-items: center; gap: 4px; margin-top: 5pt; }
.fio .regua { flex: 1; height: 2.4px; background: #111; }
.fio .no { width: 6px; height: 6px; background: #111; }
.sub { font-family: Consolas, monospace; font-size: 7.5pt; letter-spacing: .12em;
       text-transform: uppercase; color: #6B6B6B; margin-top: 4pt; }
.topo { border-bottom: 1px solid #111; padding-bottom: 7pt; margin-bottom: 9pt; }

.rotulo { font-family: Consolas, monospace; font-size: 7.5pt; letter-spacing: .12em;
          text-transform: uppercase; color: #6B6B6B; }
h1 { font-size: 17pt; font-weight: 700; letter-spacing: -.02em; margin: 4pt 0 2pt;
     line-height: 1.18; }
.cliente { font-size: 10pt; color: #6B6B6B; margin-bottom: 9pt; }

.chapeu { display: flex; gap: 22pt; margin: 0 0 11pt; }
.chapeu .cel .v { font-size: 10pt; margin-top: 1pt; }

.secao { font-family: Consolas, monospace; font-size: 7.5pt; letter-spacing: .12em;
         text-transform: uppercase; color: #6B6B6B; border-bottom: 1px solid #111;
         padding-bottom: 3.5pt; margin: 0 0 5pt; page-break-after: avoid; }
.bloco { margin-bottom: 6pt; page-break-inside: avoid; }

/* Duas colunas: são itens curtos, e em coluna única viravam uma lista magra de
   dez linhas que sozinha empurrava as condições de pagamento pra folha 2. */
ul.inclui { margin: 0; padding: 0; list-style: none; columns: 2; column-gap: 20pt; }
ul.inclui li { font-size: 9pt; color: #444; padding: 1.5pt 0;
               border-bottom: 1px solid #F0F0F0; break-inside: avoid; }

table.val { width: 100%; border-collapse: collapse; }
table.val td { padding: 2.9pt 0; border-bottom: 1px solid #DCDCDC; font-size: 10pt;
               vertical-align: top; }
table.val td.r { text-align: right; white-space: nowrap; }
table.val td.rot { color: #6B6B6B; }
table.val tr.cheio td { color: #6B6B6B; text-decoration: line-through; }
table.val tr.total td { border-bottom: 0; padding-top: 8pt; font-weight: 700; }
table.val tr.total td.r { font-size: 18pt; letter-spacing: -.02em; }

.obs { font-size: 8.5pt; color: #6B6B6B; margin-top: 6pt; }
.passo { border: 1px solid #111; padding: 8pt 10pt; margin-top: 2pt;
         page-break-inside: avoid; }
.passo .t { font-weight: 600; font-size: 10.5pt; margin-bottom: 3pt; }
.passo .d { font-size: 9pt; color: #444; }
.passo .link { font-family: Consolas, monospace; font-size: 9.5pt; margin-top: 6pt; }
.pe { border-top: 1px solid #DCDCDC; margin-top: 6pt; padding-top: 5pt;
      font-family: Consolas, monospace; font-size: 7pt; color: #6B6B6B; line-height: 1.65; }
"""

CABECA = """<div class="topo">
  <div class="marcabloco">
    <div class="marca">BORIN</div>
    <div class="fio"><span class="regua"></span><span class="no"></span></div>
  </div>
  <div class="sub">projetos elétricos industriais</div>
</div>"""


def documento(p):
    """Monta o HTML de impressão a partir do mesmo dicionário do orcamento.py."""
    chapeu = "".join(
        '<div class="cel"><div class="rotulo">%s</div><div class="v">%s</div></div>'
        % (esc(r), esc(v))
        for r, v in [("Escopo", p["escopo_txt"]),
                     ("Páginas estimadas", str(p["paginas"])),
                     ("Prazo", p["prazo"]),
                     ("Validade", "3 dias")])

    inclui = "".join("<li>%s</li>" % esc(x) for x in p["entrega"])

    # o desconto vem DEPOIS do valor cheio: "-50%" antes do número que ele
    # desconta não se lê. Mesma ordem do email, de propósito.
    somas = [(r, v) for r, v in p["linhas"] if v >= 0]
    abates = [(r, v) for r, v in p["linhas"] if v < 0]
    linhas = "".join('<tr><td class="rot">%s</td><td class="r">%s</td></tr>'
                     % (esc(r), calc.brl(v)) for r, v in somas)
    if abates:
        linhas += ('<tr class="cheio"><td class="rot">Valor cheio</td>'
                   '<td class="r">%s</td></tr>' % calc.brl(p["valor_cheio"]))
        linhas += "".join('<tr><td class="rot">%s</td><td class="r">%s</td></tr>'
                          % (esc(r), calc.brl(v)) for r, v in abates)
    linhas += ('<tr class="total"><td>Total</td><td class="r">%s</td></tr>'
               % calc.brl(p["total"]))

    cond = "".join('<tr><td class="rot">%s</td><td class="r">%s</td></tr>'
                   % (esc(r), esc(v)) for r, v in p["condicoes"])

    obs = ('<div class="obs">A condição de início vale uma vez por cliente. Você não me '
           'conhece, e eu preciso do primeiro projeto pra mostrar o padrão.</div>'
           ) if p.get("abertura") else ""

    # A linha de suporte veio pra cá junto com as outras condições, por
    # p["condicoes"] (orcamento.py). Ela morava só aqui e o email saía sem —
    # dois documentos da mesma mensagem com condições diferentes.

    return """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<title>Proposta %(num)s</title><style>%(css)s</style>
%(cabeca)s
<div class="rotulo">Proposta %(num)s</div>
<h1>%(equip)s</h1>
<div class="cliente">%(empresa)s%(contato)s</div>

<div class="chapeu">%(chapeu)s</div>

<div class="bloco">
  <div class="secao">O que está incluso</div>
  <ul class="inclui">%(inclui)s</ul>
</div>

<div class="bloco">
  <div class="secao">Valor</div>
  <table class="val">%(linhas)s</table>
  %(obs)s
</div>

<div class="bloco">
  <div class="secao">Condições</div>
  <table class="val">%(cond)s</table>
</div>

<div class="bloco">
  <div class="secao">Próximo passo</div>
  <div class="passo">
    <div class="t">Preencher os dados e gerar o contrato</div>
    <div class="d">São nove campos: dados da empresa e quem assina. Devolvo o contrato
    preenchido, faltando só a assinatura. Se preferir, responda o email desta proposta.</div>
    <div class="link">borinprojetos.com.br/cadastro</div>
  </div>
</div>

<div class="pe">
  Borin Projetos Elétricos &middot; 65.749.097 MATEUS BORIN &middot; CNPJ 65.749.097/0001-85<br>
  Caxias do Sul / RS &middot; contato@borinprojetos.com.br &middot; borinprojetos.com.br
</div>
</html>""" % {
        "css": CSS, "cabeca": CABECA, "num": esc(p["numero"]),
        "equip": esc(p["equipamento"]), "empresa": esc(p["empresa"]),
        "contato": (" &middot; " + esc(p["contato"])) if p.get("contato") else "",
        "chapeu": chapeu, "inclui": inclui, "linhas": linhas, "cond": cond, "obs": obs,
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
