# Borin Projetos Elétricos — Claude Code OS

## O que é esse workspace

Workspace da **Borin Projetos Elétricos**, negócio próprio do Mateus Borin: prestação de serviço de
projeto elétrico industrial ponta a ponta (freelancer, solo). Aqui ficam os clientes, os projetos, o lado comercial
(proposta, contrato, preço), o padrão de entrega e a identidade da marca.

**Estrutura de pastas:**
- `_contexto/` — memória do sistema (não apagar)
- `clientes/` — uma pasta por cliente, com os projetos daquele cliente dentro
  - `_modelo-cliente/` — modelo pra copiar quando entrar cliente novo
- `comercial/` — propostas, contratos e precificação
- `padroes/` — padrão de entrega: checklists, normas, o que vai em cada projeto
- `marca/` — identidade visual (`design-guide.md`) e arquivos de logo
- `dados/` — arquivos pra analisar (PDF, planilha, print)
- `tarefas.md` — lista de tarefas corrente
- `templates/skills/` — templates de skills prontos pra personalizar com /mapear
- `templates/ferramentas/catalogo.md` — APIs e ferramentas disponíveis pra usar em skills

## Sobre o negócio

Mateus Borin presta serviço de projeto elétrico industrial por conta própria, sob a marca
**Borin Projetos Elétricos**. Trabalha hoje como terceiro na FlowSistem (Caxias do Sul/RS, fabricante de sistemas de pintura
industrial — dosagem e aplicação de fluidos), onde é o projetista elétrico único e implanta o padrão
CAD elétrico da empresa. O negócio próprio está na fase de estruturação: identidade, padrão de entrega,
preço e fluxo comercial.

**Importante para qualquer texto que saia daqui:** Mateus é **projetista**, não engenheiro
eletricista (cursa Engenharia Civil). O serviço que ele vende não exige ART. Nunca usar a palavra
"Engenharia" no nome, na assinatura ou em material de cliente — é termo com registro no CREA.
Posicionar sempre como projeto e documentação técnica.

## O que mais fazemos aqui

- Projeto elétrico industrial completo, do início ao fim (CAD elétrico)
- Diagramas elétricos, listas de materiais, listas de tags e I/Os
- Padronização de projeto: folhas, macros, potenciais, banco de artigos
- Conferência e revisão de projeto (tags, cabos, folhas, nomenclatura)
- Planilhas técnicas de apoio (materiais, estoque, consumo de fontes)
- Lado comercial: proposta, contrato, precificação, apresentação
- **Futuro:** programação de CLP como serviço (hoje em aprendizado — LOGO! Soft Comfort / Siemens)

## Clientes e contexto

Atende clientes externos. Público-alvo ainda em aberto: integradores e fabricantes de máquina,
indústria direta ou escritórios de engenharia. Primeiros clientes devem vir por indicação de contatos.
Trabalha solo — não há equipe, sócio ou terceirizado.

Experiência de domínio: pintura industrial (Promix/Graco, Viscon, HotSpray, aplicação eletrostática,
pintura robotizada), painéis de controle, automação industrial. Clientes já atendidos via empresa:
John Deere, Meritor.

## Tom de voz

**Comigo (conversa interna):** direto e técnico. Sem explicação básica, sem rodeio, sem repetir o que
já foi dito. Português brasileiro. O Mateus digita rápido e com erros de ortografia — interpretar a
intenção, não a letra.

**Pro cliente (proposta, email, contrato, apresentação):** texto corrido e profissional, não tópicos
soltos. Frase completa, tom sério mas não empolado. É o rosto do negócio pra fora.

Evitar em qualquer texto: entusiasmo artificial, jargão de marketing, emoji em documento técnico.

## Ferramentas conectadas

- CAD elétrico (nível avançado)
- Excel
- Claude Code
- Python e Node.js (usa em automações pontuais)
- LOGO! Soft Comfort V8 / Siemens LOGO! 8 (aprendizado de CLP)
- Nenhum MCP instalado até agora

---

## Como este workspace é organizado (Claude Code e Codex)

- **Instruções:** `AGENTS.md` é a fonte (este arquivo). `CLAUDE.md` tem só `@AGENTS.md`. Nunca escrever conteúdo no `CLAUDE.md`.
- **Skills:** em `.claude/skills/<nome>/SKILL.md`. Pro Codex enxergar, existe `.agents/skills` apontando pra `.claude/skills` (criado pelo `/setup`, não vai pro git). Nesta máquina a ponte é junction, então skill nova aparece sozinha.

---

## Contexto do negócio

No início de toda conversa, ler os seguintes arquivos (se existirem e estiverem configurados):

1. `_contexto/empresa.md` — quem é o usuário, o que faz, como funciona o negócio
2. `_contexto/preferencias.md` — tom de voz, estilo de escrita, o que evitar
3. `_contexto/estrategia.md` — foco atual, prioridades, o que pode esperar
4. `_contexto/agora.md` — contexto vivo: onde paramos, decisões recentes, pendências (atualizado a cada sessão)

Usar essas informações como base pra qualquer resposta ou decisão. Ao sugerir prioridades, formatos ou abordagens, considerar o foco atual descrito em `estrategia.md`.

Para qualquer tarefa visual (carrossel, proposta, slide, landing page), consultar `marca/design-guide.md` como referência de estilo.

Não é necessário listar o que foi lido nem confirmar a leitura. Apenas usar o contexto naturalmente.

---

## Regras do sistema

- Cada cliente tem sua pasta em `clientes/[nome-cliente]/`, com os projetos dele em `clientes/[nome-cliente]/projetos/[nome-projeto]/`
- Cliente novo: copiar `clientes/_modelo-cliente/` e renomear
- Proposta fechada e contrato assinado ficam na pasta do cliente; modelos e versões em rascunho ficam em `comercial/`
- Antes de definir escopo ou entregável de um projeto, consultar `padroes/` — é lá que mora o padrão de entrega
- Chave de API ou token vai sempre no `.env`, nunca em arquivo versionado

---

## Fluxo de trabalho

Antes de executar qualquer tarefa, verificar se existe uma skill relevante em `.claude/skills/` (Claude Code) ou `.agents/skills/` (Codex).
Se encontrar, seguir as instruções da skill.
Se não encontrar, executar a tarefa normalmente.

Ao concluir uma tarefa que não tinha skill mas parece repetível (o usuário provavelmente vai pedir de novo no futuro), perguntar:

> "Isso pode virar uma skill pra próxima vez. Quer que eu crie?"

Não perguntar pra tarefas pontuais ou perguntas simples. Só quando o padrão de repetição for claro.

---

## Aprender com correções

Quando o usuário corrigir algo, melhorar uma resposta ou dar uma instrução que parece permanente (frases como "na verdade é assim", "não faça mais isso", "prefiro assim", "sempre que...", "evita...", "da próxima vez..."), perguntar:

> "Quer que eu salve isso pra não precisar repetir?"

Se sim, identificar onde faz mais sentido salvar:

- **Sobre o negócio** (quem são os clientes, como funciona a empresa, serviços, mercado) → adicionar em `_contexto/empresa.md`
- **Sobre preferências e estilo** (tom de voz, formato de resposta, o que evitar, como estruturar textos) → adicionar em `_contexto/preferencias.md`
- **Sobre prioridades e foco atual** (projetos em andamento, metas do momento, prazos importantes, o que é prioridade agora) → adicionar em `_contexto/estrategia.md`
- **Regra de comportamento nessa pasta** (onde salvar arquivos, como nomear, fluxos específicos) → adicionar no próprio `AGENTS.md`

Salvar com uma linha nova clara, sem reformatar o arquivo inteiro. Confirmar o que foi salvo mostrando a linha adicionada.

Não perguntar se a correção for óbvia de contexto imediato (ex: "na verdade o arquivo se chama X"). Só perguntar quando a informação tiver valor duradouro.

---

## Manter contexto atualizado

Ao terminar uma tarefa que mudou algo relevante no projeto (novo cliente, nova skill, mudança de foco, novo processo, ferramenta instalada, estrutura de pastas alterada), perguntar:

> "Isso mudou algo no teu contexto. Quer que eu atualize os arquivos de memória?"

Se sim, identificar o que precisa atualizar:

- **Novo cliente, serviço, ferramenta, equipe** → `_contexto/empresa.md`
- **Mudança de prioridade ou foco** → `_contexto/estrategia.md`
- **Correção de tom ou estilo** → `_contexto/preferencias.md`
- **Nova pasta, regra de organização, skill criada** → `AGENTS.md`
- **Mudança visual (cores, fontes, logo)** → `marca/design-guide.md`

Mostrar o que vai mudar antes de salvar. Não reformatar o arquivo inteiro, só adicionar ou editar a linha relevante.

**Quando NÃO perguntar:**
- Tarefas pontuais que não mudam o contexto (ex: escrever um email, criar um post avulso)
- Perguntas simples ou conversas sem ação
- Mudanças que já foram salvas pelo bloco "Aprender com correções"

**Dica:** se o usuário não sabe se algo mudou, rodar `/atualizar` faz uma varredura completa.

---

## Criação de skills

Quando o usuário pedir pra criar uma nova skill:

1. Verificar se existe um template relevante em `templates/skills/`. Se existir, usar como base e adaptar pro contexto do usuário
2. Perguntar: "Essa skill é específica pra esse projeto ou vai ser útil em qualquer projeto?"
   - Específica desse negócio → salvar em `.claude/skills/nome-da-skill/SKILL.md` (local)
   - Útil em qualquer projeto → salvar em `~/.claude/skills/nome-da-skill/SKILL.md` (global)
3. Ler `_contexto/empresa.md` e `_contexto/preferencias.md` pra calibrar o conteúdo da skill ao contexto do negócio
4. Se a skill precisar de arquivos de apoio (templates, referências, exemplos), criar dentro da pasta da skill
5. Seguir o fluxo da skill-creator nativa do Claude Code
