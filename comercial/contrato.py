"""
Gera o contrato preenchido, em PDF, a partir dos dados da proposta.

    python comercial/contrato.py --de exemplo

Le comercial/modelo-contrato.md, troca os campos entre colchetes pelo que veio
da proposta, e imprime em PDF pelo Chrome. O que sobrar entre colchetes fica
marcado em vermelho no documento — e melhor o Mateus ver um campo vazio na
tela do que descobrir depois que o cliente assinou um contrato com "[N] dias".

Usado pelo orcamento.py, que anexa o PDF no email da proposta.
"""

import datetime
import io
import os
import re
import shutil
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.join(RAIZ, "comercial")
MODELO = os.path.join(AQUI, "modelo-contrato.md")
PASTA = os.path.join(AQUI, "contratos")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
           shutil.which("chrome") or ""]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font: 10.5pt/1.5 'Segoe UI', Arial, sans-serif; color: #111; margin: 0; }
h1 { font-size: 15pt; letter-spacing: -.01em; margin: 0 0 14pt; line-height: 1.25; }
h2 { font-size: 11pt; margin: 16pt 0 6pt; border-top: 1px solid #111; padding-top: 5pt;
     page-break-after: avoid; }
h3 { font-size: 10pt; margin: 10pt 0 4pt; color: #5A5A5A; page-break-after: avoid; }
p { margin: 0 0 6pt; text-align: justify; }
table { width: 100%; border-collapse: collapse; margin: 0 0 10pt; font-size: 9.5pt; }
td { border-bottom: 1px solid #DCDCDC; padding: 4pt 8pt 4pt 0; vertical-align: top; }
tr td:first-child { width: 32%; color: #5A5A5A; }
strong { font-weight: 600; }
hr { border: 0; border-top: 1px solid #DCDCDC; margin: 12pt 0; }
.marca { font-size: 20pt; font-weight: 700; letter-spacing: 3px; }
.regua { height: 2px; background: #111; width: 118px; margin: 3pt 0 0; }
.no { display: inline-block; width: 6px; height: 6px; background: #C1121F;
      position: relative; top: -6px; left: 122px; }
.sub { font-family: Consolas, monospace; font-size: 7.5pt; letter-spacing: .12em;
       text-transform: uppercase; color: #5A5A5A; margin-top: -3pt; }
.topo { border-bottom: 1px solid #111; padding-bottom: 10pt; margin-bottom: 14pt; }
.falta { background: #FDE7E9; color: #C1121F; padding: 0 2px; font-weight: 600; }
.assina { margin-top: 26pt; page-break-inside: avoid; }
.assina div { border-top: 1px solid #111; padding-top: 4pt; margin-top: 30pt;
              font-size: 9pt; width: 62%; }
"""


def calc_brl(v):
    t = format(abs(v), ",.2f").replace(",", "#").replace(".", ",").replace("#", ".")
    return ("-R$ " if v < 0 else "R$ ") + t


UNI = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
       "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito",
       "dezenove"]
DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta",
       "noventa"]
CEM = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos",
       "setecentos", "oitocentos", "novecentos"]


def _ate999(n):
    if n == 0:
        return ""
    if n == 100:
        return "cem"
    c, r = divmod(n, 100)
    partes = []
    if c:
        partes.append(CEM[c])
    if r:
        if r < 20:
            partes.append(UNI[r])
        else:
            d, u = divmod(r, 10)
            partes.append(DEZ[d] + (" e " + UNI[u] if u else ""))
    return " e ".join(partes)


def extenso(v):
    """Valor por extenso, como contrato exige. Ate 999 mil, que cobre folgado."""
    reais, cent = int(v), int(round((v - int(v)) * 100))
    if reais == 0:
        t = "zero reais"
    else:
        mil, resto = divmod(reais, 1000)
        partes = []
        if mil:
            partes.append(("mil" if mil == 1 else _ate999(mil) + " mil"))
        if resto:
            partes.append(_ate999(resto))
        # A regra do "e": entra antes do ultimo grupo quando ele e menor que
        # cem OU multiplo de cem. "seis mil E setecentos", mas "seis mil
        # setecentos E quarenta e dois". Como o total agora sai sempre redondo,
        # o caso comum e o multiplo de cem, que antes saia com virgula.
        if len(partes) == 2:
            t = (" e " if (resto < 100 or resto % 100 == 0) else ", ").join(partes)
        else:
            t = partes[0]
        t += " real" if reais == 1 else " reais"
    if cent:
        t += " e %s %s" % (_ate999(cent), "centavo" if cent == 1 else "centavos")
    return t


def chrome():
    for c in CHROMES:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chrome nao encontrado")


def md_para_html(md):
    """Conversao suficiente para este documento: titulo, tabela, negrito, lista."""
    fora, tabela = [], []

    def fecha():
        if not tabela:
            return
        linhas = [l for l in tabela if not re.match(r"^\|[\s:|-]+\|$", l)]
        fora.append("<table>")
        for l in linhas:
            cel = [c.strip() for c in l.strip().strip("|").split("|")]
            fora.append("<tr>" + "".join("<td>%s</td>" % c for c in cel) + "</tr>")
        fora.append("</table>")
        tabela.clear()

    for linha in md.split("\n"):
        if linha.startswith("|"):
            tabela.append(linha)
            continue
        fecha()
        l = linha.rstrip()
        if l.startswith("### "):
            fora.append("<h3>%s</h3>" % l[4:])
        elif l.startswith("## "):
            fora.append("<h2>%s</h2>" % l[3:])
        elif l.startswith("# "):
            fora.append("<h1>%s</h1>" % l[2:])
        elif l.startswith("---"):
            fora.append("<hr>")
        elif l.strip() == "":
            fora.append("")
        else:
            fora.append("<p>%s</p>" % l)
    fecha()

    h = "\n".join(fora)
    h = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", h)
    h = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", h)
    return h


def gerar(p, saida=None):
    """p vem do orcamento.py. Devolve o caminho do PDF."""
    md = io.open(MODELO, encoding="utf-8").read()

    # so o contrato: fora o cabecalho de instrucao e as secoes de apoio
    i = md.find("# CONTRATO DE PRESTAÇÃO")
    j = md.find("# O que este contrato resolve")
    md = md[i:j if j > i else len(md)]

    hoje = datetime.date.today()

    # As linhas do Quadro Resumo sao trocadas INTEIRAS, nao por token: com
    # "[N]" solto, o numero de paginas ia parar tambem no campo de itens fora
    # do banco e na composicao. Linha inteira nao tem como errar de campo.
    linhas = {
        "**Páginas de diagrama estimadas**": str(p["paginas"]),
        "**Itens fora do banco de artigos previstos**": str(p.get("itens", 0)),
        "**Preço total**": "**%s** (%s)" % (calc_brl(p["total"]), p["total_extenso"]),
        "**Composição**": p["composicao"],
        "**Prazo de entrega**": ("%s, contados do que ocorrer por último entre o pagamento "
                                 "da parcela inicial e o recebimento da Ficha Técnica completa"
                                 % p["prazo"]),
        "**Objeto**": "Documentação técnica do sistema elétrico de " + p["equipamento"],
        "**Escopo**": "Escopo " + p["escopo_txt"] + ", conforme o Anexo III",
        "**Proposta**": "nº %s, de %s" % (p["numero"], hoje.strftime("%d/%m/%Y")),
    }
    saida_md = []
    for linha in md.split("\n"):
        trocou = False
        for rotulo, valor in linhas.items():
            if linha.startswith("| " + rotulo + " |"):
                saida_md.append("| %s | %s |" % (rotulo, valor))
                trocou = True
                break
        if not trocou:
            saida_md.append(linha)
    md = "\n".join(saida_md)

    # O cadastro que o cliente preencheu em /cadastro fecha os campos que
    # sobravam em vermelho. Sem ele, o contrato sai com os buracos marcados —
    # de proposito, pra ninguem assinar um documento com "[endereço]".
    c = p.get("cadastro") or {}
    end = ", ".join(x for x in [
        " ".join(x for x in [c.get("logradouro"), c.get("numero_end")] if x),
        c.get("complemento"), c.get("bairro"),
        " / ".join(x for x in [c.get("cidade"), (c.get("uf") or "").upper()] if x),
        c.get("cep"),
    ] if x)

    campos = {
        "[Razão social]": c.get("razao_social") or p["empresa"] or "[Razão social]",
        "[identificação do equipamento]": p["equipamento"],
        "[dd/mm/aaaa]": hoje.strftime("%d/%m/%Y"),
        "[dd]": "%02d" % hoje.day,
        "[mês]": MESES[hoje.month - 1],
        "[aaaa]": str(hoje.year),
        "[Cidade]": "Caxias do Sul",
        "[nome do representante]": p["contato"] or "[nome do representante]",
        "[Nome do representante]": p["contato"] or "[Nome do representante]",
        "[email]": p["email"] or "[email]",
        "[N] dias úteis": p["prazo"],
    }
    # As duas qualificacoes sao trocadas como LINHA INTEIRA, cada uma com o seu
    # endereco. Substituindo "[endereço completo]" solto, o endereco do cliente
    # ia parar tambem na qualificacao do CONTRATADO — e o contrato passava a
    # dizer que o Mateus fica na sede do cliente.
    if c:
        qual_contratante = (
            "**CONTRATANTE:** %s, CNPJ nº %s, com sede em %s, neste ato representada por "
            "%s, %s, CPF nº %s."
            % (c.get("razao_social") or p["empresa"] or "[Razão social]",
               c.get("cnpj") or "[CNPJ]", end or "[endereço]",
               c.get("rep_nome") or "[nome]", c.get("rep_cargo") or "[cargo]",
               c.get("rep_cpf") or "[CPF]"))
        # a qualificacao ocupa DUAS linhas no modelo: a segunda e a continuacao
        # com o representante. Troca a primeira e descarta a continuacao.
        linhas, saida2, pular = md.split("\n"), [], False
        for linha in linhas:
            if pular:
                pular = False
                continue
            if linha.startswith("**CONTRATANTE:**"):
                saida2.append(qual_contratante)
                pular = True
            else:
                saida2.append(linha)
        md = "\n".join(saida2)

        # bloco de assinatura, no fim do contrato
        md = md.replace("**CONTRATANTE** — [Nome do representante], [cargo]",
                        "**CONTRATANTE** — %s, %s"
                        % (c.get("rep_nome") or "[nome]", c.get("rep_cargo") or "[cargo]"))
        # o CNPJ do Mateus ja esta literal no modelo: qualquer "CNPJ [numero]"
        # que sobre e o do cliente
        md = md.replace("CNPJ [número]", "CNPJ " + (c.get("cnpj") or "[CNPJ]"))
        md = md.replace("[Razão social] — CNPJ [número] — [email]",
                        "%s — CNPJ %s — %s"
                        % (c.get("razao_social") or p["empresa"] or "[Razão social]",
                           c.get("cnpj") or "[CNPJ]",
                           c.get("rep_email") or p["email"] or "[email]"))

    # o endereco do Mateus nao muda de cliente pra cliente: fica no .env
    meu = ""
    envp = os.path.join(RAIZ, ".env")
    if os.path.exists(envp):
        for l in io.open(envp, encoding="utf-8"):
            k, _, v = l.partition("=")
            if k.strip() == "BORIN_ENDERECO":
                meu = v.strip().strip("'\"")
    if meu:
        md = md.replace("estabelecido em [endereço completo]", "estabelecido em " + meu)
        md = md.replace("estabelecido em [endereço]", "estabelecido em " + meu)
    for k, v in campos.items():
        md = md.replace(k, str(v))

    html = md_para_html(md)
    # o que sobrou pra preencher fica visivel, nao escondido
    html = re.sub(r"\[([^\]<>]{1,60})\]", r'<span class="falta">[\1]</span>', html)

    doc = ("""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<title>Contrato %s</title><style>%s</style>
<div class="topo">
  <div class="marca">BORIN</div><div class="regua"></div><span class="no"></span>
  <div class="sub">projetos elétricos industriais</div>
</div>
""" % (p["numero"], CSS)) + html + """
<div class="assina">
  <div>Mateus Borin — 65.749.097 MATEUS BORIN · CNPJ 65.749.097/0001-85</div>
  <div>%s — %s</div>
</div></html>""" % (p["contato"] or "CONTRATANTE", p["empresa"] or "")

    os.makedirs(PASTA, exist_ok=True)
    nome = saida or os.path.join(
        PASTA, "Contrato %s - %s" % (p["numero"], (p["empresa"] or "cliente")[:40]))
    io.open(nome + ".html", "w", encoding="utf-8").write(doc)

    # Chrome nao aceita acento no caminho de --print-to-pdf de forma confiavel
    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "borin-contrato")
    io.open(tmp + ".html", "w", encoding="utf-8").write(doc)
    subprocess.run([chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + tmp + ".pdf", "--virtual-time-budget=6000",
                    "file:///" + tmp.replace("\\", "/") + ".html"],
                   capture_output=True, timeout=120)
    if not os.path.exists(tmp + ".pdf"):
        raise SystemExit("Chrome nao gerou o PDF do contrato")
    shutil.copy2(tmp + ".pdf", nome + ".pdf")
    os.remove(tmp + ".pdf"); os.remove(tmp + ".html")

    faltam = re.findall(r'class="falta">\[([^\]]+)\]', doc)
    return nome + ".pdf", sorted(set(faltam))


def buscar_cadastro(email):
    """Puxa o cadastro que o cliente preencheu na conta dele."""
    import json, subprocess, urllib.parse
    seg = ""
    env = os.path.join(RAIZ, ".env")
    if os.path.exists(env):
        for l in io.open(env, encoding="utf-8"):
            k, _, v = l.partition("=")
            if k.strip() == "BORIN_SEGREDO_ADMIN":
                seg = v.strip().strip("'\"")
    if not seg:
        raise SystemExit("Falta BORIN_SEGREDO_ADMIN no .env")
    # o segredo vai no cabecalho, nunca na URL: query string entra em log da
    # Cloudflare, no historico e no Referer
    u = ("https://borinprojetos.com.br/api/acesso/cliente?email="
         + urllib.parse.quote(email))
    r = subprocess.run(["curl", "-s", "-H", "Authorization: Bearer " + seg, u],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    d = json.loads(r.stdout or "{}")
    if not d.get("ok"):
        raise SystemExit("Nao achei o cliente: " + str(d.get("erro")))
    return d["conta"], (d.get("fichas") or {}).get("cadastro")


if __name__ == "__main__":
    import importlib.util, argparse
    _s = importlib.util.spec_from_file_location("orc", os.path.join(AQUI, "orcamento.py"))
    orc = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(orc)
    a = argparse.ArgumentParser()
    a.add_argument("--de", choices=["exemplo"], required=True)
    o = a.parse_args()
    ns = argparse.Namespace(**dict(orc.EXEMPLO, numero=None, paginas=None,
                                   urgencia=False, arquivo_fonte=False))
    p = orc.montar(ns)
    p["total_extenso"] = extenso(p["total"])
    p["itens"] = ns.itens_manuais
    p["composicao"] = orc.composicao(p, ns)
    caminho, faltam = gerar(p)
    print("\n  PDF:", caminho)
    if faltam:
        print("  campos ainda em branco:", ", ".join(faltam))
    print()
