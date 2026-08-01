# Precificação

> A preencher com os teus números. A estrutura abaixo é o método — os valores só você pode definir,
> e definir errado no começo é o erro mais caro que dá pra cometer.

---

## Como chegar no preço

**Não comece pelo preço do concorrente.** Comece pelo teu custo-hora, chegue no preço mínimo, e só
então compare com o mercado pra ver se cabe.

### 1. Quantas horas você tem por mês

Você trabalha em tempo integral na FlowSistem. As horas do negócio próprio são noite e fim de semana.

| | Base | Com sábado |
|---|---|---|
| Horas disponíveis por semana | 12 | 20 (12 + 8 no sábado) |
| Semanas por mês | 4 | 4 |
| Horas brutas por mês | 48 | 80 |
| Menos 20% (proposta, cobrança, conversa, retrabalho) | −9,6 | −16 |
| **Horas faturáveis por mês** | **38** | **64** |

O sábado é reserva, não rotina — 80h/mês em cima de um emprego integral não se sustenta por muitos
meses seguidos. **Planeje pelo base (38h), use o sábado para absorver pico e urgência.**

### 2. Quanto você precisa faturar

Meta de retirada: R$ 6.000 a 10.000/mês. A conta abaixo usa **R$ 8.000** (meio da faixa).

| | |
|---|---|
| Retirada pretendida | R$ 8.000 |
| Licença CAD elétrico (mensalizada) | R$ 0 — ver decisão abaixo |
| Domínio + email (Cloudflare, grátis) | R$ 4 |
| Contador (ME, estimado) | R$ 400 |
| Faturamento antes de imposto | R$ 8.404 |
| Imposto (Simples Anexo III, 6% inicial — confirmar) | ÷ 0,94 |
| **Faturamento necessário por mês** | **R$ 8.940** |
| **Custo-hora mínimo (38h)** | **R$ 235/h** |
| Custo-hora se puxar o sábado (64h) | R$ 140/h |

> **Decisão de 29/07/2026 — operar sem custo de licença no início.** O sistema de geração cobre o
> papel do módulo de automação (eBuild/Cogineer), então esse custo não existe. A licença base do
> EPLAN fica sem custo próprio nesta fase, por decisão do Mateus.
>
> **Gatilho de revisão: entrar outra pessoa no trabalho.** No dia em que chamar alguém pra ajudar,
> a licença passa a ser necessária, entra na conta e **todos os preços desta tabela sobem**. Refazer
> a conta antes de fechar proposta a partir daí — não depois.

**R$ 235/h é piso, não método de preço.** É o mínimo que cada hora sua precisa render pra meta
fechar. Não multiplique por hora de projeto pra chegar no valor — com o sistema de geração, isso
daria R$ 2.100 num projeto que o mercado cobra R$ 5.900. Ver *Por que o preço não cai junto com o
custo*, mais abaixo.

> **Atenção MEI:** o teto do MEI (~R$ 81 mil/ano, confirmar valor vigente) dá cerca de R$ 6.750/mês
> de faturamento. A meta acima estoura. Provavelmente é **ME no Simples**, não MEI — levar essa
> conta pro contador, é a primeira pergunta.

### 3. Quantas horas leva cada escopo

**Existem duas colunas de hora, e confundir as duas é o erro mais caro deste documento.**

- **Hora de mercado** — quanto o projeto custa feito à mão, do jeito que integradora, escritório e
  fabricante grande fazem. É contra isso que o cliente compara quando pede orçamento em três lugares.
- **Hora sua** — quanto custa com o sistema de geração rodando: cerca de **8x mais rápido** na
  execução, e mais assertivo, porque o gerador confere o próprio resultado.

**Único dado real que existe:** o 04003478 — Painel de Interface, 51 folhas, 96 pontos de I/O
(32 DI + 64 DQ), 3 instalações, ~32 cabos, Escopo B. **40 a 60h feito à mão** (estimativa do Mateus).
A tabela usa 50h como hora de mercado e deriva o resto proporcionalmente.

| Escopo | Hora de mercado | Execução (÷8) | Piso humano | **Hora sua** |
|---|---|---|---|---|
| A — pequeno (até ~30 I/Os) | 15 | 2 | 4 | **6** |
| A — médio (~30 a 80 I/Os) | 25 | 3 | 6 | **9** |
| A — grande (acima de 80 I/Os) | 35 | 4,5 | 8 | **12** |
| B — médio | 35 | 4,5 | 8 | **12** |
| B — grande | 50 | 6 | 8 | **14** |

**O piso humano não tem 8x.** Briefing, alinhamento de premissa, conferência final do PDF, rodadas
de revisão e entrega são teus, não do gerador. Ele acelera desenho, listas e etiquetas — não a
conversa com o cliente. Os pisos acima são estimativa: **cronometre o primeiro projeto separando as
duas partes** (tempo de máquina x tempo teu) e substitua.

Só a coluna "hora de mercado" da última linha é medida. Todo o resto é derivado.

---

## Modelo de cobrança

**Preço fechado por escopo.** É o recomendado, e por três motivos: o cliente sabe quanto vai gastar,
você ganha por eficiência em vez de perder, e não abre discussão item a item.

Cobrar por hora só em revisão extra e em serviço de escopo indefinido, tipo revisar projeto de
terceiro.

---

## Tabela

**Versão 1 — 29/07/2026.** Preço de mercado: calculado a R$ 235/h sobre a **hora de mercado** (o
projeto feito à mão), não sobre a tua. Isso é deliberado — ver a seção logo abaixo da tabela.
Sem custo de licença na conta, conforme a decisão registrada na seção 2.

| Serviço | Unidade | Horas | Valor |
|---|---|---|---|
| Escopo A — painel pequeno (até ~30 I/Os) | projeto | 15 | R$ 3.500 |
| Escopo A — painel médio (~30 a 80 I/Os) | projeto | 25 | R$ 5.900 |
| Escopo A — painel grande (acima de 80 I/Os) | projeto | 35 | R$ 8.200 |
| Escopo B — acréscimo sobre o Escopo A | projeto | +40% | +40% sobre o valor |
| — Escopo B pequeno | projeto | 21 | R$ 4.900 |
| — Escopo B médio | projeto | 35 | R$ 8.200 |
| — Escopo B grande | projeto | 50 | R$ 11.700 |
| Revisão de projeto de terceiro | hora | — | R$ 250 |
| Rodada extra de revisão | hora | — | R$ 250 |
| Arquivo-fonte do CAD | projeto | — | 50% sobre o valor |
| Visita técnica | dia | 8 | R$ 1.900 + deslocamento |
| Urgência (prazo abaixo do padrão) | acréscimo | — | 30% |

Hora avulsa a R$ 250 e não R$ 235 de propósito: escopo indefinido carrega risco, e quem compra por
hora não deve pagar menos que quem compra pacote fechado.

---

## Por que o preço não cai junto com o custo

O sistema de geração faz a execução do projeto cerca de 8x mais rápido. A tentação é repassar isso
pro preço. **Não repasse.**

O cliente não compra as suas horas. Ele compra um projeto elétrico completo, conferido, que resolve
o problema dele — e o valor disso pra ele é o mesmo se você levou 50h ou 6h. O que mudou não foi o
valor entregue: foi o seu custo de entregar. Essa diferença tem nome, e é **margem**. É ela que paga
os anos que você gastou construindo o sistema, e é o único ativo que a concorrência não copia.

Quem precifica pelo próprio custo depois de automatizar destrói o mercado em que trabalha e leva
junto a própria margem. O ganho de eficiência vira três outras coisas, todas melhores que desconto:

| O 8x vira | Como aparece pro cliente |
|---|---|
| **Prazo** | Você entrega em uma fração do tempo do concorrente. É o argumento mais forte que existe |
| **Capacidade** | Você atende mais clientes com as mesmas 38h — o negócio escala sem contratar |
| **Qualidade** | O gerador confere o próprio resultado. Menos erro, menos revisão, menos retrabalho |

**Nunca abra a hora na proposta.** Preço fechado por escopo, sempre. No dia em que o cliente
descobrir que o projeto levou 9h, a conversa deixa de ser sobre o projeto e passa a ser sobre a sua
hora — e você perde, porque nenhuma hora vale R$ 655. O que vale R$ 5.900 é o projeto.

Se um dia precisar justificar preço, justifique pelo entregável: 51 folhas, 96 pontos mapeados, 10
planilhas, conferência completa, duas revisões inclusas. Nunca por tempo.

**A margem real, com os números de hoje:**

| Escopo | Preço | Hora sua | Rende por hora |
|---|---|---|---|
| A médio | R$ 5.900 | 9 | R$ 655/h |
| A grande | R$ 8.200 | 12 | R$ 683/h |
| B grande | R$ 11.700 | 14 | R$ 836/h |

Contra um piso de R$ 235/h. **A margem é o sistema.**

---

## Capacidade — o que mudou

Com 38h faturáveis por mês e o sistema rodando:

| Combinação | Horas suas | Faturamento |
|---|---|---|
| 1 Escopo A médio | 9 | R$ 5.900 |
| 2 Escopo A médio | 18 | R$ 11.800 |
| 4 Escopo A médio | 36 | **R$ 23.600** |
| 2 Escopo B grande + 1 A médio | 37 | **R$ 29.300** |

A meta de R$ 8.940/mês fecha com **um projeto médio e meio — cerca de 14h, uma semana das suas
quatro.** O teto teórico do mês passa de R$ 20.000.

**A trava deixou de ser capacidade e passou a ser demanda.** Não adianta mais otimizar processo:
o gargalo agora é quantos clientes chegam. Toda energia que sobra vai pra prospecção, indicação e
presença — não pra ganhar mais velocidade que você já tem sobrando.

Uma ressalva: esse teto pressupõe que o piso humano (briefing, revisão, atendimento) segure o
volume. Quatro clientes ao mesmo tempo são quatro conversas simultâneas, e é aí que o mês estoura —
não no desenho. Cronometre o piso humano antes de assumir compromisso com quatro.

---

## Regras de escopo

| | |
|---|---|
| Correção de erro meu | ilimitada, sem prazo e sem cobrança |
| Alteração de escopo inclusa | 2 rodadas; da terceira em diante, R$ 250/h |
| O que conta como escopo novo | Qualquer coisa fora da premissa registrada no briefing |
| Pagamento | 40% na assinatura · 60% na entrega, 15 dias |
| Validade da proposta | 15 dias |

**Prazo padrão, do sinal** — com o sistema rodando, a 12h/semana:

| Escopo | Hora sua | Prazo padrão | Mercado faz em |
|---|---|---|---|
| A pequeno | 6 | 5 dias úteis | ~15 |
| A médio | 9 | 8 dias úteis | ~25 |
| A grande | 12 | 10 dias úteis | ~35 |
| B médio | 12 | 10 dias úteis | ~35 |
| B grande | 14 | 12 dias úteis | ~45 |

**Não prometa o mínimo técnico.** Um Escopo A médio cabe em uma semana sua, mas o prazo publicado é
de 8 dias porque revisão do cliente, resposta de dúvida e imprevisto consomem dia de calendário, não
hora de trabalho. A folga entre o que você consegue e o que você promete é o que faz você entregar
antes do prazo — que vale mais como referência do que qualquer desconto.

Esses prazos pressupõem fila curta. Nunca prometa sem olhar o que já está aceito.

---

## Condição de abertura (ativa desde 29/07/2026)

Está no topo do site: **traga o orçamento que você já tem, e eu faço por metade do valor e na metade
do prazo**, para escopo equivalente de projeto e documentação.

**Por que ela é assim e não só "50% de desconto":** desconto sem motivo declarado lê como o trabalho
valer menos, e vira preço de tabela — quem paga metade indica dizendo "ele faz pela metade".
Declarar que é condição de abertura, para formar as primeiras referências, dá o motivo e preserva o
preço cheio depois.

### O que ela custa, agora que existe número

Ela cabe — e com folga, porque o custo é a tua hora, não a de mercado:

| | Preço cheio | Condição de abertura | Hora sua | Rende |
|---|---|---|---|---|
| Escopo A médio | R$ 5.900 | R$ 2.950 | 9 | R$ 328/h |
| Escopo A grande | R$ 8.200 | R$ 4.100 | 12 | R$ 342/h |
| Escopo B grande | R$ 11.700 | R$ 5.850 | 14 | R$ 418/h |

Mesmo pela metade, todos ficam **acima do piso de R$ 235/h**. A condição não dá prejuízo: dá margem
menor. E a metade do prazo é trivial — você já entrega em um terço do tempo do mercado sem esforço.

O risco não é financeiro, é de ancoragem. **O preço do primeiro vira referência pra todo mundo que
vier por indicação dele.** Por isso:

**Limite: 3 projetos.** Custa cerca de R$ 11.000 em receita aberta mão — o preço de entrar com
portfólio e indicação. Depois disso, tabela cheia.

Sempre escreva o valor cheio na proposta e mostre o desconto como linha separada, nomeado como
*condição de abertura*. Se o cliente nunca vê o preço cheio, o de abertura é o único que existe
pra ele.

### As três travas que precisam ser respeitadas

1. **Escopo equivalente.** Orçamento de integradora costuma incluir montagem e programação. Metade
   daquilo pode ficar abaixo do teu custo. Só vale contra a parte de projeto e documentação — e é
   por isso que a comparação é documento por documento
2. **Prazo que você consegue cumprir.** O prazo do concorrente é, em boa parte, fila. Você não tem
   fila, então metade do prazo dele costuma ser possível. Mas confira antes de aceitar: você
   trabalha à noite e nos fins de semana. Atrasar o primeiro projeto destrói a referência que a
   condição existe para construir
3. **Ela tem que acabar.** Defina o gatilho de encerramento agora — três projetos fechados, ou uma
   data — e tire a faixa do site quando chegar lá. Condição de abertura que não acaba é tabela de
   preço

- [ ] Confirmar o gatilho de encerramento: **3 projetos fechados** (sugerido) ou até ___/___/______

## Acordo em avaliação — possível sócio (aberto em 29/07/2026)

Conversa em andamento com uma pessoa que pode virar **sócio** ou passar projetos. Proposta do
Mateus: cerca de **3 projetos de médio porte a 20% da tabela** (80% de desconto).

| 3 projetos médios | Tabela cheia | A 20% | Horas suas | Rende | Investimento |
|---|---|---|---|---|---|
| Escopo A | R$ 17.700 | R$ 3.540 | 27 | R$ 131/h | **R$ 14.160** |
| Escopo B | R$ 24.600 | R$ 4.920 | 36 | R$ 137/h | **R$ 19.680** |

Fica **abaixo do piso de R$ 235/h**. Isso não é preço, é investimento na relação — e é maior que
todo o orçamento da condição de abertura (R$ 11.000, 3 projetos), concentrado numa pessoa só.
Decisão consciente do Mateus; registrada aqui pra não virar precedente esquecido.

### Antes do primeiro projeto — resolver por escrito

1. **De quem é o sistema de geração.** É o ativo que sustenta a margem inteira (R$ 655/h contra
   R$ 235 de piso). Rodar projeto conjunto em cima dele sem nada escrito cria relação de trabalho
   compartilhado sobre o ativo principal. Uma frase antes evita uma briga depois
2. **Qual é a contrapartida.** Sócio que traz fluxo recorrente justifica o desconto; alguém que
   leva 3 projetos baratos e some, não. O que o Mateus recebe em troca precisa estar dito
3. **Onde o desconto acaba.** Depois dos 3, tabela cheia — com data ou contagem, escrito
4. **Licença.** Sócio entrando puxa o gatilho da seção 2: a licença entra na conta e todos os
   preços sobem. Refazer a conta antes de fechar qualquer proposta a partir daí

### Trava de comunicação

Este desconto é **privado e não encosta no público**. O site anuncia condição de abertura de 50%.
Se um cliente descobrir que alguém pagou 20%, não existe mais tabela — existe negociação. Valor
cheio em toda proposta, desconto como linha separada e nomeada.

- [ ] Definir por escrito a propriedade do sistema de geração — **antes** do primeiro projeto
- [ ] Definir a contrapartida do sócio e o fim do desconto

---

## Regras de bolso

**Nunca dê desconto sem tirar escopo.** Cortar 15% do preço mantendo tudo ensina o cliente que o
preço era inflado, e ele vai pedir de novo no próximo. Se precisa baixar, tire o dimensionamento
térmico, tire a lista de identificações, reduza pra uma rodada de revisão.

**Cobre a urgência.** Prazo apertado é o cliente comprando o teu fim de semana. Tem preço.

**O arquivo-fonte do CAD é o teu ativo.** Quem tem o fonte não precisa de você na próxima revisão.
Se for vender, venda caro — não menos que 50% sobre o valor do projeto.

**Reajuste todo ano.** Escreva na agenda. Preço que não sobe, cai.

**O primeiro cliente vai puxar o preço pra baixo.** Resista. O preço do primeiro vira referência pra
todos os que vierem por indicação dele.
