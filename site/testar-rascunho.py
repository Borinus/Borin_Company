# -*- coding: utf-8 -*-
"""Prova que o link de rascunho preenche o formulario CERTO — e que sabe falhar.

O RISCO QUE ESTE TESTE MATA: o rascunho atravessa tres fronteiras — Python
codifica (comercial/rascunho.py), a pagina decodifica (_orcamento.html) e o
aplicarFormulario() casa cada chave com um id do formulario. Divergencia em
QUALQUER uma e falha calada: o campo simplesmente nao aparece preenchido e
ninguem ve erro nenhum. Entao aqui:

  1. o decode replicado do site (rodado no node, LINHA POR LINHA igual a
     pagina) devolve exatamente o JSON que o Python codificou — com acento,
     com base64url (-/_) e com padding cortado
  2. as linhas do decode replicadas aqui EXISTEM na pagina — se alguem mexer
     no decode do site, este teste quebra e cobra a atualizacao
  3. toda chave de `campos` e um id de input real do _orcamento.html, e todo
     radio usa name/value que existem la
  4. link corrompido LANCA no decode (o catch da pagina tem o que pegar)
  5. defeito plantado: corromper um byte tem que ser DETECTADO — prova que a
     comparacao do passo 1 nao e enfeite
  6. rascunho.py recusa "10 a 15" em campo de contagem, em voz alta
  7. o loader esta no template E no build (build velho sem o loader = FALHA)
  8. o IIFE do loader e EXTRAIDO DO BUILD e EXECUTADO no node com DOM de
     mentira: preenche, reseta o form, tira a isca de link forjado, limpa o
     hash, e avisa em voz alta no link quebrado e no aplicar que lanca. A
     revisao de 10/08/2026 provou por mutacao que checar só a PRESENCA do
     texto deixava um loader morto (nunca invocado, ou lendo a chave errada
     do hash) passar 28/28 verde — este passo mata essa classe inteira.

Roda com: python site/testar-rascunho.py   (precisa do node no PATH)
"""

import importlib.util
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(RAIZ, "site", "_orcamento.html")
BUILD = os.path.join(RAIZ, "site", "orcamento.html")

_s = importlib.util.spec_from_file_location(
    "rasc", os.path.join(RAIZ, "comercial", "rascunho.py"))
rasc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(rasc)

passos = []


def P(nome, ok, detalhe=""):
    passos.append((nome, ok))
    print("  %s %-52s %s" % ("ok   " if ok else "FALHA", nome, detalhe))


# as MESMAS linhas do decode da pagina; o passo 2 confere que continuam la
DECODE_DA_PAGINA = [
    "var b = cru.replace(/-/g, '+').replace(/_/g, '/');",
    "while (b.length % 4) { b += '='; }",
    "dados = JSON.parse(decodeURIComponent(escape(atob(b))));",
]


def decodificar_no_node(cru):
    """Roda o decode da pagina no node. Devolve (json, None) ou (None, erro)."""
    js = (
        "var cru = process.argv[1];\n"
        "var dados;\n"
        "try {\n  " + "\n  ".join(DECODE_DA_PAGINA) + "\n"
        "} catch (e) { console.log('LANCOU:' + e.name); process.exit(0); }\n"
        "console.log(JSON.stringify(dados));\n"
    )
    r = subprocess.run(["node", "-e", js, cru],
                       capture_output=True, text=True, encoding="utf-8",
                       timeout=30)
    if r.returncode != 0:
        raise SystemExit("node falhou: " + (r.stderr or "")[:300])
    saida = (r.stdout or "").strip()
    if saida.startswith("LANCOU:"):
        return None, saida
    return json.loads(saida), None


class Args:
    """O argparse de mentira: os campos que o montar_dados() le."""
    def __init__(self, **kw):
        base = dict(empresa="", contato="", email="", fone="", equipamento="",
                    codigo="", escopo="?", nr12="?", canal="email",
                    io="", acionamentos="", seg="", prazo="")
        base.update(kw)
        self.__dict__.update(base)


print()
print("  " + "=" * 70)
print("  LINK DE RASCUNHO — codifica no Python, decodifica como a pagina")
print("  " + "=" * 70)

# ---------------------------------------------------------------- passo 1
# o caso cheio, com acento, cedilha e travessao: prova o UTF-8 de ponta a ponta
rasc.ERROS[:] = []
a = Args(empresa="Aço & Cia — Pintura Ltda", contato="João Vieira",
         email="joao@acocia.com.br", fone="+55 54 99911-2233",
         equipamento="instalação de estufa de pintura", codigo="EQ-77",
         escopo="B", nr12="sim", canal="email+whats",
         io="96", acionamentos="8", seg="6", prazo="15/09/2026")
dados = rasc.montar_dados(a)
cru = rasc.link_de(dados).split("#rascunho=", 1)[1]
P("rascunho.py nao acusou erro no caso valido", not rasc.ERROS,
  "; ".join(rasc.ERROS))

decodado, lancou = decodificar_no_node(cru)
P("decode da pagina devolve o JSON identico", decodado == dados and not lancou,
  lancou or ("acentos ok" if decodado == dados else "DIVERGIU"))

# payload desenhado pra FORCAR '-' e '_' no base64url — texto comum quase nunca
# gera os sextetos 62/63, e sem eles a troca -/+ e _// do decode passaria a
# vida sem ser exercitada. "ç" (byte final A7, bits baixos 11) colado num
# travessao (lead E2) da o '+', e um '?' literal como 3o byte do grupo da o
# '/'; o prefixo X*i so desliza o alinhamento ate os dois cairem no lugar.
alfabeto = None
for i in range(12):
    b = Args(empresa="X" * (i % 3 + 1), contato="João", email="x@y.com.br",
             equipamento="pintura eletrostática — cabine %d? ç— aço" % i,
             escopo="B", nr12="sim", io="96")
    d2 = rasc.montar_dados(b)
    c2 = rasc.link_de(d2).split("#rascunho=", 1)[1]
    if "-" in c2 and "_" in c2 and len(c2) % 4 != 0:
        alfabeto = (d2, c2)
        break
P("ha payload com '-', '_' e padding cortado", alfabeto is not None,
  "" if alfabeto else "nenhum em 12 alinhamentos — o truque do ç—/? quebrou")
if alfabeto:
    dec_a, lanc_a = decodificar_no_node(alfabeto[1])
    P("a troca -/+ e _// do decode funciona", dec_a == alfabeto[0] and not lanc_a,
      lanc_a or "")

# tambem o caso minimo, sem nenhum campo de contagem
rasc.ERROS[:] = []
minimo = rasc.montar_dados(Args(empresa="X", contato="Y", email="x@y.com.br",
                                equipamento="painel"))
dec2, lanc2 = decodificar_no_node(rasc.link_de(minimo).split("#rascunho=")[1])
P("caso minimo tambem roda redondo", dec2 == minimo and not lanc2, lanc2 or "")

# ---------------------------------------------------------------- passo 2
tpl = open(TEMPLATE, encoding="utf-8").read()
build = open(BUILD, encoding="utf-8").read() if os.path.exists(BUILD) else ""
for ln in DECODE_DA_PAGINA:
    P("template contem: %s" % ln[:42], ln in tpl)
    # o build e o que vai pro ar: decode velho SO no build (esqueceu o
    # montar.py) quebrava acento em producao com a suite verde
    P("build contem:    %s" % ln[:42], ln in build)
P("delete da isca esta no template e no build",
  "delete dados.campos.website" in tpl and "delete dados.campos.website" in build)
# o input date rejeita valor nao-ISO EM SILENCIO: se data_iso() regredir e
# devolver 15/09/2026 cru, o campo fica vazio e o roundtrip nem percebe
P("data_iso converte 15/09/2026 -> 2026-09-15",
  rasc.data_iso("15/09/2026") == "2026-09-15")
P("prazo no rascunho sai ISO pro input date",
  re.fullmatch(r"\d{4}-\d{2}-\d{2}", dados["campos"].get("prazo", "")) is not None,
  repr(dados["campos"].get("prazo")))

# ---------------------------------------------------------------- passo 3
ids_do_form = set(re.findall(r'id="([a-z_]+)"', tpl))
radios_do_form = {}
for name, value in re.findall(r'name="([a-z0-9]+)"\s+value="([^"]*)"', tpl):
    radios_do_form.setdefault(name, set()).add(value)

for chave in dados["campos"]:
    P("campo '%s' existe no formulario" % chave, chave in ids_do_form)
for nome, valor in dados["radios"].items():
    P("radio %s=%s existe no formulario" % (nome, valor),
      valor in radios_do_form.get(nome, set()),
      "tem: %s" % sorted(radios_do_form.get(nome, set())))

# a isca de robo nunca pode sair preenchida do rascunho.py
P("rascunho.py nunca inclui a isca 'website'",
  "website" not in dados["campos"] and "website" not in minimo["campos"])

# ---------------------------------------------------------------- passo 4
_, lancou_corrompido = decodificar_no_node(cru[: len(cru) // 2] + "!!!" )
P("link corrompido LANCA (o catch da pagina age)",
  bool(lancou_corrompido), lancou_corrompido or "decodificou lixo sem reclamar")

# ---------------------------------------------------------------- passo 5
# defeito plantado: um byte trocado no meio do base64 precisa ser DETECTADO
# (JSON diferente ou decode lancando). Se passar igual, a comparacao e enfeite.
meio = len(cru) // 2
trocado = cru[:meio] + ("A" if cru[meio] != "A" else "B") + cru[meio + 1:]
dec_def, lanc_def = decodificar_no_node(trocado)
P("defeito plantado foi detectado", dec_def != dados or bool(lanc_def),
  "byte trocado passou batido!" if (dec_def == dados and not lanc_def) else "")

# ---------------------------------------------------------------- passo 6
r = subprocess.run(
    [sys.executable, os.path.join(RAIZ, "comercial", "rascunho.py"),
     "--io", "10 a 15", "--empresa", "X"],
    capture_output=True, text=True, encoding="utf-8", errors="replace")
P("'10 a 15' em --io e recusado em voz alta",
  r.returncode != 0 and "número" in (r.stdout + r.stderr),
  "saiu %d" % r.returncode)

r2 = subprocess.run(
    [sys.executable, os.path.join(RAIZ, "comercial", "rascunho.py"),
     "--equipamento", "painel", "--email", "x@y.com.br"],
    capture_output=True, text=True, encoding="utf-8", errors="replace")
P("faltando empresa/contato avisa FALTA mas gera o link",
  r2.returncode == 0 and "FALTA" in r2.stdout and "#rascunho=" in r2.stdout)

# seg_qtd mora atras do "tem NR-12": mandar --seg sem --nr12 sim enviaria um
# numero que a tela esconde e o resumo omite — invisivel na conferencia
r3 = subprocess.run(
    [sys.executable, os.path.join(RAIZ, "comercial", "rascunho.py"),
     "--empresa", "X", "--seg", "6"],
    capture_output=True, text=True, encoding="utf-8", errors="replace")
P("--seg sem --nr12 sim e recusado em voz alta",
  r3.returncode != 0 and "nr12" in (r3.stdout + r3.stderr),
  "saiu %d" % r3.returncode)

# ---------------------------------------------------------------- passo 7
P("template tem o loader de rascunho", "carregarRascunhoDoLink" in tpl)
P("build (orcamento.html) tem o loader — senao e build velho",
  "carregarRascunhoDoLink" in build,
  "" if "carregarRascunhoDoLink" in build else "rode: python site/montar.py")

# ---------------------------------------------------------------- passo 8
# extrai o IIFE do BUILD (o codigo que vai pro ar) e EXECUTA no node com um
# DOM de mentira que registra cada chamada. A ancora `\n})();` exige o IIFE
# INVOCADO: um loader definido e nunca chamado nem casa no regex.
m_iife = re.search(r"\(function carregarRascunhoDoLink\(\)[\s\S]*?\n\}\)\(\);",
                   build)
P("IIFE invocado extraido do build", m_iife is not None)

HARNESS = """
var hash = process.argv[1], modo = process.argv[2], iife = process.argv[3];
var registro = { aplicar: null, avisos: [], resumo: null, resumo_ativo: false,
                 replace: 0, reset: 0 };
var location = { hash: hash, pathname: '/orcamento', search: '' };
var history = { replaceState: function () { registro.replace++; } };
function avisoConta(t) { registro.avisos.push(t); }
function montar() { return 'RESUMO-MONTADO'; }
function aplicarFormulario(d) {
  if (modo === 'lanca') { throw new Error('seletor invalido'); }
  registro.aplicar = d;
  return Object.keys(d.campos || {}).length;
}
var resumoEl = { textContent: null, classList: {
  ativo: false,
  add: function () { this.ativo = true; },
  contains: function () { return this.ativo; } } };
var document = {
  getElementById: function (id) {
    if (id === 'formOrcamento') { return { reset: function () { registro.reset++; } }; }
    if (id === 'resumo') { return resumoEl; }
    return null;
  },
  querySelector: function () { return { textContent: '' }; }
};
eval(iife);
registro.resumo = resumoEl.textContent;
registro.resumo_ativo = resumoEl.classList.ativo;
console.log(JSON.stringify(registro));
"""


def rodar_loader(hash_, modo="ok"):
    if not m_iife:
        return None
    r = subprocess.run(["node", "-e", HARNESS, hash_, modo, m_iife.group(0)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=30)
    if r.returncode != 0:
        raise SystemExit("harness falhou: " + (r.stderr or "")[:300])
    return json.loads(r.stdout)


if m_iife:
    # link forjado COM a isca preenchida: o loader tem que tira-la sozinho
    forjado = {"campos": dict(dados["campos"], website="ROBO"),
               "radios": dict(dados["radios"])}
    cru_forjado = rasc.link_de(forjado).split("#rascunho=", 1)[1]

    reg = rodar_loader("#rascunho=" + cru_forjado)
    P("loader executado: aplica, reseta o form, limpa o hash",
      reg["aplicar"] is not None and reg["reset"] == 1 and reg["replace"] == 1,
      "reset=%s replace=%s" % (reg["reset"], reg["replace"]))
    P("loader tira a isca do link forjado",
      reg["aplicar"] is not None and "website" not in reg["aplicar"]["campos"]
      and reg["aplicar"]["campos"].get("empresa") == dados["campos"]["empresa"])
    P("banner e resumo saem do loader executado",
      bool(reg["avisos"]) and reg["avisos"][0].startswith("Rascunho carregado")
      and reg["resumo"] == "RESUMO-MONTADO" and reg["resumo_ativo"])

    reg2 = rodar_loader("#rascunho=!!!lixo!!!")
    P("link quebrado: aviso em voz alta, nada aplicado",
      reg2["aplicar"] is None and any("quebrado" in x for x in reg2["avisos"])
      and reg2["replace"] == 0)

    reg3 = rodar_loader("#rascunho=" + cru_forjado, modo="lanca")
    P("aplicar lancando: aviso em voz alta, nada calado",
      any("consegui aplicar" in x for x in reg3["avisos"])
      and reg3["replace"] == 0)

    reg4 = rodar_loader("#outra=coisa")
    P("hash sem rascunho: loader nao mexe em nada",
      not reg4["avisos"] and reg4["aplicar"] is None and reg4["reset"] == 0)

print()
bons = sum(1 for _, o in passos if o)
print("  " + "=" * 70)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o in passos:
    if not o:
        print("    FALHOU: %s —" % n)
print("  " + "=" * 70)
print()
raise SystemExit(0 if bons == len(passos) else 1)
