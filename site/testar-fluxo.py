"""
Testa o fluxo do orcamento no site NO AR, com navegador de verdade.

    python site/testar-fluxo.py

O que faz: sobe uma pagina de teste temporaria (precisa ser da mesma origem,
senao o navegador bloqueia o script por cross-origin), dirige o formulario como
um cliente faria, le o resultado de cada etapa e apaga a pagina no fim.

Por que existe: sem isto, so da pra testar pedindo pro Mateus clicar e conferir.
E ele nao deveria precisar. Cada mudanca no formulario tem que passar aqui antes
de eu dizer que esta pronto.

Cuidados que ja custaram diagnostico errado:
  - cache de borda do Cloudflare serve versao antiga; a pagina de teste leva uma
    query aleatoria pra furar
  - o Pages redireciona /x.html -> /x (308), entao a URL vai sem extensao
"""

import io
import os
import re
import random
import shutil
import subprocess
import sys
import time
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PUBLICO = os.path.join(AQUI, "publico")
SITE = "https://borinprojetos.com.br"
NOME = "t-fluxo"

CHROMES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    shutil.which("chrome") or "", shutil.which("google-chrome") or "",
]

PAGINA = """<meta charset="utf-8"><body style="margin:0;font:13px monospace;background:#111;color:#0f0">
<div id="log" style="padding:12px;white-space:pre-wrap"></div>
<iframe id="f" src="/orcamento" style="width:900px;height:200px;border:0;opacity:.25"></iframe>
<script>
var L=document.getElementById('log'),ok=true;
function p(m){L.textContent+=m+"\\n";}
function checa(nome,cond,detalhe){ if(!cond){ok=false;} p((cond?'PASSOU  ':'FALHOU  ')+nome+(detalhe?'  ['+detalhe+']':'')); }
window.onerror=function(m){ok=false;p('FALHOU  erro de javascript ['+m+']');};
var f=document.getElementById('f'),n=0;
f.addEventListener('load',function(){
  n++; var d=this.contentDocument,w=this.contentWindow;
  if(n===1){
    d.querySelector('button.botao').click();
    setTimeout(function(){
      var av=d.getElementById('avisoFalta').textContent;
      checa('bloqueia envio vazio', av.indexOf('Falta')===0, av);
      checa('continua no formulario', w.location.pathname==='/orcamento');
      d.getElementById('empresa').value='TESTE AUTOMATICO - ignore';
      d.getElementById('contato').value='Joao Vieira';
      d.getElementById('equipamento').value='painel de estufa de pintura';
      d.getElementById('email').value='naoresponda@exemplo.com';
      var fone=d.getElementById('fone');
      fone.value='54996642003'; fone.dispatchEvent(new w.Event('input'));
      checa('mascara do telefone', fone.value==='+55 54 99664-2003', fone.value);
      d.getElementById('acionamentos').value='8';
      d.getElementById('ios').value='96';
      d.getElementById('prazo').value='2026-09-15';
      d.querySelector('input[name="escopo"][value="B"]').click();
      d.querySelector('input[name="nr12"][value="sim"]').click();
      setTimeout(function(){
        checa('NR-12 abre campo de seguranca', d.getElementById('seg_qtd').offsetHeight>0);
        d.getElementById('seg_qtd').value='6';
        d.querySelector('input[name="canal"][value="email+whats"]').click();
        d.querySelector('button.botao').click();
      },250);
    },400);
  } else {
    checa('vai pra confirmacao', w.location.pathname==='/enviado', w.location.pathname);
    var t=d.getElementById('titulo').textContent;
    checa('servidor recebeu', t.indexOf('Recebido')===0, t);
    checa('esconde o socorro', d.getElementById('socorro').style.display==='none');
    checa('oferece padrao e ficha', !!d.querySelector('a[href="/padrao"]') && !!d.querySelector('a[href="/projeto"]'));
    checa('nao mostra o texto cru', L.textContent.indexOf('O que foi montado')<0);
    p('');
    p(ok ? 'RESULTADO: TUDO PASSOU' : 'RESULTADO: TEM FALHA');
    document.title = ok ? 'TUDO PASSOU' : 'TEM FALHA';
  }
});
</script></body>
"""


def chrome():
    for c in CHROMES:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chrome nao encontrado")


def deploy():
    env = dict(os.environ)
    caminho = os.path.join(RAIZ, ".env")
    if os.path.exists(caminho):
        for linha in io.open(caminho, encoding="utf-8"):
            if "=" in linha and not linha.strip().startswith("#"):
                k, _, v = linha.partition("=")
                env[k.strip()] = v.strip().strip("'\"")
    return subprocess.run(
        ["npx", "wrangler", "pages", "deploy", PUBLICO,
         "--project-name", "borin", "--branch", "main"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, shell=(os.name == "nt"),
    )


def esperar(url, esperado, limite=180):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status == esperado:
                    return True
        except urllib.error.HTTPError as e:
            if e.code == esperado:
                return True
        except Exception:
            pass
        time.sleep(5)
    return False


# 1. monta o site e poe a pagina de teste junto
subprocess.run([sys.executable, os.path.join(AQUI, "publicar.py")],
               check=True, capture_output=True)
alvo = os.path.join(PUBLICO, NOME + ".html")
io.open(alvo, "w", encoding="utf-8").write(PAGINA)

print("  subindo o site com a pagina de teste...")
r = deploy()
if r.returncode != 0:
    print(r.stdout[-800:], r.stderr[-800:])
    raise SystemExit("deploy falhou")

url = SITE + "/" + NOME
# Uma leitura so nao basta: com a query anti-cache cada requisicao pode cair
# num no diferente da borda, e o navegador chegava antes de propagar em todos.
# Tres leituras seguidas com 200 resolvem.
seguidas, fim = 0, time.time() + 240
while seguidas < 3 and time.time() < fim:
    seguidas = seguidas + 1 if esperar(
        url + "?c=" + str(random.randint(1, 10**9)), 200, limite=10) else 0
    if seguidas < 3:
        time.sleep(4)
if seguidas < 3:
    raise SystemExit("a pagina de teste nao propagou")

# 2. O navegador faz o papel do cliente.
#    Esperar 200 nao basta: a borda tem no frio, e o Chrome as vezes cai num
#    que ainda nao recebeu o deploy — o teste "falhava" mostrando a pagina 404.
#    Entao a gente confere o resultado e tenta de novo se vier vazio.
print("  rodando o fluxo no navegador...\n")
saida = os.path.join(AQUI, "ultimo-teste.png")
base = [chrome(), "--headless", "--disable-gpu", "--hide-scrollbars",
        "--virtual-time-budget=30000", "--window-size=980,420"]

dom = ""
for tentativa in range(1, 4):
    alvo_q = url + "?c=" + str(random.randint(1, 10**9))
    r = subprocess.run(base + ["--dump-dom", alvo_q], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=180)
    dom = r.stdout or ""
    if "RESULTADO:" in dom:
        break
    motivo = "pagina 404" if "não existe" in dom else "sem resultado"
    print("  tentativa %d: %s, tentando de novo..." % (tentativa, motivo))
    time.sleep(8)

subprocess.run(base + ["--screenshot=" + saida,
                       url + "?c=" + str(random.randint(1, 10**9))],
               capture_output=True, timeout=180)

if "RESULTADO:" not in dom:
    print("\n  NAO CONSEGUI RODAR O TESTE — a pagina nao carregou em 3 tentativas.")
else:
    for linha in dom.splitlines():
        t = linha.strip()
        if t.startswith("PASSOU") or t.startswith("FALHOU") or t.startswith("RESULTADO:"):
            print("  " + t)

# 3. tira a pagina de teste do ar de novo
os.remove(alvo)
deploy()
esperar(url + "?c=" + str(random.randint(1, 10**9)), 404, limite=120)

print("  resultado em:", saida)
print("  (a pagina de teste ja saiu do ar)")
