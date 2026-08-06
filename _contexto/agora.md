# Agora — contexto vivo

> Este é o contexto que muda toda semana (diferente de `estrategia.md`, que é o foco de fundo).
> O `/iniciar` lê isto no começo da sessão; o `/atualizar` escreve aqui no fim.
> Mantenha curto: o que passou de ~30 dias sai daqui (vai pro histórico ou some).

## Onde paramos

Sessão de 05/08/2026. O plano ganhou calendário: **preparar até o início de setembro, começar a
vender depois.** Detalhe em `_contexto/estrategia.md`, seção "Plano em duas faixas".

O que fechou nesta sessão:

- **Proposta em PDF** com a identidade (`comercial/proposta.py`), uma folha, anexada junto do contrato
- **`TODOS_NOVOS` desarmado** — dava desconto de abertura pra todo cliente, inclusive repetido
- **Controle de faturamento** (`comercial/faturar.py`) com o gatilho de R$ 55 mil, e as parcelas
  40/60 a receber (`cobrar` + `receber.json`)
- **NFS-e corrigida:** MEI emite pelo portal nacional, não pelo sistema da prefeitura
- **Logo alinhado** — o fio agora acompanha a largura do nome
- **WhatsApp com botões no ar** (06/08): modelo `pedido_recebido_botoes` aprovado e ativo —
  "Falar com o Mateus" leva pro número real; resposta no número automático não se perde mais
- **Login com Google pronto** — código publicado e provado (13/13); o botão aparece quando o
  Mateus criar o client_id (passo dele, em `tarefas.md`)
- **Travessia ponta a ponta verde** (`site/testar-travessia.py`) — as 8 "falhas" da primeira
  rodada eram do rascunho de teste, não do sistema. Sobra real: `apagarConta` deixava PDF
  órfão no R2 — corrigido, e os 6 órfãos de teste apagados do bucket

**Esperando só o Mateus (2 chaves, 5 min cada):** `BORIN_META_APP_SECRET` (liga o webhook —
resposta de cliente vira email) e `BORIN_GOOGLE_CLIENT_ID` (faz o botão do Google aparecer).
Os dois entram no `.env`; os passos estão em `tarefas.md`.

## Como trabalhamos daqui pra frente

- **Conteúdo técnico de projeto é do Mateus.** Simbologia, memorial, dissipação, normas, cores de
  cabo: ele faz, e faz junto quando pedir. Não propor, não preencher, não cobrar. Está no `AGENTS.md`
- **Marketing e anúncios estão com um amigo dele.** Assunto encerrado até setembro/2026 — não
  levantar, não perguntar, não sugerir anúncio
- O que é nosso: comercial, formalização, marca, site, sistema, automação e preço

## Decisões recentes

- **29/07 — Preço:** piso de R$ 235/h. Escopo A: R$ 3.500 / 5.900 / 8.200. Escopo B grande:
  R$ 11.700. Prazos de 5 a 12 dias úteis
- **29/07 — Preço se calcula pela hora de mercado, não pela sua.** O sistema faz 8x mais rápido; se
  o preço saísse do custo próprio, um projeto de R$ 5.900 sairia por R$ 2.100. O 8x vira margem,
  prazo e capacidade — nunca desconto. **Nunca abrir hora na proposta**
- **29/07 — Licença:** começar sem custo de licença própria. O sistema cobre o papel do módulo pago
  de automação (eBuild/Cogineer). Gatilho pra revisar: entrar outra pessoa no trabalho
- **29/07 — Condição de abertura:** limite de 3 projetos. Rende R$ 328 a 418/h mesmo pela metade,
  acima do piso. O risco dela é ancoragem, não prejuízo
- **29/07 — CONFERENCIAS é produto próprio**, não material de empregador. O código é do Mateus; os
  dados dentro da pasta são da FlowSistem

## Pendências

**Trava tudo:**
- Registrar `borinprojetos.com.br` (R$ 40) — trava site e email
- Contador: ME no Simples (a meta estoura o teto do MEI), CNAE e alíquota real
- ~~Conflito de interesse com a FlowSistem~~ — resolvido em 03/08, não impede prospectar. Sobrou ler o contrato e avisar lá antes do primeiro cliente

**Conversa com o possível sócio (aberta):**
- Definir **por escrito de quem é o sistema de geração, antes do primeiro projeto**
- Definir a contrapartida dele e onde o desconto de 80% acaba

**Preço:**
- Cronometrar o próximo projeto separando tempo de máquina e tempo humano — o piso humano
  (4 a 8h/projeto) é a estimativa mais frágil da tabela

## Quente agora

A trava do negócio virou **demanda, não capacidade**. Sobra produção e falta cliente. Prospecção
passa na frente de qualquer refino de processo.
