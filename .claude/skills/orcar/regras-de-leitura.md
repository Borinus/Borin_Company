# Regras de leitura da ficha — ensinadas pelo Mateus

Como contar os pontos quando um cliente descreve o projeto por mensagem.
Cada regra veio de correção dele; aplicar sempre, sem rediscutir.
Formato: **regra** — de onde veio.

## Segurança / NR-12

- **Chave com trava (trava de porta) normalmente é item de NR-12** → conta em
  `seg_qtd`, não em I/O comum. — 10/08/2026, orçamento do elevador.
  **MAS não é "sempre": é decisão do projeto.** No mesmo elevador, o chefe
  confirmou depois que chave e trava eram SEM NR-12 — aí contam como I/O
  comum e `seg_qtd` fica zero. Na dúvida, contar como NR-12 e PERGUNTAR ao
  Mateus antes de fechar; nunca decidir sozinho. — 10/08/2026, correção do
  chefe no mesmo orçamento.

## I/O

- Sensor comum (porta fechada, fim de curso, posição) e botoeira de comando
  contam como I/O comum, 1 ponto cada.
- Somar uns poucos pontos de painel além dos de campo (interface de inversor,
  encoder, emergência) e mostrar a conta aberta pro Mateus conferir.

## Acionamentos

- Contar motores/inversores/válvulas de potência. Dispositivo já contado em
  I/O ou segurança NÃO conta de novo como acionamento (conta dobrada infla a
  estimativa).

## Ficha

- **`equipamento` é o NOME do projeto, curto** ("elevador de cargas de 20
  andares"). A lista do que ele tem vai em `observacao`, com as palavras do
  cliente. — 10/08/2026, correção do Mateus no orçamento do elevador (a spec
  inteira tinha ido pro nome).

## Escopo e o que NÃO decidir

- Escopo A/B e NR-12 só saem de `?` se a conversa disser explicitamente.
  Decisão técnica é do Mateus, na tela do rascunho.
