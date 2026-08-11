# -*- coding: utf-8 -*-
"""A travessia: o caminho INTEIRO, uma vez, como um cliente de verdade.

    python site/testar-travessia.py

POR QUE ESTA SEPARADA DAS OUTRAS SUÍTES

Cada pedaço já tem teste próprio. Esta existe pra pegar o que só quebra na
EMENDA entre duas partes que funcionam sozinhas — que é onde defeito de sistema
mora. Ela atravessa site, Worker, KV, R2, Resend e os comandos em Python numa
sequência só, na ordem em que um integrador da Serra vai andar nela:

   1. pede orçamento no site           6. recebe a proposta por email, com PDFs
   2. recebe a senha por email         7. preenche o cadastro da empresa
   3. entra na conta                   8. o contrato sai preenchido
   4. troca a senha provisória         9. acha proposta e contrato na conta
   5. vê o próprio pedido             10. acompanha o projeto até 'Entregue'

O passo 10 é o que evita o "e o meu projeto?" no WhatsApp: se a trilha de etapas
quebrar, o cliente não vê nada e volta a perguntar — que é exatamente o que ela
foi feita pra impedir.

TRÊS COISAS QUE ESTA SUÍTE APRENDEU NA MARRA (05/08/2026)

Na primeira execução ela acusou 8 defeitos. Os 8 eram dela, não do site:

  - batia em `/api/acesso/criar`, que é rota de ADMIN, achando que era a de
    trocar senha. A do cliente é `/api/acesso/trocar`, com `atual` e `nova`
  - mandava o endereço do cadastro como um texto só. O formulário de verdade
    usa campos separados: logradouro, numero_end, bairro, cidade, uf, cep
  - lia `propostas` da resposta de `/api/acesso/cliente`, que nunca devolveu
    esse campo. Campo que não existe lê como lista vazia, e lista vazia parece
    defeito

E a quarta, que é de projeto e não de teste: **o KV da Cloudflare é
eventualmente consistente.** Escrever e ler no instante seguinte devolve o
estado velho. Por isso toda leitura de estado derivado aqui usa `insistir()`,
com espera. Sem isso a suíte fica intermitente — e suíte intermitente ninguém
olha, que é pior que suíte nenhuma.

LIMPA O QUE SUJA: no fim apaga a conta de teste e tira o email do
clientes-atendidos.json. Sem isso cada execução deixaria um cliente fantasma no
arquivo que decide a condição de abertura.

CUSTA: 1 pedido do freio de 40/hora por IP, 2 emails e 1 conta temporária.
"""

import io
import json
import os
import random
import re
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SITE = "https://borinprojetos.com.br"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATENDIDOS = os.path.join(RAIZ, "comercial", "clientes-atendidos.json")

# Proposta e contrato de TESTE nunca na pasta real: o numero() conta os
# arquivos de comercial/propostas/, e cada travessia inflava a numeração das
# propostas de verdade. Os subprocessos (orcamento.py etc.) herdam o ambiente.
import tempfile
_SAIDA = tempfile.mkdtemp(prefix="borin-travessia-")
os.environ["BORIN_PROPOSTAS"] = _SAIDA
os.environ["BORIN_CONTRATOS"] = _SAIDA
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")
NOVA_SENHA = "TravessiaDoTeste2026"

passos = []
cookie = {"v": ""}


def P(nome, ok, detalhe=""):
    passos.append((nome, ok, detalhe))
    print("  %s %-46s %s" % ("ok   " if ok else "FALHA", nome, detalhe))
    sys.stdout.flush()


def req(u, m="GET", c=None, com_cookie=False):
    d = json.dumps(c, ensure_ascii=False).encode("utf-8") if c is not None else None
    r = urllib.request.Request(u, data=d, method=m)
    r.add_header("Content-Type", "application/json; charset=utf-8")
    r.add_header("User-Agent", UA)
    if com_cookie and cookie["v"]:
        r.add_header("Cookie", cookie["v"])
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            sc = x.headers.get("Set-Cookie")
            if sc:
                cookie["v"] = sc.split(";")[0]
            return x.status, json.loads(x.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def insistir(fn, tentativas=10, espera=6):
    """Repete até dar certo. O KV é eventualmente consistente: o que foi escrito
    agora pode não aparecer na leitura seguinte. Sem isto a suíte oscila."""
    for i in range(tentativas):
        r = fn()
        if r:
            return r
        if i < tentativas - 1:
            time.sleep(espera)
    return None


def admin(caminho, metodo="GET", corpo=None):
    seg = ""
    env = os.path.join(RAIZ, ".env")
    if os.path.exists(env):
        for l in io.open(env, encoding="utf-8"):
            k, _, v = l.partition("=")
            if k.strip() == "BORIN_SEGREDO_ADMIN":
                seg = v.strip().strip("'\"")
    if not seg:
        return {}
    cmd = ["curl", "-s", "-H", "Authorization: Bearer " + seg]
    if metodo != "GET":
        cmd += ["-X", metodo, "-H", "Content-Type: application/json",
                "-d", json.dumps(corpo or {}, ensure_ascii=False)]
    r = subprocess.run(cmd + [SITE + caminho], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    try:
        return json.loads(r.stdout or "{}")
    except ValueError:
        return {}


def caixa():
    s, d = req("https://api.mail.tm/domains")
    dom = (d if isinstance(d, list) else d.get("hydra:member"))[0]["domain"]
    a = "tv" + "".join(random.choice(string.ascii_lowercase + string.digits)
                       for _ in range(9)) + "@" + dom
    req("https://api.mail.tm/accounts", "POST",
        {"address": a, "password": "Cx12345678ab"})
    s, t = req("https://api.mail.tm/token", "POST",
               {"address": a, "password": "Cx12345678ab"})
    return a, t["token"]


def esperar_email(tok, padrao, vistos, limite=22):
    for _ in range(limite):
        time.sleep(8)
        s, v = req("https://api.mail.tm/messages", tok=None) if False else (0, None)
        r = urllib.request.Request("https://api.mail.tm/messages")
        r.add_header("Authorization", "Bearer " + tok)
        r.add_header("User-Agent", UA)
        try:
            with urllib.request.urlopen(r, timeout=45) as x:
                v = json.loads(x.read().decode() or "{}")
        except Exception:
            continue
        for m in (v if isinstance(v, list) else v.get("hydra:member", [])):
            if m["id"] in vistos or not re.search(padrao, m.get("subject") or "", re.I):
                continue
            r2 = urllib.request.Request("https://api.mail.tm/messages/" + m["id"])
            r2.add_header("Authorization", "Bearer " + tok)
            r2.add_header("User-Agent", UA)
            with urllib.request.urlopen(r2, timeout=45) as x:
                f = json.loads(x.read().decode() or "{}")
            vistos.add(m["id"])
            return f
    return None


def texto_do(msg):
    return " ".join(msg.get("html") or []) + (msg.get("text") or "")


# errors="replace" em toda leitura de subprocesso: quando o argparse recusa um
# argumento, ele escreve o erro no code page do console (cp1252 aqui), não em
# utf-8. Sem isso a thread que lê a saída estoura com UnicodeDecodeError — o
# passo até passava, mas com um traceback no meio do relatório e com risco de
# perder saída de um erro de verdade.
def orcar(alvo, *extra):
    r = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "comercial", "orcamento.py"),
         "--email", alvo, "--empresa", "Travessia Integracao Ltda",
         "--contato", "Carlos Mendes",
         "--equipamento", "Painel de comando da estufa de secagem",
         "--io", "48", "--acionamentos", "6", "--escopo", "A"] + list(extra),
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ, timeout=420)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def linha(saida, marca):
    for l in saida.splitlines():
        if marca in l:
            return l.strip()
    return ""


# ============================================================================
print()
print("  " + "=" * 70)
print("  A TRAVESSIA — o caminho inteiro, como cliente")
print("  " + "=" * 70)

alvo, tok = caixa()
vistos = set()
numero = {"v": ""}
print("  caixa do cliente: %s\n" % alvo)

try:
    # ------------------------------------------------------------ 1. o pedido
    print("  [1] pede orçamento no site")
    st, d = req(SITE + "/api/pedido", "POST", {
        "empresa": "Travessia Integracao Ltda", "contato": "Carlos Mendes",
        "email": alvo, "fone": "+55 54 99888-1122",
        "equipamento": "Painel de comando da estufa de secagem",
        "canal": "email", "para_cliente": True})
    if st == 429:
        raise SystemExit("  429: é o freio de 40/hora, não regressão. Espere e repita.")
    P("o site aceitou o pedido", st == 200 and d.get("ok") is True, "http %d" % st)
    P("a conta nasceu junto", d.get("conta") == "criada", str(d.get("conta")))

    # ------------------------------------------------------------- 2. a senha
    print("\n  [2] a senha chega por email")
    m = esperar_email(tok, r"seu acesso", vistos)
    P("o email de acesso chegou", bool(m), (m or {}).get("subject", "")[:40])
    if not m:
        raise SystemExit(1)
    mm = re.search(r"BORIN[0-9]{6}", texto_do(m))
    senha = mm.group(0) if mm else None
    P("a senha está legível", bool(senha), senha or "NAO ACHEI")

    # -------------------------------------------------------------- 3. entrar
    print("\n  [3] entra na conta")
    st, d = req(SITE + "/api/acesso/entrar", "POST", {"email": alvo, "senha": senha})
    P("entrou com a senha do email", st == 200 and d.get("ok") is True, "http %d" % st)
    P("o site marca a senha como provisória", d.get("senha_provisoria") is True,
      "senha_provisoria=%s" % d.get("senha_provisoria"))

    # -------------------------------------------------------------- 4. trocar
    print("\n  [4] troca a senha provisória")
    st, d = req(SITE + "/api/acesso/trocar", "POST",
                {"atual": senha, "nova": NOVA_SENHA}, com_cookie=True)
    P("a troca foi aceita", st == 200 and d.get("ok") is True,
      "http %d %s" % (st, (d.get("erro") or "")[:30]))
    st, d = req(SITE + "/api/acesso/entrar", "POST",
                {"email": alvo, "senha": NOVA_SENHA})
    P("entra com a senha nova", d.get("ok") is True, "http %d" % st)
    st, d2 = req(SITE + "/api/acesso/entrar", "POST", {"email": alvo, "senha": senha})
    P("a provisória deixou de valer", not d2.get("ok"), (d2.get("erro") or "")[:36])
    conta = insistir(lambda: (admin("/api/acesso/cliente?email="
                                    + urllib.parse.quote(alvo)) or {}).get("conta")
                     if (admin("/api/acesso/cliente?email=" + urllib.parse.quote(alvo))
                         or {}).get("conta", {}).get("estado") == "ativa" else None)
    P("a conta saiu de 'pendente' pra 'ativa'", bool(conta),
      (conta or {}).get("estado", "?"))

    # --------------------------------------------------------- 5. vê o pedido
    print("\n  [5] vê o próprio pedido na conta")
    req(SITE + "/api/acesso/entrar", "POST", {"email": alvo, "senha": NOVA_SENHA})
    st, d = req(SITE + "/api/acesso/projetos", com_cookie=True)
    P("a conta abre", st == 200, "http %d" % st)
    peds = d.get("pedidos") or []
    P("o pedido dele está lá",
      any("estufa" in json.dumps(p, ensure_ascii=False).lower() for p in peds),
      "%d pedido(s)" % len(peds))

    # ------------------------------------------------------------ 6. proposta
    print("\n  [6] recebe a proposta, com os dois PDFs")
    cod, saida = orcar(alvo, "--enviar")
    P("o comando rodou", cod == 0, "saida %d" % cod)
    P("tratado como cliente NOVO", "cliente:  NOVO" in saida, linha(saida, "cliente:")[:56])
    P("gerou o PDF da proposta", "proposta:" in saida, "")
    P("registrou na conta do cliente", "proposta e contrato disponiveis" in saida,
      linha(saida, "conta:")[:56])
    mm = re.search(r"PROP-\d{4}-\d+", saida)
    numero["v"] = mm.group(0) if mm else ""
    P("a proposta tem número", bool(numero["v"]), numero["v"])

    m = esperar_email(tok, r"proposta", vistos)
    P("a proposta chegou na caixa", bool(m), (m or {}).get("subject", "")[:44])
    if m:
        nomes = [a.get("filename", "") for a in (m.get("attachments") or [])]
        P("veio o PDF da proposta", any(n.startswith("Proposta") for n in nomes),
          "%d anexo(s)" % len(nomes))
        P("veio o PDF do contrato", any(n.startswith("Contrato") for n in nomes), "")
        t = texto_do(m)
        P("o valor está no corpo", "R$" in t, "")
        P("NÃO repete senha nenhuma", not re.search(r"BORIN[0-9]{6}", t),
          "senha só no primeiro email")

    # ------------------------------------------------------------ 7. cadastro
    print("\n  [7] preenche o cadastro da empresa")
    req(SITE + "/api/acesso/entrar", "POST", {"email": alvo, "senha": NOVA_SENHA})
    st, d = req(SITE + "/api/acesso/ficha", "POST", {
        "tipo": "cadastro", "avisar": False,
        "dados": {                       # os MESMOS campos do site/cadastro.html
            "razao_social": "Travessia Integracao Industrial Ltda",
            "cnpj": "12.345.678/0001-90", "ie": "0123456789",
            "logradouro": "Rua da Travessia", "numero_end": "100",
            "complemento": "Galpão 2", "bairro": "Distrito Industrial",
            "cidade": "Caxias do Sul", "uf": "RS", "cep": "95000-000",
            "rep_nome": "Carlos Mendes", "rep_cargo": "Diretor",
            "rep_cpf": "123.456.789-00", "rep_email": alvo,
        }}, com_cookie=True)
    P("o cadastro foi guardado", st == 200 and d.get("ok") is True,
      "http %d %s" % (st, (d.get("erro") or "")[:30]))
    achou = insistir(lambda: (admin("/api/acesso/cliente?email="
                                    + urllib.parse.quote(alvo)).get("fichas") or {}
                              ).get("cadastro"))
    P("o cadastro já é visível pro contrato", bool(achou),
      (achou or {}).get("razao_social", "")[:44])

    # ------------------------------------------------------------ 8. contrato
    print("\n  [8] o contrato sai preenchido")
    cod, saida2 = orcar(alvo)
    P("agora é cliente ANTIGO, sem desconto de novo", "cliente:  ANTIGO" in saida2,
      linha(saida2, "cliente:")[:56])
    P("o contrato achou o cadastro", "CNPJ 12.345.678" in saida2,
      linha(saida2, "cadastro:")[:52])
    falta = linha(saida2, "a preencher no contrato")
    P("nenhum campo ficou em branco", not falta, falta[:52])

    # ----------------------------------------------- 9. proposta e contrato
    print("\n  [9] proposta e contrato aparecem na conta dele")
    req(SITE + "/api/acesso/entrar", "POST", {"email": alvo, "senha": NOVA_SENHA})
    props = insistir(lambda: (req(SITE + "/api/acesso/projetos",
                                  com_cookie=True)[1].get("propostas") or None))
    P("a proposta está registrada", bool(props), "%d proposta(s)" % len(props or []))

    arqs = insistir(lambda: (req(SITE + "/api/acesso/arquivos?codigo="
                                 + urllib.parse.quote(numero["v"]),
                                 com_cookie=True)[1].get("arquivos") or None))
    P("o contrato está lá pra baixar", bool(arqs),
      (arqs or [{}])[0].get("titulo", "")[:44])
    P("marcado como 'para assinar'",
      any(a.get("etapa") == "para assinar" for a in (arqs or [])),
      (arqs or [{}])[0].get("etapa", ""))

    # --------------------------------------------- 10. a vida depois da assinatura
    print("\n  [10] o projeto anda, e o cliente acompanha sem perguntar")

    def projetar(*extra):
        r = subprocess.run(
            [sys.executable, os.path.join(RAIZ, "comercial", "projeto.py"),
             alvo, "TRAV001"] + list(extra),
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ, timeout=120)
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    def projeto_do_cliente():
        req(SITE + "/api/acesso/entrar", "POST",
            {"email": alvo, "senha": NOVA_SENHA})
        st, d = req(SITE + "/api/acesso/projetos", com_cookie=True)
        for pr in (d.get("projetos") or []):
            if pr.get("codigo") == "TRAV001":
                return pr
        return None

    cod, _ = projetar("--nome", "Painel da estufa de secagem",
                      "--status", "Contrato assinado", "--prazo", "12 dias úteis")
    P("o projeto foi criado", cod == 0, "saida %d" % cod)
    pr = insistir(projeto_do_cliente)
    P("o cliente já vê o projeto", bool(pr), (pr or {}).get("nome", "")[:40])
    P("na etapa 'Contrato assinado'", (pr or {}).get("status") == "Contrato assinado",
      (pr or {}).get("status", ""))
    P("com o prazo à vista", (pr or {}).get("prazo") == "12 dias úteis",
      (pr or {}).get("prazo", ""))

    cod, _ = projetar("--status", "Em execução")
    pr = insistir(lambda: (lambda x: x if x and x.get("status") == "Em execução"
                           else None)(projeto_do_cliente()))
    P("a etapa avança pra 'Em execução'", bool(pr), (pr or {}).get("status", ""))

    cod, saida = projetar("--status", "Entregue",
                          "--link", "https://drive.google.com/drive/pasta-teste",
                          "--nota", "Databook vai em arquivo separado.")
    pr = insistir(lambda: (lambda x: x if x and x.get("status") == "Entregue"
                           else None)(projeto_do_cliente()))
    P("chega em 'Entregue'", bool(pr), (pr or {}).get("status", ""))
    P("o link da entrega chegou junto",
      "drive.google.com" in ((pr or {}).get("link") or ""), "")
    P("e o recado do cartão também",
      "Databook" in ((pr or {}).get("nota") or ""), (pr or {}).get("nota", "")[:34])

    cod, saida = projetar("--status", "Etapa Inventada")
    P("etapa fora da lista é recusada", cod != 0,
      "só as 7 de projeto.py valem")

finally:
    # ------------------------------------------------------------- limpeza
    print("\n  [limpeza] não pode sobrar cliente fantasma")
    r = admin("/api/acesso/apagar", "POST", {"email": alvo})
    # `apagados` vem como NÚMERO, não lista — len() nele estourava a limpeza
    # depois de todos os 29 passos terem passado, e ainda deixava a conta viva
    ap = r.get("apagados")
    P("a conta de teste foi apagada", r.get("ok") is True,
      ("%s chave(s)" % (ap if not isinstance(ap, list) else len(ap)))
      if r.get("ok") else str(r.get("erro"))[:40])
    try:
        d = json.loads(io.open(ATENDIDOS, encoding="utf-8").read())
        if alvo in d:
            del d[alvo]
            io.open(ATENDIDOS, "w", encoding="utf-8").write(
                json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
            P("tirado do clientes-atendidos.json", True, alvo)
        else:
            P("nada a tirar do clientes-atendidos.json", True, "")
    except Exception as e:
        P("limpar o clientes-atendidos.json", False, str(e)[:40])

print()
bons = sum(1 for _, o, _ in passos if o)
print("  " + "=" * 70)
print("  %d/%d passos ok" % (bons, len(passos)))
for n, o, dd in passos:
    if not o:
        print("    FALHOU: %s — %s" % (n, dd))
print("  " + "=" * 70)
print()
raise SystemExit(0 if bons == len(passos) else 1)
