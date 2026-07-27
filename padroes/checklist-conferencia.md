# Checklist de conferência

> Roda antes de toda entrega, sem exceção — inclusive nas revisões.
> É isso que sustenta a promessa de "projeto conferido". Se o checklist não rodou, a entrega não sai.

---

## 1. Coerência de tags

- [ ] Toda tag segue o padrão definido (IEC 81346) e o mesmo prefixo em todo o projeto
- [ ] Nenhuma tag duplicada
- [ ] Nenhuma tag no diagrama que não exista na lista de material
- [ ] Nenhum item na lista de material sem tag no diagrama
- [ ] Tags de campo batem com a lista de identificações

## 2. Cabos e fios

- [ ] Todo cabo tem identificação, bitola e destino declarados
- [ ] Cores conforme o padrão da casa (potência preto, neutro azul claro, PE verde/amarelo, 24VCC vermelho, comando cinza, 0VCC marrom)
- [ ] Numeração de fio sem repetição dentro do mesmo potencial
- [ ] Cabo de interligação com origem e destino coerentes nos dois lados *(Escopo B)*

## 3. Folhas e navegação

- [ ] Folhas numeradas em sequência, sem furo
- [ ] Índice bate com o conteúdo real, folha por folha
- [ ] Referência cruzada entre folhas aponta para folha existente
- [ ] Carimbo presente e preenchido em todas as folhas
- [ ] Revisão declarada igual em capa, carimbo e nome de arquivo

## 4. Régua de bornes

- [ ] Todo ponto do diagrama que sai do painel passa por borne
- [ ] Numeração de borne sem repetição
- [ ] Jumpers representados
- [ ] Destino de cada borne coerente com o diagrama e com a lista de instalação

## 5. CLP

- [ ] Todo endereço de I/O do diagrama existe na planilha de I/Os
- [ ] Nenhum endereço duplicado
- [ ] Reserva de I/O declarada
- [ ] Descrição do ponto na planilha bate com a descrição no diagrama

## 6. Proteção e dimensionamento

- [ ] Toda carga tem proteção declarada
- [ ] Fusível 2A na CPU/fonte do CLP e 1A por módulo de I/O
- [ ] Disjuntor em fonte, tomada, ar-condicionado e ventilador
- [ ] DJM em inversor e RFF
- [ ] Balanço de consumo fecha com a capacidade da fonte 24VCC
- [ ] Dimensionamento térmico feito e a solução de ventilação ou climatização especificada

## 7. Layout do painel

- [ ] Todos os componentes da lista de material aparecem no layout
- [ ] Espaço de canaleta suficiente para o volume de fiação
- [ ] Componente que dissipa calor posicionado coerentemente com o dimensionamento térmico
- [ ] Acesso e manutenção viáveis

## 8. Layout de instalação *(Escopo B)*

- [ ] Todo periférico do diagrama aparece no layout 2D
- [ ] Passagem de cabo definida para todos os trechos
- [ ] Lista de material de instalação cobre todo o percurso previsto
- [ ] Tags de campo batem com o diagrama de interligação

## 9. Documentos e arquivos

- [ ] Memorial descreve o que o projeto realmente ficou, não o que se planejou no começo
- [ ] Lista de material do PDF idêntica à do Excel
- [ ] Todos os arquivos no padrão de nomenclatura, com a mesma revisão
- [ ] PDF pesquisável e paginado
- [ ] Tabela de revisões atualizada com o que mudou nesta rodada

## 10. Última passada

- [ ] Nome do cliente e do projeto escritos corretamente em todos os documentos
- [ ] Data de emissão correta
- [ ] Nenhum campo de template deixado em branco ou com texto de exemplo
- [ ] Nenhuma anotação interna, comentário ou marcação de rascunho esquecida no arquivo
- [ ] Abrir o PDF final do zero e folhear inteiro, como se fosse o cliente recebendo

---

**Registro.** Anotar na pasta do projeto quem conferiu, quando e o que foi corrigido. Erro que
aparece duas vezes em projetos diferentes vira item novo deste checklist.
