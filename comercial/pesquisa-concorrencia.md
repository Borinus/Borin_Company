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

### 3. Existe um vão de mercado entre o freelance e o engenheiro

| Faixa | Quem ocupa | O que entrega |
|---|---|---|
| ~R$ 37/hora | Freelance de plataforma | Desenho do que mandarem. Perfil AutoCAD/Revit, predial |
| **vazio** | **—** | **projeto de painel de máquina como produto** |
| R$ 150–300/hora | Engenheiro eletricista com ART | Projeto com responsabilidade técnica, foco predial e industrial de obra |

No meio não há oferta estruturada. Quem precisa de projeto de painel hoje compra do fabricante do
painel, embutido — e recebe documentação de subproduto.

**É esse vão que a Borin ocupa.** E é por isso que a comparação de preço não deve ser com o
freelance: o que se vende não é desenho por hora, é pacote fechado e conferido.

### 4. Prazo se promete em duas camadas, não em uma

Achado da rodada 3, e o mais imediatamente aplicável de toda a pesquisa. Provedor internacional
garante **primeiro rascunho em 48 horas** e entrega o pacote completo em 2 a 6 semanas.

Separar as duas promessas resolve o risco da condição de abertura:

- **Primeira emissão parcial, prazo curto e garantido** — capa, memorial, potência e arquitetura de CLP
- **Pacote completo, na data fechada da proposta**

O cliente vê andamento em dias e para de cobrar; o prazo total continua realista mesmo com produção
noturna. É melhor que prometer metade do prazo do concorrente para tudo.

### 5. Ninguém vende o pacote como produto

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

- [x] Quem no Brasil vende projeto de painel de máquina como serviço, sem obra e sem ART — rodada 2
- [ ] Faixa de preço praticada em projeto de painel por I/O ou por folha
- [x] Como as ofertas gringas de *electrical design outsourcing* estruturam pacote e prazo — rodada 3
- [ ] Casos de fabricante de máquina que terceiriza projeto: o que reclamam, o que valorizam
- [ ] Concorrentes que já usam geração automática e como comunicam isso ao cliente
- [x] Marketplaces e plataformas de freelance: quanto se pratica e qual o perfil de demanda — rodada 2
- [x] Se algum player publica prazo garantido — e como se protege — rodada 3
- [ ] Como o mercado gringo cobra revisão e mudança de escopo
- [ ] Fabricantes de painel do Sul: eles projetam internamente ou terceirizam?
- [ ] Como integradoras comunicam prazo de projeto na proposta

**Fontes da rodada:** [Cronoshare](https://www.cronoshare.com.br/quanto-custa/projeto-eletrico) ·
[CD Consultoria](https://blog.cdconsultoria.net/instalacoes-hidraulicas-e-eletricas/quanto-custa-um-projeto-eletrico-industrial) ·
[EPLAN Automated Project Generation](https://www.eplan.com/us-en/products/automated-project-generation/) ·
[WSCAD ELECTRIX AI](https://www.wscad.com/us/electrix/) ·
[Festo System Configurator](https://www.automation.com/article/festo-system-configurator-engineering-tool-speed-machine-design) ·
[AutoPanel Design](https://www.autopaneldesign.com/) ·
[Chemionix](https://www.chemionix.com/electrical-panel-design-services.html) ·
[BackOfficePro](https://www.backofficepro.com/engineering/electrical-design-services.php)

---

## Rodada 2 — 29/07/2026

**Lacunas atacadas:** quem vende projeto de painel de máquina sem obra · o que se pratica em
plataforma de freelance.

### Achado principal: o projeto vem embutido na fabricação

Procurando quem vende **projeto de painel de máquina como serviço isolado** no Brasil, o resultado é
sistematicamente o mesmo — aparecem **fabricantes de painel**, não projetistas:

| Empresa | Onde | O que vende |
|---|---|---|
| [LogTek](https://www.logtek.com.br/quadro-comando-eletrico) | desde 2011 | Montagem de painel com equipe de engenheiros e projetistas própria |
| [JHP Automação](https://www.jhpautomacao.com.br/fabricapaineiseletricos) | — | Fabrica painel de baixa tensão e faz o projeto conforme a necessidade |
| [Inspectro](https://www.inspectro.com.br/montagem-painel-comando-eletrico) | 10+ anos | Montagem de painel |
| [Monpaineis](https://www.monpaineis.com.br/painel-de-comando-de-maquinas.php) | — | Fabricação, com NR-10 e normas ABNT |
| [Comando Painéis](https://comandopaineis.com.br/) | Santa Catarina | Painéis certificados, uma das maiores do estado |

**Todas vendem o painel montado e dão o projeto de brinde dentro do preço.** Nenhuma vende o
projeto separado — e nenhuma publica prazo de projeto.

**Por que isso é bom para a Borin.** O projeto embutido na fabricação tem dois problemas para quem
compra, e os dois são argumento de venda:

1. **Amarra o cliente ao fabricante.** Quem tem só o painel montado e nenhum projeto decente não consegue pedir cotação para outro fabricante no ano seguinte. Projeto independente é liberdade de compra
2. **O projeto é subproduto, não entrega.** Feito rápido, para a fábrica interna, com a qualidade mínima para montar. Documentação para *manter* o equipamento por dez anos é outra coisa

Isso vira uma frase de proposta: *o projeto independente é seu, não do fabricante do painel.*

### Freelance: o piso do mercado é baixo, e isso é uma armadilha

| Referência | Valor |
|---|---|
| Projetista elétrico CLT, média | ~R$ 36.000/ano · ~R$ 18,46/hora |
| Regra usual de conversão para autônomo | dobro da hora CLT · ~R$ 37,50/hora |

Nas plataformas de freelance o perfil que aparece é AutoCAD, BIM e Revit — instalação predial, não
painel de máquina. **Praticamente não há oferta de projeto de painel industrial nesse canal.**

**Leitura:** o piso de R$ 37/hora é o preço de quem desenha o que mandam. Não é o mercado da Borin, e
ancorar nele seria erro — mas é o número que um comprador desinformado vai jogar na mesa. A resposta
é escopo, não desconto: o freelance de R$ 37 entrega desenho; a Borin entrega pacote conferido,
identificação pronta para imprimir e plano de instalação.

E confirma o vão do mercado: entre o freelance de R$ 37/hora e o engenheiro de R$ 150–300/hora **não
existe oferta estruturada de projeto de painel de máquina**. É exatamente onde a Borin se encaixa.

**Fontes:** [LogTek](https://www.logtek.com.br/quadro-comando-eletrico) ·
[JHP Automação](https://www.jhpautomacao.com.br/fabricapaineiseletricos) ·
[Inspectro](https://www.inspectro.com.br/montagem-painel-comando-eletrico) ·
[Monpaineis](https://www.monpaineis.com.br/painel-de-comando-de-maquinas.php) ·
[Comando Painéis](https://comandopaineis.com.br/) ·
[Freelancer.com.br — projeto elétrico](https://freelancer.com.br/freelancers/s/projeto-el%C3%A9trico) ·
[Referência de hora de projetista](https://www.auditorioibirapuera.com.br/quanto-ganha-um-projetista-por-hora/)

---

## Rodada 3 — 29/07/2026

**Lacunas atacadas:** como o mercado maduro empacota e comunica prazo · quem publica prazo garantido.

### Dois modelos coexistem lá fora, e são mercados diferentes

| Modelo | Quem | Como vende | Preço |
|---|---|---|---|
| **Offshore de desenho** | [Outsource2India](https://www.outsource2india.com/engineering/electrical/electrical-schematic-drawing-services.asp), [Flatworld](https://www.flatworldsolutions.com/electrical-engineering/electrical-2d-drafting-services.php), [IndiaCADworks](https://www.indiacadworks.com/electrical/schematic-drawings.php), [CHCADD](https://www.chcaddoutsourcing.com/services/electrical-cad-drafting-drawing-services.html), [GSourceData](https://www.gsourcedata.com/mepf-design-services/electrical-drawing/) | Volume, hora barata, promessa de rapidez | **a partir de US$ 9/hora** |
| **Engenharia de painel** | [PanelTEK](https://www.paneltekllc.com/electrical-engineering-services/plc-control-panel-documentation/), [DMC](https://www.dmcinfo.com/services/manufacturing-automation-and-intelligence/control-panel-design/), [Gibson](https://www.gibsonengineering.com/support/gibson-panel-shop-page), [iAutomation](https://iautomation.com/panel-building-assembly/), [The Industrial Controls Co](https://www.theindustrialcontrolsco.com/engineering/control-panel-design/) | Documentação completa de painel, do primeiro rascunho ao as-built | Preço fechado **ou** hora, conforme o escopo |

O primeiro grupo compete por preço de hora e some. O segundo é o espelho do que a Borin quer ser —
e nenhum deles publica valor.

### Prazo: existe quem garanta, e o mecanismo é inteligente

O achado mais aproveitável da rodada. Um provedor anuncia **primeiro rascunho em 48 horas**, com o
projeto completo levando de **2 a 6 semanas** conforme escopo.

O truque é separar as duas promessas. **Garantir o rascunho é barato e vende muito**, porque o
cliente ansioso quer sinal de vida, não o pacote fechado. Garantir o pacote inteiro num prazo curto é
o que quebra a perna de quem promete.

**Aplicável direto na Borin, e resolve o risco da condição de abertura:** em vez de prometer metade
do prazo do concorrente para tudo, prometer **primeira emissão parcial em prazo curto e garantido** —
capa, memorial, potência e arquitetura de CLP — e o pacote completo na data fechada. O cliente vê
andamento em dias, e o prazo total continua realista mesmo sendo produzido à noite.

### A lista de entregáveis do mercado é mais curta que a da Borin

O que esses provedores listam como documentação de painel: **captura do esquema, layout do painel,
numeração de fios, régua de bornes e BOM**. Alguns acrescentam documentação de manufatura e registro
fotográfico da montagem.

Comparando com o pacote da Borin: falta neles **design térmico, arquitetura de CLP como planilha,
identificações prontas para impressão e plano de instalação com horas**. O manifesto de entrega do
site já é mais completo do que o padrão de mercado internacional — vale usar isso na proposta em vez
de tratar como óbvio.

### Qualidade é vendida como processo, não como adjetivo

Todos falam em "verificação rigorosa contra normas internacionais". É genérico e ninguém mostra o
método. **Publicar a lista de doze blocos de conferência, como o site já faz, é mais concreto do que
o que o mercado internacional comunica.**

### Onde há freelance de painel

A [Cad Crowd](https://www.cadcrowd.com/hire/control-panel-design) mantém um diretório de projetistas
de painel de controle — canal que não existe no Brasil com essa especificidade. Vale acompanhar como
referência de como o serviço é descrito e precificado quando é vendido por pessoa física.

Também apareceu a [EPLAN Center](https://eplancenter.com/eplan-engineering-services/), que vende
serviços de engenharia sobre a plataforma. É o concorrente conceitualmente mais próximo do modelo da
Borin lá fora.

**Fontes:** [Outsource2India](https://www.outsource2india.com/engineering/electrical/electrical-schematic-drawing-services.asp) ·
[Flatworld Solutions](https://www.flatworldsolutions.com/electrical-engineering/electrical-2d-drafting-services.php) ·
[IndiaCADworks](https://www.indiacadworks.com/electrical/schematic-drawings.php) ·
[CAD/CAM Services](https://www.cadcam.org/engineering/electrical-drawings) ·
[PanelTEK](https://www.paneltekllc.com/electrical-engineering-services/plc-control-panel-documentation/) ·
[DMC](https://www.dmcinfo.com/services/manufacturing-automation-and-intelligence/control-panel-design/) ·
[Cad Crowd](https://www.cadcrowd.com/hire/control-panel-design) ·
[CAD Drafter — custos](https://caddrafter.us/how-much-do-cad-drafting-services-cost/)
