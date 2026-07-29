"""
Gera os PNGs do logo da Borin a partir das medidas do design-guide.md.

Rode de novo depois de instalar a fonte Inter (rsms.me/inter) — o script detecta
a Inter automaticamente e refaz os arquivos com a tipografia definitiva.

    python marca/gerar-logos.py

Saida: marca/png/
"""

import os
import glob
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- configuracao

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "png")

NOME = "BORIN"
DESCRITOR = "projetos elétricos industriais"
MONOGRAMA = "BRN"

TINTA = (17, 17, 17, 255)          # #111111
PAPEL = (255, 255, 255, 255)       # #FFFFFF
CINZA_600 = (107, 107, 107, 255)   # #6B6B6B
CINZA_300 = (220, 220, 220, 255)   # #DCDCDC
COMANDO = (193, 18, 31, 255)       # #C1121F

# proporcoes do design-guide (todas relativas a altura da letra B)
TRACK_NOME = 0.08        # em
TRACK_DESC = 0.12        # em
DESC_RATIO = 0.22        # corpo do descritor / corpo do nome
FIO_ESP = 0.08           # espessura do fio / altura de B
GAP_NO = 0.12            # intervalo fio -> no / altura de B
NO_TAM = 0.20            # lado do no / altura de B
GAP_NOME_FIO = 0.40      # nome -> fio / altura de B
GAP_FIO_DESC = 0.36      # fio -> descritor / altura de B

MARGEM = 6               # respiro em px para nao cortar antialiasing


def achar_fonte():
    """Prefere Inter Bold; cai para Arial Bold."""
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


def achar_fonte_media():
    """Peso intermediario para o descritor."""
    for raiz in (
        r"C:\Windows\Fonts",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
    ):
        for padrao in ("*nter*Medium*.ttf", "*nter*Regular*.ttf"):
            achados = glob.glob(os.path.join(raiz, padrao))
            if achados:
                return achados[0]
    return r"C:\Windows\Fonts\arial.ttf"


def largura_track(fonte, texto, track):
    """Largura do texto com espacamento entre letras aplicado."""
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
    esq, topo, dir_, base = fonte.getbbox("B")
    return base - topo


# ---------------------------------------------------------------- composicoes

def logo_completo(corpo_nome, cor_nome, cor_desc, cor_no, fundo=None):
    fonte_nome = ImageFont.truetype(CAMINHO_BOLD, corpo_nome)
    fonte_desc = ImageFont.truetype(CAMINHO_MEDIA, int(corpo_nome * DESC_RATIO))

    B = altura_caixa_alta(fonte_nome)
    track_nome = TRACK_NOME * corpo_nome
    track_desc = TRACK_DESC * int(corpo_nome * DESC_RATIO)

    larg_nome = largura_track(fonte_nome, NOME, track_nome)
    larg_desc = largura_track(fonte_desc, DESCRITOR, track_desc)

    esp_fio = max(1, round(FIO_ESP * B))
    lado_no = max(2, round(NO_TAM * B))
    gap_no = round(GAP_NO * B)
    larg_fio = max(1, round(larg_desc - lado_no - gap_no))

    alt_desc = altura_caixa_alta(fonte_desc)
    _, topo_desc, _, base_desc = fonte_desc.getbbox("pj")
    desc_desce = base_desc - alt_desc - topo_desc  # descida do "p" e do "j"

    y_nome_base = MARGEM + B
    y_fio_topo = y_nome_base + round(GAP_NOME_FIO * B)
    y_desc_base = y_fio_topo + esp_fio + round(GAP_FIO_DESC * B) + alt_desc

    larg = round(max(larg_nome, larg_desc)) + MARGEM * 2
    alt = round(y_desc_base + desc_desce) + MARGEM

    img = Image.new("RGBA", (larg, alt), fundo if fundo else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    desenha_track(d, (MARGEM, y_nome_base), NOME, fonte_nome, track_nome, cor_nome)

    y_no = y_fio_topo + esp_fio / 2 - lado_no / 2
    d.rectangle([MARGEM, y_fio_topo, MARGEM + larg_fio, y_fio_topo + esp_fio - 1], fill=cor_nome)
    x_no = MARGEM + larg_fio + gap_no
    d.rectangle([x_no, y_no, x_no + lado_no - 1, y_no + lado_no - 1], fill=cor_no)

    desenha_track(d, (MARGEM, y_desc_base), DESCRITOR, fonte_desc, track_desc, cor_desc)
    return img


def apenas_nome(texto, corpo, cor, fundo=None):
    fonte = ImageFont.truetype(CAMINHO_BOLD, corpo)
    track = TRACK_NOME * corpo
    B = altura_caixa_alta(fonte)
    larg = round(largura_track(fonte, texto, track)) + MARGEM * 2
    alt = round(B) + MARGEM * 2
    img = Image.new("RGBA", (larg, alt), fundo if fundo else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    desenha_track(d, (MARGEM, MARGEM + B), texto, fonte, track, cor)
    return img


# ---------------------------------------------------------------- execucao

CAMINHO_BOLD, TEM_INTER = achar_fonte()
CAMINHO_MEDIA = achar_fonte_media()

os.makedirs(SAIDA, exist_ok=True)

arquivos = {
    # lockup completo — capa de projeto, proposta, apresentacao
    "borin-completo.png":          logo_completo(400, TINTA, CINZA_600, TINTA),
    "borin-completo-branco.png":   logo_completo(400, PAPEL, CINZA_300, PAPEL),
    "borin-completo-comando.png":  logo_completo(400, TINTA, CINZA_600, COMANDO),

    # so o nome — carimbo de folha
    "borin-carimbo.png":           apenas_nome(NOME, 400, TINTA),
    "borin-carimbo-branco.png":    apenas_nome(NOME, 400, PAPEL),
    "borin-carimbo-fundo.png":     apenas_nome(NOME, 400, TINTA, fundo=PAPEL),
    "borin-carimbo-600px.png":     apenas_nome(NOME, 130, TINTA),

    # monograma — espaco muito curto, favicon
    "brn-monograma.png":           apenas_nome(MONOGRAMA, 400, TINTA),
    "brn-monograma-branco.png":    apenas_nome(MONOGRAMA, 400, PAPEL),
}

for nome, img in arquivos.items():
    caminho = os.path.join(SAIDA, nome)
    img.save(caminho, "PNG", dpi=(300, 300))
    print(f"{nome:32} {img.width:5} x {img.height:4} px")

print()
print("Fonte usada:", os.path.basename(CAMINHO_BOLD), "(Inter)" if TEM_INTER else "(Arial — instale a Inter e rode de novo)")
print("Saida:", SAIDA)
