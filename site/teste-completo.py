"""
Roda o fluxo inteiro com um projeto real e manda cada etapa por email.

    python site/teste-completo.py

Usa o 04003478 - Painel de Interface, o unico projeto com numero medido:
51 folhas, 96 pontos de I/O, escopo B. Simula o cliente pedindo orcamento no
site no ar, calcula o valor, preenche a ficha tecnica e manda 5 emails
numerados pro Mateus acompanhar de fora do PC.

O email sai pelo proprio Worker do site (/api/orcamento), entao o teste tambem
prova que o caminho de email esta de pe.
"""

import io
import json
import os
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
API = SITE + "/api/orcamento"
TMP = os.path.join(AQUI, "_teste_tmp")

sys.path.insert(0, os.path.join(RAIZ, "comercial"))
import importlib.util
_s = importlib.util.spec_from_file_location("calc", os.path.join(RAIZ, "comercial", "calcular.py"))
calc = importlib.util.module_from_spec(_s); _s.loader.exec_module(calc)

# ---------- o projeto real ----------
P = {
    "empresa": "Metalúrgica Serra Ltda",
    "contato": "João Vieira",
    "email": "mateusborin20@gmail.com",
    "fone": "54996642003",
    "equipamento": "Painel de interface de sistema de pintura",
    "codigo": "04003478",
    "escopo": "B",
    "io": 96, "di": 32, "dq": 64,
    "acionamentos": 8,
    "seguranca": 6,
    "prazo": "2026-09-15",
}


def chrome():
    for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              shutil.which("chrome") or ""]:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chrome nao encontrado")


def enviar(titulo, corpo, etapa=""):
    """Manda um email pelo Worker do site. Passa por arquivo em UTF-8 porque o
    shell do Windows corrompe acento em argumento."""
    os.makedirs(TMP, exist_ok=True)
    p = os.path.join(TMP, "corpo.json")
    io.open(p, "w", encoding="utf-8").write(json.dumps(
        {"empresa": "Fluxo completo", "contato": "relatório automático",
         "codigo": etapa or titulo, "equipamento": titulo, "doc": "",
         "email": "", "intencao": "teste-completo", "texto": corpo},
        ensure_ascii=False))
    r = subprocess.run(["curl", "-s", "-X", "POST", API,
                        "-H", "Content-Type: application/json",
                        "--data-binary", "@" + p],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = '"ok":true' in (r.stdout or "")
    print("   email %-46s %s" % (titulo[:46], "enviado" if ok else "FALHOU: " + str(r.stdout)))
    return ok


def deploy():
    env = dict(os.environ)
    c = os.path.join(RAIZ, ".env")
    if os.path.exists(c):
        for l in io.open(c, encoding="utf-8"):
            if "=" in l and not l.strip().startswith("#"):
                k, _, v = l.partition("=")
                env[k.strip()] = v.strip().strip("'\"")
    return subprocess.run(["npx", "wrangler", "pages", "deploy", PUBLICO,
                           "--project-name", "borin", "--branch", "main"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, shell=(os.name == "nt"))


def esperar(url, codigo, limite=180):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status == codigo:
                    return True
        except urllib.error.HTTPError as e:
            if e.code == codigo:
                return True
        except Exception:
            pass
        time.sleep(5)
    return False


# ---------- a pagina que dirige o site ----------

HARNESS = """<meta charset="utf-8"><body style="margin:0;font:12px monospace;background:#111;color:#0f0">
<pre id="log" style="padding:10px"></pre>
<iframe id="a" style="width:900px;height:120px;border:0;opacity:.15"></iframe>
<script>
var L=document.getElementById('log'), R={etapas:[], ficha:'', ok:true};
function p(m){L.textContent+=m+"\\n";}
function ck(n,c,d){ if(!c){R.ok=false;} R.etapas.push((c?'PASSOU':'FALHOU')+'  '+n+(d?'  ['+d+']':'')); p((c?'PASSOU  ':'FALHOU  ')+n+(d?'  ['+d+']':'')); }
window.onerror=function(m){R.ok=false;ck('erro de javascript',false,m);};
var D=%(dados)s;
var fr=document.getElementById('a'), fase=0, n=0;

fr.addEventListener('load', function(){
  var d=this.contentDocument, w=this.contentWindow;
  n++;
  if(fase===0 && n===1){
    // ---- etapa 1: cliente pede orcamento ----
    d.getElementById('empresa').value=D.empresa;
    d.getElementById('contato').value=D.contato;
    d.getElementById('email').value=D.email;
    var f=d.getElementById('fone'); f.value=D.fone; f.dispatchEvent(new w.Event('input'));
    ck('mascara do telefone', f.value==='+55 54 99664-2003', f.value);
    d.getElementById('equipamento').value=D.equipamento;
    d.getElementById('codigo').value=D.codigo;
    d.getElementById('acionamentos').value=D.acionamentos;
    d.getElementById('ios').value=D.io;
    d.getElementById('prazo').value=D.prazo;
    d.querySelector('input[name="escopo"][value="B"]').click();
    d.querySelector('input[name="nr12"][value="sim"]').click();
    setTimeout(function(){
      d.getElementById('seg_qtd').value=D.seguranca;
      ck('NR-12 abre campo de seguranca', d.getElementById('seg_qtd').offsetHeight>0);
      R.pedido = w.montar(true);
      d.querySelector('button.botao').click();
    }, 250);
  } else if(fase===0){
    // ---- confirmacao ----
    ck('vai pra confirmacao', w.location.pathname==='/enviado', w.location.pathname);
    var t=d.getElementById('titulo').textContent;
    ck('servidor recebeu o pedido', t.indexOf('Recebido')===0, t);
    ck('esconde o socorro', d.getElementById('socorro').style.display==='none');
    ck('oferece padrao e ficha', !!d.querySelector('a[href="/padrao"]'));
    // ---- etapa 2: a ficha tecnica ----
    fase=1; n=0; fr.src='/projeto';
  } else if(fase===2){
    // ---- padrao do cliente: os campos ja vem com o padrao da casa ----
    ck('padrao abre', !!d.getElementById('alim'));
    ck('tensao ja preenchida', d.getElementById('alim').value==='380 V', d.getElementById('alim').value);
    ck('comando ja preenchido', d.getElementById('comando').value==='24 Vcc', d.getElementById('comando').value);
    ck('aterramento ja preenchido', d.getElementById('aterramento').value==='TN', d.getElementById('aterramento').value);
    ck('grau de protecao ja preenchido', d.getElementById('ip').value==='IP54', d.getElementById('ip').value);
    ck('cores de fio ja escritas', (d.getElementById('cores').value||'').indexOf('Fase R')===0);
    ck('temperatura maxima removida', !d.getElementById('temp'));
    ck('CLP e perifericos separados', !!d.getElementById('m_perif'));
    ck('identificacao oculta por enquanto', d.getElementById('tag').offsetHeight===0);
    p(''); p(R.ok ? 'RESULTADO: TUDO PASSOU' : 'RESULTADO: TEM FALHA');
    document.title='FIM';
    var sc=document.createElement('script'); sc.id='r';
    sc.type='application/json'; sc.textContent=JSON.stringify(R);
    document.body.appendChild(sc);
  } else {
    // ---- ficha do projeto ----
    ck('ficha abre', !!d.getElementById('projeto_descricao'));
    d.getElementById('empresa').value=D.empresa;
    d.getElementById('contato').value=D.contato;
    d.getElementById('projeto_descricao').value=D.equipamento;
    d.getElementById('projeto_numero').value=D.codigo;
    d.getElementById('projeto_cliente').value='FlowSistem';
    d.getElementById('io_processo_entradas_digitais').value=D.di;
    d.getElementById('io_processo_saidas_digitais').value=D.dq;
    d.getElementById('io_processo_valvulas').value=D.acionamentos;
    d.querySelector('input[name="alimentacao_tipo"][value="TRI"]').click();
    var cg=d.getElementById('alimentacao_chave_geral'); cg.value='CHGERAL_TRI';
    // 6 dispositivos de seguranca, como no projeto real
    var seg=d.querySelector('.repetivel[data-lista="dispositivos"]');
    var macros=['EME_RST_PAINEL','EME_RST','EME_RST_SOLI','TRAVA_GS71PC','DX200_SAFETY_BOARD','EQUIPAMENTO_PINTURA'];
    for(var i=0;i<macros.length;i++){ seg.querySelector('.link-acao').click(); }
    setTimeout(function(){
      var ls=seg.querySelectorAll('.linha');
      ck('6 dispositivos de seguranca adicionados', ls.length===6, ls.length+' linhas');
      for(var i=0;i<ls.length;i++){ ls[i].querySelector('.item-macro').value=macros[i]; }
      // 8 valvulas no bloco de campo, com funcao por unidade
      var camp=d.querySelector('.repetivel[data-lista="campo"]');
      camp.querySelector('.link-acao').click();
      setTimeout(function(){
        var l=camp.querySelector('.linha'), cat=l.querySelector('select');
        cat.value='5'; cat.dispatchEvent(new w.Event('change'));
        setTimeout(function(){
          var q=l.querySelector('.item-qtd'); q.value='8'; q.dispatchEvent(new w.Event('input'));
          setTimeout(function(){
            var fs=l.querySelectorAll('.item-funcao');
            ck('funcao abre uma por unidade', fs.length===8, fs.length+' campos');
            for(var i=0;i<fs.length;i++){ fs[i].value='Acionamento da pistola de pintura '+(i+1); }
            R.ficha = w.montar(true);
            ck('ficha carrega as macros', R.ficha.indexOf('[CHGERAL_TRI]')>0, 'de/para');
            ck('ficha carrega as funcoes', R.ficha.indexOf('pistola de pintura 8')>0);
            // ---- a ficha vira o documento assinavel (Anexo II do contrato) ----
            w.gerarFicha();
            setTimeout(function(){
              var doc=d.getElementById('documento');
              ck('ficha vira documento', doc.classList.contains('ativo'));
              var t=doc.innerText;
              ck('documento tem declaracao', t.indexOf('Declara')>0);
              ck('documento tem assinatura', t.indexOf('Data:')>0);
              ck('documento traz a macro', t.indexOf('CHGERAL_TRI')>0);
              ck('documento traz a funcao por unidade', t.indexOf('Pistola de pintura 8')>0 || t.indexOf('pistola de pintura 8')>0);
              ck('formulario sai da frente', d.querySelector('form').offsetHeight===0);
              R.documento = t;
              // ---- ultima etapa: o padrao do cliente ----
              fase=2; n=0; fr.src='/padrao';
            }, 400);
          },120);
        },120);
      },120);
    },200);
  }
});
fr.src='/orcamento';
</script></body>
"""


def main():
    print("\n  TESTE COMPLETO — 04003478 Painel de Interface\n")

    # 1. sobe o site com a pagina que dirige o teste
    subprocess.run([sys.executable, os.path.join(AQUI, "publicar.py")],
                   check=True, capture_output=True)
    alvo = os.path.join(PUBLICO, "t-completo.html")
    io.open(alvo, "w", encoding="utf-8").write(
        HARNESS % {"dados": json.dumps(P, ensure_ascii=False)})
    print("   subindo o site...")
    if deploy().returncode != 0:
        raise SystemExit("deploy falhou")
    url = SITE + "/t-completo"
    # com a query, cada leitura pode cair num no diferente; exigir 200 tres
    # vezes seguidas evita comecar o teste antes de propagar em todos
    seguidas = 0
    fim = time.time() + 240
    while seguidas < 3 and time.time() < fim:
        alvo_q = url + "?c=" + str(random.randint(1, 10**9))
        seguidas = seguidas + 1 if esperar(alvo_q, 200, limite=10) else 0
        if seguidas < 3:
            time.sleep(4)
    if seguidas < 3:
        raise SystemExit("a pagina de teste nao propagou")

    # 2. o navegador faz o papel do cliente (isso dispara o email 1 de verdade)
    print("   rodando o fluxo no navegador...")
    saida = os.path.join(AQUI, "ultimo-teste-completo.png")
    dom = os.path.join(TMP, "dom.html")
    os.makedirs(TMP, exist_ok=True)
    base = [chrome(), "--headless", "--disable-gpu", "--hide-scrollbars",
            "--virtual-time-budget=40000", "--window-size=960,520"]
    alvo_q = url + "?c=" + str(random.randint(1, 10**9))
    subprocess.run(base + ["--screenshot=" + saida, alvo_q],
                   capture_output=True, timeout=200)
    r = subprocess.run(base + ["--dump-dom", url + "?c=" + str(random.randint(1, 10**9))],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=200)
    io.open(dom, "w", encoding="utf-8").write(r.stdout or "")

    R = {}
    cru = r.stdout or ""
    i = cru.find('<script id="r" type="application/json">')
    if i > 0:
        j = cru.find("</script>", i)
        try:
            R = json.loads(cru[i + len('<script id="r" type="application/json">'):j])
        except Exception:
            pass

    etapas = R.get("etapas", [])
    pedido = R.get("pedido", "(nao capturado)")
    ficha = R.get("ficha", "(nao capturada)")
    passou = R.get("ok", False) and etapas

    # 3. o calculo
    paginas = calc.estimar_paginas(P["io"], P["acionamentos"], P["seguranca"], P["escopo"])
    orc = calc.calcular(paginas, itens_manuais=2, setup_padrao=True, abertura=True)
    linhas = "\n".join("  %-42s %14s" % (a, calc.brl(b)) for a, b in orc["linhas"])

    if not etapas:
        print("\n   NAO CAPTUROU O RESULTADO — nada foi enviado por email.")
        print("   dom salvo em:", dom)
        print("   imagem:", saida)
        os.remove(alvo); deploy()
        raise SystemExit(1)

    # 4. os emails, numerados
    enviar("O que o cliente enviou", 
           "Etapa 1 do fluxo: o cliente preencheu /orcamento no site no ar.\n"
           "Este texto e exatamente o que o formulario montou.\n\n"
           + "-" * 56 + "\n\n" + pedido, etapa="TESTE 1/5")

    enviar("O valor calculado", 
           ("Etapa 2: o valor sai de comercial/calcular.py, sem digitacao.\n\n"
            "Entradas vindas do pedido:\n"
            "  pontos de I/O ............ %d\n  acionamentos ............. %d\n"
            "  disp. de seguranca ....... %d\n  escopo ................... %s\n\n"
            "Paginas estimadas: %d   (o projeto real tem 51 folhas)\n\n"
            % (P["io"], P["acionamentos"], P["seguranca"], P["escopo"], paginas))
           + "-" * 56 + "\n" + linhas + "\n" + "-" * 56 + "\n"
           + "  %-42s %14s\n" % ("Valor cheio", calc.brl(orc["valor_cheio"]))
           + "  %-42s %14s\n" % ("TOTAL com condicao de abertura", calc.brl(orc["total"]))
           + "\nRende %s/h sobre 14 h suas. Piso: %s/h.\n"
           % (calc.brl(orc["total"] / 14), calc.brl(calc.POR_PAGINA)), etapa="TESTE 2/5")

    enviar("A ficha técnica preenchida", 
           "Etapa 3: o cliente preencheu /projeto.\n"
           "Repare que cada escolha traz a macro entre colchetes — e isso que o\n"
           "gerador consome. O cliente nunca viu esses nomes na tela.\n\n"
           + "-" * 56 + "\n\n" + ficha, etapa="TESTE 3/5")

    verif = "\n".join("  " + e for e in etapas) if etapas else "  (nenhuma etapa capturada)"
    enviar("Verificação automática", 
           ("Etapa 4: o que foi conferido clicando de verdade no site no ar,\n"
            "nao em copia local.\n\n") + verif +
           ("\n\n  RESULTADO: %s\n" % ("TUDO PASSOU" if passou else "TEM FALHA")), etapa="TESTE 4/5")

    falta = """Etapa 5: o que separa isto do fluxo que voce descreveu.

O QUE JA RODA SOZINHO
  1. Cliente preenche o pedido no site
  2. O pedido chega no seu email em segundos
  3. O valor sai calculado, sem digitacao
  4. A ficha tecnica sai com as macros prontas pro gerador

O QUE AINDA E MANUAL
  5. Montar o PDF do orcamento e responder
  6. Assinatura do contrato e cobranca da entrada
  7. Levar a ficha ate a VM e rodar o gerador
  8. Entregar o PDF quando o pagamento fechar

A PONTE QUE FALTA, NA ORDEM
  a) A ficha precisa chegar ate voce por email, como o pedido ja chega.
     Hoje ela so sai por WhatsApp ou arquivo, de proposito: o site promete
     que ela nao vai pra servidor. Mudar isso muda o texto do site junto.
  b) Um executor na VM que le o email, extrai as macros e monta a receita.
     O formato ja esta certo: as macros vao entre colchetes no texto.
  c) Devolver so o PDF, como voce descreveu.

O QUE NAO PRECISA DE IA
  Ler o pedido, calcular, estimar pagina, montar o PDF e gerar o projeto sao
  todos deterministicos. IA so serve pra interpretar a descricao livre do
  equipamento e pra casar item escrito com macro do banco — e nos dois casos
  propondo pra voce aprovar, nao decidindo.

Detalhe completo em comercial/fluxo-ponta-a-ponta.md
"""
    enviar("O que falta pro fluxo fechar",  falta, etapa="TESTE 5/5")

    # 5. limpa
    os.remove(alvo)
    deploy()
    esperar(url + "?c=" + str(random.randint(1, 10**9)), 404, limite=120)
    shutil.rmtree(TMP, ignore_errors=True)

    print("\n   etapas verificadas: %d" % len(etapas))
    for e in etapas:
        print("     " + e)
    print("\n   RESULTADO: %s" % ("TUDO PASSOU" if passou else "TEM FALHA"))
    print("   imagem: %s" % saida)
    print("   5 emails enviados. A pagina de teste ja saiu do ar.\n")


if __name__ == "__main__":
    main()
