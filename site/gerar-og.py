"""
Gera a imagem de compartilhamento (og.png, 1200x630).

E o cartao que aparece quando o link do site e colado no WhatsApp, LinkedIn ou
email. Sem ela o link vira texto cru — e o canal de prospeccao e justamente o
WhatsApp.

    python site/gerar-og.py

Fotografa _og.html com o Chrome em modo headless. Roda so quando a marca ou os
prazos mudarem; o png fica versionado em site/og.png e o publicar.py so copia.
"""

import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "_og.html")
MONTADO = os.path.join(AQUI, "_og-montado.html")
SAIDA = os.path.join(AQUI, "og.png")

CHROMES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    shutil.which("chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("google-chrome") or "",
]


def achar_chrome():
    for c in CHROMES:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chrome nao encontrado — instale ou ajuste CHROMES em gerar-og.py")


# injeta a fonte embutida, igual o montar.py faz nas paginas
with open(FONTE, encoding="utf-8") as f:
    pagina = f.read()

fontes = os.path.join(AQUI, "fontes.css")
if os.path.exists(fontes):
    with open(fontes, encoding="utf-8") as f:
        pagina = pagina.replace("/* FONTES */", f.read())

with open(MONTADO, "w", encoding="utf-8") as f:
    f.write("<!doctype html>\n<html lang=\"pt-BR\">\n" + pagina)

subprocess.run([
    achar_chrome(),
    "--headless", "--disable-gpu", "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--window-size=1200,630",
    "--virtual-time-budget=5000",
    f"--screenshot={SAIDA}",
    "file:///" + MONTADO.replace("\\", "/"),
], check=True, capture_output=True)

os.remove(MONTADO)

if not os.path.exists(SAIDA):
    raise SystemExit("Chrome nao gerou o png")

print(f"  og.png  {os.path.getsize(SAIDA) / 1024:.0f} KB  1200x630")
