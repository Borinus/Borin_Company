# Guia de Design — Borin Projetos Elétricos

> Você pode editar esse arquivo a qualquer momento.
> As skills que geram proposta, slide, capa de projeto ou qualquer peça visual leem este arquivo antes.

---

## A ideia da marca

O mercado de elétrica e automação da Serra é todo azul-corporativo, com foto de máquina e lista de
serviços. Ver `comercial/analise-mercado.md`. A Borin não compete por abrangência — compete por
rigor de documentação. Então a marca não é feita de enfeite: é feita da linguagem da folha de
desenho técnico.

Dois elementos sustentam isso, e são eles que dão personalidade à marca:

1. **O carimbo** — toda peça carrega um bloco de identificação igual ao de uma folha A3. Não é
   decoração: é a assinatura estrutural de quem vive dentro de prancha.
2. **A cor de comando** — o vermelho do 24VCC, do próprio padrão de cabo dele. Único acento, em
   doses mínimas. Tem razão técnica pra existir, não escolha estética.

---

## Nome

**Borin Projetos Elétricos**.

Nome próprio porque o canal de venda é indicação: quem indica, indica o Mateus. Nunca acompanhar de
"Engenharia" — o serviço é projeto e documentação técnica, e o termo é regulado pelo CREA.

Domínio: `borinprojetos.com.br` — registrado em 29/07/2026, site no ar. CNPJ 65.749.097/0001-85,
razão social `65.749.097 MATEUS BORIN`, nome fantasia Borin Projetos Elétricos.

---

## Logo

Nome em caixa alta, fio horizontal com um nó no fim, descritor embaixo. O fio é a linha de cota do
desenho técnico; o nó é o ponto de conexão que a encerra.

```
BORIN
────────────────────────────  ■
projetos elétricos industriais
```

**Construção** — todas as medidas relativas à altura da letra B:

| Elemento | Especificação |
|---|---|
| Nome | Inter Bold (700), caixa alta, `letter-spacing` +0.08em |
| Fio | Espessura 0,08 B. Largura = **largura do nome** menos o nó e o intervalo |
| Intervalo fio → nó | 0,12 B |
| Nó | Quadrado de 0,2 B, centrado na altura do fio |
| Descritor | Inter Medium (500), caixa baixa, `letter-spacing` **calculado** — ≈ +0.068em |
| Corpo do descritor | 0,22 da altura do nome |
| Nome → fio | 0,4 B |
| Fio → descritor | 0,4 B |
| Alinhamento | Tudo à esquerda |

### A regra que segura o desenho: os três elementos têm a mesma largura

Revisado em 05/08/2026. Antes, o fio acompanhava o descritor e o descritor tinha `letter-spacing`
fixo de +0.12em — o que deixava "projetos elétricos industriais" **159 px mais comprido que BORIN**
num logo de 1500 px. O fio e o nó sobravam à direita do N, e a marca escorria para o lado.

Agora **quem manda é a largura do nome.** O fio e o nó terminam onde o N termina, e o
`letter-spacing` do descritor é calculado (busca binária em `gerar-logos.py`) para dar exatamente
essa mesma largura. Com o texto de hoje, dá ≈ +0.068em. Fica calculado e não fixo para continuar
valendo se o nome ou o descritor mudarem de texto.

**Alinhamento é pela tinta, não pelo avanço da fonte.** Os dois bugs corrigidos no mesmo dia vieram
disso: à esquerda, o "B" tem mais respiro que o "p" e o fio não tem nenhum — 26 px de escada; à
direita, o respiro do "N" é maior que o do "s" — outros 26 px. Quem gerar arte da marca por outro
caminho precisa saber disso, senão reintroduz os dois.

**Área de proteção:** margem livre igual à altura da letra B. Nada entra nesse espaço.

**Tamanho mínimo:** 24mm de largura em impresso, 90px em tela. Abaixo disso, usar o monograma.

O logo padrão é monocromático de propósito: assim funciona em impressão preto e branco, em carimbo,
gravado ou fotocopiado. A versão com o nó vermelho é exceção, não regra.

### A marca compacta — a folha

Criada em 29/07/2026, para o tamanho em que o logo e o monograma param de funcionar.

```
┌──────────────┐
│              │
│   ────  ■    │
│              │
└──────────────┘
```

Uma folha com a linha de cota e o nó dentro. Os três elementos do logo reduzidos ao essencial: a
moldura é a folha de desenho, a linha é o fio, o quadrado é o nó em Comando.

| Elemento | Especificação (canvas 32×32) |
|---|---|
| Fundo | Papel sólido |
| Moldura | 1,5 de Tinta, recuada 0,75 da borda |
| Linha | 13 × 2 de Tinta, começando em x=6, centrada na altura |
| Nó | 6 × 6 de Comando, em x=21 |

**Arquivo:** `marca/favicon.svg`. Também embutido em data URI no `site/_pagina.html`.

**Por que fundo Papel e não Tinta:** a folha branca sobrevive em aba de navegador claro e escuro, e
lê como uma folha de desenho — o que é o conceito. Fundo preto virava um bloco, e com o nó do mesmo
peso da linha o desenho lia como dois quadrados soltos, não como uma marca.

**A proporção é o que faz funcionar:** linha longa e fina, nó pequeno. Se os dois ficarem com peso
parecido, perde a leitura de "linha que termina num ponto".

### Como chamar a marca em cada lugar

Esta é a regra que evita repetir o nome inteiro numa folha de projeto:

| Onde | Como aparece |
|---|---|
| Capa do projeto, proposta, apresentação, assinatura de email | Logo completo: `BORIN` + fio + nó + *projetos elétricos industriais* |
| **Carimbo de folha do CAD** | **Só `BORIN`** — sem fio, sem nó, sem descritor |
| **Favicon, avatar, ícone de app** | **Marca compacta** (`marca/favicon.svg`) |
| Rodapé de slide, etiqueta, carimbo digital | Monograma `BRN` |
| Texto corrido, contrato, nota fiscal | Razão social: `65.749.097 MATEUS BORIN`. Nome fantasia Borin Projetos Elétricos |

O nome completo aparece **uma vez por documento**, na capa ou no memorial. Repetir "Borin Projetos
Elétricos" em 51 folhas não reforça a marca — polui a folha.

### Arquivos

**Vetor** — peça definitiva e gráfica:

| Arquivo | Uso |
|---|---|
| `marca/logo.svg` | Fundo claro, monocromático. **É a versão padrão** |
| `marca/logo-branco.svg` | Fundo escuro |
| `marca/logo-comando.svg` | Só em peça digital colorida — nó em vermelho |
| `marca/monograma-brn.svg` | Uso reduzido |
| `marca/favicon.svg` | **Marca compacta** — favicon, avatar, ícone |

**PNG** — para colocar dentro do CAD, Word e apresentação (`marca/png/`):

| Arquivo | Uso |
|---|---|
| `borin-completo.png` | Capa de projeto e proposta — fundo transparente |
| `borin-completo-branco.png` | Sobre fundo escuro |
| `borin-completo-comando.png` | Peça digital colorida, nó em vermelho |
| `borin-carimbo.png` | **Carimbo de folha do CAD** — só o nome, transparente, alta resolução |
| `borin-carimbo-600px.png` | Mesma coisa reduzida, se o CAD elétrico engasgar com arquivo grande |
| `borin-carimbo-fundo.png` | Com fundo branco sólido, se a transparência não se comportar |
| `brn-monograma.png` · `-branco.png` | Espaço curto e favicon |

Os PNGs saem de `marca/gerar-logos.py`, que lê as medidas deste guia. **Depois de instalar a fonte
Inter, rode o script de novo** — ele detecta a Inter sozinho e refaz tudo com a tipografia
definitiva. Os arquivos atuais foram gerados com Arial Bold, o fallback previsto.

```
python marca/gerar-logos.py
```

> Os SVGs usam a fonte Inter por referência. Antes de mandar pra gráfica, abra no Inkscape ou
> Illustrator e converta o texto em curvas — assim o logo não depende da fonte estar instalada.

---

## O carimbo

**É o elemento mais característico da marca.** Toda peça leva um, no rodapé, ocupando a largura total.
Vem direto do carimbo de folha — quem recebe reconhece na hora de onde veio.

```
┌───────┬──────────────────┬───────────────┬────────┬────────────┐
│  BRN  │ DOCUMENTO        │ CLIENTE       │ REV    │ DATA       │
│       │ Proposta técnica │ Metalúrgica X │ 02     │ 27/07/2026 │
└───────┴──────────────────┴───────────────┴────────┴────────────┘
```

**Construção:**

| Elemento | Especificação |
|---|---|
| Moldura externa | 1px Tinta |
| Divisórias internas | 1px Cinza 300 |
| Primeira célula | Monograma BRN, largura fixa |
| Rótulo do campo | Mono, 7pt, caixa alta, `letter-spacing` +0.1em, Cinza 600 |
| Valor do campo | Mono, 9pt, Tinta |
| Altura | Duas linhas de texto mais 0,5rem de respiro |
| Canto | Reto, sempre |

**Campos por tipo de peça:**

| Peça | Campos |
|---|---|
| Proposta comercial | Documento · Cliente · Revisão · Data |
| Capa de projeto | Projeto · Cliente · Revisão · Data · Folhas |
| Folha A3 (dentro do CAD) | Projeto · Folha · Revisão |
| Apresentação | Documento · Data (rodapé de todo slide) |
| Assinatura de email | Versão reduzida: monograma, nome, função, cidade |

**Regra:** se a peça não tem o que preencher em algum campo, o campo sai — nunca fica vazio nem com
travessão.

---

## Cores

Monocromática com um único acento. A hierarquia se faz por tamanho, peso e espaço.

| Nome | Hex | Uso |
|---|---|---|
| **Tinta** | `#111111` | Texto principal, logo, fios, botões |
| **Papel** | `#FFFFFF` | Fundo principal |
| **Cinza 100** | `#F4F4F4` | Fundo alternativo, faixa de seção |
| **Cinza 300** | `#DCDCDC` | Bordas, divisórias, linhas de tabela |
| **Cinza 600** | `#6B6B6B` | Texto secundário, legenda, rótulo de campo |
| **Cinza 900** | `#171717` | Fundo escuro (capa, slide de abertura) |

### Comando — o acento

| Nome | Hex | Variante para fundo escuro |
|---|---|---|
| **Comando** | `#C1121F` | `#E5484D` |

É o vermelho do 24VCC no padrão de cabo da casa. Só existe porque tem razão técnica.

**Onde pode aparecer:**
- O nó do logo, em peça digital colorida
- O marcador de revisão no carimbo
- Estado ativo, link em foco, item selecionado
- Marcação de pendência ou divergência em documento técnico

**Onde não pode:**
- Fundo de área grande, faixa, cabeçalho
- Texto corrido ou título
- Mais de uma ocorrência por vista
- Qualquer peça impressa em preto e branco

**Teto:** 5% da área da peça. Se estiver dando na vista, já passou.

### Cor crítica

| Nome | Hex | Uso |
|---|---|---|
| Crítico | `#7F1D1D` | Só em documento técnico: erro que impede a entrega |

**Proibido em qualquer caso:** gradiente, azul corporativo, mais de um acento na mesma peça,
cor saturada em área grande.

---

## Tipografia

**Inter** — neo-grotesca, licença SIL Open Font License, livre para uso comercial.
Baixar em [rsms.me/inter](https://rsms.me/inter/) e instalar na máquina, para usar também no Word e
no CAD.

| Uso | Fonte | Peso | Observação |
|---|---|---|---|
| Nome do logo | Inter | 700 | Caixa alta, `letter-spacing` +0.08em |
| Título de seção | Inter | 700 | |
| Subtítulo | Inter | 600 | |
| Corpo | Inter | 400 | Entrelinha 1.5 |
| Legenda, descritor, rodapé | Inter | 500 | Cinza 600 |
| Carimbo, tag, código, número | JetBrains Mono ou Consolas | 400 | Monoespaçada — alinha coluna |

A monoespaçada não é enfeite: é o que faz tag e número de item alinharem em coluna, e é a voz do
carimbo. Ela separa o que é *dado* do que é *texto*.

**Fallback:** Arial ou Helvetica. Nunca Calibri, Times ou Comic.

**Hierarquia:** no máximo três tamanhos por página. Se precisar de um quarto, o problema é de
estrutura, não de tipografia.

---

## Estilo geral

Minimalista e monocromático, com a disciplina de uma folha de desenho bem feita: linha fina,
alinhamento rigoroso, informação onde deve estar, zero enfeite. Se um elemento não informa, sai.

---

## Elementos-chave

- **Bordas:** 1px Cinza 300. Nunca borda dupla
- **Border-radius:** 0. Canto reto em tudo
- **Botões:** retângulo sólido Tinta com texto Papel. Sem ícone, sem sombra
- **Sombras:** nenhuma
- **Tabelas:** linha horizontal apenas, sem coluna vertical. Cabeçalho em peso 600
- **Fio de seção:** 1px Cinza 300, o mesmo do logo
- **Grid:** margem generosa. Em A4, mínimo 25mm nas laterais

---

## O que NUNCA fazer

- Usar "Engenharia" ou "Engenheiro" em qualquer peça — regulado pelo CREA
- Azul corporativo, gradiente, sombra, canto arredondado
- Emoji em material de cliente ou documento técnico
- Esticar, distorcer, rotacionar ou recolorir o logo
- Logo sobre foto ou fundo com ruído
- Foto de máquina genérica de banco de imagem — é o que todo concorrente faz
- Peça sem carimbo

---

## Aplicações

| Peça | Logo | Carimbo |
|---|---|---|
| Capa de projeto | Completo, canto superior esquerdo, fundo Cinza 900 | Projeto · Cliente · Revisão · Data · Folhas |
| Folha A3 no CAD | Monograma BRN | Projeto · Folha · Revisão |
| Proposta comercial | Completo no cabeçalho da primeira página | Documento · Cliente · Revisão · Data |
| Apresentação | Completo no primeiro e no último slide | Documento · Data, no rodapé de todo slide |
| Assinatura de email | Completo, 140px de largura | Versão reduzida |

**Assinatura em documento técnico:**
`Borin Projetos Elétricos — Mateus Borin, projetista`

---

## Perfil do autor

- **Nome:** Mateus Borin
- **Handle:** *(a definir — checar disponibilidade no Instagram)*
- **Foto:** *(ex: marca/foto-perfil.jpg)*
- **Badge verificado:** não

---

## Observações adicionais

Enquanto a marca for desconhecida, o descritor "projetos elétricos industriais" é parte fixa do logo.
Só faz sentido soltar o nome sozinho quando o cliente já souber o que você faz sem ler.
