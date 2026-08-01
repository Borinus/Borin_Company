# Estrutura de cálculo do valor do projeto

> Modelo v1 — 01/08/2026. Substitui a leitura da tabela por faixas.
> A tabela de `precificacao.md` continua válida: ela **é** este cálculo, arredondado.
> Executável em `comercial/calcular.py`.

---

## A descoberta que sustenta o modelo

A tabela de preço, dividida por R$ 235, dá o número de páginas de diagrama:

| Escopo | Preço da tabela | ÷ R$ 235 | Faixa de páginas |
|---|---|---|---|
| A pequeno | R$ 3.500 | 14,9 | até 15 |
| A médio | R$ 5.900 | 25,1 | 15 a 40 |
| A grande | R$ 8.200 | 34,9 | 40 a 80 |
| B grande | R$ 11.700 | 49,8 | acima |

E o único projeto medido — **04003478, 51 folhas, estimado em 50h feito à mão** — fecha em cima:
**uma hora de mercado por folha de diagrama.**

Então o preço não precisa de faixa. Ele é:

```
PREÇO BASE = PÁGINAS DE DIAGRAMA × R$ 235
```

A faixa era um atalho para não ter que contar página. Agora que a ficha dá os dados para estimar
a página, o atalho não é mais necessário — e some o degrau injusto de quem tem 41 páginas pagar
o mesmo de quem tem 79.

**O escopo B não leva multiplicador.** As folhas de interconexão de campo já entram na contagem.
Aplicar o "+40%" da tabela antiga **em cima** de uma contagem que já inclui campo cobra duas vezes
pela mesma coisa.

---

## As quatro parcelas

```
VALOR = BASE          páginas de diagrama × R$/página
      + ITENS NOVOS   peças que não existem no banco e precisam ser criadas à mão
      + SETUP         só na primeira vez, se o cliente impõe o padrão dele
      × MODIFICADORES urgência, arquivo-fonte, condição de abertura
      com piso de R$ 2.400
```

### 1. Base — páginas de diagrama

R$ 235 por página. É a hora de mercado, não a sua. O ganho de velocidade é margem, nunca desconto —
o raciocínio inteiro está em `precificacao.md`, seção *Por que o preço não cai junto com o custo*.

### 2. Itens novos no banco — a parcela que ninguém mais cobra

Esta é a parcela que quebra a linearidade, e é a que precisa existir separada.

O gerador só é rápido para o que **já está no banco**. Peça que não está tem que ser criada, e
criar peça é trabalho manual que o 8x não alcança. Mas o custo depende de onde a peça vem:

| Origem da peça | O que acontece | Custo | Cobrança |
|---|---|---|---|
| **Marca grande** — Siemens, Schneider, WEG, Rockwell, Phoenix, Weidmüller, ABB | O fabricante publica os dados. Importa e ajusta | ~0 h | **R$ 0** |
| **Marca pequena** — Weintek e abaixo, sem dados publicados | Cadastro 100% manual: símbolo, conexões, dados, macro | **1 h por peça** | **R$ 250 por peça** |

Cobrado a R$ 250 — a hora avulsa da tabela, não os R$ 235 do piso. É deliberado: essa hora é
irreplicável, não escala e não tem 8x. Quem traz peça exótica paga por ela.

**Isto precisa aparecer na proposta como linha separada e nomeada.** Diluir no valor do projeto
esconde do cliente que a escolha de marca dele tem preço — e ele escolhe de novo igual no próximo.
Vendo a linha, muitos trocam a peça por uma equivalente que já está no banco, o que é melhor para
os dois lados.

**No orçamento isso ainda é estimativa.** A contagem verdadeira só sai depois da ficha do projeto
preenchida, quando dá para comparar a lista de material contra o banco. Por isso a proposta traz o
número previsto e a regra do que acontece se mudar (ver *O que fazer quando a contagem muda*).

### 3. Setup de padrão do cliente

Cliente que impõe o padrão dele — carimbo próprio, nomenclatura de tag própria, cores próprias,
código de ERP — obriga a montar esse padrão uma vez. O gerador não tem isso pronto.

| | Horas | Valor |
|---|---|---|
| Usa o padrão Borin | 0 | **R$ 0** |
| Padrão do cliente, primeira vez | 4 | **R$ 1.000** |
| Projetos seguintes do mesmo cliente | 0 | **R$ 0** |

É cobrado uma vez por cliente, não por projeto. É o que justifica a ficha `/padrao` existir separada
da ficha de projeto: o padrão é ativo do relacionamento, não do pedido.

### 4. Modificadores

| | Efeito | Quando |
|---|---|---|
| Urgência | **+30%** | prazo abaixo do padrão da tabela |
| Arquivo-fonte do CAD | **+50%** | cliente quer o editável |
| Condição de abertura | **−50%** | primeiro projeto de cada cliente |

Ordem de aplicação: base + itens + setup → acréscimos → desconto por último. Aplicar o desconto
antes dos acréscimos reduz também o que não deveria ser descontado.

### Piso

**R$ 2.400.** Abaixo de ~10 páginas o trabalho humano — briefing, alinhamento, conferência final,
entrega — domina o custo e não encolhe junto com o desenho. Projeto de 4 páginas não custa
R$ 940 de fazer.

---

## Estimador de páginas

Quando o cliente não sabe quantas páginas — que é o caso normal no orçamento — as páginas saem dos
números que a ficha pede.

```
PÁGINAS = 14                              fixas: capa, índice, potência, arquitetura de CLP,
                                          layout, memorial, referência cruzada
        + pontos de I/O      ÷ 4,5        multifilar de comando
        + acionamentos       ÷ 2,5        partidas, inversores, válvulas, resistências
        + disp. de segurança ÷ 2          NR-12
        + pontos de I/O      ÷ 35         réguas de bornes
        + cabos de campo     ÷ 6          só escopo B
          onde cabos ≈ (I/O + acionamentos) ÷ 3
        arredondado para cima
```

**Calibração.** Aplicado ao 04003478 — 96 pontos de I/O, 8 válvulas, 6 dispositivos de segurança,
escopo B:

```
14 + 21,3 + 3,2 + 3,0 + 2,7 + 5,8 = 50,1  ->  51 páginas
```

O projeto real tem **51 folhas**. O estimador acerta em cima do único caso medido.

**Isso é um caso, não uma amostra.** Todas as constantes acima são derivadas dele. Depois de cada
projeto entregue, comparar página estimada com página real e corrigir a constante que errou — as
constantes ficam isoladas no topo de `calcular.py` justamente para isso.

---

## O que fazer quando a contagem muda

O orçamento sai antes da ficha. Entre o orçamento e o projeto, o número muda — e isso precisa ter
regra escrita, senão vira discussão a cada vez.

| Diferença entre estimado e real | O que acontece |
|---|---|
| Até 15% para mais | **Absorve.** Está dentro do erro do estimador, e cobrar por isso queima a relação |
| Acima de 15% para mais | **Aditivo**, cobrado só sobre o excedente que passa dos 15% |
| Para menos | **Mantém o valor fechado.** Preço fechado é fechado nos dois sentidos |

Isso precisa estar no contrato, não só aqui. Ver a lacuna apontada em `fluxo-comercial.md`.

Item novo de marca pequena que aparece depois da ficha entra como aditivo integral — não tem faixa
de tolerância, porque é hora manual pura e o cliente escolheu a peça.

---

## Exemplos fechados

**1 · Painel médio, padrão Borin, tudo no banco**
40 I/O · 6 acionamentos · sem NR-12 · escopo A

```
páginas   14 + 8,9 + 2,4 + 0 + 1,1            = 27
base      27 × R$ 235                          = R$ 6.345
                                          TOTAL  R$ 6.345
```

**2 · O 04003478, se fosse cliente próprio**
96 I/O · 8 acionamentos · 6 disp. segurança · escopo B · 2 peças Weintek novas

```
páginas   51
base      51 × R$ 235                          = R$ 11.985
itens     2 × R$ 250                           = R$ 500
                                          TOTAL  R$ 12.485
```

**3 · O mesmo, primeiro projeto do cliente, com padrão próprio dele**

```
base      51 × R$ 235                          = R$ 11.985
itens     2 × R$ 250                           = R$ 500
setup     padrão do cliente                    = R$ 1.000
subtotal                                       = R$ 13.485
abertura  −50%                                 = R$ 6.743
                                          TOTAL  R$ 6.743
```

Rende R$ 482/h sobre as 14h suas. Acima do piso de R$ 235 mesmo pela metade.

**4 · Projeto pequeno, para ver o piso agir**
8 I/O · 2 acionamentos · escopo A

```
páginas   14 + 1,8 + 0,8 + 0,2                 = 17
base      17 × R$ 235                          = R$ 3.995
```

Acima do piso. O piso só age abaixo de ~10 páginas, que na prática quase não existe — as 14 páginas
fixas garantem isso. **Serve de alerta:** se um orçamento sair abaixo de R$ 2.400, é sinal de que o
estimador recebeu dado errado, não de que o projeto é barato.

---

## O que este modelo ainda não cobre

Registrado para não parecer resolvido:

- **Revisão de projeto de terceiro** — continua por hora, R$ 250. Não tem página estimável
- **Instalação e comissionamento** — não é escopo hoje
- **Programação de CLP** — plano de expansão, sem preço definido
- **Cliente que exige norma fora do padrão** — IEC/NFPA já estão no banco; exigência de norma de
  cliente final estrangeiro é escopo novo e precisa ser orçado à parte
- **Projeto multi-painel** — o estimador trata um painel. Dois painéis não são duas vezes o preço
  (o fixo não dobra), mas também não é linear. Medir no primeiro caso que aparecer
