# Fluxo ponta a ponta — o que existe, o que falta

> Mapa de 01/08/2026. Cada etapa diz o que já roda, o que ainda é manual e o que é decisão sua.
> O objetivo final descrito pelo Mateus: **o pedido chega por email, o projeto é gerado, e sai
> quando o pagamento fecha.** Este documento mede a distância até lá.

---

## O fluxo, em oito etapas

| # | Etapa | Hoje | Falta |
|---|---|---|---|
| 1 | Cliente acha o site | no ar | tráfego |
| 2 | Preenche `/orcamento` | **automático** | — |
| 3 | Pedido chega em você | **automático**, email em segundos | — |
| 4 | Você responde com o orçamento | **manual** | valor calculado, PDF, envio |
| 5 | Cliente aceita e assina | **manual** | assinatura digital, cobrança da entrada |
| 6 | Cliente informa padrão e projeto | `/padrao` e `/projeto` no ar | escolha de padrão, ficha completa |
| 7 | Projeto é gerado | **manual**, pelo gerador local | ponte entre a ficha do site e a receita do gerador |
| 8 | Entrega após pagamento final | **manual** | cobrança e liberação |

**Três das oito etapas já estão automáticas.** As outras cinco são o trabalho pela frente.

---

## Etapa 4 — o orçamento

A etapa que mais custa hoje, e a mais próxima de resolver.

### O que já existe
- `comercial/calcular.py` — o valor sai dos dados que o `/orcamento` já coleta
- O email do pedido chega estruturado

### O que falta

**a) O arquivo do orçamento.** Hoje não existe formato definido. Precisa ser um PDF de uma página,
no padrão da marca, com: identificação do cliente e do projeto, escopo nomeado, o que entra no
pacote, páginas estimadas, valor cheio, desconto como linha separada, prazo, condições de pagamento,
validade e o link para as fichas.

Decisão sua: **gerar do mesmo jeito que o site é gerado** (HTML + `montar.py` + impressão headless
para PDF, ferramenta que já está montada), ou usar modelo de Word. A primeira é coerente com o resto
e não custa licença.

**b) A ponte cálculo → PDF.** Um comando que recebe o email do pedido e devolve o PDF pronto.
Com `calcular.py` e o gerador de páginas já prontos, é trabalho de horas, não de dias.

**c) A revisão humana.** O orçamento não deve sair sozinho. O valor calculado é estimativa de
página — você olha, ajusta se o equipamento tem algo que o estimador não vê, e aprova. **Um clique
seu entre o cálculo e o cliente.**

---

## Etapa 5 — aceite, contrato e entrada

### O que falta

**a) Assinatura digital.** O contrato existe em `modelo-contrato.md` mas não há como assinar.
Opções reais no Brasil: Clicksign, Autentique (tem plano grátis), D4Sign, ou assinatura ICP via
gov.br. **Autentique no plano grátis resolve o começo** — 5 documentos por mês.

**b) Cobrança da entrada de 40%.** Não existe. Opções: Pix com QR estático (grátis, manual de
conferir), Pix com cobrança dinâmica via API do banco (automático, exige integração), ou gateway
tipo Asaas/Mercado Pago (taxa, mas com webhook que avisa o pagamento).

O webhook importa mais do que parece: é ele que permite a etapa 8 ser automática. **Sem aviso
automático de pagamento, alguém tem que olhar o extrato.**

**c) O gatilho.** Hoje o site diz que o prazo conta do pagamento da entrada. Falta o que
transforma "pagou" em "projeto entrou na fila".

---

## Etapa 6 — as duas fichas

### O que existe
`/padrao` (padrão do cliente, uma vez) e `/projeto` (por projeto), ambas no ar, salvando no
navegador do cliente.

### O que falta

**a) A escolha entre padrão Borin e padrão do cliente.** Decidido, não construído: depois do
orçamento, uma tela pergunta se ele usa o padrão Borin (segue direto) ou monta o dele (vai pro
`/padrao`). Isso tem consequência de preço — `calculo-preco.md` cobra R$ 1.000 de setup na primeira
vez que o cliente impõe padrão próprio.

**b) A ficha de projeto completa.** A `/projeto` de hoje tem 18 campos genéricos. A ficha que o
gerador realmente consome é a do `FICHA_APP.yaml`: alimentação, segurança com lista de dispositivos,
remota, IHM, rede, I/O de processo, catálogo de entradas e saídas de campo com quantidade e função
por unidade. **É essa que precisa estar no site**, porque é ela que alimenta a etapa 7.

**c) As fichas não chegam em você.** `/padrao` e `/projeto` só mandam por WhatsApp ou arquivo, de
propósito — carregam o padrão interno e o desenho da máquina do cliente, e o bloco de sigilo do
site promete que não vão pra servidor. **Para automatizar a etapa 7, isso precisa mudar**, e o
texto do site precisa mudar junto. Não dá pra prometer sigilo e mandar pra fora ao mesmo tempo.

---

## Etapa 7 — geração do projeto

### O que existe
O gerador completo, rodando local, consumindo uma receita YAML no formato do `FICHA_APP.yaml`.

### O que falta

**a) A ponte.** A ficha preenchida no site precisa virar o YAML que o gerador consome. Se a ficha
do site for construída **com os mesmos campos e os mesmos nomes de macro** do `FICHA_APP.yaml`,
essa ponte é quase nada — é serializar o formulário. Se for construída livre, vira tradutor.

**Isto é a decisão de arquitetura mais importante do documento:** construir a ficha do site
espelhando o YAML, não inventando campos.

**b) A checagem de banco.** O que decide preço e prazo: quais peças da ficha **não existem** no
banco. Precisa de um comando que leia a ficha e devolva a lista de peças ausentes, separando marca
grande (importa, R$ 0) de marca pequena (1 h manual, R$ 250). Sem isso, a parcela de itens novos
do cálculo é chute.

**c) O gerador roda local, o site roda na nuvem.** Cloudflare Pages não chama processo na sua
máquina. O jeito que já foi resolvido na CONFERENCIAS v2: o site enfileira o pedido numa KV e um
executor local puxa. Mesmo padrão serve aqui.

---

## Etapa 8 — entrega após o pagamento

### O que falta
- Confirmação de pagamento (webhook, ver etapa 5)
- Um lugar pro cliente baixar — hoje seria email com anexo, o que quebra com PDF de 51 folhas
- Registro de que foi entregue

---

## Sobre "uma IA lê o email e faz"

Vale separar o que é automação determinística do que precisa de julgamento, porque tratar tudo como
IA cria dois problemas: custo e erro silencioso.

| Tarefa | Precisa de IA? | Por quê |
|---|---|---|
| Ler o pedido e extrair os campos | **Não** | O formulário já manda estruturado. Ler texto livre para tirar o que você mesmo estruturou é criar um problema para resolver depois |
| Calcular o valor | **Não** | É aritmética. `calcular.py` já faz, e faz igual toda vez |
| Estimar páginas | **Não** | Fórmula calibrada. IA daria número diferente a cada chamada |
| Montar o PDF | **Não** | Template |
| Gerar o projeto | **Não** | O gerador já existe e é determinístico |
| Interpretar "o que o equipamento faz" em sequência de operação | **Sim** | Texto livre, exige julgamento técnico |
| Sugerir a macro certa para um item descrito por escrito | **Sim** | Casamento aproximado contra o banco |
| Decidir se um pedido é sério ou é concorrente pescando preço | **Sim** | Julgamento |

**A conclusão prática:** o caminho do pedido até o orçamento pode ser 100% determinístico e sair em
segundos, sem IA nenhuma no meio. A IA entra onde há texto livre e ambiguidade — e nesses pontos ela
deve **propor para você aprovar**, não decidir sozinha.

E há um limite que não é técnico: **o projeto sai com o seu nome.** Entregar projeto elétrico que
ninguém olhou é o risco que destrói a referência que o negócio inteiro depende. O clique humano
antes de enviar não é gargalo, é o produto.

---

## Ordem sugerida

Cada item depende do anterior, e cada um tem valor sozinho.

| | O que | Por que agora |
|---|---|---|
| 1 | **Ficha de projeto espelhando o `FICHA_APP.yaml`** | Destrava a etapa 7 inteira. Feita errado, tudo depois vira tradutor |
| 2 | **Tela de escolha de padrão** | Barata, fecha o buraco entre orçamento e ficha |
| 3 | **PDF do orçamento + `calcular.py`** | Tira a etapa que mais consome seu tempo hoje |
| 4 | **Checagem de banco** | Sem ela, o preço de itens novos é chute |
| 5 | **Assinatura digital + Pix** | Só vale depois que houver volume; antes disso, manual é mais rápido |
| 6 | **Fila site → executor local** | O último passo, e o que exige mais cuidado |

---

## Decisões travando o resto

1. **A ficha do site espelha o `FICHA_APP.yaml`?** Recomendo sim, campo a campo, com os mesmos
   nomes de macro. Custa mais agora e elimina o tradutor depois.
2. **As fichas passam a ir pro servidor?** Precisa, para automatizar. Exige reescrever o bloco de
   sigilo do site — e decidir onde os dados ficam.
3. **O orçamento sai sozinho ou com seu aceite?** Recomendo com aceite, sempre.
4. **Qual meio de cobrança?** Define se a etapa 8 pode ser automática.
