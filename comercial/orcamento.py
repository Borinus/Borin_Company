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
# BORIN_PROPOSTAS: as suítes de teste apontam pra um diretório descartável.
# Sem isso, cada rodada gerava proposta AQUI e o numero() — que conta os
# arquivos da pasta — inflava: a primeira proposta real ia sair PROP-2026-115.
PASTA = os.environ.get("BORIN_PROPOSTAS") or os.path.join(AQUI, "propostas")
# /api/enviar e o caminho de admin: e o unico que aceita HTML, anexo e
# escolher destinatario, e exige o segredo no cabecalho. O /api/orcamento
# ficou so pro formulario do site, sem nenhum desses poderes.
API = "https://borinprojetos.com.br/api/enviar"

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
    """NAO VAI MAIS PRO CONTRATO. Entregava a formula ao cliente e convidava
    ele a negociar pagina por pagina; saiu do Quadro Resumo em 02/08/2026.
    Fica aqui porque a conta ainda serve pra eu conferir de onde saiu o preco.

    A linha de composicao do Quadro Resumo do contrato: mesma conta da
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
    if getattr(o, "desconto", 0):
        partes.append("desconto combinado −%g%%" % o.desconto)
    return " · ".join(partes)


# ---------------------------------------------------------- primeira vez -----
#
# A condição de abertura e o setup do padrão valem UMA VEZ por cliente. Estavam
# presos a `--abertura` e `--setup-padrao` digitados na mão, e o resultado foi o
# esperado: a primeira proposta de verdade saiu sem os dois, com uma linha só e
# sem o desconto — não por decisão, por esquecimento.
#
# Agora entram sozinhos. Novo é quem nunca recebeu proposta ENVIADA antes, e
# quem controla isso é `clientes-atendidos.json`, escrito a cada envio.
#
# ISTO AQUI ERA UMA BOMBA, desarmada em 05/08/2026. No lugar da regra havia uma
# constante `TODOS_NOVOS = True`, com um comentário em maiúsculas mandando
# trocar pra False quando o primeiro cliente de verdade entrasse. Enquanto
# estivesse ligada, TODO cliente levava a condição de abertura — inclusive o
# segundo projeto do mesmo cliente, que já viu o padrão e não precisa de
# desconto nenhum. Num Escopo B são R$ 6.700 por proposta.
#
# O problema não era o valor da constante: era ela existir. Regra de negócio que
# depende de alguém lembrar de trocar uma linha é a mesma armadilha da regra #3
# do AGENTS.md, e já custou caro aqui antes ("o desconto que dependia de eu
# lembrar de uma opção").
#
# A necessidade real era outra: ver a proposta COMPLETA ao conferir formato.
# Isso virou `--forcar-novo`, que é por execução e não pode vazar pra produção.
# `--de exemplo` liga sozinho, porque exemplo é justamente pra ver o formato.

ATENDIDOS = os.path.join(AQUI, "clientes-atendidos.json")


def _atendidos():
    """Quem já recebeu proposta. Arquivo vazio e arquivo ILEGÍVEL não são a
    mesma coisa, e o `except Exception: return {}` de antes tratava os dois
    igual.

    A diferença importa em dinheiro: sem registro, todo cliente vira novo e leva
    a condição de abertura. Se o arquivo existir e não abrir — JSON quebrado,
    disco, permissão —, isso tem que aparecer na tela antes de a proposta sair,
    e não virar um desconto silencioso de R$ 6.700.
    """
    if not os.path.exists(ATENDIDOS):
        return {}                      # primeira vez: normal, sem alarde
    try:
        with io.open(ATENDIDOS, encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict):
            raise ValueError("o arquivo não é um objeto JSON")
        return d
    except Exception as e:
        print("  !! NAO CONSEGUI LER %s (%s)." % (os.path.basename(ATENDIDOS), e))
        print("     Sem esse arquivo TODO cliente conta como novo e leva o")
        print("     desconto de abertura. Confira antes de enviar.")
        return {}


# Havia aqui um `ehClienteNovo(email)`. Foi removido em 05/08/2026 depois que a
# prova de falha do teste mostrou o problema: nada mais chamava essa função, e
# quebrá-la de propósito não deixava um único teste de comportamento vermelho.
# Uma função com esse nome parece SER a regra; quem fosse mexer no desconto
# mexeria nela e não mudaria nada. A regra mora em aplicar_primeira_vez, que
# consulta _atendidos() direto — um lugar só.


def marcar_atendido(email, numero):
    """Chamado só quando a proposta REALMENTE sai. Gerar sem enviar não pode
    queimar a condição de abertura — senão testar um formato tira o desconto do
    cliente."""
    chave = (email or "").strip().lower()
    if not chave:
        return
    d = _atendidos()
    if chave in d:
        return
    d[chave] = {"primeira_proposta": numero,
                "em": datetime.date.today().isoformat()}
    with io.open(ATENDIDOS, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, sort_keys=True)


def registrar_na_conta(p, pdf=None, pdf_proposta=None):
    """Põe a proposta na conta do cliente — o registro, o PDF dela e o contrato.

    A proposta existia só no email. Cliente que apagou sem querer, ou que foi
    procurar seis semanas depois, não tinha onde olhar — e valor e prazo são
    justamente o que se procura depois. O PDF sobe também (10/08/2026): o
    registro sozinho não bastava, o documento que se baixa e se repassa é o
    PDF, e ele só existia no anexo do email. Falhar aqui NÃO derruba nada: o
    email já saiu e o cliente já foi atendido.
    """
    import re
    import urllib.error
    import urllib.parse
    import urllib.request

    seg = ""
    env = os.path.join(os.path.dirname(AQUI), ".env")
    if os.path.exists(env):
        for l in io.open(env, encoding="utf-8"):
            m = re.match(r"\s*BORIN_SEGREDO_ADMIN\s*=\s*(.+?)\s*$", l)
            if m:
                seg = m.group(1).strip('"').strip("'")
    if not seg:
        return

    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")
    SITE = "https://borinprojetos.com.br"

    def bate(url, metodo, corpo, tipo):
        r = urllib.request.Request(url, data=corpo, method=metodo)
        r.add_header("Authorization", "Bearer " + seg)
        r.add_header("User-Agent", UA)
        r.add_header("Content-Type", tipo)
        try:
            with urllib.request.urlopen(r, timeout=180) as x:
                return json.loads(x.read().decode() or "{}")
        except Exception as e:
            return {"erro": str(e)[:80]}

    d = bate(SITE + "/api/acesso/proposta", "POST", json.dumps({
        "email": p["email"], "numero": p["numero"],
        "equipamento": p["equipamento"], "codigo": p["codigo"],
        "escopo": p["escopo_txt"], "paginas": p["paginas"],
        "total": p["total"], "prazo": p["prazo"], "validade": "3 dias",
    }, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    if not d.get("ok"):
        print("  conta:   nao registrei a proposta (%s)" % (d.get("erro") or "?"))
        return

    def subir(caminho, titulo, etapa):
        nome = os.path.basename(caminho)
        url = ("%s/api/acesso/arquivo?email=%s&codigo=%s&nome=%s&titulo=%s&etapa=%s"
               % (SITE, urllib.parse.quote(p["email"]),
                  urllib.parse.quote(p["numero"]), urllib.parse.quote(nome),
                  urllib.parse.quote(titulo), urllib.parse.quote(etapa)))
        a = bate(url, "PUT", io.open(caminho, "rb").read(), "application/pdf")
        return a.get("ok"), (a.get("erro") or "?")

    subiu = []
    if pdf_proposta and os.path.exists(pdf_proposta):
        ok_, erro_ = subir(pdf_proposta, "Proposta " + p["numero"], "proposta")
        if ok_:
            subiu.append("proposta em PDF")
        else:
            # em voz alta: PDF que nao sobe calado e documento que "sumiu"
            print("  conta:   o PDF da proposta nao subiu (%s)" % erro_)
    if pdf and os.path.exists(pdf):
        ok_, erro_ = subir(pdf, "Contrato " + p["numero"], "para assinar")
        if ok_:
            subiu.append("contrato")
        else:
            print("  conta:   o contrato nao subiu (%s)" % erro_)

    print("  conta:   registrado em /conta%s"
          % ((" com " + " e ".join(subiu)) if subiu else " (sem arquivos)"))


def aplicar_primeira_vez(o):
    """Liga o desconto e o setup para cliente novo, sem apagar o que foi pedido
    na mão: quem digitou `--abertura` continua com ela.

    E DIZ EM VOZ ALTA o que decidiu. Antes isto acontecia calado, e a diferença
    entre um caminho e o outro é R$ 6.700 num Escopo B — o tipo de número que
    não pode ser decidido por um `if` que ninguém vê.
    """
    if getattr(o, "desconto", 0):
        # desconto negociado NO projeto substitui a condição de abertura;
        # deixar a abertura entrar junto empilharia 50% + N% sem ninguém decidir
        print("  cliente:  desconto combinado de %g%% pedido na mão — "
              "substitui a condição de abertura" % o.desconto)
        return
    if o.ja_e_cliente:
        print("  cliente:  ANTIGO por --ja-e-cliente — sem condição de abertura")
        return
    if getattr(o, "forcar_novo", False):
        o.abertura = True
        o.setup_padrao = True
        print("  cliente:  NOVO forçado por --forcar-novo — condição de abertura aplicada")
        return
    ficha = _atendidos().get((o.email or "").strip().lower())
    if ficha:
        print("  cliente:  ANTIGO — primeira proposta %s em %s. Sem condição de abertura"
              % (ficha.get("primeira_proposta", "?"), ficha.get("em", "?")))
        return
    o.abertura = True
    o.setup_padrao = True
    print("  cliente:  NOVO — nunca recebeu proposta. Condição de abertura aplicada")


def montar(o):
    paginas = o.paginas or calc.estimar_paginas(o.io, o.acionamentos, o.seguranca, o.escopo)
    r = calc.calcular(paginas, o.itens_manuais, o.setup_padrao,
                      o.urgencia, o.arquivo_fonte, o.abertura,
                      desconto_pct=getattr(o, "desconto", 0))
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
            # Suporte entra na PROPOSTA, não numa conversa seis meses depois.
            # Fica AQUI, e não no proposta.py, porque esta lista alimenta o
            # email HTML, o .txt E o PDF — quando a linha morava só no PDF,
            # o cliente recebia dois documentos com condições diferentes na
            # mesma mensagem. Ver comercial/suporte.md.
            ("Suporte após a entrega", "30 dias inclusos"),
        ],
    }


def enviar(p, corpo_html, para_mim, anexos=None):
    # nada de marca de copia: o objetivo do --para-mim e ver exatamente o
    # que o cliente vai abrir, inclusive o assunto
    doc = p.get("doc") or ("Proposta " + p["numero"])
    # O assunto vai pronto: o /api/enviar nao remonta nada, so entrega.
    #
    # "Proposta"/"Contrato" vem na FRENTE. Antes o assunto abria com o codigo e
    # a empresa e fechava com o tipo do documento, 102 caracteres depois \u2014 o
    # Gmail corta por volta de 70 no computador e de 35 no celular, entao o
    # cliente via duas linhas identicas na caixa e nao sabia qual era o
    # contrato. O codigo foi pro fim: ele serve pra buscar, nao pra ler.
    assunto = "%s \u00b7 %s \u2014 %s \u00b7 #%s" % (
        doc, p["empresa"] or "cliente", p["equipamento"],
        p["codigo"]) if p["codigo"] else "%s \u00b7 %s \u2014 %s" % (
        doc, p["empresa"] or "cliente", p["equipamento"])
    d = {
        "assunto": assunto,
        "empresa": p["empresa"] or "cliente",
        "contato": p["contato"], "codigo": p["codigo"],
        "equipamento": p["equipamento"],
        "doc": doc,
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
        seg = ""
        _env = os.path.join(RAIZ, ".env")
        if os.path.exists(_env):
            for _l in io.open(_env, encoding="utf-8"):
                _k, _, _v = _l.partition("=")
                if _k.strip() == "BORIN_SEGREDO_ADMIN":
                    seg = _v.strip().strip("'\"")
        if not seg:
            raise SystemExit("Falta BORIN_SEGREDO_ADMIN no .env")
        r = subprocess.run(["curl", "-s", "-X", "POST", API,
                            "-H", "Authorization: Bearer " + seg,
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
    a.add_argument("--desconto", type=float, default=0, metavar="PCT",
                   help="desconto combinado deste projeto, em %% — substitui a condição de abertura")
    a.add_argument("--enviar", action="store_true")
    a.add_argument("--para-mim", action="store_true", help="manda so pro Mateus, identico ao do cliente")
    a.add_argument("--sem-contrato", action="store_true", help="nao anexa o contrato")
    a.add_argument("--com-cadastro", action="store_true",
                   help="exige o cadastro: falha se o cliente ainda nao preencheu")
    a.add_argument("--sem-cadastro", action="store_true",
                   help="ignora o cadastro e manda o contrato em branco")
    a.add_argument("--ja-e-cliente", action="store_true",
                   help="forca cliente ANTIGO: sem condicao de abertura e sem setup")
    a.add_argument("--forcar-novo", action="store_true",
                   help="forca cliente NOVO: mostra a proposta completa, com desconto "
                        "e setup. Pra conferir formato, nao pra mandar")
    o = a.parse_args()

    if o.forcar_novo and o.ja_e_cliente:
        raise SystemExit("--forcar-novo e --ja-e-cliente dizem o contrario um do "
                         "outro. Escolha um.")

    if o.de == "exemplo":
        # exemplo existe pra ver o formato inteiro. Sem isto o email do Mateus já
        # está em clientes-atendidos.json, e o exemplo sairia sem desconto e sem
        # setup — que são justamente as linhas que ele quer conferir
        o.forcar_novo = True
        # o exemplo preenche o que faltou, nao atropela o que eu escrevi
        dados = " ".join(sys.argv)
        for k, v in EXEMPLO.items():
            if ("--" + k.replace("_", "-")) not in dados:
                setattr(o, k, v)
    if not o.email:
        raise SystemExit("Informe --email, ou use --de exemplo")

    aplicar_primeira_vez(o)

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

    anexos = []
    pdf_prop = None

    # A proposta em PDF vai SEMPRE, mesmo com --sem-contrato: ela é o documento
    # que o contato repassa pro chefe ou pro comprador, e email encaminhado
    # chega desmontado. O corpo em HTML continua sendo o que ele lê primeiro;
    # o PDF é o que sobrevive ao encaminhamento e à impressão.
    try:
        import base64 as _b64, importlib.util as _ip
        _p = _ip.spec_from_file_location("pr", os.path.join(AQUI, "proposta.py"))
        pr = _ip.module_from_spec(_p); _p.loader.exec_module(pr)
        pdf_prop = pr.gerar(p)
        print("  proposta: %s" % pdf_prop)
        anexos.append({
            "nome": "Proposta %s - Borin Projetos Eletricos.pdf" % p["numero"],
            "tipo": "application/pdf",
            "base64": _b64.b64encode(io.open(pdf_prop, "rb").read()).decode(),
        })
    except Exception as e:
        # não derruba o envio: proposta sem anexo ainda é proposta. Mas grita,
        # porque anexo que some calado ninguém repara — a regra #3 do AGENTS.md
        print("  proposta: NAO GEREI O PDF (%s) — o email vai sem anexo de proposta"
              % str(e)[:70])

    if not o.sem_contrato:
        import base64, importlib.util as _iu
        _c = _iu.spec_from_file_location("ct", os.path.join(AQUI, "contrato.py"))
        ct = _iu.module_from_spec(_c); _c.loader.exec_module(ct)
        p["total_extenso"] = ct.extenso(p["total"])
        p["itens"] = o.itens_manuais
        # O cadastro entra SOZINHO. Se o cliente ja preencheu, o contrato sai
        # pronto pra assinar; se nao preencheu, sai em branco e o email
        # convida ele a preencher. Isto era uma flag que precisava ser
        # lembrada, e no primeiro uso real eu esqueci: o cliente tinha
        # preenchido tudo e recebeu o contrato vazio.
        cad = None
        if not o.sem_cadastro:
            try:
                conta, cad = ct.buscar_cadastro(p["email"], calado=True)
            except SystemExit:
                cad = None
        if cad:
            p["cadastro"] = cad
            # A razão social manda no CONTRATO, que é documento e precisa do
            # nome legal. No assunto do email e no corpo da proposta continua
            # valendo o nome que o cliente usou no pedido: o corpo já mostrava
            # "Flowsistem" e o assunto saía "3321-0001", duas fontes pro mesmo
            # nome. E razão social ruim — código, abreviação — estragava a
            # única linha que o cliente lê antes de abrir.
            p["razao_social"] = cad.get("razao_social") or p["empresa"]
            p["contato"] = cad.get("rep_nome") or p["contato"]
            print("  cadastro: %s, CNPJ %s" % (p["razao_social"], cad.get("cnpj", "?")))
        elif o.com_cadastro:
            raise SystemExit("Esse cliente ainda nao preencheu /cadastro.")
        else:
            print("  cadastro: o cliente ainda nao preencheu — contrato em branco")
        pdf, faltam = ct.gerar(p)
        print("  contrato: %s" % pdf)
        if faltam:
            print("  a preencher no contrato: %s" % ", ".join(faltam))
        anexos.append({
            "nome": "Contrato %s - Borin Projetos Eletricos.pdf" % p["numero"],
            "tipo": "application/pdf",
            "base64": base64.b64encode(io.open(pdf, "rb").read()).decode(),
        })

    if o.enviar:
        ok = enviar(p, h, o.para_mim, anexos)
        print("  email:   %s" % ("enviado para " + ("você (cópia)" if o.para_mim else p["email"])
                                 if ok else "FALHOU"))
        # marcado só depois de sair de verdade, e nunca na cópia de conferência
        if ok and not o.para_mim:
            marcar_atendido(p["email"], p["numero"])
            # O try existe porque o email JÁ SAIU aqui. Sem ele, um erro no
            # registro derruba o comando depois do cliente já ter recebido a
            # proposta — foi o que aconteceu na primeira versão, por um import
            # que faltava. Registrar é bônus; entregar é o serviço.
            try:
                registrar_na_conta(p, pdf if not o.sem_contrato else None, pdf_prop)
            except Exception as e:
                print("  conta:   nao registrei a proposta (%s)" % str(e)[:70])
    else:
        print("  (nada enviado — use --enviar, ou --enviar --para-mim pra conferir antes)")
    print()


if __name__ == "__main__":
    main()
