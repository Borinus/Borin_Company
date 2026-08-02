"""
Monta a proposta a partir do pedido e manda por email.

    python comercial/orcamento.py --de exemplo
    python comercial/orcamento.py --email joao@empresa.com --empresa "Metalurgica Serra" \\
        --contato "Joao Vieira" --equipamento "Painel de estufa" --codigo 04003478 \\
        --io 96 --acionamentos 8 --seguranca 6 --escopo B --itens-manuais 2 --abertura
    ... --enviar            manda pro cliente
    ... --enviar --para-mim manda so pro Mateus, pra conferir antes

O valor sai de comercial/calcular.py — sem digitacao, sem planilha no meio.
A proposta vai como HTML no corpo do email: o cliente ve o documento, nao um
anexo que ele precisa abrir. Uma copia fica em comercial/propostas/ pra
imprimir em PDF pelo navegador quando ele pedir.

O numero da proposta e sequencial por ano, contado pelos arquivos ja gerados.
"""

import argparse
import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.join(RAIZ, "comercial")
PASTA = os.path.join(AQUI, "propostas")
API = "https://borinprojetos.com.br/api/orcamento"

# Paleta e fontes do email. Ficam no modulo porque o reenviar-contrato.py monta
# outro email que chega na mesma caixa — se divergir, parecem duas empresas.
T, CINZA, RULE, ACENTO = "#111111", "#6B6B6B", "#DCDCDC", "#C1121F"
MONO = "Consolas,'Courier New',monospace"
SANS = "'Segoe UI',Arial,Helvetica,sans-serif"

_s = importlib.util.spec_from_file_location("calc", os.path.join(AQUI, "calcular.py"))
calc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(calc)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

# prazo por faixa de pagina, da tabela de precificacao.md
PRAZOS = [(15, "5 dias úteis"), (25, "8 dias úteis"), (40, "10 dias úteis"),
          (80, "12 dias úteis"), (10 ** 9, "a combinar")]


def prazo(paginas):
    for teto, txt in PRAZOS:
        if paginas <= teto:
            return txt
    return "a combinar"


def numero():
    os.makedirs(PASTA, exist_ok=True)
    ano = datetime.date.today().year
    n = len([a for a in os.listdir(PASTA) if a.startswith("PROP-%d-" % ano)]) + 1
    return "PROP-%d-%03d" % (ano, n)


def esc(t):
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def html(p):
    """A proposta. Email nao aceita CSS externo nem grade moderna: tudo inline,
    tabela pra layout. Feio de escrever, e o unico jeito que chega igual no
    Gmail, no Outlook e no celular."""
    def linha(rot, val, forte=False):
        return (
            '<tr>'
            '<td style="padding:7px 0;border-bottom:1px solid %s;color:%s;font-size:14px">%s</td>'
            '<td style="padding:7px 0;border-bottom:1px solid %s;text-align:right;'
            'font-size:14px;%s">%s</td></tr>'
            % (RULE, CINZA, esc(rot), RULE, "font-weight:600" if forte else "", esc(val)))

    # o desconto sai da lista pra entrar DEPOIS do valor cheio: mostrar
    # "-50%" antes do numero que ele desconta nao se le
    somas = [(r, v) for r, v in p["linhas"] if v >= 0]
    abates = [(r, v) for r, v in p["linhas"] if v < 0]
    itens = "".join(linha(r, calc.brl(v)) for r, v in somas)

    if abates:
        itens += (
            '<tr><td style="padding:7px 0;border-bottom:1px solid %s;color:%s;font-size:14px">'
            'Valor cheio</td><td style="padding:7px 0;border-bottom:1px solid %s;text-align:right;'
            'font-size:14px;color:%s;text-decoration:line-through">%s</td></tr>'
            % (RULE, CINZA, RULE, CINZA, calc.brl(p["valor_cheio"])))
        itens += "".join(linha(r, calc.brl(v)) for r, v in abates)

    total = (
        '<tr><td style="padding:12px 0 0;font-size:15px;font-weight:600">Total</td>'
        '<td style="padding:12px 0 0;text-align:right;font-size:22px;font-weight:700">%s</td></tr>'
        % calc.brl(p["total"]))

    def bloco(rot, val):
        return ('<td style="padding:0 18px 0 0;vertical-align:top">'
                '<div style="font-family:%s;font-size:10px;letter-spacing:.08em;'
                'text-transform:uppercase;color:%s;padding-bottom:3px">%s</div>'
                '<div style="font-size:14px">%s</div></td>' % (MONO, CINZA, esc(rot), esc(val)))

    entrega = "".join(
        '<tr><td style="padding:4px 0;font-size:13px;color:%s">%s</td></tr>' % (CINZA, esc(x))
        for x in p["entrega"])

    return """<div style="margin:0;padding:24px 16px;background:#F4F4F4;font-family:%(sans)s">
<div style="max-width:640px;margin:0 auto;background:#fff;border:1px solid %(t)s">

<div style="padding:26px 28px 20px;border-bottom:1px solid %(t)s">
  <div style="font-size:30px;font-weight:700;letter-spacing:4px;color:%(t)s">BORIN</div>
  <div style="height:3px;background:%(t)s;width:170px;margin:5px 0 0"></div>
  <div style="display:inline-block;width:8px;height:8px;background:%(acento)s;margin:0 0 0 174px;
       position:relative;top:-9px"></div>
  <div style="font-family:%(mono)s;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
       color:%(cinza)s;margin-top:-4px">projetos elétricos industriais</div>
</div>

<div style="padding:22px 28px 0">
  <div style="font-family:%(mono)s;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
       color:%(cinza)s">Proposta %(numero)s</div>
  <h1 style="font-size:22px;font-weight:700;margin:6px 0 4px;letter-spacing:-.02em">%(equipamento)s</h1>
  <div style="font-size:14px;color:%(cinza)s">%(empresa)s%(contato)s</div>
</div>

<table style="width:100%%;border-collapse:collapse;margin:20px 0 0"><tr>
  <td style="padding:0 28px"><table style="border-collapse:collapse"><tr>%(cabecalho)s</tr></table></td>
</tr></table>

<div style="padding:24px 28px 0">
  <div style="font-family:%(mono)s;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
       color:%(cinza)s;border-bottom:1px solid %(t)s;padding-bottom:5px">O que está incluso</div>
  <table style="width:100%%;border-collapse:collapse;margin-top:8px">%(entrega)s</table>
</div>

<div style="padding:24px 28px 0">
  <div style="font-family:%(mono)s;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
       color:%(cinza)s;border-bottom:1px solid %(t)s;padding-bottom:5px">Valor</div>
  <table style="width:100%%;border-collapse:collapse;margin-top:6px">%(itens)s%(total)s</table>
  %(nota_abertura)s
</div>

<div style="padding:24px 28px 0">
  <div style="font-family:%(mono)s;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
       color:%(cinza)s;border-bottom:1px solid %(t)s;padding-bottom:5px">Condições</div>
  <table style="width:100%%;border-collapse:collapse;margin-top:6px">
    %(cond)s
  </table>
</div>

<div style="padding:26px 28px 28px">
  <a href="https://borinprojetos.com.br/cadastro" style="display:inline-block;background:%(t)s;
     color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:13px 22px">Preencher meus dados e gerar o contrato</a>
  <div style="font-size:12px;color:%(cinza)s;margin-top:10px">
    São nove campos: os dados da empresa e quem assina. Em seguida eu devolvo o contrato
    já preenchido, faltando só a sua assinatura. Se preferir, responda este email e eu mando
    o contrato em branco para você completar.
  </div>
</div>

<div style="padding:14px 28px;border-top:1px solid %(rule)s;font-family:%(mono)s;font-size:10px;
     color:%(cinza)s">
  Borin Projetos Elétricos &middot; CNPJ 65.749.097/0001-85 &middot; Caxias do Sul / RS<br>
  contato@borinprojetos.com.br &middot; borinprojetos.com.br
</div>

</div></div>""" % {
        "sans": SANS, "mono": MONO, "t": T, "cinza": CINZA, "rule": RULE, "acento": ACENTO,
        "numero": p["numero"], "equipamento": esc(p["equipamento"]),
        "empresa": esc(p["empresa"]),
        "contato": (" &middot; " + esc(p["contato"])) if p["contato"] else "",
        "cabecalho": bloco("Escopo", p["escopo_txt"]) + bloco("Páginas estimadas", str(p["paginas"]))
                     + bloco("Prazo", p["prazo"]) + bloco("Validade", "3 dias"),
        "entrega": entrega, "itens": itens, "total": total,
        "nota_abertura": (
            '<div style="font-size:12px;color:%s;margin-top:10px">A condição de início vale uma vez '
            'por cliente. Você não me conhece, e eu preciso do primeiro projeto pra mostrar o padrão.'
            '</div>' % CINZA) if p["abertura"] else "",
        "cond": "".join(linha(r, v) for r, v in p["condicoes"]),
    }


def texto(p):
    """Versao em texto puro, pro arquivo e pra quem le email sem HTML."""
    t = "PROPOSTA %s — BORIN PROJETOS ELÉTRICOS\n" % p["numero"]
    t += "=" * 52 + "\n\n"
    t += "%s\n%s%s\n\n" % (p["equipamento"], p["empresa"],
                           (" · " + p["contato"]) if p["contato"] else "")
    t += "Escopo: %s\nPáginas estimadas: %d\nPrazo: %s\nValidade: 3 dias\n\n" % (
        p["escopo_txt"], p["paginas"], p["prazo"])
    t += "O QUE ESTÁ INCLUSO\n"
    for x in p["entrega"]:
        t += "  - %s\n" % x
    t += "\nVALOR\n"
    for r, v in p["linhas"]:
        t += "  %-44s %14s\n" % (r, calc.brl(v))
    if p["total"] != p["valor_cheio"]:
        t += "  %-44s %14s\n" % ("Valor cheio", calc.brl(p["valor_cheio"]))
    t += "  %-44s %14s\n\n" % ("TOTAL", calc.brl(p["total"]))
    t += "CONDIÇÕES\n"
    for r, v in p["condicoes"]:
        t += "  %-44s %14s\n" % (r, v)
    t += "\nAceitar: https://borinprojetos.com.br/entrar\n"
    return t


def composicao(p, o):
    """A linha de composicao do Quadro Resumo do contrato: mesma conta da
    proposta, escrita numa linha."""
    partes = ["%d páginas × R$ 235" % p["paginas"]]
    if o.itens_manuais:
        partes.append("%d %s × R$ 250" % (o.itens_manuais,
                                          "item" if o.itens_manuais == 1 else "itens"))
    if o.setup_padrao:
        partes.append("setup de padrão do cliente R$ 1.000")
    for liga, txt in ((o.urgencia, "urgência +30%"), (o.arquivo_fonte, "arquivo-fonte +50%"),
                      (o.abertura, "condição de abertura −50%")):
        if liga:
            partes.append(txt)
    return " · ".join(partes)


def montar(o):
    paginas = o.paginas or calc.estimar_paginas(o.io, o.acionamentos, o.seguranca, o.escopo)
    r = calc.calcular(paginas, o.itens_manuais, o.setup_padrao,
                      o.urgencia, o.arquivo_fonte, o.abertura)
    escopo = o.escopo.upper()
    entrega = [
        "Diagramas de alimentação, comando e I/O",
        "Régua de bornes com destino de cada ponto",
        "Layout do painel e design térmico",
        "Lista de materiais com código de fabricante",
        "Arquitetura de CLP e lista de I/O",
        "Identificações prontas para impressão",
        "Databook com manual de cada equipamento",
        "Conferência de 12 blocos antes da entrega",
    ]
    if escopo == "B":
        entrega += ["Interconexão de campo e base de cabos",
                    "Lista de instalação com horas estimadas"]
    hoje = datetime.date.today()
    return {
        "numero": o.numero or numero(),
        "data": "%d de %s de %d" % (hoje.day, MESES[hoje.month - 1], hoje.year),
        "empresa": o.empresa, "contato": o.contato, "equipamento": o.equipamento,
        "codigo": o.codigo, "email": o.email,
        "escopo_txt": "B — painel e instalação" if escopo == "B" else "A — painel",
        "paginas": paginas, "prazo": prazo(paginas), "entrega": entrega,
        "linhas": r["linhas"], "valor_cheio": r["valor_cheio"], "total": r["total"],
        "abertura": o.abertura,
        "condicoes": [
            ("Entrada, na assinatura", "40%"),
            ("Saldo, na aprovação", "60% em 15 dias"),
            ("Correção de erro meu", "sem limite"),
            ("Alteração de escopo inclusa", "2 rodadas"),
            ("Sigilo", "2 anos, em contrato"),
        ],
    }


def enviar(p, corpo_html, para_mim, anexos=None):
    # nada de marca de copia: o objetivo do --para-mim e ver exatamente o
    # que o cliente vai abrir, inclusive o assunto
    d = {
        "empresa": p["empresa"] or "cliente",
        "contato": p["contato"], "codigo": p["codigo"],
        "equipamento": p["equipamento"],
        "doc": p.get("doc") or ("Proposta " + p["numero"]),
        "email": "" if para_mim else p["email"],
        # o Worker so entrega no cliente com esta marca; sem ela vai pro Mateus.
        # --para-mim continua sendo copia de conferencia, identica ao que ele veria.
        "para_cliente": not para_mim,
        "intencao": "proposta", "html": True, "texto": corpo_html,
    }
    if anexos:
        d["anexos"] = anexos
    f = os.path.join(tempfile.gettempdir(), "borin-proposta.json")
    io.open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False))
    try:
        r = subprocess.run(["curl", "-s", "-X", "POST", API,
                            "-H", "Content-Type: application/json", "--data-binary", "@" + f],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(f)
    return '"ok":true' in (r.stdout or "")


EXEMPLO = dict(email="mateusborin20@gmail.com", empresa="Metalúrgica Serra Ltda",
               contato="João Vieira", equipamento="Painel de interface de sistema de pintura",
               codigo="04003478", io=96, acionamentos=8, seguranca=6, escopo="B",
               itens_manuais=2, setup_padrao=True, abertura=True)


def main():
    a = argparse.ArgumentParser(description="Monta e envia a proposta")
    a.add_argument("--de", choices=["exemplo"], help="usa o 04003478 como exemplo")
    a.add_argument("--email"); a.add_argument("--empresa", default="")
    a.add_argument("--contato", default=""); a.add_argument("--equipamento", default="Projeto elétrico")
    a.add_argument("--codigo", default=""); a.add_argument("--numero")
    a.add_argument("--paginas", type=int)
    a.add_argument("--io", type=int, default=0); a.add_argument("--acionamentos", type=int, default=0)
    a.add_argument("--seguranca", type=int, default=0)
    a.add_argument("--escopo", default="A", choices=["A", "B", "a", "b"])
    a.add_argument("--itens-manuais", type=int, default=0)
    a.add_argument("--setup-padrao", action="store_true")
    a.add_argument("--urgencia", action="store_true")
    a.add_argument("--arquivo-fonte", action="store_true")
    a.add_argument("--abertura", action="store_true")
    a.add_argument("--enviar", action="store_true")
    a.add_argument("--para-mim", action="store_true", help="manda so pro Mateus, identico ao do cliente")
    a.add_argument("--sem-contrato", action="store_true", help="nao anexa o contrato")
    a.add_argument("--com-cadastro", action="store_true",
                   help="puxa os dados que o cliente preencheu e fecha o contrato")
    o = a.parse_args()

    if o.de == "exemplo":
        # o exemplo preenche o que faltou, nao atropela o que eu escrevi
        dados = " ".join(sys.argv)
        for k, v in EXEMPLO.items():
            if ("--" + k.replace("_", "-")) not in dados:
                setattr(o, k, v)
    if not o.email:
        raise SystemExit("Informe --email, ou use --de exemplo")

    p = montar(o)
    h = html(p)
    txt = texto(p)

    os.makedirs(PASTA, exist_ok=True)
    base = os.path.join(PASTA, "%s - %s" % (p["numero"], (p["empresa"] or "cliente")[:40]))
    io.open(base + ".html", "w", encoding="utf-8").write(
        '<!doctype html>\n<html lang="pt-BR">\n<meta charset="utf-8">\n'
        '<title>Proposta %s</title>\n' % p["numero"] + h)
    io.open(base + ".txt", "w", encoding="utf-8").write(txt)

    # Guarda o que gerou o preco. Sem isso nao da pra reemitir o contrato
    # depois que o cliente preenche o cadastro: os numeros que definem o
    # valor se perdem e o contrato reemitido sairia com outro valor.
    io.open(base + ".json", "w", encoding="utf-8").write(json.dumps(
        {"argumentos": vars(o), "numero": p["numero"], "email": p["email"],
         "total": p["total"], "paginas": p["paginas"],
         "em": datetime.date.today().isoformat()},
        ensure_ascii=False, indent=2))

    print()
    print("  " + "-" * 56)
    print("  %-12s %s" % ("PROPOSTA", p["numero"]))
    print("  %-12s %s" % ("CLIENTE", p["empresa"] or p["email"]))
    print("  %-12s %s" % ("PROJETO", p["equipamento"]))
    print("  %-12s %s  (%d páginas estimadas)" % ("ESCOPO", p["escopo_txt"], p["paginas"]))
    print("  %-12s %s" % ("PRAZO", p["prazo"]))
    print("  " + "-" * 56)
    for r, v in p["linhas"]:
        if v < 0 and p["total"] != p["valor_cheio"]:
            print("  %-40s %14s" % ("Valor cheio", calc.brl(p["valor_cheio"])))
        print("  %-40s %14s" % (r, calc.brl(v)))
    print("  %-40s %14s" % ("TOTAL", calc.brl(p["total"])))
    print("  " + "-" * 56)
    print("  arquivo: %s.html" % base)

    anexos = None
    if not o.sem_contrato:
        import base64, importlib.util as _iu
        _c = _iu.spec_from_file_location("ct", os.path.join(AQUI, "contrato.py"))
        ct = _iu.module_from_spec(_c); _c.loader.exec_module(ct)
        p["total_extenso"] = ct.extenso(p["total"])
        p["itens"] = o.itens_manuais
        p["composicao"] = composicao(p, o)
        if o.com_cadastro:
            conta, cad = ct.buscar_cadastro(p["email"])
            if not cad:
                raise SystemExit("Esse cliente ainda nao preencheu /cadastro.")
            p["cadastro"] = cad
            p["empresa"] = cad.get("razao_social") or p["empresa"]
            p["contato"] = cad.get("rep_nome") or p["contato"]
            print("  cadastro: %s, CNPJ %s" % (p["empresa"], cad.get("cnpj", "?")))
        pdf, faltam = ct.gerar(p)
        print("  contrato: %s" % pdf)
        if faltam:
            print("  a preencher no contrato: %s" % ", ".join(faltam))
        anexos = [{
            "nome": "Contrato %s - Borin Projetos Eletricos.pdf" % p["numero"],
            "tipo": "application/pdf",
            "base64": base64.b64encode(io.open(pdf, "rb").read()).decode(),
        }]

    if o.enviar:
        ok = enviar(p, h, o.para_mim, anexos)
        print("  email:   %s" % ("enviado para " + ("você (cópia)" if o.para_mim else p["email"])
                                 if ok else "FALHOU"))
    else:
        print("  (nada enviado — use --enviar, ou --enviar --para-mim pra conferir antes)")
    print()


if __name__ == "__main__":
    main()
