# Padrão de entrega

> O que a Borin entrega em cada projeto, em que formato e com que nível de detalhe.
> Calibrado em 27/07/2026 sobre um projeto real entregue (painel de interface, 51 folhas,
> três instalações: painel, campo e painel pneumático).
> A proposta cita este arquivo, o contrato anexa ele, e a conferência antes da entrega segue o
> `checklist-conferencia.md`.

---

## O princípio: organizar por instalação

O projeto não se organiza por tipo de documento, e sim por **instalação** — e dentro de cada
instalação, pelo tipo de montagem.

```
PAINEL 1              →  multifilar · régua de bornes · layout · lista de materiais
CAMPO                 →  diagrama de interconexão · lista de materiais · plaqueta
PAINEL PNEUMÁTICO     →  régua de bornes · lista de materiais · interconexão
```

Isso escala sozinho: se o projeto tiver quatro painéis e dois campos, a estrutura é a mesma,
repetida. O índice do CAD já sai com as colunas **Página · Descrição · Instalação · Montagem**,
que é exatamente essa lógica.

---

## Os dois escopos

| | **Escopo A — Painel** | **Escopo B — Painel + Instalação** |
|---|---|---|
| O que cobre | O painel elétrico completo | O painel mais a instalação em campo |
| Para quem | Fabricante de máquina e integrador que instala por conta | Cliente que também precisa da instalação especificada e planejada |
| Acrescenta | — | Interconexão de campo, listas de campo, lista de instalação com horas, tags de campo |

Sempre nomear o escopo na proposta pelo nome: *Escopo A* ou *Escopo B*.

---

## Escopo A — Projeto de painel

### Pacote PDF

Documento único, paginado, indexado, na ordem abaixo.

| # | Folha | O que contém |
|---|---|---|
| 1 | **Título / Capa** | Tabela *Descrição do Quadro*: código do produto, código do projeto, tensão de comando, tensão de força, potência total, temperatura ambiente máxima considerada, alimentação com bitola de fase/neutro/terra, corrente nominal e potência dissipada calculada. No rodapé, a **tabela de revisões** e a **legenda de cores de cabo** |
| 2 | **Memorial descritivo** | Seis blocos — ver detalhamento abaixo |
| 3 | **Visão geral de símbolos** | Simbologia usada no projeto, com nome e desenho de cada símbolo |
| 4–5 | **Índice** | Uma linha por folha: página, descrição, instalação, montagem. Quebra por instalação |
| 6 | **Potência** | Alimentação, chave geral, proteção, fonte, distribuição 24VCC |
| 7 | **Arquitetura do CLP** | Topologia: CPU, módulos, remotas, rede |
| 8–13 | **Visão geral do CLP** | Módulo a módulo, ponto a ponto |
| 14–17 | **Comando — entradas** | Digitais e analógicas |
| 18–22 | **Comando — saídas** | Digitais e analógicas |
| 23–26 | **Comando — acionamento** | Partidas, válvulas, atuadores |
| 27 | **Layout** | Disposição física na placa de montagem e na porta |
| 28–36 | **Régua de bornes** | Um diagrama de conexão por régua (X0, X1, X2…), com destino de cada ponto |
| 37 | **Lista de peças totalizadas** | Consolidada da instalação, com código e quantidade |

Além do documento único acima, o pacote leva o **Databook** — PDF separado com manual e datasheet de
cada equipamento, indexado por tag. Ver detalhamento abaixo.

**Faixa de páginas é referência, não regra.** O que é fixo é a ordem e a existência de cada bloco.

### Memorial descritivo — os seis blocos

O memorial cabe em uma folha e é preenchido com campos e caixas de seleção, não com texto corrido.

1. **Características técnicas** — cliente, tensão nominal, frequência, tensão de comando, corrente nominal, corrente de curto-circuito (Icc), normas aplicáveis (NR-10, NR-12), forma de montagem, painel testado, esquema de aterramento (TN-C, TN-S, TT, IT)
2. **Estrutura** — fornecedor, dimensões, material, grau de proteção, cor RAL, tipo de pintura, placa de montagem, fixação, entrada e saída de cabos, lado de acesso, acessórios
3. **Condições de serviço** — ambiente da instalação (área classificada, corrosivo, úmido, próximo do mar), local (abrigado ou ao tempo), temperatura ambiente e de sala
4. **Condutores** — isolação de comando e de potência, tabela de cores por função, seção transversal padrão quando não especificada no diagrama, barramento
5. **Identificação** — forma de identificação de dispositivos (letra identificadora e contador) e de fios
6. **Observações** — exceções do projeto

### Planilhas Excel

Arquivos separados do PDF, porque o cliente trabalha em cima deles.

| Planilha | Estrutura | Para que serve ao cliente |
|---|---|---|
| **Lista de materiais** | Código, descrição, quantidade, por instalação | Compra e cotação |
| **Arquitetura de CLP** | Aba de pontos (local, tag, peça, código, quantidade, função) + aba de materiais com dissipação | Programação e compra do hardware de automação |
| **Design térmico** | Aba de itens com dissipação por tag, aba de materiais com dissipação de bobina e contatos, aba de cálculo térmico por superfície e material da caixa | Definir ventilação ou climatização, e justificar a escolha |
| **Identificações** | Seis arquivos — ver abaixo | Impressão das etiquetas |

### Databook

PDF separado, com o **manual e o datasheet de cada equipamento do projeto**, indexado por tag.

| | |
|---|---|
| Organização | uma seção por tag, na ordem da lista de materiais |
| Conteúdo por seção | manual do fabricante, datasheet, certificado quando houver |
| Índice | tag · descrição · fabricante · código · página |

**Por que entregar.** Quem monta e quem faz manutenção passa a não depender de procurar manual no site
do fabricante dois anos depois, quando o modelo saiu de linha. É o documento que o cliente descobre
que precisa na primeira parada de máquina — e aí não tem.

**O custo é baixo e a percepção é alta:** os arquivos vêm dos fabricantes, o trabalho é organizar e
indexar. Nenhum concorrente da Serra entrega isso hoje (ver `comercial/analise-mercado.md`).

**Cuidado:** não redistribuir material com restrição explícita de redistribuição. Na dúvida, entrar
com o link oficial do fabricante em vez do arquivo.

### Identificações — seis arquivos

Cada um com a aba de dados e uma aba de instrução de impressão, com impressora e modelo de etiqueta.

| Arquivo | Conteúdo |
|---|---|
| Painel — TAG's Fios | Numeração de fio por régua e local |
| Painel — TAG'S Bornes | Código do borne, régua, local |
| Painel — TAG's Dispositivos | Identificação dos componentes do painel |
| Painel — TAG's Relé | Identificação dos relés |
| Campo — TAG's Fios | Numeração de fio dos cabos de campo |
| Campo — TAG's de Cabos | Identificação de cabo (W0, W1…) e sensor (BG1, BG2…) |

**A aba de impressão é parte da entrega.** É ela que faz o cliente conseguir imprimir sem te ligar —
impressora, modelo de etiqueta e ordem das colunas.

---

## Escopo B — Projeto de painel + instalação

Tudo do Escopo A, mais o que segue.

### No pacote PDF

| Folha | O que contém |
|---|---|
| **Diagrama de interconexão** | Um bloco por conjunto de cabos (W0, W1, W2…), com origem, destino, vias e bitola |
| **Lista de peças totalizadas — CAMPO** | Material de campo consolidado, separado do painel |
| **Título / plaqueta de campo** | Capa da instalação de campo |
| **Régua de bornes e interconexão das demais instalações** | Se houver painel pneumático ou outro conjunto, repete a estrutura |

### Planilhas Excel

| Planilha | Estrutura | Para que serve |
|---|---|---|
| **Interligação base** | Base de cabos e ligações ponto a ponto | Fonte da interconexão |
| **Lista de instalação** | Ver abaixo — é a planilha mais completa da entrega | Comprar, planejar e acompanhar a instalação |

### A lista de instalação

É o documento que mais diferencia a entrega. Abas:

| Aba | O que faz |
|---|---|
| `BASE_CABOS` | Tag, nome, código ERP, especificação, vias, bitola, comprimento e função de cada cabo |
| `Lista_de_materiais` | Material de instalação consolidado, com quantidade e ocorrências |
| `Acompanhamento_instalação` | Uma linha por tarefa: descrição, painel, tag, tag do cabo, material, código, comprimento, status, **horas estimadas**, % de conclusão e horas concluídas |
| `Acessórios_por_ocorrência` | Acessório que entra por ocorrência de cabo (identificação, luva, prensa) |
| `Acessórios_por_comprimento` | Acessório proporcional ao metro (corrugado, clip, abraçadeira) |
| `Acessórios_por_item` | Acessório por item (flange, acabamento) |
| `Acessórios_fixos` | Parafuso, arruela, bucha — quantidade fixa por obra |
| `Arredondamento` | Regra de arredondamento de compra por código (terminal de 100 em 100, por exemplo) |
| `Fornecedor` | Código, descrição e fornecedor |

**A aba de acompanhamento com horas estimadas é um diferencial comercial real.** Ela transforma a
entrega de "lista de material" em "plano de instalação" — o cliente consegue dimensionar equipe e
prazo, não só comprar. Nenhum concorrente da Serra comunica isso.

---

## Regras de entrega

**Formato.** PDF paginado e pesquisável, mais os arquivos Excel. Nunca print, foto de tela ou
documento sem revisão declarada.

**Nomenclatura.** O padrão observado no projeto real já funciona — manter:

```
[Documento] - [Código] - [Nome do projeto].[ext]

Ex: Lista de Materiais - 04003478 - Painel de Interface.xlsx
    Design Térmico - 04003478 - Painel de Interface.xlsx
    Campo - TAG's de Cabos - 04003478 - Painel de Interface.xlsx
```

Estrutura de pastas da entrega:

```
[Código] - [Nome do projeto]/
  [Código] - [Nome do projeto].pdf
  Docs/
    Lista de Materiais - ...xlsx
    Arquitetura de CLP - ...xlsx
    Design Térmico - ...xlsx
    Interligação base - ...xlsx          (Escopo B)
    Lista de instalação - ...xlsm        (Escopo B)
    Identificações/
      Painel - TAG's Fios - ...xlsx
      Painel - TAG'S Bornes - ...xlsx
      Painel - TAG's Dispositivos - ...xlsx
      Painel - TAG's Relé - ...xlsx
      Campo - TAG's Fios - ...xlsx       (Escopo B)
      Campo - TAG's de Cabos - ...xlsx   (Escopo B)
```

**Revisão.** V0 é a primeira emissão. A tabela de revisões na capa registra revisão, data,
modificado por, verificado por, aprovado por e descrição da modificação. Nunca sobrescrever revisão
anterior.

**Carimbo.** Toda folha leva o carimbo, conforme `marca/design-guide.md`. O carimbo do CAD traz
projeto, cliente, código do produto, nº do documento, diretório do arquivo, descrição da página,
localização, data e folha X de Y, mais os quatro campos de responsabilidade:

| Campo | Quem preenche |
|---|---|
| **Elaborado** | Borin — só o nome, sem título profissional e sem registro em conselho |
| **Verificado** | **em branco** — é do cliente |
| **Aprovado** | **em branco** — é do cliente |
| **Responsável técnico** | **em branco** — é do cliente, ou do profissional habilitado que ele contratar |

**Os três últimos saem sempre em branco, e isso não é descuido.** É o que a cláusula 2.2 do contrato
promete, e é o que separa "elaborei o documento" de "sou o responsável técnico pela instalação".
O documento circula até o usuário final; nome em campo de responsabilidade técnica é o que cria
exposição. Nunca preencher, nunca deixar o cliente mudar o modelo de legenda.

**Meio de envio.** Link ou pasta compartilhada, nunca anexo solto de email.

**Aceite.** Confirmação escrita do cliente; por conduta, como pedido de compra pela lista
de materiais ou início da montagem; ou por decurso, 10 dias úteis da entrega sem
manifestação mais 5 dias úteis após novo aviso. Este documento é anexo do contrato e
segue a cláusula 12 dele — se um dia divergirem, vale o contrato.

---

## Normas de referência

| Norma | O que rege |
|---|---|
| IEC 81346 | Estrutura e designação de tags |
| IEC 61082 | Elaboração de documentos de projeto |
| NFPA 79 | Fiação de máquinas industriais |
| IEC 60204-1 | Segurança de máquinas — equipamento elétrico, cores e identificação |
| NR-10 | Segurança em instalações e serviços em eletricidade |
| NR-12 | Segurança no trabalho em máquinas e equipamentos |

## Padrões técnicos da casa

**Cores de cabo:** fase R/S/T preto · neutro azul claro · terra verde/amarelo · 24VCC vermelho ·
0VCC marrom · sinal 24VCC cinza.

**Seção padrão:** 0,5 mm² para comando geral, quando não especificada no diagrama.

**Proteção:** CLP com fusível 2A na CPU/fonte e 1A por módulo de I/O. Disjuntor em fonte, tomada,
ar-condicionado e ventilador. DJM em inversor e RFF.

**Identificação:** letra identificadora mais contador, conforme IEC 81346. Fios de 24V e 0V não
levam tag nem luva — são identificados pela cor.

**Banco de artigos:** enxuto — poucos artigos, alta repetição.

---

## O que NÃO está incluso em nenhum dos escopos

Deixar explícito na proposta evita a maior parte do atrito depois.

- **ART e responsabilidade técnica.** O serviço é projeto e documentação técnica. Se o cliente
  precisar de ART, é com engenheiro eletricista habilitado, contratado à parte
- **Programação de CLP, IHM ou supervisório**
- **Montagem, comissionamento e startup**
- **Execução da instalação** — o Escopo B especifica e planeja, não instala
- **Compra de material e intermediação de fornecedor**
- **Arquivo-fonte do CAD** — negociado à parte, ver `comercial/precificacao.md`
- **Acompanhamento em obra ou visita técnica**, salvo se previsto na proposta
- **Revisões acima do número contratado**

## Revisões inclusas

Duas coisas diferentes, e a distinção é o que evita discussão:

**Erro meu — correção ilimitada, sem prazo e sem cobrança.** Divergência entre o projeto e a ficha
técnica assinada, erro de cálculo, tag duplicada, borne sem destino, item errado na lista. Se está
fora do que foi combinado, é meu, e eu corrijo quantas vezes for preciso. Não consome rodada.

**Alteração de escopo — duas rodadas inclusas.** Mudou a necessidade depois da ficha assinada:
acrescentar ponto de I/O, trocar marca de componente, mudar tensão, incluir dispositivo novo.
Rodada é o conjunto de alterações devolvido de uma vez. Da terceira em diante, cobra-se por hora.

**O critério é objetivo: compara-se contra a ficha técnica assinada.** O que está na ficha e saiu
diferente é erro meu. O que não está na ficha é alteração. Não é opinião de ninguém.

---

## Aviso — templates e propriedade

O projeto usado para calibrar este padrão foi feito dentro da FlowSistem, com os **templates,
macros e banco de artigos da empresa** (as planilhas trazem abas nomeadas "1 Flow –" e a lista de
instalação é uma macro proprietária).

**A estrutura de uma entrega não é propriedade de ninguém** — é boa prática de engenharia, e é isso
que este documento registra. **Os arquivos, macros, templates de folha e banco de artigos são.**

Antes de entregar o primeiro projeto pela Borin, é preciso construir os próprios:

- Template de folha do CAD com o carimbo da marca
- Template de capa e de memorial descritivo
- Planilhas modelo de material, identificações, arquitetura de CLP e design térmico
- Macro ou planilha própria de lista de instalação
- Banco de artigos próprio

Dá trabalho, mas é o que separa "usar o padrão da empresa onde trabalho" de "ter um padrão".
