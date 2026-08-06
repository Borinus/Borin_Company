# -*- coding: utf-8 -*-
"""Gera o marcador de 'logo do cliente aqui' pro projeto base.

PRA QUE SERVE

No projeto base (o arquivo que voce copia pra comecar cada trabalho), o espaco
do logo do cliente nao pode ficar vazio: espaco vazio some, ninguem lembra de
preencher e o projeto sai sem a marca de quem contratou. Um marcador cinza no
lugar faz o contrario — ele incomoda ate ser trocado.

Fundo transparente de proposito, pra cair sobre folha branca, sobre carimbo
cinza ou sobre a capa escura sem recorte esquisito em volta.

Cinza 600 (#6B6B6B) e a cor de texto secundario do design-guide. E claro o
bastante pra ninguem confundir com conteudo do projeto e escuro o bastante pra
aparecer na impressao — que e a unica hora em que alguem percebe o esquecimento.

Roda com:  python marca/gerar-placeholder.py
"""

import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "png")

CINZA_600 = (0x6B, 0x6B, 0x6B, 255)
CINZA_300 = (0xDC, 0xDC, 0xDC, 255)

TEXTO = "SUA LOGO AQUI"
TRACK = 0.08          # letter-spacing do nome, igual ao design-guide
ESCALA = 4            # desenha grande e reduz: borda limpa na impressao


def achar_fonte():
    """Prefere Inter Bold; cai para Arial Bold. Mesma regra do gerar-logos.py."""
    candidatos = []
    for raiz in (
        r"C:\Windows\Fonts",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
    ):
        candidatos += glob.glob(os.path.join(raiz, "*nter*Bold*.ttf"))
        candidatos += glob.glob(os.path.join(raiz, "Inter*.ttc"))
    if candidatos:
        candidatos.sort(key=lambda p: ("18pt" not in p, len(p)))
        return candidatos[0], True
    for p in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\Arial Bold.ttf"):
        if os.path.exists(p):
            return p, False
    raise SystemExit("Nenhuma fonte encontrada. Instale a Inter ou a Arial.")


def largura_track(fonte, texto, track):
    total = 0
    for c in texto:
        total += fonte.getlength(c) + track
    return total - track if texto else 0


def desenha_track(draw, xy, texto, fonte, track, cor):
    x, y = xy
    for c in texto:
        draw.text((x, y), c, font=fonte, fill=cor, anchor="ls")
        x += fonte.getlength(c) + track


def altura_caixa_alta(fonte):
    _, topo, _, base = fonte.getbbox("B")
    return base - topo


def gerar(nome, larg_final, alt_final, corpo_rel=0.16, com_borda=True):
    """Desenha o marcador centralizado numa moldura tracejada.

    corpo_rel = tamanho da letra em fracao da ALTURA. Fixar pela altura, e nao
    pela largura, e o que mantem o texto do mesmo tamanho visual entre o formato
    largo (carimbo) e o quadrado (capa).
    """
    L, A = larg_final * ESCALA, alt_final * ESCALA
    img = Image.new("RGBA", (L, A), (0, 0, 0, 0))   # transparente
    d = ImageDraw.Draw(img)

    corpo = max(8, int(A * corpo_rel))
    fonte = ImageFont.truetype(CAMINHO, corpo)
    track = corpo * TRACK

    # o texto encolhe ate caber com folga, em vez de estourar a moldura
    folga = L * 0.80
    while largura_track(fonte, TEXTO, track) > folga and corpo > 8:
        corpo -= 2
        fonte = ImageFont.truetype(CAMINHO, corpo)
        track = corpo * TRACK

    if com_borda:
        # moldura tracejada: le como "lugar reservado", nao como desenho
        passo, traco, esp = 14 * ESCALA, 9 * ESCALA, 2 * ESCALA
        # a moldura recua o suficiente pra sobrar pixel limpo depois do LANCZOS.
        # Com recuo curto, o filtro espalha tinta ate a linha 0 e a moldura
        # aparece cortada justamente na borda, que e onde o olho repara.
        m = esp * 4
        for x in range(m, L - m, passo):
            d.line([(x, m), (min(x + traco, L - m), m)], fill=CINZA_300, width=esp)
            d.line([(x, A - m), (min(x + traco, L - m), A - m)], fill=CINZA_300, width=esp)
        for y in range(m, A - m, passo):
            d.line([(m, y), (m, min(y + traco, A - m))], fill=CINZA_300, width=esp)
            d.line([(L - m, y), (L - m, min(y + traco, A - m))], fill=CINZA_300, width=esp)

    larg_txt = largura_track(fonte, TEXTO, track)
    B = altura_caixa_alta(fonte)
    desenha_track(d, ((L - larg_txt) / 2, (A + B) / 2), TEXTO, fonte, track, CINZA_600)

    img = img.resize((larg_final, alt_final), Image.LANCZOS)
    destino = os.path.join(SAIDA, nome)
    img.save(destino)
    print("  %-38s %4d x %-4d px" % (nome, larg_final, alt_final))
    return destino


CAMINHO, TEM_INTER = achar_fonte()
os.makedirs(SAIDA, exist_ok=True)

print()
print("  marcador de logo do cliente — fundo transparente, Cinza 600")
print()
gerar("placeholder-logo-cliente.png", 1200, 400)              # 3:1, carimbo
gerar("placeholder-logo-cliente-largo.png", 1600, 320)        # 5:1, faixa
gerar("placeholder-logo-cliente-quadrado.png", 800, 800, 0.10)
gerar("placeholder-logo-cliente-sem-borda.png", 1200, 400, 0.16, com_borda=False)
print()
print("  fonte:", os.path.basename(CAMINHO),
      "(Inter)" if TEM_INTER else "(Arial — instale a Inter e rode de novo)")
print()
