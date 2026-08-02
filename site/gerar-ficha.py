"""
Gera site/_projeto.html a partir de site/ficha-campos.json.

    python site/gerar-ficha.py     # depois: python site/publicar.py

Por que gerado e nao escrito a mao: a ficha e um de/para. O que o cliente le
("Fonte de 24 V — 5 A") e o que o gerador consome (FONTE_24V_5A) sao a mesma
coisa vista de dois lados. Mantendo isso num JSON, mudar rotulo nao arrisca
quebrar macro, e a lista de macros fica auditavel num arquivo so.

Origem dos nomes tecnicos:
  CONFERENCIAS/_eplan_gerador/FICHA_APP.yaml
  CONFERENCIAS/_eplan_gerador/docs_banco/MACROS_BIBLIOTECA.xlsx
"""

import io
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "ficha-campos.json")
SAIDA = os.path.join(AQUI, "_projeto.html")

d = json.load(io.open(FONTE, encoding="utf-8"))

ICONE = ("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20"
         "viewBox%3D%220%200%2032%2032%22%3E%3Cstyle%3E.t%7Bfill%3A%23111111%7D%40media("
         "prefers-color-scheme%3Adark)%7B.t%7Bfill%3A%23FFFFFF%7D%7D%3C%2Fstyle%3E%3Cpath%20"
         "class%3D%27t%27%20d%3D%27M4%204h10.4c3.9%200%206.3%202%206.3%205.2%200%202.1-1.2%203.6-3.1%204.3%202.4.6%203.9%202.4%203.9%205%200%203.7-2.7%206-7.1%206H4V4zm4.4%203.7v4.9h5.6c1.8%200%202.8-.9%202.8-2.4%200-1.6-1-2.5-2.8-2.5H8.4zm0%208.3v5.2h6.2c2%200%203.2-1%203.2-2.6%200-1.7-1.2-2.6-3.2-2.6H8.4z%27%2F%3E%3Crect%20x%3D%2724%27%20y%3D%2722%27%20width%3D%276%27%20height%3D%276%27%20fill%3D%27%23C1121F%27%2F%3E%3C%2Fsvg%3E")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def campo(c, secao):
    cid = secao + "_" + c["id"]
    rot = esc(c["rotulo"])
    dica = ' placeholder="%s"' % esc(c["dica"]) if c.get("dica") else ""
    t = c["tipo"]

    if t == "numero":
        return ('      <div class="campo"><label for="%s">%s</label>'
                '<input type="text" inputmode="numeric" id="%s"%s></div>\n' % (cid, rot, cid, dica))

    if t == "texto":
        return ('      <div class="campo"><label for="%s">%s</label>'
                '<input type="text" id="%s"%s></div>\n' % (cid, rot, cid, dica))

    if t == "marca":
        return ('      <label class="opcao"><input type="checkbox" id="%s">'
                '<span class="opcao__texto"><span class="opcao__titulo">%s</span></span></label>\n'
                % (cid, rot))

    if t == "lista":
        ops = "".join('<option value="%s">%s</option>' % (esc(o["macro"]), esc(o["rotulo"]))
                      for o in c["opcoes"])
        return ('      <div class="campo"><label for="%s">%s</label>'
                '<select id="%s">%s</select></div>\n' % (cid, rot, cid, ops))

    if t == "opcao":
        linhas = ""
        for i, o in enumerate(c["opcoes"]):
            m = " checked" if i == 0 else ""
            linhas += ('        <label class="opcao"><input type="radio" name="%s" value="%s"%s>'
                       '<span class="opcao__texto"><span class="opcao__titulo">%s</span></span>'
                       '</label>\n' % (cid, esc(o["macro"]), m, esc(o["rotulo"])))
        return ('      <p class="campo__grupo">%s</p>\n      <div class="opcoes">\n%s      </div>\n'
                % (rot, linhas))
    return ""


corpo = ""
for s in d["secoes"]:
    corpo += '    <div class="bloco">\n      <div class="bloco__cabeca"><h2>%s</h2>' % esc(s["titulo"])
    if s.get("nota"):
        corpo += "<p>%s</p>" % esc(s["nota"])
    corpo += "</div>\n"

    simples = [c for c in s["campos"] if c["tipo"] in ("texto", "numero", "lista")]
    outros = [c for c in s["campos"] if c["tipo"] not in ("texto", "numero", "lista")]
    if simples:
        corpo += '      <div class="grade">\n'
        for c in simples:
            corpo += campo(c, s["id"])
        corpo += "      </div>\n"
    marcas = [c for c in outros if c["tipo"] == "marca"]
    for c in [x for x in outros if x["tipo"] == "opcao"]:
        corpo += campo(c, s["id"])
    if marcas:
        corpo += '      <div class="opcoes">\n'
        for c in marcas:
            corpo += campo(c, s["id"])
        corpo += "      </div>\n"

    rep = s.get("repetivel")
    if rep:
        ops = "".join('<option value="%s">%s</option>' % (esc(o["macro"]), esc(o["rotulo"]))
                      for o in rep["opcoes"])
        corpo += ('      <div class="repetivel" data-lista="%s" data-rotulo="%s"'
                  ' data-funcao="%s">\n'
                  '        <span class="rotulo">%s</span>\n'
                  '        <template>%s</template>\n'
                  '        <div class="linhas"></div>\n'
                  '        <button type="button" class="link-acao" onclick="addLinha(this)">'
                  '+ adicionar</button>\n      </div>\n'
                  % (rep["id"], esc(rep["rotulo_linha"]),
                     "1" if rep.get("com_funcao") else "",
                     esc(rep["titulo"]), ops))
    corpo += "    </div>\n\n"

# bloco de campo: categoria -> item -> quantidade -> funcao por unidade
cat = d["campo"]
catjson = json.dumps(cat["categorias"], ensure_ascii=False)
corpo += ('    <div class="bloco">\n      <div class="bloco__cabeca"><h2>%s</h2><p>%s</p></div>\n'
          '      <div class="repetivel" data-lista="campo" data-rotulo="Item" data-funcao="1"'
          ' data-categorias="1">\n'
          '        <div class="linhas"></div>\n'
          '        <button type="button" class="link-acao" onclick="addLinha(this)">'
          '+ adicionar item</button>\n      </div>\n    </div>\n\n'
          % (esc(cat["titulo"]), esc(cat["nota"])))

CSS = """
/* ---------- a ficha como documento assinavel ---------- */
/* A clausula 3 do contrato compara todo pedido posterior contra esta ficha.
   Para isso ela precisa ser um documento datado e confirmado, nao um
   formulario. Este bloco e a versao de impressao: o cliente gera, salva em
   PDF pelo proprio navegador e assina junto com o contrato. */

.documento { display: none; }
.documento.ativo { display: block; }
body.modo-documento .esconde-no-doc { display: none; }
/* gerou a ficha, o formulario sai da frente: o cliente confere o
   documento, nao o formulario que ele acabou de preencher */
body.modo-documento form,
body.modo-documento .topo,
body.modo-documento footer { display: none; }

.doc__cabeca { border: 1px solid var(--ink); margin-bottom: 1.2rem; }
.doc__titulo { padding: 0.9rem 1.1rem; border-bottom: 1px solid var(--ink); }
.doc__titulo h2 { font-size: 1.25rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
.doc__titulo p { margin: 0.15rem 0 0; font-family: var(--mono); font-size: var(--fs-micro); color: var(--ink-micro); }
.doc__ident { display: grid; grid-template-columns: repeat(4, 1fr); }
.doc__ident > div { padding: 0.55rem 0.7rem; border-right: 1px solid var(--rule); display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
.doc__ident > div:last-child { border-right: 0; }
.doc__ident b { font-family: var(--mono); font-size: var(--fs-micro); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-micro); font-weight: 400; }
.doc__ident span { font-size: var(--fs-small); overflow-wrap: anywhere; }

.doc__secao { margin: 0 0 1rem; break-inside: avoid; }
.doc__secao h3 {
  font-family: var(--mono); font-size: var(--fs-micro); letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--ink-micro); font-weight: 400;
  border-bottom: 1px solid var(--ink); padding-bottom: 0.25rem; margin: 0 0 0.4rem;
}
.doc__linha { display: grid; grid-template-columns: 15rem 1fr; gap: 0.5rem; padding: 0.22rem 0; font-size: var(--fs-small); border-bottom: 1px solid var(--rule); }
.doc__linha > b { font-weight: 400; color: var(--ink-soft); }
.doc__linha .macro { font-family: var(--mono); font-size: var(--fs-micro); color: var(--ink-micro); }
.doc__sub { padding: 0.15rem 0 0.15rem 1.4rem; font-size: var(--fs-small); color: var(--ink-soft); }

.doc__declara { border: 1px solid var(--ink); padding: 0.9rem 1.1rem; margin: 1.4rem 0 1.2rem; font-size: var(--fs-small); break-inside: avoid; }
.doc__assina { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; margin-top: 2.5rem; break-inside: avoid; }
.doc__assina div { border-top: 1px solid var(--ink); padding-top: 0.35rem; font-family: var(--mono); font-size: var(--fs-micro); color: var(--ink-micro); }

@media print {
  .esconde-no-doc, .topo, footer { display: none !important; }
  .pagina { max-width: none; padding: 0; gap: 0; }
  .documento.ativo { display: block; }
  .doc__secao { page-break-inside: avoid; }
}
@media (max-width: 40rem) {
  .doc__ident { grid-template-columns: 1fr 1fr; }
  .doc__linha { grid-template-columns: 1fr; gap: 0; }
  .doc__assina { grid-template-columns: 1fr; gap: 1.5rem; }
}

.campo__grupo { font-size: var(--fs-small); font-weight: 600; margin: 0 0 0.4rem; }

/* linhas que o cliente adiciona: categoria -> item -> quantidade */
.repetivel { display: flex; flex-direction: column; gap: 0.6rem; }
.repetivel > .rotulo { display: block; }
.linhas { display: flex; flex-direction: column; gap: 0.6rem; }

.linha {
  border: 1px solid var(--rule);
  padding: 0.7rem 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.linha__topo { display: grid; grid-template-columns: 1fr 1fr 5rem auto; gap: 0.5rem; align-items: center; }
/* linha sem categoria tem uma coluna a menos, senao a quantidade estica */
.linha__topo--simples { grid-template-columns: 1fr 5rem auto; }
@media (max-width: 44rem) {
  .linha__topo { grid-template-columns: 1fr 1fr; }
  .linha__topo--simples { grid-template-columns: 1fr 5rem; }
}

.linha__tirar {
  background: none; border: 1px solid var(--rule); color: var(--ink-soft);
  font-family: var(--mono); font-size: var(--fs-micro); cursor: pointer;
  padding: 0.35rem 0.5rem; line-height: 1;
}
.linha__tirar:hover { border-color: var(--acento); color: var(--acento); }

.funcoes { display: flex; flex-direction: column; gap: 0.35rem; }
.funcao { display: grid; grid-template-columns: 5.5rem 1fr; gap: 0.5rem; align-items: center; }
.funcao > span {
  font-family: var(--mono); font-size: var(--fs-micro); color: var(--ink-micro);
  text-align: right; white-space: nowrap;
}
@media (max-width: 30rem) { .funcao { grid-template-columns: 1fr; } .funcao > span { text-align: left; } }
"""

JS = """
/* ---------- a ficha como documento ---------- */

function hoje() {
  var d = new Date(), z = function (n) { return (n < 10 ? '0' : '') + n; };
  return z(d.getDate()) + '/' + z(d.getMonth() + 1) + '/' + d.getFullYear();
}

function esc(t) {
  return String(t == null ? '' : t)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* Monta o documento a partir das MESMAS secoes que geram o texto do envio,
   pra nao existir duas verdades sobre o que a ficha diz. */
function montarDocumento() {
  var h = '';

  h += '<div class="doc__cabeca">'
     +   '<div class="doc__titulo"><h2>Ficha Técnica do Projeto</h2>'
     +     '<p>Anexo II do contrato de prestação de serviços &middot; Borin Projetos Elétricos</p></div>'
     +   '<div class="doc__ident">'
     +     '<div><b>Empresa</b><span>' + esc(v('empresa') || '\u2014') + '</span></div>'
     +     '<div><b>Contato</b><span>' + esc(v('contato') || '\u2014') + '</span></div>'
     +     '<div><b>Projeto</b><span>' + esc(v('projeto_descricao') || '\u2014') + '</span></div>'
     +     '<div><b>Código</b><span>' + esc(v('projeto_numero') || '\u2014') + '</span></div>'
     +   '</div></div>';

  SECOES.forEach(function (s) {
    var corpo = '';
    (s.campos || []).forEach(function (par) {
      var val = v(par[1]);
      if (val) { corpo += '<div class="doc__linha"><b>' + esc(par[0]) + '</b><span>' + esc(val) + '</span></div>'; }
    });
    (s.texto || []).forEach(function (par) {
      var val = v(par[1]);
      if (val) { corpo += '<div class="doc__linha"><b>' + esc(par[0]) + '</b><span>' + esc(val) + '</span></div>'; }
    });
    if (s.extra) { corpo += linhasDoc(s.extra(true)); }
    if (corpo) { h += '<div class="doc__secao"><h3>' + esc(s.titulo) + '</h3>' + corpo + '</div>'; }
  });

  h += '<div class="doc__declara">'
     + '<b>Declaração.</b> Confirmo que as informações registradas nesta ficha são verdadeiras, '
     + 'completas e atuais, e que ela é a base técnica do projeto contratado. Entendo que qualquer '
     + 'pedido posterior será comparado contra esta ficha: divergência entre o que está aqui e o que '
     + 'for entregue é corrigida sem custo e sem limite; alteração de dado registrado aqui é '
     + 'alteração de escopo.'
     + '</div>';

  h += '<div class="doc__assina">'
     +   '<div>' + esc(v('contato') || 'Responsável') + ' &mdash; ' + esc(v('empresa') || 'CONTRATANTE') + '</div>'
     +   '<div>Data: ' + hoje() + '</div>'
     + '</div>';

  return h;
}

/* converte as linhas do texto (rotulo: valor [MACRO]) em linhas do documento */
var QUEBRA = String.fromCharCode(10);

/* separa "rotulo [MACRO]" e estiliza a macro em vez de deixar o colchete cru */
function comMacro(txt) {
  var i = txt.lastIndexOf('[');
  var f = txt.lastIndexOf(']');
  if (i < 0 || f < i) { return esc(txt); }
  return esc(txt.slice(0, i).trim()) + ' <span class="macro">'
       + esc(txt.slice(i + 1, f)) + '</span>' + esc(txt.slice(f + 1));
}

function linhasDoc(txt) {
  var out = '';
  String(txt || '').split(QUEBRA).forEach(function (l) {
    if (!l.trim()) { return; }
    if (l.indexOf('    ') === 0) { out += '<div class="doc__sub">' + esc(l.trim()) + '</div>'; return; }
    if (l.indexOf('- ') === 0) { out += '<div class="doc__linha"><b></b><span>' + comMacro(l.slice(2)) + '</span></div>'; return; }
    if (l === l.toUpperCase() && l.indexOf(':') < 0) { return; }
    var i = l.indexOf(':');
    if (i < 0) { out += '<div class="doc__linha"><b></b><span>' + esc(l) + '</span></div>'; return; }
    var rot = l.slice(0, i), val = l.slice(i + 1).trim();
    out += '<div class="doc__linha"><b>' + esc(rot) + '</b><span>' + comMacro(val) + '</span></div>';
  });
  return out;
}

function verDocumento() {
  var d = document.getElementById('documento');
  d.innerHTML = montarDocumento();
  d.classList.add('ativo');
  document.body.classList.add('modo-documento');
  var a = document.getElementById('acoesDoc');
  if (a) { a.style.display = 'flex'; }
  d.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function voltarAoFormulario() {
  document.getElementById('documento').classList.remove('ativo');
  document.body.classList.remove('modo-documento');
  var a = document.getElementById('acoesDoc');
  if (a) { a.style.display = 'none'; }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function gerarFicha() {
  verDocumento();
}

var CATEGORIAS = %s;

/* Cada linha guarda a macro no value; o cliente so ve o rotulo. O de/para
   inteiro esta em ficha-campos.json — mudar rotulo la nao mexe em macro. */
function addLinha(bt) {
  var caixa = bt.closest('.repetivel');
  var alvo = caixa.querySelector('.linhas');
  var linha = document.createElement('div');
  linha.className = 'linha';

  var topo = document.createElement('div');
  topo.className = 'linha__topo' + (caixa.dataset.categorias ? '' : ' linha__topo--simples');

  var opcoes;
  if (caixa.dataset.categorias) {
    var cat = document.createElement('select');
    cat.innerHTML = '<option value="">categoria…</option>' +
      CATEGORIAS.map(function (c, i) { return '<option value="' + i + '">' + c.rotulo + '</option>'; }).join('');
    opcoes = document.createElement('select');
    opcoes.innerHTML = '<option value="">escolha a categoria antes</option>';
    opcoes.disabled = true;
    cat.addEventListener('change', function () {
      var c = CATEGORIAS[this.value];
      if (!c) { opcoes.innerHTML = '<option value="">escolha a categoria antes</option>'; opcoes.disabled = true; return; }
      opcoes.disabled = false;
      opcoes.innerHTML = c.itens.map(function (i) {
        return '<option value="' + i.macro + '">' + i.rotulo + '</option>';
      }).join('');
    });
    topo.appendChild(cat);
  } else {
    opcoes = document.createElement('select');
    opcoes.innerHTML = caixa.querySelector('template').innerHTML;
  }
  opcoes.className = 'item-macro';
  topo.appendChild(opcoes);

  var qtd = document.createElement('input');
  qtd.type = 'text'; qtd.inputMode = 'numeric'; qtd.value = '1';
  qtd.className = 'item-qtd'; qtd.setAttribute('aria-label', 'Quantidade');
  topo.appendChild(qtd);

  var tirar = document.createElement('button');
  tirar.type = 'button'; tirar.className = 'linha__tirar'; tirar.textContent = 'remover';
  tirar.addEventListener('click', function () { linha.remove(); });
  topo.appendChild(tirar);

  linha.appendChild(topo);

  if (caixa.dataset.funcao) {
    var funcoes = document.createElement('div');
    funcoes.className = 'funcoes';
    linha.appendChild(funcoes);
    /* uma descricao por unidade: 8 valvulas = 8 campos de funcao */
    function refazer() {
      var n = Math.max(0, Math.min(30, parseInt(qtd.value, 10) || 0));
      var atuais = funcoes.querySelectorAll('.funcao');
      var textos = [];
      atuais.forEach(function (f) { textos.push(f.querySelector('input').value); });
      funcoes.innerHTML = '';
      for (var i = 0; i < n; i++) {
        var f = document.createElement('div');
        f.className = 'funcao';
        var rot = document.createElement('span');
        rot.textContent = n > 1 ? 'função ' + (i + 1) + '/' + n : 'função';
        var inp = document.createElement('input');
        inp.type = 'text'; inp.className = 'item-funcao';
        inp.placeholder = 'o que este item faz';
        if (textos[i]) { inp.value = textos[i]; }
        f.appendChild(rot); f.appendChild(inp);
        funcoes.appendChild(f);
      }
    }
    qtd.addEventListener('input', refazer);
    refazer();
  }

  alvo.appendChild(linha);
}

/* Le as linhas de uma caixa: [{macro, qtd, funcoes[]}] */
function lerLinhas(lista) {
  var caixa = document.querySelector('.repetivel[data-lista="' + lista + '"]');
  if (!caixa) { return []; }
  var out = [];
  caixa.querySelectorAll('.linha').forEach(function (l) {
    var m = l.querySelector('.item-macro');
    if (!m || !m.value) { return; }
    var f = [];
    l.querySelectorAll('.item-funcao').forEach(function (i) { f.push(i.value.trim()); });
    out.push({
      macro: m.value,
      rotulo: m.options[m.selectedIndex].textContent,
      qtd: parseInt(l.querySelector('.item-qtd').value, 10) || 1,
      funcoes: f.filter(Boolean)
    });
  });
  return out;
}

function blocoLinhas(titulo, lista) {
  var itens = lerLinhas(lista);
  if (!itens.length) { return ''; }
  var t = '\\n' + titulo.toUpperCase() + '\\n';
  itens.forEach(function (i) {
    t += '- ' + i.rotulo + ' [' + i.macro + '] x' + i.qtd + '\\n';
    i.funcoes.forEach(function (f, n) {
      t += '    ' + (i.qtd > 1 ? (n + 1) + ': ' : '') + f + '\\n';
    });
  });
  return t;
}
""" % catjson

HTML = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ficha do projeto — Borin Projetos Elétricos</title>
<meta name="description" content="A ficha técnica que eu preciso para começar o projeto.">
<meta name="robots" content="noindex">
<link rel="icon" href="%(icone)s">

<style>
/* FONTES */
/* BASE-FORM */
%(css)s
</style>

<div class="pagina">

  <header class="topo">
    <div class="marca">
      <svg viewBox="0 0 420 128" role="img" aria-label="Borin — projetos elétricos industriais">
        <g font-family="Inter, 'Segoe UI', Arial, sans-serif">
          <text x="0" y="62" font-size="72" font-weight="700" letter-spacing="5.76" fill="currentColor">BORIN</text>
          <rect x="0" y="84" width="316" height="4" fill="currentColor"></rect>
          <rect x="322" y="79" width="14" height="14" fill="var(--acento)"></rect>
          <text x="0" y="118" font-size="16" font-weight="500" letter-spacing="1.92" fill="currentColor" opacity="0.62">projetos elétricos industriais</text>
        </g>
      </svg>
    </div>

    <a class="voltar" href="/">← Início</a>

    <div>
      <span class="rotulo">Ficha do projeto</span>
      <h1 id="titulo">O que eu preciso para começar.</h1>
      <p class="topo__texto">O que é padrão da sua empresa fica no <a href="/padrao">padrão do cliente</a> e não se repete aqui. Estimativa serve em tudo que for número.</p>
    </div>

    <div class="perfil-barra" id="perfilBarra">
      <span class="perfil-barra__topo"><span class="no" aria-hidden="true"></span><span class="rotulo">Seu padrão está salvo</span></span>
      <p class="perfil-barra__resumo" id="perfilResumo"></p>
      <div class="perfil-barra__acoes">
        <a class="link-acao" href="/padrao" style="text-decoration: none;">Editar o padrão</a>
      </div>
    </div>
  </header>

  <form onsubmit="return false;">

    <div class="bloco perfil">
      <div class="bloco__cabeca">
        <h2>Identificação</h2>
        <span class="marca-perfil">do padrão</span>
      </div>
      <div class="grade">
        <div class="campo"><label for="empresa">Empresa</label><input type="text" id="empresa" data-perfil></div>
        <div class="campo"><label for="contato">Contato</label><input type="text" id="contato" data-perfil></div>
      </div>
    </div>

%(corpo)s
    <div class="bloco" style="margin-bottom: 0;">
      <div class="bloco__cabeca"><h2>Enviar</h2></div>
      <div class="acoes">
        <button type="button" class="botao" onclick="enviarWhats()">Enviar pelo WhatsApp</button>
        <button type="button" class="botao botao--vazado" onclick="baixar()">Baixar como arquivo</button>
        <button type="button" class="botao botao--vazado" onclick="gerarFicha()">Gerar ficha para assinar</button>
      </div>
      <p class="aviso">Se você entrou na sua conta, a ficha fica salva nela e dá pra continuar de outro computador. Sem conta, ela não sai deste navegador.</p>
      <pre class="resumo" id="resumo"></pre>
    </div>

  </form>

  <div class="documento" id="documento"></div>

  <div class="acoes esconde-no-doc" id="acoesDoc" style="display:none">
    <button type="button" class="botao" onclick="window.print()">Salvar em PDF</button>
    <button type="button" class="botao botao--vazado" onclick="voltarAoFormulario()">Voltar ao formulário</button>
  </div>

  <footer>
    <div class="carimbo">
      <div class="carimbo__marca">
        <svg viewBox="0 0 160 72" role="img" aria-label="BRN">
          <g font-family="Inter, 'Segoe UI', Arial, sans-serif" fill="currentColor">
            <text x="0" y="52" font-size="60" font-weight="700" letter-spacing="4.8">BRN</text>
          </g>
        </svg>
      </div>
      <div><span class="c-campo">DOCUMENTO</span><span class="c-valor">Ficha do projeto</span></div>
      <div><span class="c-campo">CONTATO</span><span class="c-valor">contato@borinprojetos.com.br</span></div>
      <div><span class="c-campo">LOCAL</span><span class="c-valor">Caxias do Sul · RS</span></div>
    </div>
  </footer>

</div>

<script>
/* BASE-JS */
%(js)s

var DOC = 'Ficha do projeto';

var SECOES = %(secoes)s;

/* uma ficha por projeto: a chave leva o codigo que o cliente digitou */
ligarConta(function () {
  var c = (v('projeto_numero') || '').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 30);
  return c ? 'projeto:' + c : 'projeto';
});

iniciarForm({ recolher: true });
</script>

<!-- ANALYTICS -->
"""

# SECOES do texto que vai pro Mateus: rotulo legivel + macro entre colchetes
secoes_js = []
for s in d["secoes"]:
    campos = []
    for c in s["campos"]:
        if c["tipo"] in ("texto", "numero"):
            campos.append([c["rotulo"], s["id"] + "_" + c["id"]])
    item = {"titulo": s["titulo"], "campos": campos}
    secoes_js.append(item)

extra = []
for s in d["secoes"]:
    listas = [c for c in s["campos"] if c["tipo"] in ("lista", "opcao")]
    if listas or s.get("repetivel"):
        extra.append((s["id"], s["titulo"], listas, s.get("repetivel")))

js_secoes = "[\n"
for i, s in enumerate(d["secoes"]):
    campos = [[c["rotulo"], s["id"] + "_" + c["id"]]
              for c in s["campos"] if c["tipo"] in ("texto", "numero")]
    js_secoes += "  { titulo: %s,\n    campos: %s,\n" % (
        json.dumps(s["titulo"], ensure_ascii=False), json.dumps(campos, ensure_ascii=False))
    partes = []
    for c in s["campos"]:
        if c["tipo"] == "lista":
            partes.append("      t += rotuloLista(%s, %s);\n"
                          % (json.dumps(c["rotulo"], ensure_ascii=False),
                             json.dumps(s["id"] + "_" + c["id"])))
        elif c["tipo"] == "opcao":
            partes.append("      t += rotuloOpcao(%s, %s);\n"
                          % (json.dumps(c["rotulo"], ensure_ascii=False),
                             json.dumps(s["id"] + "_" + c["id"])))
        elif c["tipo"] == "marca":
            partes.append("      t += v(%s) ? %s + ': sim\\n' : '';\n"
                          % (json.dumps(s["id"] + "_" + c["id"]),
                             json.dumps(c["rotulo"], ensure_ascii=False)))
    if s.get("repetivel"):
        partes.append("      t += blocoLinhas(%s, %s);\n"
                      % (json.dumps(s["repetivel"]["titulo"], ensure_ascii=False),
                         json.dumps(s["repetivel"]["id"])))
    if partes:
        js_secoes += "    extra: function () {\n      var t = '';\n" + "".join(partes) + "      return t;\n    } "
    js_secoes += "},\n"
js_secoes += ("  { titulo: %s, extra: function () { return blocoLinhas('', 'campo'); } }\n]"
              % json.dumps(cat["titulo"], ensure_ascii=False))

AJUDA = """
/* le um select mostrando o rotulo e a macro, que e o que o gerador consome */
function rotuloLista(rotulo, id) {
  var el = document.getElementById(id);
  if (!el || !el.value) { return ''; }
  return rotulo + ': ' + el.options[el.selectedIndex].textContent + ' [' + el.value + ']\\n';
}
function rotuloOpcao(rotulo, nome) {
  var el = document.querySelector('input[name="' + nome + '"]:checked');
  if (!el) { return ''; }
  var t = el.closest('.opcao').querySelector('.opcao__titulo').textContent;
  return rotulo + ': ' + t + (el.value ? ' [' + el.value + ']' : '') + '\\n';
}
"""

io.open(SAIDA, "w", encoding="utf-8").write(HTML % {
    "icone": ICONE, "css": CSS, "corpo": corpo,
    "js": JS + AJUDA, "secoes": js_secoes,
})
print("  _projeto.html gerado — %d secoes, %d categorias de campo"
      % (len(d["secoes"]), len(cat["categorias"])))
