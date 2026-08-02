"""
Monta o site: injeta fontes, CSS e JS comuns nos templates e gera os .html.

    python site/gerar-fontes.py    # 1. subset da Inter -> fontes.css
    python site/montar.py          # 2. injeta e gera os html

Marcadores que o template pode declarar dentro de <style> ou <script>:

    /* FONTES */      -> fontes.css        (a Inter embutida em base64)
    /* BASE-FORM */   -> _form.css         (tokens e componentes de formulario)
    /* BASE-JS */     -> _form.js          (montar texto, WhatsApp, download, padrao)

Os html resultantes sao autocontidos: nao buscam fonte, script nem imagem de
lugar nenhum. Da pra abrir por file:// ou subir em qualquer hospedagem.
"""

import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))

# marcador -> arquivo com o conteudo que entra no lugar dele
INJECOES = {
    "/* FONTES */": "fontes.css",
    "/* BASE-FORM */": "_form.css",
    "/* BASE-JS */": "_form.js",
}

PAGINAS = [
    ("_pagina.html", "index.html"),
    ("_orcamento.html", "orcamento.html"),
    ("_entrar.html", "entrar.html"),
    ("_conta.html", "conta.html"),
    ("_cadastro.html", "cadastro.html"),
    ("_enviado.html", "enviado.html"),
    ("_padrao.html", "padrao.html"),
    ("_projeto.html", "projeto.html"),
    ("_privacidade.html", "privacidade.html"),
    ("_404.html", "404.html"),
]


def do_env(chave):
    """Le uma chave do .env da raiz. Fica fora do git de proposito: sem ela o
    site sobe igual, so nao mede nada."""
    env = os.path.join(os.path.dirname(AQUI), ".env")
    if not os.path.exists(env):
        return ""
    with open(env, encoding="utf-8") as f:
        for linha in f:
            k, _, v = linha.partition("=")
            if k.strip() == chave:
                return v.strip().strip("'\"")
    return ""


# Duas medicoes, e elas respondem coisas diferentes.
#   Cloudflare Web Analytics — quantos entram, de onde, em que pagina. Numero.
#   Microsoft Clarity — o que a pessoa FAZ: mapa de calor, ate onde rola,
#     gravacao de sessao, e o "dead click", que e o clique em coisa que nao e
#     botao. Foi exatamente isso que a gestora de marketing apontou.
CF = do_env("BORIN_ANALYTICS_TOKEN")
CLARITY = do_env("BORIN_CLARITY_ID")

_partes = []
if CF:
    _partes.append(
        '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
        'data-cf-beacon=\'{"token": "%s"}\'></script>' % CF)
if CLARITY:
    _partes.append(
        '<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[])'
        '.push(arguments)};t=l.createElement(r);t.async=1;'
        't.src="https://www.clarity.ms/tag/"+i;'
        'y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);'
        '})(window,document,"clarity","script","%s");</script>' % CLARITY)

if _partes:
    BEACON = "\n".join(_partes)
else:
    BEACON = "<!-- sem medicao: defina BORIN_ANALYTICS_TOKEN e BORIN_CLARITY_ID no .env -->"

for _nome, _valor in (("BORIN_ANALYTICS_TOKEN", CF), ("BORIN_CLARITY_ID", CLARITY)):
    if not _valor:
        print("  aviso: %s nao definido no .env" % _nome)

# A medicao vai no TOPO, logo apos o viewport. Estava no ultimo byte de
# 168 KB de HTML: quem entrava e saia rapido nao era contado, porque o
# Clarity so inicializava depois de todo o parse. O marcador do fim vira
# vazio para nao sobrar comentario solto.
conteudo = {"<!-- ANALYTICS -->": ""}
for marcador, arquivo in INJECOES.items():
    caminho = os.path.join(AQUI, arquivo)
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            conteudo[marcador] = f.read()
    else:
        conteudo[marcador] = f"/* {arquivo} nao encontrado */"
        print(f"  aviso: {arquivo} nao encontrado")

def por_no_topo(html, beacon):
    """Enfia a medicao logo depois do <meta name="viewport">."""
    m = re.search(r'<meta name="viewport"[^>]*>', html)
    if not m:
        return beacon + "\n" + html
    return html[:m.end()] + "\n" + beacon + html[m.end():]


for template, saida in PAGINAS:
    origem = os.path.join(AQUI, template)
    destino = os.path.join(AQUI, saida)

    if not os.path.exists(origem):
        raise SystemExit(f"Template nao encontrado: {origem}")

    with open(origem, encoding="utf-8") as f:
        pagina = f.read()

    if "/* FONTES */" not in pagina:
        raise SystemExit(f"Marcador /* FONTES */ nao encontrado em {template}")

    for marcador, texto in conteudo.items():
        if marcador in pagina:
            pagina = pagina.replace(marcador, texto)

    # Sem doctype o navegador cai em quirks mode, onde o box model e o antigo.
    # Vai junto com o box-sizing declarado no CSS — um sem o outro estoura os
    # campos, que sao width:100% com padding. Nao abrir <head> nem <body>:
    # o parser cria os dois e move title/meta/style pra dentro do head sozinho.
    pagina = por_no_topo(pagina, BEACON)

    with open(destino, "w", encoding="utf-8") as f:
        f.write('<!doctype html>\n<html lang="pt-BR">\n' + pagina)

    print(f"  {saida:18} {os.path.getsize(destino) / 1024:6.0f} KB")

print("  saida:", AQUI)
