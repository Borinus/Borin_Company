# Templates de entrega

Planilhas modelo da Borin, com o carimbo da marca no topo e a estrutura definida em
`padroes/padrao-entrega.md`.

Os arquivos em `xlsx/` são gerados por `gerar-planilhas.py`. Se precisar mudar coluna, fórmula ou
regra, **mude o script e rode de novo** — assim os dez arquivos continuam consistentes entre si.

```
python padroes/templates/gerar-planilhas.py
```

## O que tem

| Arquivo | Escopo | Abas |
|---|---|---|
| Lista de Materiais | A e B | Lista, agrupada por instalação |
| Arquitetura de CLP | A e B | Pontos + Resumo com contagem automática por tipo |
| Design Térmico | A e B | Dissipação (com total) · Cálculo (superfície, ΔT, excedente, veredito) · Base de dissipação |
| Painel — TAGs Fios, Bornes, Dispositivos, Relé | A e B | Dados + Impressão |
| Campo — TAGs Fios, Cabos | B | Dados + Impressão |
| Lista de Instalação | B | Base de cabos · Acompanhamento com horas · Material · Acessórios por ocorrência, comprimento e item · Acessórios fixos · Fornecedores |

## O que já funciona sozinho

- **Design Térmico** — a aba Cálculo puxa a dissipação total, calcula a superfície efetiva pelas dimensões, aplica o coeficiente do material da caixa e diz se a ventilação natural resolve ou se precisa de forçada. Coeficientes conforme prática usual da IEC 60890; confira contra o catálogo do fabricante da caixa
- **Arquitetura de CLP** — o Resumo conta entradas e saídas digitais e analógicas sozinho, a partir da coluna Tipo
- **Material de instalação** — a coluna *Qtd a comprar* aplica o arredondamento de compra (terminal de 100 em 100, luva de 10 em 10)
- **Acompanhamento** — horas concluídas saem de horas estimadas vezes percentual, com total no rodapé

## O que ainda precisa de você

- Preencher a **Base de dissipação** a partir dos catálogos dos fabricantes. O dado é público no datasheet; a compilação é ativo seu e cresce a cada projeto
- Preencher a aba **Impressão** de cada planilha de tags com a tua impressora e o modelo de etiqueta
- Montar a base de **Fornecedores**
- Ajustar coluna ou nomenclatura que o teu fluxo no EPLAN exigir — a exportação tem que cair direto nessas colunas, sem retrabalho manual

## Templates do EPLAN

Ficam de fora deste script: folha, carimbo, capa, memorial e simbologia precisam ser montados dentro
do EPLAN, na máquina onde ele está instalado. Os PNGs da marca para usar no carimbo estão em
`marca/png/` — o do carimbo é o `borin-carimbo.png`.
