# Ligar o WhatsApp automático — passo a passo

O código já está pronto e no ar, **desligado**. Ele acorda sozinho no instante
em que as duas chaves existirem: não precisa publicar nada depois.

Este guia é pra você seguir clicando. Vai levar uma tarde de trabalho e alguns
dias de espera da Meta no meio. Faça na ordem — o passo 5 depende do 4.

**Estado de hoje:**

```
Chip ativado (Vivo)          +55 54 99951-7183   ✓ 3 de agosto de 2026
Frase do webhook             borin-zinco-motor-tampa-5621   ✓ já no servidor
ID do número de telefone     ____________________  ← falta
Token do usuário do sistema  ____________________  ← falta
```

Este é o número que vai **mandar** as confirmações. O teu número de sempre
(54 99664-2003) continua intacto no celular, e é nele que a conversa acontece:
quando o cliente responde, o aviso cai no email com um link pra você responder
do teu WhatsApp normal.

---

## Passo 0 — Comprar um chip pré-pago

Um chip novo, de qualquer operadora. Vivo, Claro ou TIM, tanto faz.

**Compre em lotérica, banca de jornal, supermercado ou farmácia: uns R$ 10.**
São revendas autorizadas, sai na hora e é o mesmo chip.

Pelo site das operadoras sai bem mais caro — a Claro, por exemplo, vende por
R$ 30, mas isso é um **plano com 21GB de internet**, não o chip. Este número não
vai navegar: ele recebe um SMS de verificação e depois fica parado. Pagar por
internet aqui é jogar dinheiro fora, e ainda espera dias de entrega.

**Por que não dá pra usar o teu número atual:** ao registrar um número na API do
WhatsApp, ele **sai do aplicativo do celular**. Você perderia a conversa manual
no teu número comercial, que é justamente onde teus clientes te chamam hoje.

**Por que não um número virtual:** a Meta recusa quase todo número de VoIP na
verificação. Você gastaria a tarde pra descobrir isso no fim.

O que fazer:

1. Comprar o chip e ativar (precisa do teu CPF, é na hora)
2. Colocar em qualquer celular — pode ser o segundo slot do teu
3. **Não instalar WhatsApp nesse número.** Se instalar, vai ter que desinstalar
   e apagar a conta antes de seguir
4. Anotar o número com DDD

Depois de tudo pronto, o chip pode ficar numa gaveta — mas **não pode morrer**.

Pré-pago não tem mensalidade: você só paga se recarregar. Só que operadora
cancela linha parada. Sem recarga, ela bloqueia por volta de 90 dias e cancela
por volta de 180 — e aí o número volta pro estoque e vai pra outra pessoa.

Como esse número fica registrado na Meta e é o que o cliente vê no WhatsApp,
perdê-lo dá trabalho de verdade: teria que refazer o registro com outro número.

**Uma recarga mínima a cada 3 meses, uns R$ 15 cada — R$ 60 por ano.** O jeito
de não esquecer é ativar a recarga automática da operadora no cartão. Prazo
exato varia por operadora; confirme o da tua na hora de comprar.

---

## Passo 1 — Criar a conta de negócio na Meta

1. Abrir **business.facebook.com**
2. Entrar com teu Facebook pessoal (a Meta exige; ele não fica visível pro
   cliente)
3. **Criar conta** → preencher:
   - Nome da empresa: `Borin Projetos Elétricos`
   - Teu nome
   - Email comercial: `contato@borinprojetos.com.br`
4. Confirmar o email que chega

> Atenção ao nome: **nunca** "Borin Engenharia". Engenharia é termo com registro
> no CREA e você é projetista. "Borin Projetos Elétricos" é o nome certo e é o
> que aparece pro cliente no WhatsApp.

---

## Passo 2 — Criar o app

1. Abrir **developers.facebook.com** → **Meus apps** → **Criar app**
2. Tipo: **Empresa** (ou "Negócios", depende da tradução do dia)
3. Nome do app: `Borin Site` — esse nome é interno, o cliente não vê
4. Vincular à conta de negócio que você criou no passo 1
5. Dentro do app, procurar **WhatsApp** na lista de produtos → **Configurar**

Nesse ponto a Meta cria um número de teste automático. Ele serve pra testar com
até 5 números que você cadastrar, e só. Não é o número que vai valer.

---

## Passo 3 — Registrar o teu número

Ainda em WhatsApp → **Configuração da API**:

1. No campo do número remetente, **Adicionar número de telefone**
2. Preencher o perfil do negócio:
   - Nome de exibição: `Borin Projetos Elétricos`
   - Categoria: `Serviços profissionais`
   - Descrição: `Projeto elétrico industrial`
3. Informar o número do chip novo, com DDD
4. Escolher verificação por **SMS**
5. Digitar o código que chega no celular

**Anotar agora:** logo abaixo do número aparece o **ID do número de telefone**.
É um código de uns 15 dígitos, e **não** é o número em si. É a primeira das duas
coisas que eu preciso.

---

## Passo 4 — Verificar a empresa

Sem isso, o número fica preso a 250 conversas por dia e só para números de
teste. Dá pra testar, não dá pra usar de verdade.

1. **business.facebook.com** → Configurações (engrenagem)
2. **Central de Segurança** → **Verificação da empresa** → Iniciar
3. Preencher com os dados do CNPJ:
   - CNPJ: `65.749.097/0001-85`
   - Razão social: exatamente como está no cartão CNPJ
   - Endereço: o do cartão CNPJ
   - Telefone e site: `borinprojetos.com.br`
4. Anexar o **cartão CNPJ** (baixa no site da Receita, é grátis)
5. Enviar

**A resposta leva de 2 a 10 dias.** Chega por email. Enquanto espera, faça os
passos 5 e 6 — eles não dependem disso.

Se recusarem, quase sempre é divergência entre o nome que você digitou e o que
está no cartão CNPJ. Corrige e reenvia.

---

## Passo 5 — Cadastrar a mensagem

O WhatsApp não deixa mandar texto livre quando é **você** que começa a conversa
— e é o caso, porque o cliente preencheu um formulário no site em vez de te
mandar mensagem. Só sai como modelo aprovado.

1. **business.facebook.com** → **WhatsApp Manager** → **Modelos de mensagem**
2. **Criar modelo**
3. Preencher exatamente assim:

```
Nome        pedido_recebido
Categoria   Utilidade
Idioma      Português (BR)
```

4. No corpo da mensagem, colar:

```
Olá {{1}}, recebi seu pedido de orçamento para {{2}}. Respondo com valor e prazo em até 24 horas. Você acompanha em borinprojetos.com.br/conta.
```

5. A Meta vai pedir um exemplo pra cada campo. Preencher:
   - `{{1}}` → `Carlos`
   - `{{2}}` → `painel de comando da estufa`
6. Enviar pra análise

**Categoria Utilidade, nunca Marketing.** Utilidade aprova em poucas horas,
custa menos e não deixa o cliente marcar como propaganda. Marketing é analisado
com rigor e pode ser bloqueado pelo cliente.

Se recusarem, a Meta diz o motivo — me manda que eu reescrevo o texto.

---

## Passo 6 — Gerar o token que não expira

O token que aparece na tela do app **dura 24 horas** e não serve pra nada aqui.
O que serve é o de usuário do sistema:

1. **business.facebook.com** → Configurações → **Usuários do sistema**
2. **Adicionar** → nome: `site` → papel: **Administrador**
3. Selecionar ele → **Atribuir ativos** → escolher o app `Borin Site` →
   marcar **Controle total**
4. **Gerar novo token**:
   - App: `Borin Site`
   - Validade: **Nunca expira**
   - Permissões: marcar `whatsapp_business_messaging` **e**
     `whatsapp_business_management`
5. **Copiar o token na hora.** Ele não aparece de novo — se perder, gera outro.

**Anotar:** essa é a segunda coisa que eu preciso.

---

## Passo 7 — Ligar o retorno das respostas

Sem este passo, o cliente que **responder** a confirmação escreve pra um número
que não está em celular nenhum: a mensagem chega na API e morre ali. Ele fica
falando sozinho e você nunca fica sabendo — pior que não ter mandado nada.

Já está pronto e testado. Falta apontar a Meta pra ele:

1. No app, em **WhatsApp → Configuração** → seção **Webhook** → **Editar**
2. URL de callback: `https://borinprojetos.com.br/api/zap`
3. Token de verificação: invente uma frase qualquer e **anote** — é a terceira
   coisa que eu preciso. Exemplo: `borin-2026-abelha-torta`
4. **Verificar e salvar** — a Meta chama a URL na hora; se der erro, o token
   digitado aqui não bate com o que está no Worker
5. Em **Campos do webhook**, assinar **messages**

A partir daí, toda resposta do cliente vira email pra `contato@borinprojetos.com.br`
em segundos, com o nome, o número e o texto — e um link pra você responder do teu
WhatsApp de sempre. A conversa continua no teu número normal; o número da API
serve só pra avisar.

## Passo 8 — Me mandar

Três valores:

```
ID do número de telefone:  1234567890123456
Token:                     EAAG...
Token de verificação:      a frase que você inventou no passo 7
```

Eu coloco como segredo do Worker (nunca em arquivo do git) e testo mandando pro
teu número pessoal antes de valer pra cliente.

Se preferir colocar você mesmo, na pasta `site/worker`:

```
npx wrangler secret put ZAP_TOKEN
npx wrangler secret put ZAP_NUMERO_ID
npx wrangler secret put ZAP_VERIFY
```

---

## Quanto custa

| O quê | Quanto | Quando |
|---|---|---|
| Chip pré-pago | ~R$ 15 | uma vez |
| Manter o número vivo | ~R$ 15 | a cada 3 meses (~R$ 60/ano) |
| Mensagem de confirmação | centavos cada | por orçamento pedido com WhatsApp |
| Plataforma da Meta | R$ 0 | não tem mensalidade |

Não existe mensalidade obrigatória em lugar nenhum. A recarga trimestral não é
cobrança da operadora — é você mantendo a linha ativa pra ela não ser reciclada.

**Sobre a franquia grátis, pra não criar expectativa errada:** a Meta dá um
número de conversas grátis por mês, mas ela vale pra conversa que o **cliente**
começa — ele te manda mensagem primeiro. O nosso caso é o contrário: o cliente
preencheu um formulário no site e quem começa a conversa somos nós, com modelo
aprovado. Isso é cobrado.

A categoria Utilidade é a mais barata que existe, na casa de centavos por
mensagem. No teu volume — um punhado de orçamentos por semana — dá poucos reais
por mês. Vale a pena, mas não é zero.

A Meta mexe nessa tabela com frequência. Confira a página de preços dela na hora
de ligar, e configure um limite de gasto na conta de anúncios pra não haver
surpresa.

---

## Como conferir que funcionou

Pedir um orçamento pelo site marcando **"email e WhatsApp"**. Duas coisas têm
que acontecer:

1. A mensagem chega no número que você informou
2. A resposta do servidor traz `"zap": true`

Se vier `"zap": false`, o motivo está no log do Worker. Rodar na pasta
`site/worker`:

```
npx wrangler tail
```

Os dois erros mais comuns:

- **131026** — o número informado não tem WhatsApp
- **132001** — o modelo não existe ou ainda não foi aprovado

---

## Referência técnica

Configuração, em segredo do Worker:

| Segredo | O que é | Padrão |
|---|---|---|
| `ZAP_TOKEN` | token do usuário do sistema | — (sem ele, desligado) |
| `ZAP_NUMERO_ID` | ID do número de telefone | — (sem ele, desligado) |
| `ZAP_VERIFY` | frase que valida o webhook | — (sem ela, o webhook recusa) |
| `ZAP_TEMPLATE` | nome do modelo | `pedido_recebido` |
| `ZAP_IDIOMA` | idioma do modelo | `pt_BR` |

Rotas:

| Rota | Método | O que faz |
|---|---|---|
| `/api/zap` | GET | aperto de mão da Meta ao cadastrar o webhook |
| `/api/zap` | POST | resposta do cliente → email pro Mateus |

O webhook responde **200 sempre**, mesmo com corpo estranho. A Meta repete o
que dá erro e, se insistir errando, desliga o webhook — perder uma resposta é
ruim, ficar sem canal nenhum é pior.

O que a resposta do pedido diz no campo `zap`:

| Valor | Significa |
|---|---|
| `null` | o cliente escolheu só email — não recebe WhatsApp, de propósito |
| `false` | pediu WhatsApp, mas o canal está desligado ou a Meta recusou |
| `true` | a mensagem saiu |

Só recebe WhatsApp quem **marcou WhatsApp** no formulário. Mandar pra quem
escolheu só email é mensagem não solicitada; na Meta isso vira denúncia, e
denúncia derruba a qualidade do número até ele parar de entregar.

O código está em `site/worker/zap.js`. Ele nunca derruba um pedido: se a Meta
estiver fora do ar, o email sai igual e o pedido é registrado do mesmo jeito.

## O que o cliente já recebe hoje, sem nada disso

Não é o vazio. O cliente recebe email de confirmação em segundos, o pedido
aparece na conta dele, e quando o freio recusa um pedido a tela mostra um botão
"Falar no WhatsApp agora" com o teu número. O WhatsApp automático é um ganho em
cima disso, não o único caminho.
