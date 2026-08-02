"""
Prepara a pasta de publicacao e mostra o comando de deploy.

Monta o site, copia so o que e publico para site/publico/ e imprime o comando
do wrangler. A pasta publico/ nao vai pro git — e artefato de build.

    python site/publicar.py
"""

import os
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PUBLICO = os.path.join(AQUI, "publico")

# gerados por montar.py que vao pro ar
PAGINAS = [
    "index.html",
    "orcamento.html",
    "entrar.html",
    "conta.html",
    "cadastro.html",
    "enviado.html",
    "padrao.html",
    "projeto.html",
    # sem isto o Pages devolve a home com HTTP 200 em qualquer
    # endereco errado, o que vira soft 404 no Google
    "privacidade.html",
    "404.html",
]

# rota antiga -> rota nova, para link que ja circulou nao morrer
REDIRECTS = "/checklist /projeto 301\n"

ROBOTS = """User-agent: *
Allow: /
Sitemap: https://borinprojetos.com.br/sitemap.xml
"""

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://borinprojetos.com.br/</loc><priority>1.0</priority></url>
  <url><loc>https://borinprojetos.com.br/orcamento</loc><priority>0.8</priority></url>
  <url><loc>https://borinprojetos.com.br/privacidade</loc><priority>0.3</priority></url>
</urlset>
"""

# 1. a ficha e gerada do ficha-campos.json, e so depois os templates viram
#    html. Rodar so o montar.py deixava o _projeto.html velho, e o erro
#    era invisivel: o site subia com a ficha da versao anterior.
subprocess.run([sys.executable, os.path.join(AQUI, "gerar-ficha.py")], check=True)
subprocess.run([sys.executable, os.path.join(AQUI, "montar.py")], check=True)

# 2. Monta numa pasta nova e so troca no fim.
#    Por que nao limpar publico/ direto: no Windows, qualquer processo com a
#    pasta aberta (um servidor de teste, o Explorer) trava o rmtree no meio.
#    A pasta ficava vazia, o deploy subia um site sem pagina nenhuma e o
#    wrangler dizia "sucesso". Aconteceu duas vezes.
#    Montando fora e trocando por ultimo, publico/ so deixa de ser a versao
#    antiga quando a nova ja esta inteira em disco.
NOVO = PUBLICO + ".novo"
VELHO = PUBLICO + ".velho"
for lixo in (NOVO, VELHO):
    shutil.rmtree(lixo, ignore_errors=True)
os.makedirs(NOVO)
DESTINO = NOVO

for nome in PAGINAS:
    origem = os.path.join(AQUI, nome)
    if not os.path.exists(origem):
        raise SystemExit(f"Faltou gerar {nome} — rode montar.py")
    shutil.copy2(origem, os.path.join(DESTINO, nome))

# cartao de compartilhamento, gerado por gerar-og.py
OG = os.path.join(AQUI, "og.png")
if os.path.exists(OG):
    shutil.copy2(OG, os.path.join(DESTINO, "og.png"))
else:
    print("  aviso: og.png nao existe — rode python site/gerar-og.py")

with open(os.path.join(DESTINO, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(ROBOTS)

with open(os.path.join(DESTINO, "_redirects"), "w", encoding="utf-8") as f:
    f.write(REDIRECTS)

with open(os.path.join(DESTINO, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(SITEMAP)

# 3. Trava antes da troca: se faltar pagina, publico/ nem chega a ser tocada
#    e o que estava no ar continua valendo.
faltando = [p for p in PAGINAS if not os.path.exists(os.path.join(DESTINO, p))]
if faltando:
    shutil.rmtree(NOVO, ignore_errors=True)
    raise SystemExit("NAO PUBLIQUE: faltou %s no build" % ", ".join(faltando))

vazias = [p for p in PAGINAS
          if os.path.getsize(os.path.join(DESTINO, p)) < 10 * 1024]
if vazias:
    shutil.rmtree(NOVO, ignore_errors=True)
    raise SystemExit("NAO PUBLIQUE: %s saiu pequeno demais, o build falhou"
                     % ", ".join(vazias))

# 4. A troca. Se publico/ estiver travada, renomear tambem falha — mas aqui
#    falha ANTES de destruir qualquer coisa, e a versao antiga sobrevive.
try:
    if os.path.exists(PUBLICO):
        os.rename(PUBLICO, VELHO)
    os.rename(NOVO, PUBLICO)
except OSError as e:
    shutil.rmtree(NOVO, ignore_errors=True)
    if os.path.exists(VELHO) and not os.path.exists(PUBLICO):
        os.rename(VELHO, PUBLICO)
    raise SystemExit(
        "NAO PUBLIQUE: nao consegui trocar a pasta (%s).\n"
        "Alguma coisa esta com %s aberta — normalmente um python -m http.server.\n"
        "Feche e rode de novo. O que estava no ar continua intacto." % (e, PUBLICO))
shutil.rmtree(VELHO, ignore_errors=True)

print(f"\n  pasta de publicacao pronta: {PUBLICO}")
for a in sorted(os.listdir(PUBLICO)):
    kb = os.path.getsize(os.path.join(PUBLICO, a)) / 1024
    print(f"    {a:18} {kb:7.1f} KB")

# 5. Deploy opcional, no mesmo comando. Separar build de deploy foi o que
#    permitiu subir pasta vazia: o build falhava e o deploy rodava assim mesmo.
if "--deploy" in sys.argv:
    env = dict(os.environ)
    dotenv = os.path.join(os.path.dirname(AQUI), ".env")
    if os.path.exists(dotenv):
        for linha in open(dotenv, encoding="utf-8"):
            if "=" in linha and not linha.strip().startswith("#"):
                k, _, v = linha.partition("=")
                env[k.strip()] = v.strip().strip("'\"")
    print("\n  subindo...")
    r = subprocess.run(["npx", "wrangler", "pages", "deploy", PUBLICO,
                        "--project-name", "borin", "--branch", "main"],
                       env=env, shell=(os.name == "nt"))
    raise SystemExit(r.returncode)

print("""
  Deploy:

      python site/publicar.py --deploy

  Rotas:  /  ·  /orcamento  ·  /enviado  ·  /padrao  ·  /projeto
  /enviado e a confirmacao pos-envio, e a unica marca de conversao contavel.
  /padrao e /projeto sao pos-contrato: fora do robots e sem link no site.
""")
