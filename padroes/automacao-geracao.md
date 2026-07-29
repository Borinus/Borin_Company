# A automação de geração de projeto

> Registro do que a ferramenta faz, por que ela é o motivo real do preço baixo, e o que precisa
> acontecer antes de ela poder servir à Borin.
> Levantado em 29/07/2026 lendo o workspace `CONFERENCIAS/`.

---

## O que existe hoje

Dois sistemas na mesma pasta, encadeados num ciclo fechado.

### 1. Geração — ficha vira projeto

```
FICHA_PROJETO.xlsx  →  plano de colagem  →  execução no CAD  →  projeto + PDF + Excels
   (checklist)         (auditável)          (VM, via ponte)      (entrega completa)
```

A ficha é um formulário com listas suspensas. Os blocos que ela cobre:

| Bloco | O que define |
|---|---|
| Projeto | Nome, descrição, cliente, obra, número |
| Alimentação | Mono ou tri, chave geral, entrada, fonte 24V, tomada |
| Segurança | Plataforma, CLP de segurança, expansões, dispositivos (emergência de painel, emergência + reset, trava de porta, interface de robô, equipamento de pintura), contatora de saídas |
| Remota | Se usa, qual acoplador |
| IHM | Modelo e rede |
| Rede | Switch, quantidade, gateway, pontos de rede, cabo |
| I/O de processo | Entradas e saídas digitais e analógicas, sensores NAMUR, válvulas, reservas |
| Entradas | Um contador por tipo de sensor: pressostatos por faixa, sensores de temperatura, seletoras, botões, fluxostato |
| Saídas | Sinaleiros, buzzer, válvulas, reservas |

Cada linha da ficha vira uma **colagem de macro** num plano auditável, com a origem declarada. Um
executor burro aplica o plano — ele não decide nada, o que torna o resultado reproduzível e o erro
rastreável até a linha da ficha que o causou.

### 2. Conferência — o projeto é auditado sozinho

Pipeline de extração, checagem e relatório que compara o PDF exportado contra as listas e contra um
banco de regras. Cobre, entre outras coisas: extração de fios por coordenada, grafo de topologia para
resolver origem e destino, bornes, consumo de 24V contra a fonte, nomenclatura de tags, e um checker
específico com as regras de revisão vindas do gestor.

### 3. O ciclo

Gerar → conferir → corrigir → gerar de novo, até a conferência passar limpa. **É esse laço fechado
que é o diferencial**, não a geração isolada. Gerar rápido qualquer um vai conseguir; gerar rápido e
**provar que está certo** é o que permite cobrar menos sem virar fama de trabalho malfeito.

---

## Por que isso muda o negócio

O preço baixo da Borin não é desconto: é **custo unitário menor de verdade**. Um projeto que o
concorrente monta folha por folha sai de uma ficha preenchida em minutos, com a conferência rodando
sozinha em cima.

Mas isso só se sustenta com três condições:

1. **A biblioteca de macros precisa cobrir o domínio.** É ela que carrega o conhecimento — cabine de pintura, dosagem, segurança de robô. Sem biblioteca, o gerador não gera nada
2. **O cliente precisa ter Perfil de Padrão preenchido.** É o que transforma a ficha em algo que dá pra preencher sozinho. Ver `perfil-cliente.md`
3. **A conferência precisa continuar apertada.** É o contrapeso da velocidade

---

## O problema que precisa ser resolvido antes de usar na Borin

**A ferramenta como está hoje é da FLOWSISTEM, não da Borin.** Isso está escrito no próprio
workspace, e não é uma interpretação minha:

- O `CLAUDE.md` do projeto abre com "Workspace FLOWSISTEM" e fala em conferir "contra as regras da FLOWSISTEM"
- A biblioteca de macros mora na VM da empresa, num caminho da empresa
- A execução acontece numa VM da empresa, com licença da empresa
- O banco de regras de conferência foi construído a partir das conversas com o gestor, no Teams da empresa
- Os projetos de referência e os códigos são da empresa e dos clientes dela

**O método é conhecimento seu. A implementação, não.** Vale exatamente o mesmo raciocínio já
aplicado aos templates de planilha em `padrao-entrega.md`: saber que um projeto se gera a partir de
uma ficha é boa prática de engenharia e ninguém é dono disso. A biblioteca, o banco de regras, os
scripts e a infraestrutura construídos lá dentro são outra coisa.

### O que precisa ser feito

- [ ] Conversar com a FlowSistem sobre a titularidade da automação **antes** de usar qualquer parte dela fora
- [ ] Construir uma **biblioteca de macros própria**, do zero — é o item de maior esforço de todo o negócio
- [ ] Reescrever o gerador com estrutura própria, sem herdar código, regras nem nomenclatura de lá
- [ ] Rodar em licença própria, em máquina própria
- [ ] Montar o banco de regras de conferência a partir das normas públicas, não das regras internas do gestor

Enquanto isso não estiver resolvido, **a automação não entra em proposta, nem em contrato, nem no
site**. O que já está no ar hoje — prazo curto e preço de abertura — se sustenta sem ela: prazo do
concorrente é fila, e a Borin não tem fila.

---

## O que a pesquisa de mercado mostrou sobre isso

Ver `comercial/pesquisa-concorrencia.md`. Em resumo: geração automática de projeto **já é categoria
de mercado**. O próprio fabricante do CAD vende, e há concorrentes com IA prometendo layout
automático a partir do diagrama.

Ou seja: o método sozinho não é fosso. O fosso é a **biblioteca do domínio** mais o **Perfil de
Padrão do cliente** — os dois dados que nenhum software genérico tem.
