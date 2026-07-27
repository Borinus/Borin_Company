# Padrão de entrega

> O que a Borin entrega em cada projeto, em que formato e com que nível de detalhe.
> Este arquivo é a referência de escopo: a proposta cita ele, o contrato anexa ele, e a conferência
> antes da entrega segue o `checklist-conferencia.md`.

---

## Os dois escopos

| | **Escopo A — Painel** | **Escopo B — Painel + Instalação** |
|---|---|---|
| O que cobre | O painel elétrico completo | O painel mais a instalação em campo |
| Para quem | Fabricante de máquina e integrador que monta e instala por conta | Cliente que também precisa da instalação especificada |
| Diferença | — | Interligação de campo, layout 2D da instalação, listas de instalação e tags de campo |

Sempre nomear o escopo na proposta pelo nome: *Escopo A* ou *Escopo B*. Evita a discussão de
"eu achei que estava incluso".

---

## Escopo A — Projeto de painel

### Pacote PDF

Documento único, paginado e indexado, na ordem abaixo.

| # | Documento | O que contém |
|---|---|---|
| 1 | **Capa** | Identificação do projeto, cliente, revisão, data, número de folhas |
| 2 | **Memorial descritivo** | O que o painel faz, filosofia de comando, tensões, proteções adotadas, premissas e normas de referência |
| 3 | **Índice** | Relação de folhas com descrição e número |
| 4 | **Diagrama elétrico** | Alimentação, distribuição, comando, CLP, acionamentos |
| 5 | **Régua de bornes** | Bornes numerados, destino de cada ponto, jumpers |
| 6 | **Layout do painel** | Disposição física dos componentes na placa de montagem e na porta |
| 7 | **Lista de material** | Consolidada, com código, descrição, fabricante e quantidade |

### Planilhas Excel

Arquivos separados do PDF, porque o cliente trabalha em cima deles.

| Planilha | Para que serve ao cliente |
|---|---|
| **Lista de material** | Compra e cotação — versão manipulável da lista do PDF |
| **Lista de identificações** | Impressão de etiquetas de fio, cabo, borne, relé e componente |
| **Planilha de I/Os do CLP** | Programação: endereço, tag, descrição, tipo de sinal |
| **Dimensionamento térmico** | Cálculo de dissipação e definição de ventilação ou climatização do painel |

---

## Escopo B — Projeto de painel + instalação

Tudo do Escopo A, mais o que segue.

### No pacote PDF

| Documento | O que contém |
|---|---|
| **Interligação de campo** | Seção adicional no diagrama: ligação entre painel e periféricos, com cabo, bitola e destino |
| **Layout 2D da instalação** | Planta com posição dos periféricos, eletrocalhas, eletrodutos e passagem de cabos |

### Nas planilhas Excel

| Planilha | Para que serve |
|---|---|
| **Lista de instalação** | Roteiro de o que ligar onde, ponto a ponto |
| **Lista de material de instalação** | Cabo, eletroduto, calha, prensa-cabo, fixação — separada da lista do painel |
| **Tags de campo** | Identificação de sensor, atuador e caixa de passagem em campo |

---

## Regras de entrega

**Formato.** PDF paginado e pesquisável, mais os arquivos Excel. Não se entrega print, foto de tela
nem documento sem revisão declarada.

**Nomenclatura de arquivo.** Sempre no padrão:

```
CLIENTE_PROJETO_DOCUMENTO_REV##.extensão
Ex: MetalSerra_Dosagem-L4_Projeto_REV02.pdf
    MetalSerra_Dosagem-L4_ListaMaterial_REV02.xlsx
```

**Revisão.** Toda entrega sai com número de revisão. REV00 é a primeira emissão. Cada rodada de
alteração sobe um número, e o que mudou fica registrado numa tabela de revisões na capa. Nunca
sobrescrever revisão anterior — o histórico é parte da entrega.

**Carimbo.** Toda folha e todo documento levam o carimbo da marca, conforme `marca/design-guide.md`.

**Meio de envio.** Link de download ou pasta compartilhada, nunca anexo solto de email — anexo pesado
se perde e não tem controle de versão.

**Aceite.** A entrega se considera aceita quando o cliente confirma por escrito, ou após 10 dias
corridos sem manifestação.

---

## Normas de referência

| Norma | O que rege aqui |
|---|---|
| IEC 81346 | Estrutura e designação de tags |
| IEC 61082 | Elaboração de documentos de projeto |
| NFPA 79 | Fiação de máquinas industriais |
| IEC 60204-1 | Segurança de máquinas — equipamento elétrico, cores e identificação |

## Padrões técnicos da casa

**Cores de cabo:** potência preto · neutro azul claro · PE verde/amarelo · 24VCC vermelho ·
comando cinza · 0VCC marrom.

**Proteção:** CLP com fusível 2A na CPU/fonte e 1A por módulo de I/O. Disjuntor para fonte, tomada,
ar-condicionado e ventilador. DJM para inversor e RFF.

**Banco de artigos:** enxuto — poucos artigos, alta repetição. Padronização vence variedade.

---

## O que NÃO está incluso em nenhum dos escopos

Deixar explícito na proposta evita 90% do atrito depois.

- **ART e responsabilidade técnica.** O serviço é projeto e documentação técnica. Se o cliente
  precisar de ART, é com engenheiro eletricista habilitado, contratado à parte
- **Programação de CLP, IHM ou supervisório**
- **Montagem, comissionamento e startup**
- **Compra de material e intermediação de fornecedor**
- **Arquivo-fonte do EPLAN.** A entrega padrão é PDF mais Excel. O fonte é negociado à parte —
  ver `comercial/precificacao.md`
- **Acompanhamento em obra ou visita técnica**, salvo se previsto na proposta
- **Revisões acima do número contratado.** Ver o item abaixo

## Revisões inclusas

**Duas rodadas de revisão** estão inclusas no preço, contadas após a primeira emissão (REV00).

Rodada de revisão é o conjunto de ajustes que o cliente devolve de uma vez. Pedido novo, fora do que
foi levantado no briefing, não é revisão — é escopo novo, e se cobra à parte.

A partir da terceira rodada, cobra-se por hora conforme a tabela vigente.
