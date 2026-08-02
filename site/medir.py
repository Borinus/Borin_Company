"""
Liga a medicao do site: Microsoft Clarity e Cloudflare Web Analytics.

    python site/medir.py --clarity s7k2m9x1qp
    python site/medir.py --cloudflare 1a2b3c...
    python site/medir.py --clarity s7k2m9x1qp --cloudflare 1a2b... --publicar
    python site/medir.py                      # so mostra como esta

Guarda no .env da raiz, que esta fora do git. O montar.py le de la e injeta o
script nas paginas. Sem as chaves, o site sobe igual — so nao mede nada.

Onde pegar:
  Clarity     clarity.microsoft.com > seu projeto > Settings > Overview
              (ou Setup > Install manually: e a ultima string do codigo)
  Cloudflare  dash.cloudflare.com > Analytics & Logs > Web Analytics
              > Add a site > o valor dentro de data-cf-beacon
"""

import argparse
import io
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ENV = os.path.join(RAIZ, ".env")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def ler():
    if not os.path.exists(ENV):
        return {}
    out = {}
    for linha in io.open(ENV, encoding="utf-8"):
        k, _, v = linha.partition("=")
        if v:
            out[k.strip()] = v.strip().strip("'\"")
    return out


def gravar(chave, valor):
    linhas = io.open(ENV, encoding="utf-8").read().splitlines() if os.path.exists(ENV) else []
    achou = False
    for i, l in enumerate(linhas):
        if l.split("=")[0].strip() == chave:
            linhas[i] = chave + "=" + valor
            achou = True
            break
    if not achou:
        if linhas and linhas[-1].strip():
            linhas.append("")
        linhas.append(chave + "=" + valor)
    io.open(ENV, "w", encoding="utf-8").write("\n".join(linhas) + "\n")


def main():
    a = argparse.ArgumentParser(description="Liga a medicao do site")
    a.add_argument("--clarity", help="Project ID do Microsoft Clarity")
    a.add_argument("--cloudflare", help="token do Cloudflare Web Analytics")
    a.add_argument("--publicar", action="store_true", help="monta e sobe depois de gravar")
    o = a.parse_args()

    if o.clarity:
        v = o.clarity.strip()
        # se ele colar o snippet inteiro, tira o ID de dentro
        m = re.search(r'"clarity"\s*,\s*"script"\s*,\s*"([a-z0-9]+)"', v)
        if m:
            v = m.group(1)
            print("  (peguei o ID de dentro do código que você colou)")
        if not re.fullmatch(r"[a-z0-9]{6,20}", v):
            raise SystemExit("ID do Clarity parece errado: %r\n"
                             "  Espero algo como s7k2m9x1qp — letras minúsculas e números." % v)
        gravar("BORIN_CLARITY_ID", v)
        print("  Clarity gravado:", v)

    if o.cloudflare:
        v = o.cloudflare.strip()
        m = re.search(r'"token"\s*:\s*"([a-f0-9]+)"', v)
        if m:
            v = m.group(1)
            print("  (peguei o token de dentro do código que você colou)")
        if not re.fullmatch(r"[a-f0-9]{20,64}", v):
            raise SystemExit("Token do Cloudflare parece errado: %r\n"
                             "  Espero uma sequência longa de letras a-f e números." % v)
        gravar("BORIN_ANALYTICS_TOKEN", v)
        print("  Cloudflare gravado:", v[:8] + "…")

    e = ler()
    print()
    print("  " + "-" * 52)
    for nome, chave, onde in (
        ("Microsoft Clarity", "BORIN_CLARITY_ID", "mapa de calor, rolagem, gravação, dead click"),
        ("Cloudflare Analytics", "BORIN_ANALYTICS_TOKEN", "quantos entram, de onde, em qual página"),
    ):
        v = e.get(chave, "")
        print("  %-22s %s" % (nome, "ligado" if v else "DESLIGADO"))
        print("  %-22s %s" % ("", onde))
    print("  " + "-" * 52)

    if not o.publicar:
        if o.clarity or o.cloudflare:
            print("\n  Falta subir:  python site/publicar.py --deploy\n")
        return

    print("\n  montando e subindo...")
    r = subprocess.run([sys.executable, os.path.join(AQUI, "publicar.py"), "--deploy"])
    raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
