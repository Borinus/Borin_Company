# Checklist de conferência

> Roda antes de toda entrega, sem exceção — inclusive nas revisões.
> É isso que sustenta a promessa de "projeto conferido". Se o checklist não rodou, a entrega não sai.
> Calibrado sobre a estrutura real de entrega descrita em `padrao-entrega.md`.

---

## 1. Capa e memorial

- [ ] Tabela *Descrição do Quadro* completa: código do produto, código do projeto, tensão de comando, tensão de força, potência total, temperatura ambiente máxima
- [ ] Alimentação com bitola declarada para fase, neutro e terra
- [ ] Corrente nominal e potência dissipada calculada preenchidas — e a dissipada bate com o design térmico
- [ ] Tabela de revisões preenchida: revisão, data, modificado, verificado, aprovado, descrição da modificação
- [ ] Legenda de cores de cabo presente e igual à do memorial
- [ ] Memorial com os seis blocos preenchidos, sem caixa de seleção esquecida em branco
- [ ] Dimensões, material e grau de proteção do memorial batem com o layout e com o design térmico

## 2. Simbologia e índice

- [ ] Folha de simbologia cobre todos os símbolos usados no projeto
- [ ] Índice bate com o conteúdo real, folha por folha
- [ ] Coluna *Instalação* preenchida em todas as linhas
- [ ] Coluna *Montagem* coerente com o tipo de folha
- [ ] Numeração sem furo, incluindo as folhas com sufixo (40.a, 40.b, 48.c)
- [ ] Total de folhas no carimbo bate com o número real

## 3. Coerência de tags

- [ ] Toda tag segue letra identificadora mais contador, conforme IEC 81346
- [ ] Nenhuma tag duplicada dentro da mesma instalação
- [ ] Nenhuma tag no diagrama ausente da lista de materiais
- [ ] Nenhum item da lista de materiais sem tag no diagrama
- [ ] Tags das planilhas de identificação batem com as do diagrama

## 4. Cabos e fios

- [ ] Todo cabo com identificação, vias, bitola e comprimento declarados
- [ ] Cores conforme o padrão: fase preto, neutro azul claro, terra verde/amarelo, 24VCC vermelho, 0VCC marrom, sinal 24VCC cinza
- [ ] Seção padrão de 0,5 mm² aplicada onde o diagrama não especifica
- [ ] Numeração de fio sem repetição dentro do mesmo potencial
- [ ] Fios de 24V e 0V sem tag nem luva — identificados pela cor, conforme a observação do memorial

## 5. Régua de bornes

- [ ] Todo ponto que sai do painel passa por borne
- [ ] Uma folha de diagrama de conexão por régua (X0, X1, X2…)
- [ ] Numeração de borne sem repetição dentro da régua
- [ ] Jumpers representados
- [ ] Destino de cada borne coerente com o diagrama e com a interconexão

## 6. CLP

- [ ] Arquitetura do CLP coerente com a visão geral folha a folha
- [ ] Todo endereço de I/O do diagrama existe na planilha de arquitetura
- [ ] Nenhum endereço duplicado
- [ ] Reserva de I/O declarada
- [ ] Função descrita na planilha bate com a descrição no diagrama

## 7. Proteção e balanço

- [ ] Toda carga com proteção declarada
- [ ] Fusível 2A na CPU/fonte do CLP e 1A por módulo de I/O
- [ ] Disjuntor em fonte, tomada, ar-condicionado e ventilador
- [ ] DJM em inversor e RFF
- [ ] Consumo total em 24VCC dentro da capacidade da fonte, com folga
- [ ] Corrente nominal declarada na capa compatível com a proteção geral

## 8. Design térmico

- [ ] Todos os itens que dissipam calor estão na planilha, com tag e dissipação
- [ ] Dissipação total bate com o valor declarado na capa
- [ ] Cálculo feito com o material e as dimensões reais da caixa
- [ ] Temperatura ambiente do cálculo igual à declarada no memorial
- [ ] Solução de ventilação ou climatização especificada e presente na lista de materiais
- [ ] Nenhuma célula da planilha com erro de fórmula

## 9. Layout

- [ ] Todos os componentes da lista de materiais aparecem no layout
- [ ] Dimensão da placa de montagem bate com o memorial
- [ ] Espaço de canaleta suficiente para o volume de fiação
- [ ] Componente que dissipa calor posicionado coerentemente com o design térmico
- [ ] Acesso e manutenção viáveis

## 10. Instalação e campo *(Escopo B)*

- [ ] Todo cabo do diagrama de interconexão existe na base de cabos
- [ ] Origem e destino coerentes nos dois lados de cada cabo
- [ ] Todo periférico do diagrama tem tag de campo correspondente
- [ ] Lista de instalação cobre todo o percurso previsto
- [ ] Horas estimadas preenchidas em todas as tarefas de acompanhamento
- [ ] Acessórios por ocorrência, comprimento e item aplicados
- [ ] Arredondamento de compra aplicado nos itens que exigem
- [ ] Lista de material de campo separada da do painel

## 11. Identificações

- [ ] Os arquivos de identificação existem para o escopo contratado
- [ ] Aba de instrução de impressão preenchida: impressora e modelo de etiqueta
- [ ] Quantidade de etiquetas coerente com o número de fios, bornes e cabos do projeto
- [ ] Nenhuma linha de tag em branco ou com resíduo de filtro

## 12. Arquivos e fechamento

- [ ] Lista de materiais do PDF idêntica à do Excel
- [ ] Todos os arquivos na nomenclatura padrão, com o mesmo código e nome de projeto
- [ ] Estrutura de pastas montada conforme o padrão de entrega
- [ ] PDF pesquisável e paginado
- [ ] Nome do cliente e do projeto corretos em todos os documentos
- [ ] Data de emissão correta
- [ ] Nenhum campo de template em branco ou com texto de exemplo
- [ ] Nenhuma anotação interna ou marcação de rascunho esquecida
- [ ] Abrir o PDF final do zero e folhear inteiro, como se fosse o cliente recebendo

---

**Registro.** Anotar na pasta do projeto quem conferiu, quando e o que foi corrigido. Erro que
aparece duas vezes em projetos diferentes vira item novo deste checklist.
