"""
Faz o subset da fonte Inter e gera os @font-face em base64 para embutir no site.

O site tem que renderizar certo na maquina de qualquer cliente, sem depender de
CDN e sem depender da Inter estar instalada. Subset reduz de ~400 KB por peso
para algo em torno de 25 KB.

    python site/gerar-fontes.py

Saida: site/fontes.css  (colar dentro do <style> do index.html)
"""

import base64
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts")

PESOS = {
    "Inter-Regular.ttf": 400,
    "Inter-Medium.ttf": 500,
    "Inter-SemiBold.ttf": 600,
    "Inter-Bold.ttf": 700,
}

# Latim basico + acentuacao do portugues + pontuacao e simbolos usados no site
CARACTERES = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ"
    "áàâãäéèêëíìîïóòôõöúùûüçñ"
    " .,;:!?¿¡'\"“”‘’()[]{}/\\|-–—_+=*&%#@$€£°ºª<>«»•·…"
    "²³×÷±≈≤≥→←↑↓✓✕Ω"
)


def subset_base64(caminho):
    fonte = TTFont(caminho)
    opcoes = subset.Options()
    opcoes.layout_features = ["kern", "liga", "calt"]
    opcoes.desubroutinize = True
    opcoes.notdef_outline = False
    opcoes.recalc_bounds = True
    opcoes.drop_tables += ["DSIG"]

    subsetter = subset.Subsetter(options=opcoes)
    subsetter.populate(text=CARACTERES)
    subsetter.subset(fonte)

    fonte.flavor = "woff2"
    buffer = io.BytesIO()
    fonte.save(buffer)
    dados = buffer.getvalue()
    return base64.b64encode(dados).decode("ascii"), len(dados)


blocos = []
total = 0

for arquivo, peso in PESOS.items():
    caminho = os.path.join(FONTES, arquivo)
    if not os.path.exists(caminho):
        caminho = os.path.join(r"C:\Windows\Fonts", arquivo)
    if not os.path.exists(caminho):
        print(f"  nao encontrada: {arquivo}")
        continue

    b64, tamanho = subset_base64(caminho)
    total += tamanho
    print(f"  {arquivo:22} peso {peso}  ->  {tamanho/1024:6.1f} KB")

    blocos.append(
        "@font-face {\n"
        "  font-family: 'Inter';\n"
        f"  font-weight: {peso};\n"
        "  font-style: normal;\n"
        "  font-display: swap;\n"
        f"  src: url(data:font/woff2;base64,{b64}) format('woff2');\n"
        "}"
    )

css = "/* Inter (SIL Open Font License) — subset embutido, sem dependencia externa */\n" + "\n".join(blocos) + "\n"

destino = os.path.join(AQUI, "fontes.css")
with open(destino, "w", encoding="utf-8") as f:
    f.write(css)

print(f"\n  total embutido: {total/1024:.1f} KB")
print("  saida:", destino)
