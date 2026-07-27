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

Domínio alvo: `borinprojetos.com.br` (livre em 26/07/2026, ainda não registrado).

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
| Fio | Espessura 0,08 B. Largura = descritor menos o nó e o intervalo |
| Intervalo fio → nó | 0,12 B |
| Nó | Quadrado de 0,2 B, centrado na altura do fio |
| Descritor | Inter Medium (500), caixa baixa, `letter-spacing` +0.12em |
| Corpo do descritor | 0,22 da altura do nome |
| Nome → fio | 0,4 B |
| Fio → descritor | 0,4 B |
| Alinhamento | Tudo à esquerda |

**Área de proteção:** margem livre igual à altura da letra B. Nada entra nesse espaço.

**Tamanho mínimo:** 24mm de largura em impresso, 90px em tela. Abaixo disso, usar o monograma.

O logo padrão é monocromático de propósito: assim funciona em impressão preto e branco, em carimbo,
gravado ou fotocopiado. A versão com o nó vermelho é exceção, não regra.

### Como chamar a marca em cada lugar

Esta é a regra que evita repetir o nome inteiro numa folha de projeto:

| Onde | Como aparece |
|---|---|
| Capa do projeto, proposta, apresentação, assinatura de email | Logo completo: `BORIN` + fio + nó + *projetos elétricos industriais* |
| **Carimbo de folha do EPLAN** | **Só `BORIN`** — sem fio, sem nó, sem descritor |
| Espaço muito curto: favicon, rodapé de slide, etiqueta | Monograma `BRN` |
| Texto corrido, contrato, nota fiscal | Nome por extenso: Borin Projetos Elétricos |

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

**PNG** — para colocar dentro do EPLAN, Word e apresentação (`marca/png/`):

| Arquivo | Uso |
|---|---|
| `borin-completo.png` | Capa de projeto e proposta — fundo transparente |
| `borin-completo-branco.png` | Sobre fundo escuro |
| `borin-completo-comando.png` | Peça digital colorida, nó em vermelho |
| `borin-carimbo.png` | **Carimbo de folha do EPLAN** — só o nome, transparente, alta resolução |
| `borin-carimbo-600px.png` | Mesma coisa reduzida, se o EPLAN engasgar com arquivo grande |
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
Vem direto do carimbo de folha do EPLAN — quem recebe reconhece na hora de onde veio.

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
| Folha A3 (dentro do EPLAN) | Projeto · Folha · Revisão |
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
no EPLAN.

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
| Folha A3 no EPLAN | Monograma BRN | Projeto · Folha · Revisão |
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
