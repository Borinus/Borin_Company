# -*- coding: utf-8 -*-
"""A marca nos PDFs — um cabeçalho e um carimbo, usados por proposta e contrato.

POR QUE EXISTE (11/08/2026): proposta.py e contrato.py tinham cada um a SUA
cópia do cabeçalho, e elas já divergiam (letter-spacing 3px num, .16em no
outro; nó preto num, vermelho no outro). O comentário do próprio proposta.py
avisa: proposta e contrato chegam na mesma caixa, e se divergirem parecem duas
empresas. Agora a marca mora aqui e os dois importam.

TUDO AQUI SAI DO marca/design-guide.md. Ao mexer, ler as seções Logo,
O carimbo, Cores e Tipografia — e rodar `python comercial/testar-proposta.py`.
"""

# ---------------------------------------------------- cores (seção Cores)
TINTA = "#111111"
PAPEL = "#FFFFFF"
CINZA100 = "#F4F4F4"
CINZA300 = "#DCDCDC"
CINZA600 = "#6B6B6B"
COMANDO = "#C1121F"          # o vermelho do 24VCC — único acento

# ------------------------------------------------- fontes (seção Tipografia)
SANS = "'Inter', Arial, Helvetica, sans-serif"
MONO = "'JetBrains Mono', Consolas, monospace"

# ------------------------------------------------------- logo (seção Logo)
# Construção relativa à altura da letra B, na régua do gerar-logos.py:
#   nome Inter 700 caixa alta ls +0.08em · fio 0,08 B · nó 0,2 B (Comando)
#   intervalo fio→nó 0,12 B · nome→fio 0,4 B · fio→descritor 0,36 B
#   descritor Inter 500 minúsculas, corpo 0,22 do corpo do nome,
#   ls calculado ≈ +0.068em — os TRÊS elementos com a MESMA largura
#   (revisão de 05/08/2026 do guia).
# O corpo de 20pt respeita o tamanho mínimo do logo: 24mm de largura em
# impresso (BORIN a 20pt ≈ 24,5mm).
_PT = 20.0                    # corpo do nome
_B = _PT * 0.73 * 96 / 72     # altura da letra B em px (cap height da Inter)

CSS_MARCA = """
.marcabloco { display: inline-block; }
.marca { font-family: %(sans)s; font-size: %(pt)gpt; font-weight: 700;
         letter-spacing: .08em; line-height: 1; color: %(tinta)s; }
.fio { display: flex; align-items: center; gap: %(gapno).1fpx; margin-top: %(nomefio).1fpx; }
.fio .regua { flex: 1; height: %(esp).1fpx; background: %(tinta)s; }
.fio .no { width: %(no).1fpx; height: %(no).1fpx; background: %(comando)s; flex: none; }
.descritor { font-family: %(sans)s; font-size: %(desc).2fpt; font-weight: 500;
             letter-spacing: .068em; color: %(tinta)s; margin-top: %(fiodesc).1fpx; }
.topo { border-bottom: 1px solid %(c300)s; padding-bottom: 6pt; margin-bottom: 8pt; }
""" % {
    "sans": SANS, "tinta": TINTA, "comando": COMANDO, "c300": CINZA300,
    "pt": _PT,
    "esp": _B * 0.08,
    "no": _B * 0.2,
    "gapno": _B * 0.12,
    "nomefio": _B * 0.40,
    "fiodesc": _B * 0.36,
    "desc": _PT * 0.22,
}

CABECA = """<div class="topo">
  <div class="marcabloco">
    <div class="marca">BORIN</div>
    <div class="fio"><span class="regua"></span><span class="no"></span></div>
    <div class="descritor">projetos el&eacute;tricos industriais</div>
  </div>
</div>"""

# -------------------------------------------------- carimbo (seção O carimbo)
# Moldura 1px Tinta, divisórias 1px Cinza 300, rótulo mono 7pt caixa alta
# ls +0.1em Cinza 600, valor mono 9pt Tinta, canto reto, BRN de largura fixa.
CSS_CARIMBO = """
/* geometria FIXA, como num carimbo de folha de verdade: valor comprido e
   cortado com reticencias, a altura nunca cresce — nome de cliente gigante
   nao pode empurrar a proposta pra folha 2 */
table.carimbo { width: 100%%; border-collapse: collapse; border: 1px solid %(tinta)s;
                table-layout: fixed; page-break-inside: avoid; }
table.carimbo td { border-left: 1px solid %(c300)s; padding: 2.5pt 6pt 3pt;
                   vertical-align: middle; overflow: hidden; }
table.carimbo td:first-child { border-left: 0; }
/* larguras do layout da proposta: BRN | DOCUMENTO | CLIENTE | REV | DATA */
table.carimbo td:nth-child(2) { width: 32%%; }
table.carimbo td:nth-child(4) { width: 42pt; }
table.carimbo td:nth-child(5) { width: 70pt; }
table.carimbo td.brn { width: 34pt; font-family: %(sans)s; font-weight: 700;
                       font-size: 11pt; letter-spacing: .08em; text-align: center;
                       color: %(tinta)s; }
table.carimbo .rot { font-family: %(mono)s; font-size: 7pt; letter-spacing: .1em;
                     text-transform: uppercase; color: %(c600)s; }
table.carimbo .val { font-family: %(mono)s; font-size: 9pt; color: %(tinta)s;
                     margin-top: 1.5pt; white-space: nowrap; overflow: hidden;
                     text-overflow: ellipsis; }
.legal { font-family: %(mono)s; font-size: 7pt; color: %(c600)s; margin-top: 3pt;
         line-height: 1.5; }
""" % {"tinta": TINTA, "c300": CINZA300, "c600": CINZA600,
       "sans": SANS, "mono": MONO}

LEGAL = ("Borin Projetos El&eacute;tricos &middot; 65.749.097 MATEUS BORIN &middot; "
         "CNPJ 65.749.097/0001-85 &middot; Caxias do Sul / RS &middot; "
         "contato@borinprojetos.com.br &middot; borinprojetos.com.br")


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def carimbo(campos, legal=True):
    """O carimbo de folha, largura total. `campos` é [(rótulo, valor)].

    Campo sem valor SAI — regra do guia: nunca vazio, nunca travessão."""
    cels = "".join(
        '<td><div class="rot">%s</div><div class="val">%s</div></td>'
        % (esc(r), esc(v))
        for r, v in campos if str(v or "").strip())
    h = '<table class="carimbo"><tr><td class="brn">BRN</td>%s</tr></table>' % cels
    if legal:
        h += '<div class="legal">%s</div>' % LEGAL
    return h
