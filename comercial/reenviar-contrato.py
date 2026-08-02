# -*- coding: utf-8 -*-
"""Reemite o contrato ja preenchido, depois que o cliente completa o cadastro.

O fluxo e este:

  1. o cliente recebe a proposta com o botao "Preencher meus dados e gerar o contrato"
  2. ele preenche /cadastro (razao social, CNPJ, endereco, quem assina)
  3. o Worker me avisa por email que o cadastro chegou
  4. eu rodo:  python comercial/reenviar-contrato.py --cliente email@dele.com --enviar

O contrato sai com os dados dele nos lugares certos, sem nenhum campo em
branco, e ele so assina. O valor e o escopo sao exatamente os da proposta
original — vem do .json que o orcamento.py gravou, nao de um novo calculo.

Sem --enviar, so gera o PDF e mostra o que sairia. Use --para-mim pra receber
o email identico ao do cliente antes de mandar pra ele.
"""

import argparse
import base64
import datetime
import glob
import importlib.util
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA = os.path.join(AQUI, "propostas")

def _mod(nome, arquivo):
    e = importlib.util.spec_from_file_location(nome, os.path.join(AQUI, arquivo))
    m = importlib.util.module_from_spec(e)
    e.loader.exec_module(m)
    return m


def achar_proposta(email):
    """A proposta mais recente daquele cliente."""
    achados = []
    for f in glob.glob(os.path.join(PASTA, "*.json")):
        try:
            d = json.loads(io.open(f, encoding="utf-8").read())
        except ValueError:
            continue
        if (d.get("email") or "").strip().lower() == email.strip().lower():
            achados.append((d.get("em", ""), d.get("numero", ""), d))
    if not achados:
        return None
    achados.sort()
    return achados[-1][2]


def corpo_html(orc, p, cad):
    """Email curto: o documento e o anexo, o email so tira a duvida do que fazer.

    O cabecalho e o rodape saem das mesmas constantes do orcamento.py — os dois
    emails chegam na mesma caixa com dias de diferenca e tem que parecer da
    mesma empresa.
    """
    e = orc.esc
    d = {
        "sans": orc.SANS, "mono": orc.MONO, "t": orc.T,
        "cinza": orc.CINZA, "rule": orc.RULE, "acento": orc.ACENTO,
        "contato": e((p["contato"] or "").split(" ")[0]) or "Olá",
        "numero": e(p["numero"]),
        "equipamento": e(p["equipamento"]),
        "razao": e(cad.get("razao_social", "")),
        "cnpj": e(cad.get("cnpj", "")),
        "assina": e(cad.get("rep_nome", "")),
        "cargo": e(cad.get("rep_cargo", "")),
        "total": e(p["total_brl"]),
    }
    return ("""<div style="margin:0;padding:24px 16px;background:#F4F4F4;font-family:%(sans)s">
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
       color:%(cinza)s">Contrato %(numero)s</div>
  <h1 style="font-size:22px;font-weight:700;margin:6px 0 10px;letter-spacing:-.02em;color:%(t)s">
    %(contato)s, o contrato está pronto</h1>
  <p style="font-size:14px;line-height:1.6;color:%(t)s;margin:0 0 16px">
    Usei os dados que você preencheu. O contrato em anexo já está completo — não há
    nenhum campo para você editar. Confira, assine e me devolva respondendo este email.
  </p>
</div>

<div style="padding:0 28px">
  <table cellpadding="0" cellspacing="0" style="width:100%%;border-collapse:collapse;
         border:1px solid %(rule)s">
    <tr><td style="padding:9px 12px;border-bottom:1px solid %(rule)s;width:34%%;
            font-family:%(mono)s;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
            color:%(cinza)s">Contratante</td>
        <td style="padding:9px 12px;border-bottom:1px solid %(rule)s;font-size:14px;color:%(t)s">%(razao)s</td></tr>
    <tr><td style="padding:9px 12px;border-bottom:1px solid %(rule)s;
            font-family:%(mono)s;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
            color:%(cinza)s">CNPJ</td>
        <td style="padding:9px 12px;border-bottom:1px solid %(rule)s;font-size:14px;color:%(t)s">%(cnpj)s</td></tr>
    <tr><td style="padding:9px 12px;border-bottom:1px solid %(rule)s;
            font-family:%(mono)s;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
            color:%(cinza)s">Assina</td>
        <td style="padding:9px 12px;border-bottom:1px solid %(rule)s;font-size:14px;color:%(t)s">%(assina)s, %(cargo)s</td></tr>
    <tr><td style="padding:9px 12px;border-bottom:1px solid %(rule)s;
            font-family:%(mono)s;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
            color:%(cinza)s">Objeto</td>
        <td style="padding:9px 12px;border-bottom:1px solid %(rule)s;font-size:14px;color:%(t)s">%(equipamento)s</td></tr>
    <tr><td style="padding:9px 12px;font-family:%(mono)s;font-size:10px;letter-spacing:.08em;
            text-transform:uppercase;color:%(cinza)s">Valor</td>
        <td style="padding:9px 12px;font-size:16px;font-weight:700;color:%(t)s">%(total)s</td></tr>
  </table>
</div>

<div style="padding:20px 28px 24px">
  <p style="font-size:13px;line-height:1.6;color:%(t)s;margin:0 0 12px">
    Assinatura eletrônica em qualquer padrão que permita verificar autoria e integridade
    serve — não precisa reconhecer firma. Assim que o contrato voltar assinado, eu mando
    a ficha do projeto e o prazo começa a contar.
  </p>
  <p style="font-size:13px;line-height:1.6;color:%(cinza)s;margin:0">
    Se algum dado saiu errado, responda dizendo qual — eu corrijo e reenvio no mesmo dia,
    sem custo.
  </p>
</div>

<div style="padding:14px 28px;border-top:1px solid %(rule)s;font-family:%(mono)s;font-size:10px;
     color:%(cinza)s">
  Borin Projetos Elétricos &middot; CNPJ 65.749.097/0001-85 &middot; Caxias do Sul / RS<br>
  contato@borinprojetos.com.br &middot; borinprojetos.com.br
</div>

</div></div>""" % d)


def main():
    a = argparse.ArgumentParser(description="Reemite o contrato preenchido pelo cadastro do cliente")
    a.add_argument("--cliente", required=True, help="email do cliente")
    a.add_argument("--enviar", action="store_true")
    a.add_argument("--para-mim", action="store_true", help="manda a copia pra mim, identica")
    o = a.parse_args()

    d = achar_proposta(o.cliente)
    if not d:
        raise SystemExit(
            "Nao achei proposta salva para %s.\n"
            "As propostas ficam em comercial/propostas/*.json — se essa e antiga,\n"
            "rode o orcamento.py de novo com --com-cadastro." % o.cliente)

    orc = _mod("orc", "orcamento.py")
    ct = _mod("ct", "contrato.py")
    calc = _mod("calc", "calcular.py")

    # remonta a proposta exatamente com os argumentos originais.
    # O numero e fixado ANTES: o montar() emite um numero novo a cada chamada,
    # e o contrato reemitido tem que levar o numero da proposta que o cliente
    # ja recebeu — senao viram dois documentos diferentes na mao dele.
    ns = argparse.Namespace(**d["argumentos"])
    ns.numero = d["numero"]
    p = orc.montar(ns)
    if p["numero"] != d["numero"]:
        raise SystemExit("O numero mudou (%s -> %s). Nao envie assim."
                         % (d["numero"], p["numero"]))

    conta, cad = ct.buscar_cadastro(o.cliente)
    if not cad:
        raise SystemExit("%s ainda nao preencheu /cadastro." % o.cliente)

    p["cadastro"] = cad
    p["empresa"] = cad.get("razao_social") or p["empresa"]
    p["contato"] = cad.get("rep_nome") or p["contato"]
    p["total_extenso"] = ct.extenso(p["total"])
    p["total_brl"] = calc.brl(p["total"])
    p["itens"] = getattr(ns, "itens_manuais", 0)

    if p["total"] != d.get("total"):
        raise SystemExit(
            "O valor mudou (%s -> %s). Isso nao pode acontecer num reenvio:\n"
            "o cliente ja recebeu a proposta com o valor antigo. Confira o calcular.py."
            % (calc.brl(d.get("total") or 0), calc.brl(p["total"])))

    pdf, faltam = ct.gerar(p)

    print()
    print("  " + "-" * 56)
    print("  %-12s %s" % ("CONTRATO", p["numero"]))
    print("  %-12s %s" % ("CLIENTE", p["empresa"]))
    print("  %-12s %s" % ("CNPJ", cad.get("cnpj", "?")))
    print("  %-12s %s, %s" % ("ASSINA", cad.get("rep_nome", "?"), cad.get("rep_cargo", "?")))
    print("  %-12s %s" % ("VALOR", p["total_brl"]))
    print("  " + "-" * 56)
    print("  pdf: %s" % pdf)
    if faltam:
        print("  AINDA EM BRANCO: %s" % ", ".join(faltam))
        print("  (o cliente nao deveria receber assim — corrija antes de enviar)")

    if not o.enviar:
        print("  (nada enviado — use --enviar, ou --enviar --para-mim pra conferir antes)")
        print()
        return

    anexos = [{
        "nome": "Contrato %s - Borin Projetos Eletricos.pdf" % p["numero"],
        "tipo": "application/pdf",
        "base64": base64.b64encode(io.open(pdf, "rb").read()).decode(),
    }]
    corpo = corpo_html(orc, p, cad)
    p2 = dict(p)
    p2["doc"] = "Contrato " + p["numero"]
    ok = orc.enviar(p2, corpo, o.para_mim, anexos)
    print("  email: %s" % ("enviado para " + ("voce (copia)" if o.para_mim else p["email"])
                           if ok else "FALHOU"))
    print()


if __name__ == "__main__":
    main()
