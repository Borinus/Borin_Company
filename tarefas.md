# Tarefas

## Trava tudo — fazer primeiro

- [ ] Registrar `borinprojetos.com.br` no registro.br — R$ 40/ano. Sem domínio não existe email da empresa
- [ ] Criar email profissional (Zoho gratuito): `mateus@` e `contato@borinprojetos.com.br`
- [ ] Conversar com contador: MEI, ME ou autônomo, CNAE da atividade, como emitir nota
- [ ] Resolver a questão de conflito de interesse com a FlowSistem antes de prospectar

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

### Construir os próprios templates — não dá pra usar os da FlowSistem

- [ ] Template de folha do EPLAN com o carimbo da Borin
- [ ] Template de capa com a tabela *Descrição do Quadro* e a tabela de revisões
- [ ] Template de memorial descritivo com os seis blocos
- [ ] Folha de simbologia própria
- [ ] Planilha modelo de lista de materiais
- [ ] Planilha modelo de arquitetura de CLP
- [ ] Planilha modelo de design térmico, com a base de dissipação por componente
- [ ] Seis planilhas modelo de identificações, com as abas de instrução de impressão
- [ ] Planilha ou macro própria de lista de instalação, com a aba de acompanhamento e horas
- [ ] Banco de artigos próprio no EPLAN

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
