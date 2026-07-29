# Tarefas

## Trava tudo — fazer primeiro

- [ ] **Registrar `borinprojetos.com.br`** no registro.br — R$ 40/ano. Continuava livre em 28/07/2026. Trava o site e o email
- [ ] Criar email profissional no Zoho (gratuito): `mateus@` e `contato@borinprojetos.com.br` — passo a passo em `site/LEIA-ME.md`
- [ ] Publicar o site: `npx wrangler pages deploy site --project-name borin`
- [ ] Conversar com contador: MEI, ME ou autônomo, CNAE da atividade, como emitir nota
- [ ] Resolver a questão de conflito de interesse com a FlowSistem antes de prospectar

## Site

- [x] Landing page com a identidade aplicada (`site/index.html`)
- [ ] Preencher o número de WhatsApp no `site/_pagina.html` e remontar
- [ ] Reler os textos e ajustar o que não soar como você
- [ ] Cadastrar no Google Search Console depois de publicar
- [ ] Perfil no LinkedIn apontando pro site

## Marca

- [x] Definir nome — **Borin Projetos Elétricos**
- [x] Identidade visual: logo, carimbo, paleta, tipografia (`marca/design-guide.md`)
- [ ] Instalar a fonte Inter na máquina — rsms.me/inter
- [ ] Converter os SVGs do logo em curvas antes de mandar pra gráfica
- [ ] Conferir a marca na base do INPI antes de registrar
- [ ] Checar o @ disponível no Instagram

## Entrega

- [x] Padrão de entrega — Escopos A e B (`padroes/padrao-entrega.md`)
- [x] Checklist de conferência (`padroes/checklist-conferencia.md`)
- [x] Calibrar o padrão com um projeto real (04003478 — Painel de Interface)

### Templates próprios — não dá pra usar os da FlowSistem

**Planilhas — feitas** (`padroes/templates/xlsx/`, geradas por `gerar-planilhas.py`)

- [x] Lista de materiais
- [x] Arquitetura de CLP, com resumo automático de pontos
- [x] Design térmico, com cálculo de superfície, ΔT e veredito de ventilação
- [x] Seis planilhas de identificações, com aba de instrução de impressão
- [x] Lista de instalação, com base de cabos, acompanhamento por horas e acessórios
- [ ] Preencher a base de dissipação a partir dos catálogos dos fabricantes
- [ ] Preencher a aba Impressão com impressora e modelo de etiqueta
- [ ] Conferir se a exportação do EPLAN cai direto nessas colunas

**EPLAN — precisa estar no PC**

- [ ] Template de folha com o carimbo da Borin (usar `marca/png/borin-carimbo.png`)
- [ ] Template de capa com a tabela *Descrição do Quadro* e a tabela de revisões
- [ ] Template de memorial descritivo com os seis blocos
- [ ] Folha de simbologia própria
- [ ] Banco de artigos próprio

## Comercial

- [x] Fluxo comercial do contato ao pagamento (`comercial/fluxo-comercial.md`)
- [x] Modelo de proposta (`comercial/modelo-proposta.md`)
- [x] Modelo de contrato (`comercial/modelo-contrato.md`)
- [ ] Revisar o contrato com advogado antes de assinar o primeiro
- [ ] Cronometrar horas dos próximos projetos pra fechar a precificação
- [ ] Preencher `comercial/precificacao.md` com os números reais
- [ ] Montar a proposta em PDF com a identidade aplicada
- [ ] Levantar lista de integradoras e fabricantes de máquina da Serra pra prospectar

## MCPs pra instalar depois

Nenhuma das ferramentas que você usa hoje (EPLAN, Excel) tem conector pronto — são locais e o Claude
já lê e escreve os arquivos direto.

- [ ] Playwright — renderiza HTML em PNG/PDF. Útil pra gerar proposta e apresentação com a identidade: `npx playwright install chromium`
- [ ] Gmail — ler e escrever email de cliente sem sair do Claude: `claude mcp add gmail -- npx -y @gongrzhe/server-gmail-autoauth-mcp`
