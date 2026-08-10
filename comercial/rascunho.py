# -*- coding: utf-8 -*-
"""Monta o link de rascunho do /orcamento — a ficha preenchida pra conferir.

USO (o fluxo do pedido que chega por conversa):

    python comercial/rascunho.py --empresa "Metalurgica Serra" --contato "Joao" \\
        --email joao@empresa.com --equipamento "Painel de estufa" \\
        --escopo B --io 96 --acionamentos 8 --nr12 sim --seg 6
    ... --abrir     ja abre no navegador

O QUE ELE FAZ: serializa os campos no MESMO formato do lerFormulario() do site
({campos, radios}), codifica em base64url e monta o link
/orcamento#rascunho=... . Abrir o link preenche o formulario REAL do site nos
tres passos, pra conferir e enviar pelo botao de sempre.

O QUE ELE NAO FAZ: nao envia nada, nao fala com servidor nenhum. O fragmento
(#) fica no navegador — o pedido so existe quando o botao Enviar for apertado.

REGRA DA CASA (nada calado): campo de contagem com letra no meio e ERRO em voz
alta, nunca coercao — "10 a 15" virar 1015 foi exatamente o defeito que a
mascara do site matou. E o que faltar pro envio sai listado como FALTA, porque
da pra completar na tela.
"""

import argparse
import base64
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SITE = "https://borinprojetos.com.br/orcamento"

# sem ponto final nas mensagens: elas entram em listas
ERROS = []


def erro(msg):
    ERROS.append(msg)


def contagem(rotulo, valor):
    """So digito. Letra no meio nao vira numero calado: vira erro com nome."""
    s = str(valor or "").strip()
    if not s:
        return ""
    if not re.fullmatch(r"\d{1,6}", s):
        erro("%s tem que ser só número (veio %r)" % (rotulo, s))
        return ""
    return s


def data_iso(valor):
    """Aceita 15/09/2026 ou 2026-09-15; o input date do site exige ISO."""
    s = str(valor or "").strip()
    if not s:
        return ""
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        return "%s-%s-%s" % (m.group(3), m.group(2), m.group(1))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    erro("prazo em formato desconhecido (veio %r; use 15/09/2026)" % s)
    return ""


def email_ok(t):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@.]+\.[^\s@]{2,}", (t or "").strip()))


def montar_dados(a):
    """O dicionario no formato exato do lerFormulario() do _form.js."""
    campos = {
        "empresa": (a.empresa or "").strip(),
        "contato": (a.contato or "").strip(),
        "email": (a.email or "").strip(),
        "fone": (a.fone or "").strip(),
        "equipamento": (a.equipamento or "").strip(),
        "codigo": (a.codigo or "").strip(),
        "ios": contagem("--io", a.io),
        "acionamentos": contagem("--acionamentos", a.acionamentos),
        "seg_qtd": contagem("--seg", a.seg),
        "prazo": data_iso(a.prazo),
    }
    if campos["email"] and not email_ok(campos["email"]):
        erro("o email %r não parece um email" % campos["email"])
    if a.canal == "email+whats" and len(re.sub(r"\D", "", campos["fone"])) < 12:
        erro("canal email+whats pede o WhatsApp completo com DDD (--fone)")
    if campos["seg_qtd"] and a.nr12 != "sim":
        # a tela esconde seg_qtd quando NR-12 nao e "sim" — o numero iria no
        # pedido sem aparecer na conferencia nem no resumo. Melhor barrar aqui.
        erro("--seg só faz sentido junto de --nr12 sim (sem isso a tela esconde o campo)")
    # campo vazio fica de fora: o aplicarFormulario() ignora '' de qualquer
    # jeito, e o link sai mais curto
    campos = {k: v for k, v in campos.items() if v}
    return {
        "campos": campos,
        "radios": {"escopo": a.escopo, "nr12": a.nr12, "canal": a.canal},
    }


def link_de(dados):
    bruto = json.dumps(dados, ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(bruto).decode("ascii").rstrip("=")
    return SITE + "#rascunho=" + b64


# o que o formulario exige pra deixar enviar (validar() do site)
PRO_ENVIO = [("empresa", "a empresa"), ("contato", "o nome do contato"),
             ("email", "o email do cliente"),
             ("equipamento", "o que precisa de projeto")]


def main():
    p = argparse.ArgumentParser(
        description="Gera o link de rascunho do formulário de orçamento.")
    p.add_argument("--empresa", default="")
    p.add_argument("--contato", default="")
    p.add_argument("--email", default="")
    p.add_argument("--fone", default="", help="+55 54 99999-0000")
    p.add_argument("--equipamento", default="")
    p.add_argument("--codigo", default="", help="código interno do cliente")
    p.add_argument("--escopo", default="?", choices=["A", "B", "?"])
    p.add_argument("--nr12", default="?", choices=["sim", "nao", "?"])
    p.add_argument("--canal", default="email", choices=["email", "email+whats"])
    p.add_argument("--io", default="", help="pontos de I/O, só número")
    p.add_argument("--acionamentos", default="", help="só número")
    p.add_argument("--seg", default="", help="dispositivos de segurança, só número")
    p.add_argument("--prazo", default="", help="data alvo: 15/09/2026")
    p.add_argument("--abrir", action="store_true", help="abre no navegador")
    a = p.parse_args()

    dados = montar_dados(a)

    if ERROS:
        print()
        for e in ERROS:
            print("  ERRO: %s" % e)
        print()
        raise SystemExit(1)

    faltando = [rot for ch, rot in PRO_ENVIO if not dados["campos"].get(ch)]

    url = link_de(dados)
    print()
    print("  Rascunho com %d campos + escopo %s, NR-12 %s, canal %s"
          % (len(dados["campos"]), a.escopo, a.nr12, a.canal))
    if faltando:
        # falta nao derruba o link: completa-se na tela. Mas sai em voz alta,
        # porque sem esses o botao Enviar do site vai barrar.
        print("  FALTA pra enviar (dá pra completar no site): "
              + ", ".join(faltando))
    print()
    print(url)
    print()

    if a.abrir:
        import webbrowser
        webbrowser.open(url)


if __name__ == "__main__":
    main()
