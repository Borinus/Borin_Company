# Pesquisa de concorrência — projeto elétrico industrial

> Arquivo **acumulativo**. Cada rodada acrescenta empresas e achados novos no fim, sem reescrever o
> que já está aqui. As conclusões estratégicas ficam sempre no topo, atualizadas.
>
> Complementa `analise-mercado.md`, que olhou só a Serra Gaúcha. Aqui o recorte é maior: Brasil e
> exterior, e principalmente **como as pessoas vendem** projeto elétrico.

---

## Conclusões estratégicas até agora

### 1. A automação de geração de projeto é uma categoria de mercado, não uma invenção isolada

Isso é a notícia mais importante da primeira rodada, e é preciso encarar de frente.

| Solução | O que faz | Situação |
|---|---|---|
| **EPLAN Automated Project Generation** | O próprio fabricante do CAD vende geração automática a partir de configuração. Promete que "trabalhador não treinado gera esquemas inserindo os requisitos do cliente" | Produto comercial maduro |
| **WSCAD ELECTRIX AI 2026** | Gera layout de painel a partir do diagrama, com IA reconhecendo padrões de projetos anteriores. Alega redução de até 50% no tempo manual | Lançado para 2026 |
| **Festo System Configurator** | Configurador online gratuito: OEM monta sistema de automação completo num fluxo só | Lançado em janeiro de 2026, gratuito |
| **AutoPanel Design** | ECAD web gratuito com IA generativa e documentação automática | Gratuito |
| **SEE Electrical Expert** | Geração automática de esquemas, alega 40% mais rápido | Comercial |

**O que isso significa na prática.** O método não é o diferencial defensável que parece. O que é
defensável é outra coisa:

- **A biblioteca de macros do domínio.** Um configurador genérico não sabe o que é Promix, Viscon, HotSpray, cabine de pintura. A biblioteca é que carrega o conhecimento, e ela leva anos pra ficar boa
- **O Perfil de Padrão do cliente.** Marca por família, de/para de ERP, regras fixas. Quem tem isso preenchido entrega em horas o que o concorrente entrega em semanas — e o concorrente com o mesmo software continua sem esse dado
- **A conferência automática.** Gerar rápido é meio caminho. Gerar rápido *e provar que está certo* é o que sustenta preço baixo sem virar reputação de porcaria

**Consequência para a estratégia de preço:** vender barato "porque sou rápido" tem prazo de validade.
Quando a ferramenta virar commodity, sobra o preço baixo e nenhuma margem. O preço baixo serve como
**entrada**, não como posicionamento permanente — o que já está registrado como condição de abertura
em `precificacao.md`.

### 2. Referências de preço no Brasil

Números públicos, de fontes de mercado, para projeto elétrico predial e industrial. **Não são
diretamente comparáveis** a projeto de painel de máquina, mas servem de âncora de ordem de grandeza.

| Base | Faixa |
|---|---|
| Projeto industrial completo | a partir de R$ 10.000 |
| Projeto industrial simples | R$ 5.000 a R$ 10.000 |
| Projeto industrial complexo | acima de R$ 50.000 |
| Por metro quadrado | R$ 60 a R$ 150/m² |
| Hora de engenheiro eletricista experiente | R$ 150 a R$ 300 |

O valor-hora é a referência mais útil aqui. Mesmo descontando que ele é de engenheiro habilitado e o
serviço da Borin é projetista, **a hora não deveria ser precificada muito abaixo de R$ 100** — abaixo
disso o negócio não paga a licença, o imposto e o tempo comercial.

### 3. Ninguém vende o pacote como produto

Das empresas brasileiras encontradas (DSF, P3, André Gomes, VEZZA, AJN), o padrão se repete:
site institucional, lista de serviços, "orçamento personalizado". **Nenhuma publica o que entrega,
documento por documento, nem o prazo, nem como o preço é formado.**

Isso confirma a aposta do site da Borin: mostrar o manifesto de entrega e a tabela de orçamento antes
do primeiro contato é diferencial real, e é barato de fazer.

---

## Rodada 1 — 29/07/2026

### Brasil — quem vende projeto elétrico como serviço

| Empresa | Onde | Recorte | Observação |
|---|---|---|---|
| [DSF Engenharia](https://www.dsfengenharia.com.br/) | São Paulo, desde 2014 | Predial e industrial, laudos, cabine primária, eficiência energética | Escopo largo, sem preço publicado |
| [P3 Engenharia Elétrica](https://p3engenharia.com.br/) | — | Projeto industrial + execução e gerenciamento de obra | Vende obra junto, não só projeto |
| [André Gomes Engenharia](https://www.andregomes-eng.com.br/preco-projeto-eletrico-industrial) | — | Consultoria, projeto e acompanhamento de instalação | Tem página de preço, sem números |
| [VEZZA](https://www.vezzaengenharia.com.br/blog/preco-projeto-eletrico-industrial) | — | Conteúdo sobre preço de projeto industrial | Usa conteúdo pra captar |
| [AJN Consultoria](https://www.ajnengenharia.com.br/) | BH | Projeto elétrico industrial | — |

**Padrão observado:** todas são de engenharia predial/industrial com ART, não de painel de máquina.
São vizinhas, não concorrentes diretas. O concorrente direto da Borin continua sendo a integradora
que faz projeto internamente — o que reforça a tese de `analise-mercado.md` de que integradora é
cliente, não rival.

### Exterior — como o mercado maduro empacota

- **Chemionix** e **BackOfficePro**: vendem *electrical panel design services* como terceirização pura, modelo offshore. Prometem redução de custo de engenharia e time-to-market. É o modelo mais próximo do que a Borin faz, e mostra que o serviço existe como categoria própria fora do Brasil
- Argumento que eles usam e vale copiar: *"o custo total de propriedade, incluindo engenharia, é significativamente menor terceirizando"* — é venda por custo total, não por preço de hora

### Lacunas a investigar nas próximas rodadas

- [ ] Quem no Brasil vende projeto de painel de máquina como serviço, sem obra e sem ART
- [ ] Faixa de preço praticada em projeto de painel por I/O ou por folha
- [ ] Como as ofertas gringas de *electrical design outsourcing* estruturam pacote e prazo
- [ ] Casos de fabricante de máquina que terceiriza projeto: o que reclamam, o que valorizam
- [ ] Concorrentes que já usam geração automática e como comunicam isso ao cliente
- [ ] Marketplaces e plataformas de freelance: quanto se pratica e qual o perfil de demanda
- [ ] Se algum player publica prazo garantido — e como se protege

**Fontes da rodada:** [Cronoshare](https://www.cronoshare.com.br/quanto-custa/projeto-eletrico) ·
[CD Consultoria](https://blog.cdconsultoria.net/instalacoes-hidraulicas-e-eletricas/quanto-custa-um-projeto-eletrico-industrial) ·
[EPLAN Automated Project Generation](https://www.eplan.com/us-en/products/automated-project-generation/) ·
[WSCAD ELECTRIX AI](https://www.wscad.com/us/electrix/) ·
[Festo System Configurator](https://www.automation.com/article/festo-system-configurator-engineering-tool-speed-machine-design) ·
[AutoPanel Design](https://www.autopaneldesign.com/) ·
[Chemionix](https://www.chemionix.com/electrical-panel-design-services.html) ·
[BackOfficePro](https://www.backofficepro.com/engineering/electrical-design-services.php)
