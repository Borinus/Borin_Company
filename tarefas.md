# Tarefas

## Trava tudo — fazer primeiro

- [x] **Registrar `borinprojetos.com.br`** no registro.br — feito em 29/07/2026. Vence em 28/07/2027
- [x] **Nameservers apontados pra Cloudflare** — delegação ativa em 29/07/2026 (`duke`/`lara`)
- [x] **Site no ar em 29/07/2026** — `borinprojetos.com.br` e `www.`, SSL válido nos dois
- [x] Email Routing ativado — MX, SPF e DKIM no ar
- [x] `contato@` e `mateus@borinprojetos.com.br` criados, encaminhando pro `mateusborin73@gmail.com`. Catch-all desligada
- [x] Recebimento testado — funciona, mas o Gmail joga no Spam (inerente a encaminhamento)
- [ ] Criar o filtro no Gmail: Para = `contato@borinprojetos.com.br OR mateus@borinprojetos.com.br` → Nunca enviar para o Spam + marcador `Borin`. Passo a passo em `site/dns.md`
- [ ] Testar de um endereço externo (não do próprio Gmail de destino)
- [ ] Revogar o token da Cloudflare usado em 29/07 (passou pelo chat) e criar outro. Se quiser que eu configure email por API na próxima, incluir `Email Routing Addresses: Edit` no nível de conta
- [x] CNPJ aberto — MEI, 65.749.097/0001-85. Simples fica pra quando o faturamento pedir
- [x] Conta bancária PJ separada da pessoal — já existe
- [ ] **Teste de 5 minutos:** entrar em `nfse.gov.br/EmissorNacional` com a conta gov.br e ver quais códigos de serviço aparecem pro CNPJ. MEI **não** usa o sistema da prefeitura desde 03/04/2023 — corrigido em 05/08/2026
- [ ] Emitir a primeira nota de teste pelo Emissor Nacional
- [x] Controle do faturamento acumulado — `comercial/faturar.py`, uma linha por nota. **Gatilho: R$ 55 mil → abrir o Simples.** O teto de 2026 é R$ 67.500 (proporcional), não R$ 81 mil; passar de R$ 81 mil desenquadra retroativo a 18/03/2026 — ver `comercial/formalizacao.md`
- [ ] Quando abrir o Simples: perguntar ao contador sobre o Fator R, que decide entre ~6% e ~15,5% de alíquota (~R$ 850/mês de diferença)
- [x] **Conflito de interesse com a FlowSistem — não é impedimento** (03/08/2026). Eles são praticamente os únicos no Brasil que vendem Graco, então o cliente atendido não concorre com eles; e o próprio chefe já faz projeto por fora. Ver `_contexto/estrategia.md`
- [ ] Ler o contrato de trabalho procurando **exclusividade**, **não concorrência** e **confidencialidade**
- [ ] Contar na FlowSistem que abriu CNPJ — **antes** do primeiro cliente, não depois

## Sistema e comercial — 05/08/2026

- [x] **`python testar-tudo.py`** — um comando, um veredito. Sem argumento roda as 3 offline; com `--tudo` inclui a travessia, que fala com produção. Hoje: **141/141**
- [x] **A travessia** (`site/testar-travessia.py`) — o caminho inteiro numa passada: pedido, senha, conta, troca de senha, proposta com PDFs, cadastro, contrato preenchido, arquivos. 41/41 — vai até o projeto entregue, com a trilha de etapas que o cliente acompanha — e apaga a conta de teste no fim
- [x] **Cobrança** em `comercial/faturar.py` — `cobrar` abre as duas parcelas (40% na assinatura, 60% em 15 dias) e a nota dá baixa sozinha. Parcela vencida sai marcada
- [x] **Suporte com taxa** desenhado em `comercial/suporte.md` — 30 dias inclusos, depois avulso, pacote ou anual. A linha já entra na proposta
- [ ] Confirmar os três preços do suporte junto com a próxima revisão de `precificacao.md`
- [ ] Cláusula de suporte no `modelo-contrato.md`, com o teto de horas
- [x] Meta aprovou os dois modelos em 06/08/2026. O Worker já usa o **`pedido_recebido_botoes`** (`ZAP_TEMPLATE` no `wrangler.toml`): botão "Acompanhar o pedido" abre /conta e "Falar com o Mateus" liga pro (54) 99664-2003 — resposta de cliente não cai mais no vazio. Demo enviada pro teu WhatsApp
- [ ] **Webhook do WhatsApp** — continua esperando a `BORIN_META_APP_SECRET` no `.env` (developers.facebook.com → app Borin Site → Configurações → Básico → Chave secreta do app). Depois: `python site/worker/ligar-webhook.py`. Sem isso, resposta escrita no número automático é descartada pela Meta

## Site

- [ ] **Ligar o "Entrar com o Google"** — código pronto e publicado em 05/08/2026, falta só o client_id. Passo do Mateus (5 min): `console.cloud.google.com` → criar projeto → Tela de permissão OAuth (External, nome "Borin Projetos Elétricos") → Credenciais → Criar credencial → ID do cliente OAuth → Aplicativo da Web → em "Origens JavaScript autorizadas" pôr `https://borinprojetos.com.br` **e** `https://www.borinprojetos.com.br` → copiar o ID (termina em `.apps.googleusercontent.com`) → colar no `.env` como `BORIN_GOOGLE_CLIENT_ID=...` e avisar. O botão aparece sozinho; até lá a página fica como era

- [x] Landing page com a identidade aplicada (`site/index.html`)
- [x] WhatsApp preenchido no `site/_pagina.html` — +55 (54) 99664-2003, com mensagem pré-pronta
- [x] Revisão de copy em 29/07/2026 — título encurtado, textos genéricos cortados, coluna do pacote consolidada de 13 pra 9 itens
- [x] Marca compacta criada (`marca/favicon.svg`) e registrada no design-guide
- [x] Prazo por páginas de diagrama no topo (5/8/12 dias úteis contra 2/3/4 semanas do mercado)
- [x] Condição de abertura limitada a 3 projetos e movida pra fora do topo
- [x] **Checklist do cliente no ar** — `/checklist`, 35 campos, monta a mensagem e abre o WhatsApp ou baixa `.txt`. Sem servidor, nada armazenado
- [ ] Aguardando retorno da amiga gestora de marketing
- [ ] Testar o checklist no celular e ver se a mensagem do WhatsApp não fica cortada (mensagem longa pode estourar o limite da URL)
- [ ] Cadastrar no Google Search Console
- [ ] Perfil no LinkedIn apontando pro site

## Marca

- [x] Definir nome — **Borin Projetos Elétricos**
- [x] Identidade visual: logo, carimbo, paleta, tipografia (`marca/design-guide.md`)
- [x] Instalar a fonte Inter na máquina — já está (`Inter-Bold.ttf` detectada em 05/08/2026). **Rodar `python marca/gerar-logos.py` de novo** pra refazer os PNGs do logo com a tipografia definitiva, em vez da Arial
- [x] Marcador "SUA LOGO AQUI" pro projeto base — `marca/gerar-placeholder.py`, 4 formatos em `marca/png/`
- [ ] Converter os SVGs do logo em curvas antes de mandar pra gráfica
- [ ] Conferir a marca na base do INPI antes de registrar
- [ ] Checar o @ disponível no Instagram

## Entrega

- [x] Padrão de entrega — Escopos A e B (`padroes/padrao-entrega.md`)
- [x] Checklist de conferência (`padroes/checklist-conferencia.md`)
- [x] Calibrar o padrão com um projeto real (04003478 — Painel de Interface)

### Templates próprios — não dá pra usar os da FlowSistem

**Planilhas — feitas** (`padroes/templates/xlsx/`, geradas por `gerar-planilhas.py`)

- [x] Lista de materiais
- [x] Arquitetura de CLP, com resumo automático de pontos
- [x] Design térmico, com cálculo de superfície, ΔT e veredito de ventilação
- [x] Seis planilhas de identificações, com aba de instrução de impressão
- [x] Lista de instalação, com base de cabos, acompanhamento por horas e acessórios
- [x] Base de dissipação semeada em 05/08/2026 — 9 faixas de minidisjuntor MDWH e a bobina do contator CWB, com documento e página na coluna de fonte. Fica em `gerar-planilhas.py` (constante `BASE_DISSIPACAO`), então regenera junto com as planilhas
- [ ] Somar à base os componentes de cada projeto novo (relé, CLP, borne, climatizador). Fonte e inversor não entram por tabela — saem do rendimento, fórmula já na planilha
- [ ] Preencher a aba Impressão com impressora e modelo de etiqueta
- [ ] Conferir se a exportação do CAD cai direto nessas colunas

**CAD elétrico — precisa estar no PC**

- [ ] Template de folha com o carimbo da Borin (usar `marca/png/borin-carimbo.png`)
- [ ] Template de capa com a tabela *Descrição do Quadro* e a tabela de revisões
- [ ] Template de memorial descritivo com os seis blocos — **conteúdo pronto** em `padroes/memorial-padrao.md` (33 dos ~45 campos já respondidos). Falta montar a folha no CAD
- [ ] **Decidir a cor do 0 VCC.** `padrao-entrega.md` diz marrom, o formulário do site diz azul. Escolher uma e acertar os dois — detalhe em `padroes/memorial-padrao.md`
- [ ] Folha de simbologia própria
- [ ] Banco de artigos próprio

## Comercial

### Elevador do Zucolotto — primeiro pedido real, aberto em 10/08/2026

- Pedido por WhatsApp (Matheus Zucolotto): elevador de cargas até 20 andares — LOGO! ou IHM
  Weintek, remota, inversor, 2 motores, encoder; trava, sensor de porta e botoeira por andar
- Ficha lida: 48 I/O + 2 acionamentos + **20 travas como NR-12** (regra na skill `/orcar`)
- [ ] **Desconto combinado: 20%** — decidido em 10/08/2026. A proposta sai com
  `--desconto 20` (substitui a condição de abertura; a ferramenta recusa os dois juntos)
- Referência: escopo A ~37 pág → **R$ 6.900** · escopo B ~40 pág → **R$ 7.500**
- [ ] Falta empresa e email dele pra enviar o pedido pelo link de rascunho
- [ ] Projeto ainda não fechado do lado dele (nº de andares em aberto)

### Conversa com possível sócio — aberta em 29/07/2026

- [x] Conversa inicial feita em 29/07/2026 — positiva, e ele já reconhece que o software é do Mateus
- [x] Memorando de entendimento escrito: `comercial/memorando-parceria.md` (cláusula 2 = propriedade do sistema)
- Memorando **parado por decisão do Mateus** em 29/07/2026 — ele considera resolvido no verbal. O parceiro também é terceiro na empresa, não é dono dela. Retomar só se ele pedir
- [ ] Definir a contrapartida: o que ele traz em troca dos ~R$ 14.000 a 19.700 de desconto
- [ ] Definir onde o desconto de 80% acaba — contagem ou data
- [ ] Se virar sócio de fato: refazer a precificação com a licença na conta, e falar com o contador sobre o regime

- [x] Fluxo comercial do contato ao pagamento (`comercial/fluxo-comercial.md`)
- [x] Modelo de proposta (`comercial/modelo-proposta.md`)
- [x] Modelo de contrato (`comercial/modelo-contrato.md`)
- [x] Preencher `comercial/precificacao.md` — tabela v1 de 29/07/2026, R$ 235/h
- [x] Licença de CAD — **decidido em 29/07/2026: começar sem custo de licença.** O sistema próprio cobre o papel do eBuild/Cogineer. Gatilho pra revisar: entrar outra pessoa no trabalho — aí a licença entra na conta e os preços sobem
- [ ] Revisar o contrato com advogado antes de assinar o primeiro
- [ ] Cronometrar o próximo projeto **separando tempo de máquina e tempo teu** (briefing, conferência, revisão) — o piso humano é a estimativa mais frágil da tabela e é ele que limita quantos clientes cabem no mês
- [ ] Levantar lista de integradoras e fabricantes de máquina da Serra — a trava agora é demanda, não capacidade
- [x] **`TODOS_NOVOS` desarmado** (05/08/2026). Era uma constante que dava a condição de abertura pra todo cliente, com um comentário pedindo pra trocar quando o primeiro pagante entrasse — R$ 6.700 por proposta dependendo de alguém lembrar. Agora a regra é o `clientes-atendidos.json`, e toda proposta imprime NOVO ou ANTIGO na tela. `--forcar-novo` cobre a conferência de formato. Teste em `comercial/testar-abertura.py` (17/17)
- [ ] **Commitar `comercial/clientes-atendidos.json`.** Ele não está no git (nunca foi adicionado, não é ignorado). É o arquivo que decide quem leva a condição de abertura — se sumir, todo cliente vira novo e leva R$ 6.700 de desconto de novo. Limpo em 05/08/2026: saíram 8 endereços de teste, ficou vazio, que é a verdade
- [x] Proposta em PDF com a identidade aplicada — `comercial/proposta.py`, uma folha A4, anexada sozinha no email junto com o contrato. Teste em `comercial/testar-proposta.py` (24/24) trava a folha única

## MCPs pra instalar depois

Nenhuma das ferramentas que você usa hoje (CAD elétrico, Excel) tem conector pronto — são locais e o Claude
já lê e escreve os arquivos direto.

- [ ] Playwright — renderiza HTML em PNG/PDF. Útil pra gerar proposta e apresentação com a identidade: `npx playwright install chromium`
- [ ] Gmail — ler e escrever email de cliente sem sair do Claude: `claude mcp add gmail -- npx -y @gongrzhe/server-gmail-autoauth-mcp`
