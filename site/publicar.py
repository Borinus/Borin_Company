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

AQUI = os.path.dirname(os.path.abspath(__file__))
PUBLICO = os.path.join(AQUI, "publico")

# 1. monta o index.html a partir do template + fontes
subprocess.run([sys.executable, os.path.join(AQUI, "montar.py")], check=True)

# 2. pasta limpa, so com o que vai pro ar
if os.path.exists(PUBLICO):
    shutil.rmtree(PUBLICO)
os.makedirs(PUBLICO)

shutil.copy2(os.path.join(AQUI, "index.html"), os.path.join(PUBLICO, "index.html"))

with open(os.path.join(PUBLICO, "robots.txt"), "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n")

arquivos = sorted(os.listdir(PUBLICO))
print(f"\n  pasta de publicacao pronta: {PUBLICO}")
for a in arquivos:
    kb = os.path.getsize(os.path.join(PUBLICO, a)) / 1024
    print(f"    {a:16} {kb:7.1f} KB")

print("""
  Agora rode o deploy (a primeira vez abre o navegador pra login na Cloudflare):

      npx wrangler pages deploy site/publico --project-name borin

  Depois, no painel da Cloudflare: Workers & Pages -> borin -> Custom domains
  -> adicionar borinprojetos.com.br e www.borinprojetos.com.br
""")
