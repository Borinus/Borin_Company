# -*- coding: utf-8 -*-
"""
Sobe arquivo pra área do cliente.

    python comercial/subir.py --cliente joao@fabrica.com.br --projeto OS-4471 \
        "C:/entregas/Diagrama rev B.pdf" "C:/entregas/Lista de materiais.xlsx"

    python comercial/subir.py --cliente joao@fabrica.com.br --projeto OS-4471 --listar
    python comercial/subir.py --cliente joao@fabrica.com.br --projeto OS-4471 \
        --apagar "Diagrama rev B.pdf"

O que sobe fica visível na conta do cliente, dentro do cartão daquele projeto,
para o dono E para quem ele liberou acesso — o pessoal do campo abre o diagrama
no celular com o login deles.

Ninguém de fora vê: o arquivo não tem link público. Cada download passa pelo
servidor, que confere a sessão e a empresa antes de devolver o primeiro byte.
"""

import argparse
import glob
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SITE = "https://borinprojetos.com.br"
LIMITE = 60 * 1024 * 1024

# A Cloudflare devolve 1010 pra user-agent de script e o erro não diz isso em
# lugar nenhum — parece que o site caiu. Basta se apresentar como navegador.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")


def segredo():
    caminho = os.path.join(RAIZ, ".env")
    if os.path.exists(caminho):
        for linha in io.open(caminho, encoding="utf-8"):
            m = re.match(r"\s*BORIN_SEGREDO_ADMIN\s*=\s*(.+?)\s*$", linha)
            if m:
                return m.group(1).strip('"').strip("'")
    raise SystemExit("Falta BORIN_SEGREDO_ADMIN no .env da raiz.")


def chamar(url, metodo="GET", corpo=None, tipo=None):
    dados = corpo
    if corpo is not None and not isinstance(corpo, (bytes, bytearray)):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        tipo = "application/json; charset=utf-8"
    r = urllib.request.Request(url, data=dados, method=metodo)
    r.add_header("Authorization", "Bearer " + segredo())
    r.add_header("User-Agent", UA)
    if tipo:
        r.add_header("Content-Type", tipo)
    try:
        with urllib.request.urlopen(r, timeout=300) as x:
            return x.status, json.loads(x.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except urllib.error.URLError as e:
        raise SystemExit("  sem conexão com o site: %s" % e.reason)


def tipo_de(nome):
    e = (nome.rsplit(".", 1)[-1] if "." in nome else "").lower()
    return {
        "pdf": "application/pdf", "zip": "application/zip",
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "dwg": "image/vnd.dwg", "csv": "text/csv", "txt": "text/plain",
        "xlsx": ("application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet"),
    }.get(e, "application/octet-stream")


def curto(n):
    if n >= 1048576:
        return "%.1f MB" % (n / 1048576.0)
    if n >= 1024:
        return "%d KB" % round(n / 1024.0)
    return "%d B" % n


def listar(cliente, projeto):
    """O que já está lá. Usa a mesma listagem que a tela do cliente usa, com o
    segredo no lugar da sessão — se fosse uma segunda implementação, as duas
    divergiriam com o tempo e eu confiaria numa lista que não é a que ele vê."""
    st, d = chamar("%s/api/acesso/arquivos-admin?email=%s&codigo=%s"
                   % (SITE, urllib.parse.quote(cliente), urllib.parse.quote(projeto)))
    if st != 200:
        raise SystemExit("  %s" % (d.get("erro") or ("http %d" % st)))
    return d.get("arquivos") or []


def mostrar(arquivos):
    if not arquivos:
        print("  (nenhum arquivo neste projeto ainda)")
        return
    for a in arquivos:
        det = [curto(a.get("tamanho", 0))]
        if a.get("etapa"):
            det.append(a["etapa"])
        if a.get("em"):
            det.append(str(a["em"])[:10])
        print("  %-46s %s" % ((a.get("titulo") or a.get("nome") or "")[:46],
                              " · ".join(det)))


def main():
    a = argparse.ArgumentParser(description="Sobe arquivo pra área do cliente")
    a.add_argument("arquivos", nargs="*", help="um ou mais arquivos")
    a.add_argument("--cliente", required=True, help="email do cliente")
    a.add_argument("--projeto", required=True, help="codigo do projeto, ex OS-4471")
    a.add_argument("--titulo", default="", help="nome que o cliente vê (padrão: o do arquivo)")
    a.add_argument("--etapa", default="", help="ex: revisão B, para aprovação")
    a.add_argument("--listar", action="store_true", help="só mostra o que já está lá")
    a.add_argument("--apagar", help="tira um arquivo pelo nome")
    o = a.parse_args()

    print()
    print("  cliente: %s" % o.cliente)
    print("  projeto: %s" % o.projeto)
    print()

    if o.apagar:
        st, d = chamar(SITE + "/api/acesso/arquivo-apagar", "POST",
                       {"email": o.cliente, "codigo": o.projeto, "nome": o.apagar})
        print("  %s  %s" % ("apagado:" if d.get("ok") else "FALHOU:",
                            o.apagar if d.get("ok") else (d.get("erro") or st)))
        print()
        return

    if o.listar and not o.arquivos:
        mostrar(listar(o.cliente, o.projeto))
        print()
        return

    # Glob resolvido aqui porque o terminal do Windows não expande sozinho: sem
    # isto, "entregas/*.pdf" chegaria como texto literal e o erro seria
    # "arquivo não encontrado" apontando pro asterisco.
    caminhos = []
    for padrao in o.arquivos:
        achados = glob.glob(padrao)
        if achados:
            caminhos.extend(sorted(achados))
        else:
            caminhos.append(padrao)

    if not caminhos:
        raise SystemExit("  Informe pelo menos um arquivo.")

    # Confere TUDO antes de subir QUALQUER COISA: subir três e falhar no quarto
    # deixa a área do cliente pela metade, e ele vê uma entrega incompleta sem
    # saber que está incompleta.
    for c in caminhos:
        if not os.path.isfile(c):
            raise SystemExit("  não achei o arquivo: %s" % c)
        t = os.path.getsize(c)
        if t == 0:
            raise SystemExit("  arquivo vazio: %s" % c)
        if t > LIMITE:
            raise SystemExit("  %s tem %s — o limite é 60 MB.\n"
                             "  Divida ou compacte antes de subir." % (c, curto(t)))

    if len(caminhos) > 1 and o.titulo:
        raise SystemExit("  --titulo vale para um arquivo só. Com vários, o título\n"
                         "  de cada um sai do nome do próprio arquivo.")

    total = 0
    for c in caminhos:
        nome = os.path.basename(c)
        titulo = o.titulo or os.path.splitext(nome)[0]
        bytes_ = io.open(c, "rb").read()

        url = ("%s/api/acesso/arquivo?email=%s&codigo=%s&nome=%s&titulo=%s&etapa=%s"
               % (SITE, urllib.parse.quote(o.cliente), urllib.parse.quote(o.projeto),
                  urllib.parse.quote(nome), urllib.parse.quote(titulo),
                  urllib.parse.quote(o.etapa)))
        st, d = chamar(url, "PUT", bytes_, tipo_de(nome))

        if d.get("ok"):
            total += d.get("bytes", 0)
            print("  ok      %-44s %s" % (nome[:44], curto(d.get("bytes", 0))))
        else:
            print("  FALHOU  %-44s %s" % (nome[:44], d.get("erro") or ("http %d" % st)))
            print()
            raise SystemExit(1)

    # Confere lendo de volta: "subiu" que não aparece na lista do cliente é o
    # tipo de sucesso mentiroso que só se descobre quando ele reclama.
    print()
    print("  na área do cliente agora:")
    mostrar(listar(o.cliente, o.projeto))
    print()
    print("  %d enviado(s), %s no total." % (len(caminhos), curto(total)))
    print("  O cliente vê em borinprojetos.com.br/conta, no cartão do projeto.")
    print()


if __name__ == "__main__":
    main()
