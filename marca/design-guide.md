# Guia de Design — Borin Projetos Elétricos

> Você pode editar esse arquivo a qualquer momento.
> As skills que geram proposta, slide, capa de projeto ou qualquer peça visual leem este arquivo antes.

---

## Nome

**Borin Projetos Elétricos**.

Nome próprio porque o canal de venda é indicação: quem indica, indica o Mateus. Nunca acompanhar de
"Engenharia" — o serviço é projeto e documentação técnica, e o termo é regulado pelo CREA.

Domínio alvo: `borinprojetos.com.br` (livre em 26/07/2026, ainda não registrado).

---

## Logo

**Arranjo: empilhado com fio.** Nome em caixa alta, fio horizontal, descritor embaixo. O fio remete à
linha de cota do desenho técnico — é o único elemento gráfico da marca, e é ele que impede o logo de
virar só um texto qualquer.

```
BORIN
──────────────────────────────
projetos elétricos industriais
```

**Construção:**

| Elemento | Especificação |
|---|---|
| Nome | Inter Bold (700), caixa alta, `letter-spacing` +0.08em |
| Fio | Espessura 8% da altura da letra B. Largura = largura do descritor |
| Descritor | Inter Medium (500), caixa baixa, `letter-spacing` +0.12em |
| Corpo do descritor | 22% da altura do nome |
| Espaço nome → fio | 40% da altura da letra B |
| Espaço fio → descritor | 40% da altura da letra B |
| Alinhamento | Tudo à esquerda |

**Área de proteção:** margem livre em volta do logo igual à altura da letra B. Nada entra nesse espaço.

**Tamanho mínimo:** 24mm de largura em impresso, 90px em tela. Abaixo disso, usar o monograma.

**Monograma:** `BRN` em Inter Bold, caixa alta, para favicon, carimbo de folha e qualquer uso onde o
logo completo não caiba. Sem moldura, sem caixa preta.

**Arquivos:** `marca/logo.svg` (fundo claro), `marca/logo-branco.svg` (fundo escuro),
`marca/monograma-brn.svg`.

> Os SVGs usam a fonte Inter por referência. Antes de mandar pra gráfica ou usar em material
> definitivo, abra no Inkscape ou Illustrator e converta o texto em curvas — assim o logo não
> depende da fonte estar instalada na máquina de quem abre.

---

## Cores

Paleta monocromática. Sem cor de acento na marca — a hierarquia se faz por tamanho, peso e espaço.

| Nome | Hex | Uso |
|---|---|---|
| **Tinta** | `#111111` | Texto principal, logo, fios, botões |
| **Papel** | `#FFFFFF` | Fundo principal |
| **Cinza 100** | `#F5F5F5` | Fundo alternativo, faixa de seção |
| **Cinza 300** | `#DDDDDD` | Bordas, linhas de tabela, divisórias |
| **Cinza 600** | `#6B6B6B` | Texto secundário, legenda, descritor |
| **Cinza 900** | `#1A1A1A` | Fundo escuro (capa, slide de abertura) |

**Cor funcional — fora da marca.** Só em documento técnico, para marcar revisão, pendência ou item
não catalogado. Nunca em logo, capa, proposta ou material comercial:

| Nome | Hex | Uso |
|---|---|---|
| Alerta | `#B45309` | Item pendente, divergência, não catalogado |
| Crítico | `#991B1B` | Erro que impede a entrega |

**Proibido:** gradiente, cor saturada, mais de um acento na mesma peça, azul corporativo genérico.

---

## Tipografia

**Inter** — neo-grotesca, licença SIL Open Font License, livre para uso comercial.
Baixar em [rsms.me/inter](https://rsms.me/inter/) ou Google Fonts. Instalar na máquina para usar no
Word e no EPLAN.

| Uso | Fonte | Peso | Observação |
|---|---|---|---|
| Nome do logo | Inter | 700 | Caixa alta, `letter-spacing` +0.08em |
| Título de seção | Inter | 700 | |
| Subtítulo | Inter | 600 | |
| Corpo | Inter | 400 | Entrelinha 1.5 |
| Legenda, descritor, rodapé | Inter | 500 | Cinza 600 |
| Tag, código, número de item | JetBrains Mono ou Consolas | 400 | Monoespaçada, para alinhar coluna |

**Fallback:** se a máquina não tiver Inter, usar Arial ou Helvetica. Nunca Calibri, Times ou Comic.

**Regra de hierarquia:** no máximo três tamanhos por página. Se precisar de um quarto, o problema é
de estrutura, não de tipografia.

---

## Estilo geral

Minimalista e monocromático. Muito espaço em branco, hierarquia por tamanho e peso, nunca por cor.
Visual técnico e sóbrio, coerente com projeto elétrico industrial — não com agência nem com startup.
Se um elemento não informa, sai.

A referência mental é a folha de desenho técnico bem feita: linha fina, alinhamento rigoroso,
informação onde deve estar, zero enfeite.

---

## Elementos-chave

- **Bordas:** linha de 1px em Cinza 300. Nunca borda dupla
- **Border-radius:** 0. Canto reto em tudo — card, botão, imagem, tabela
- **Botões:** retângulo sólido Tinta com texto Papel. Sem ícone, sem sombra, sem arredondamento
- **Sombras:** nenhuma
- **Tabelas:** linha horizontal apenas, sem coluna vertical. Cabeçalho em peso 600
- **Fio de seção:** o mesmo fio do logo, 1px Cinza 300, para separar blocos
- **Grid:** margem generosa. Em A4, mínimo 25mm nas laterais

---

## O que NUNCA fazer

- Usar "Engenharia" ou "Engenheiro" em qualquer peça
- Gradiente, cor saturada, sombra, canto arredondado
- Emoji em material de cliente ou documento técnico
- Ilustração de banco de imagem, ícone decorativo, textura de fundo
- Esticar ou distorcer o logo, mudar a cor dele, rotacionar
- Colocar o logo sobre foto ou fundo com ruído

---

## Aplicações

| Peça | Uso do logo | Observação |
|---|---|---|
| Capa de projeto | Logo completo, canto superior esquerdo | Fundo Cinza 900 ou Papel |
| Carimbo de folha A3 | Monograma BRN | Espaço curto, logo completo não cabe |
| Proposta comercial | Logo completo no cabeçalho da primeira página | Demais páginas: monograma no rodapé |
| Assinatura de email | Logo completo, 140px de largura | |
| Apresentação | Logo completo no primeiro e no último slide | |

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
