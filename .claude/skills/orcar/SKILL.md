---
name: orcar
description: Monta a ficha de orçamento a partir de mensagens de cliente (WhatsApp, email, conversa) e devolve o link de rascunho pro Mateus conferir no site e enviar. Use quando o Mateus colar mensagens de um pedido de orçamento, chamar /orcar, ou disser "monta a ficha", "faz o orçamento disso", "chegou um pedido".
---

# /orcar — do pedido por conversa ao link de rascunho

O caminho: o cliente descreve o projeto por mensagem → eu leio, conto os pontos
e monto a ficha → o Mateus **confere no site** e é ele quem envia. Eu nunca
envio nada sozinho; o botão é dele.

## Antes de contar qualquer ponto

**Ler `regras-de-leitura.md` (nesta pasta).** É a memória viva de como o
Mateus conta I/O, acionamentos e segurança. Cada regra veio de correção dele —
ignorar uma é repetir um erro que ele já corrigiu.

## O passo a passo

1. **Extrair da conversa**: contato, empresa, email, fone, equipamento (uma
   frase fiel ao que o cliente escreveu, com marcas e opções que ele citou),
   prazo se houver.

2. **Contar os pontos** aplicando as regras de `regras-de-leitura.md`. Mostrar
   a conta ABERTA no chat (ex.: "2 pontos × 20 andares + 8 do painel = 48") —
   número sem conta não dá pra conferir.

3. **Não decidir o que é técnico**: escopo (A/B) e NR-12 ficam em `?` a menos
   que a conversa diga explicitamente. Decisão técnica é do Mateus, na tela.

4. **Gerar o link**:
   ```
   python comercial/rascunho.py --contato "..." --equipamento "..." \
       --io N --acionamentos N [--nr12 sim --seg N] [--empresa ...] [--email ...]
   ```
   O que faltar pro envio o CLI lista como FALTA — repassar isso ao Mateus.

5. **Dar a referência de preço** junto do link, pros dois escopos, usando a
   calculadora oficial (nunca de memória):
   ```
   python -c "... calcular.estimar_paginas(io, acion, seg, esc) ... calcular.calcular(p)"
   ```
   Tabela: páginas, valor cheio, valor com 50% de abertura.

6. **Avisar sempre**: o email que ele puser na ficha **recebe na hora** (conta
   criada + estimativa automática se escopo for A/B). Se ele quiser só
   responder o valor por WhatsApp primeiro, é só não enviar — o link não
   expira.

## Depois que ele enviar o pedido

7. Proposta fechada: `python comercial/orcamento.py ... --enviar --para-mim`
   → ele confere na caixa dele → aprovou, roda de novo com `--enviar` pro
   cliente.
8. Contrato: `comercial/contrato.py`, mesmo esquema — conferir, aprovar, sair.

## Quando o Mateus corrigir uma contagem ou regra

Adicionar a regra em `regras-de-leitura.md` **na hora**, com uma linha de
contexto de onde veio. É o "guarda na memória" dele — a skill só vale enquanto
esse arquivo acumular o jeito DELE de contar.
