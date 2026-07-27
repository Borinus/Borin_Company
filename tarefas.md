# Tarefas

## Estruturar o negócio

- [ ] Definir nome do negócio
- [ ] Criar identidade visual (logo, paleta, aplicação) — direção: minimalista, monocromática
- [ ] Escrever `padroes/padrao-entrega.md` — o que todo projeto entrega
- [ ] Escrever `padroes/checklist-conferencia.md` — o que conferir antes de entregar
- [ ] Preencher `comercial/precificacao.md` — modelo de cobrança e valores
- [ ] Criar modelo de proposta
- [ ] Criar modelo de contrato de prestação de serviço
- [ ] Definir fluxo comercial: do primeiro contato ao pagamento

## Sistema

- [ ] Rodar `/mapear` pra criar as primeiras skills personalizadas
- [ ] Rodar `/syncar` pra conectar o workspace ao GitHub

## MCPs pra instalar depois

Nenhuma das ferramentas que você usa hoje (EPLAN, Excel) tem conector pronto — são locais e o Claude
já lê/escreve os arquivos direto. Opções que podem fazer sentido conforme o negócio andar:

- [ ] Playwright — renderiza HTML em PNG/PDF. Útil pra gerar proposta e apresentação com visual próprio: `npx playwright install chromium`
- [ ] Gmail — ler e escrever email de cliente sem sair do Claude: `claude mcp add gmail -- npx -y @gongrzhe/server-gmail-autoauth-mcp`
- [ ] Google Drive / Google Sheets — se em algum momento o material de cliente for morar na nuvem
