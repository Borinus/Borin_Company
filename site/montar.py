"""
Monta o site: injeta as fontes embutidas no template e gera index.html.

    python site/gerar-fontes.py    # 1. faz o subset da Inter -> fontes.css
    python site/montar.py          # 2. injeta e gera index.html

O index.html resultante e autocontido: nao busca fonte, script nem imagem
de lugar nenhum. Da pra abrir por file:// ou subir em qualquer hospedagem.
"""

import os

AQUI = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(AQUI, "_pagina.html")
FONTES = os.path.join(AQUI, "fontes.css")
DESTINO = os.path.join(AQUI, "index.html")

MARCADOR = "/* FONTES */"

with open(TEMPLATE, encoding="utf-8") as f:
    pagina = f.read()

if os.path.exists(FONTES):
    with open(FONTES, encoding="utf-8") as f:
        css_fontes = f.read()
else:
    css_fontes = "/* fontes.css nao encontrado — rode gerar-fontes.py primeiro */"
    print("  aviso: fontes.css nao encontrado, o site vai cair na fonte do sistema")

if MARCADOR not in pagina:
    raise SystemExit(f"Marcador {MARCADOR} nao encontrado em _pagina.html")

pagina = pagina.replace(MARCADOR, css_fontes)

with open(DESTINO, "w", encoding="utf-8") as f:
    f.write(pagina)

tamanho = os.path.getsize(DESTINO) / 1024
print(f"  index.html gerado — {tamanho:.0f} KB")
print("  saida:", DESTINO)
