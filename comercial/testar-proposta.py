# -*- coding: utf-8 -*-
"""Prova que a proposta em PDF sai inteira, numa folha, e sem campo vazio.

Regra #1 do AGENTS.md: teste só vale se souber falhar. Este foi rodado com
defeitos plantados antes de entrar no repositório — ver o rodapé.

O que ele guarda, em ordem de importância:

  1. UMA FOLHA, no caso MAIOR. Se a proposta virar duas, a folha 2 é onde caem
     as condições de pagamento — a parte que decide a venda
  2. nenhum campo vazio, nenhum "None", nenhum "%(" de formatação que escapou
  3. o número, o valor e o total aparecem mesmo, e o total bate com a conta

Roda com: python comercial/testar-proposta.py
"""

import importlib.util
import os
import sys

import fitz

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.environ.get("TEMP", "/tmp")

# ANTES de carregar os módulos: proposta de teste NUNCA na pasta real.
# O numero() conta os arquivos de comercial/propostas/, e cada rodada desta
# suíte inflava a numeração — a primeira proposta real ia sair PROP-2026-115.
import tempfile
_SAIDA = tempfile.mkdtemp(prefix="borin-teste-")
os.environ["BORIN_PROPOSTAS"] = _SAIDA
os.environ["BORIN_CONTRATOS"] = _SAIDA


def _mod(nome, arquivo):
    s = importlib.util.spec_from_file_location(nome, os.path.join(AQUI, arquivo))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


prop = _mod("prop", "proposta.py")
orc = _mod("orc", "orcamento.py")
calc = _mod("calc", "calcular.py")

passos = []


def P(nome, ok, detalhe=""):
    passos.append((nome, ok, detalhe))
    print("  %s %-50s %s" % ("ok   " if ok else "FALHA", nome, detalhe))


def pedido(**mudanca):
    class Ped(object):
        pass
    p = Ped()
    for k, v in dict(numero="TESTE-001", paginas=None, io=0, acionamentos=0,
                     seguranca=0, escopo="A", itens_manuais=0, setup_padrao=False,
                     urgencia=False, arquivo_fonte=False, abertura=False,
                     empresa="Metalúrgica Serra Ltda", contato="João Vieira",
                     equipamento="Painel de interface de sistema de pintura",
                     codigo="04003478", email="teste@exemplo.com").items():
        setattr(p, k, v)
    for k, v in mudanca.items():
        setattr(p, k, v)
    return orc.montar(p)


def gerar(p, rotulo):
    caminho = os.path.join(TMP, "teste-proposta-" + rotulo)
    pdf = prop.gerar(p, saida=caminho)
    d = fitz.open(pdf)
    texto = "\n".join(pg.get_text() for pg in d)
    n = len(d)
    fim = 0
    for b in d[0].get_text("blocks"):
        fim = max(fim, b[3])
    d.close()
    for ext in (".pdf", ".html"):
        try:
            os.remove(caminho + ext)
        except OSError:
            pass
    return n, texto, fim


print()
print("  " + "=" * 66)
print("  PROPOSTA EM PDF")
print("  " + "=" * 66)
print()
print("  [uma folha] o caso maior tem que caber sozinho")

# o pior caso: Escopo B, muitas paginas, itens manuais, setup e desconto —
# e o que gera mais linha de valor e mais item de entrega
maior = pedido(escopo="B", io=96, acionamentos=8, seguranca=6,
               itens_manuais=2, setup_padrao=True, abertura=True)
n, txt, fim = gerar(maior, "maior")
P("caso maior cabe em 1 folha", n == 1, "%d folha(s), conteúdo até y=%.0f de 842" % (n, fim))
P("sobra margem no pé da folha", fim < 815, "y final = %.0f" % fim)

for rot, p in [("A simples", pedido()),
               ("A com urgência", pedido(urgencia=True, io=40)),
               ("B sem desconto", pedido(escopo="B", io=96, acionamentos=8, seguranca=6)),
               # nome comprido quebra em duas linhas e come uma linha inteira do
               # topo — é o jeito realista de a folha estourar sem ninguém mexer
               # no CSS. Cliente real escreve assim.
               ("nome comprido", pedido(
                   escopo="B", io=96, acionamentos=8, seguranca=6, itens_manuais=2,
                   setup_padrao=True, abertura=True,
                   empresa="Indústria Metalúrgica e Caldeiraria Serra Gaúcha Ltda ME",
                   contato="João Carlos Vieira de Alencar Sobrinho",
                   equipamento="Painel de comando e interface do sistema de pintura "
                               "eletrostática da linha 3"))]:
    n, _, fim = gerar(p, rot.replace(" ", "-"))
    P("%s cabe em 1 folha" % rot, n == 1, "%d folha(s), y=%.0f" % (n, fim))

print()
print("  [conteúdo] o que o cliente precisa ler tem que estar lá")
n, txt, fim = gerar(maior, "conteudo")
for pedaco, rotulo in [("TESTE-001", "o número da proposta"),
                       ("Metalúrgica Serra", "o nome do cliente"),
                       ("João Vieira", "o contato"),
                       ("Painel de interface", "o equipamento"),
                       ("Entrada, na assinatura", "as condições de pagamento"),
                       ("Sigilo", "o sigilo"),
                       ("Databook", "o databook na lista de entrega"),
                       ("65.749.097/0001-85", "o CNPJ no rodapé"),
                       ("borinprojetos.com.br/cadastro", "o link do próximo passo")]:
    P("aparece: %s" % rotulo, pedaco in txt, "" if pedaco in txt else "SUMIU")

P("o total confere com o calculado", calc.brl(maior["total"]) in txt,
  calc.brl(maior["total"]))
P("o valor cheio aparece com 2+ somas e desconto", calc.brl(maior["valor_cheio"]) in txt,
  calc.brl(maior["valor_cheio"]))

# o redesenho de 11/08/2026: validade com data-limite, escopo protegido,
# normas de volta e o carimbo de folha no rodapé
for pedaco, rotulo in [("15 dias — até", "a validade com a data-limite"),
                       (maior["data_curta"], "a data de emissão no carimbo"),
                       ("BRN", "o monograma no carimbo"),
                       ("Não inclusos", "a proteção de escopo"),
                       ("IEC 60204-1", "a linha de normas"),
                       ("REV", "o campo de revisão do carimbo")]:
    P("aparece: %s" % rotulo, pedaco in txt, "" if pedaco in txt else "SUMIU")

print()
print("  [--direto] proposta de WhatsApp: sem /cadastro, mas COM aceite")
n3, txt3, _ = gerar(pedido(direto=True), "direto")
P("--direto sai sem o bloco do /cadastro",
  "borinprojetos.com.br/cadastro" not in txt3)
P("--direto tem a instrução 'Para fechar'",
  "PARA FECHAR" in txt3.upper() and "contrato preenchido" in txt3)
P("--direto também cabe em 1 folha", n3 == 1, "%d folha(s)" % n3)

print()
print("  [valor cheio] só quando informa algo")
_, txt4, _ = gerar(pedido(desconto=20), "uma-soma")
P("uma soma só + desconto: SEM linha 'Valor cheio'",
  "Valor cheio" not in txt4 and "Desconto combinado" in txt4,
  "riscado repetindo o mesmo número era ruído")

print()
print("  [sujeira] nada de campo cru vazando pro cliente")
for lixo in ("None", "%(", "{}", "[", "&amp;amp;"):
    P("não aparece %r" % lixo, lixo not in txt,
      "" if lixo not in txt else "VAZOU pro PDF")

print()
print("  [texto de verdade] o PDF não pode ser imagem")
P("o PDF tem texto selecionável", len(txt) > 800, "%d caracteres" % len(txt))

print()
print("  [escapa HTML] nome de empresa com < ou & não pode quebrar o documento")
n2, txt2, _ = gerar(pedido(empresa="Aço & Cia <Ltda>"), "escape")
P("empresa com & e < sai legível", "Aço & Cia <Ltda>" in txt2 and n2 == 1,
  "%d folha(s)" % n2)

print()
bons = sum(1 for _, o, _ in passos if o)
print("  " + "=" * 66)
print("  %d/%d passos ok" % (bons, len(passos)))
for nm, o, d in passos:
    if not o:
        print("    FALHOU: %s — %s" % (nm, d))
print("  " + "=" * 66)
print()

# COMO ESTE ARQUIVO FOI PROVADO (05/08/2026) — defeitos plantados e efeito:
#   1. espaço entre blocos de 8pt pra 24pt    -> 2 vermelhos (caso maior, nome comprido)
#   2. margem de rodapé da folha de 9 pra 45mm-> 2 vermelhos (os mesmos dois)
#   3. tirar as duas colunas da lista inclui  -> 2 vermelhos (os mesmos dois)
#   4. remover o bloco de condições do HTML   -> 2 vermelhos (pagamento, sigilo)
#   5. tirar o esc() do nome da empresa       -> 1 vermelho (escapa HTML)
# Se algum dia esses cinco passarem verde, o teste virou enfeite.
#
# UM DEFEITO QUE PASSOU BATIDO, e o que ele ensinou: mudar o `font` do body de
# 9,5 pra 12pt NÃO derrubou nada. Motivo: quase todo elemento aqui declara o
# próprio font-size, então a regra do body quase não governa nada. Não é bug —
# mas quem for enxugar a folha mexendo só no corpo do body vai achar que mexeu
# e não mexeu. O que realmente muda altura é espaçamento (.bloco, padding das
# tabelas, padding dos li) e a margem da @page.

raise SystemExit(0 if bons == len(passos) else 1)
