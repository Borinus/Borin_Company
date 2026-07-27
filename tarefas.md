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
- [ ] Calibrar o padrão com um projeto real já entregue — colocar o exemplo em `dados/`
- [ ] Montar o template de capa, memorial e índice no EPLAN, com o carimbo da marca
- [ ] Montar os templates das planilhas: material, identificações, I/Os, dimensionamento térmico

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
