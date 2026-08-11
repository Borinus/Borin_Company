# Auditoria de UX — teste frio com três personas (11/08/2026)

> Método: telas reais do site no ar (mobile 390px e desktop 1366px) capturadas por
> navegador automatizado e entregues a três avaliadores SEM contexto nenhum do
> projeto: um dono de metalúrgica no celular, um projetista avaliando fornecedor
> pro chefe, e uma avaliação heurística de usabilidade. Ninguém sabia o que o
> site vendia antes de abrir a primeira tela.

## O que os três concordaram

1. **A tela pós-envio é o pior momento do site.** Quem cai no estado vazio do
   `/enviado` lê "Nada pra enviar aqui." depois de ter apertado Enviar — e o
   carimbo da mesma tela diz "Pedido enviado". O comprador declarou desistência
   exatamente aí. O estado vazio é alcançável de verdade: navegador embutido
   (Instagram/WhatsApp) chega nele após envio real quando o sessionStorage falha.
2. **Vitrine sem vidro:** o site fala a língua certa (normas, entregáveis,
   perguntas do /padrao — o técnico validou tudo), mas não MOSTRA nada: nenhuma
   folha de exemplo, nenhum caso, nenhuma linha sobre quem é o profissional.
   As duas personas de compra pediram isso como item nº 1.
3. **O cartão de login social atrapalha mais do que ajuda:** aparece inteiro nos
   3 passos do formulário (~300px antes do primeiro campo), com promessa que só
   vale no passo 3, botão "Microsoft" inconsistente com o "Continuar com o
   Google", e um vão branco no passo 1.
4. **Validação um-erro-por-vez e longe do campo** — ciclo de enviar → bronca →
   enviar → outra bronca.
5. **Placeholder do WhatsApp é o número real do negócio** — parece campo
   preenchido, e alguém pode copiá-lo achando que é formato.

## Corrigido em 11/08/2026 (mesmo dia)

| # | Achado | Correção |
|---|---|---|
| 1 | /enviado estado vazio hostil e contraditório | Texto reescrito (sem "Nada pra enviar aqui."), carimbo do estado vazio virou "Pedido de orçamento", botão unificado "Pedir orçamento" |
| 2 | Validação um-por-vez, longe do campo | `validar()` agora junta TODAS as pendências numa mensagem só, marca os campos e rola até o primeiro |
| 3 | Placeholder com número real | Trocado por formato genérico |
| 4 | Cartão social 3× + vão branco | Cartão só no passo 1; nos passos 2–3 vira uma linha "Já tem conta? Entrar"; botão "Continuar com a Microsoft" |
| 5 | "Continuar — falta pouco" no passo 1/3 | "Continuar" nos dois passos |
| 6 | Entrada de 40% só em microcopy | Cartão próprio em "O combinado": "Entrada de 40%, saldo na aprovação" |
| 7 | "Onze campos" (são ~13) | "Três passos, cinco minutos" |
| 8 | "12 blocos" sem tradução | Uma linha dizendo o que os blocos conferem |
| 9 | Legenda do quadrado vermelho nos 4 passos | Rótulo VOCÊ/EU direto em cada cartão |
| 10 | /entrar sem propósito + 2 explicações de senha | Linha de valor ("acompanhe o pedido, baixe proposta e contrato"), explicação única da senha, "não achei minha senha" logo sob o campo |
| 11 | "Acionamentos" parece obrigatório | Ganhou "(se souber)" como o I/O |
| 12 | "Some partidas..." ambíguo | "Conte tudo: partidas de motor + inversores + válvulas + resistências" |

## Em aberto — decisão do Mateus

- **Prova de trabalho** (o nº 1 das duas personas de compra): folhas de exemplo
  anonimizadas, caso com números ("painel de X I/O, N páginas, N dias"), uma
  linha sobre o profissional. Conteúdo técnico é do Mateus — montar juntos.
- **"Empresa" obrigatória** trava pessoa física (o servidor já NÃO exige;
  só o front exige). Tornar opcional?
- **Posicionamento do 50%**: as duas personas leram como "carteira vazia".
  Alternativas: tirar da home (fica só na proposta), ou reescrever como
  "condição de primeiro projeto".
- **Responsabilidade técnica (ART)** dita com todas as letras na home — o
  técnico chamou de quase eliminatório não achar.
- **Arquivo-fonte do CAD**: dizer no site que existe como opcional (já é
  acréscimo de 50% na calculadora; hoje o site não menciona).
- Comparação "mercado: 2/3/4 semanas" sem fonte; "design térmico" → o técnico
  sugeriu "dissipação térmica"; /padrao com exemplo preenchido; cor padrão do
  comando CC (apontada pela persona técnica) — **tudo conteúdo do Mateus**.
- Senha por email como prática (mudança maior de fluxo — login social já cobre).
