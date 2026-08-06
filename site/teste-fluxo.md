# Teste do fluxo inteiro — 2 de agosto de 2026

Rodado contra o site no ar (`borinprojetos.com.br`), com caixa de email de verdade
e navegador de verdade. Nenhum passo lê o banco por dentro para descobrir senha:
tudo que o cliente precisa saber é lido da caixa de entrada dele, como ele leria.

## Resultado

| Suíte | O que prova | Passos |
|---|---|---|
| `ciclo.py` | Um cliente do primeiro clique ao contrato assinável | 16/16 |
| `portas.py` | O que tem que estar trancado continua trancado | 16/16 |
| `equipe_teste.py` | Empresa, convite de funcionário e remoção de acesso | 14/14 |
| `pend_teste.py` | Conta pendente — o lead de outra pessoa não é queimado | 13/13 |
| `fichas.mjs` | `/padrao` e `/projeto` gravam na conta e voltam preenchidos | 11/11 |
| `tecla.mjs` | Enter envia formulário e faz login | 6/6 |
| `recusa.mjs` | Recusa do servidor não manda o cliente pra "recebido" | 3/3 |
| `equipe_ui.py` | A tela `/equipe`: dono libera, funcionário entra, dono remove | 25/25 |
| `tres.py` | Entrada da conta na home, orçamentos na conta, cores e predefinições | 18/18 |
| `volta.py` | O cliente que volta: conta já ativa pedindo orçamento de novo | 12/12 |
| `repro_login.py` | Vários pedidos com o mesmo email sem login | corrigido |
| `arquivos_teste.py` | Arquivos no R2: sobe, baixa, e o vizinho não vê | 15/15 |
| `arq_ui.py` | Os arquivos dentro do cartão do projeto, na tela | 15/15 |
| `proposta_conta.py` | A proposta e o contrato aparecem na conta | 13/13 |
| `conta_completa.py` | A conta com proposta, orçamento, projeto e equipe | 18/18 |
| `medir.mjs` | Celular de 390px, sem rolagem horizontal | ok |

**79 passos, todos verdes.**

Uma observação sobre repetir a bateria: o freio do formulário é de 12 pedidos por
IP por hora, e a bateria inteira gasta perto disso. Rodando tudo duas vezes
seguidas, a segunda leva 429 no primeiro passo — não é defeito do site, é o freio
funcionando. A janela abre uma hora depois do último pedido aceito. Proposta e
contrato saem pelo `/api/enviar` e não passam pelo freio, então dá pra conferir
essa parte a qualquer hora.

## O que estava errado

### 1. A área de arquivos não existe — só a metade de baixo foi feita

O balde R2 está criado, o vínculo `ARQUIVOS` está no `wrangler.toml` e o
`site/worker/arquivos.js` está escrito e correto. Mas o `index.js` **não importa
esse arquivo em lugar nenhum**, e não existe rota que chame qualquer função dele.

Efeito prático: não há como subir um arquivo nem baixar um. O código é morto em
produção.

Falta: ligar as rotas de arquivo no Worker e desenhar a aba de arquivos na conta.

**A parte de acesso disso já foi resolvida:** a tela de equipe também não
existia — funcionava só por API, ou seja, só por linha de comando. Agora existe
em `/equipe`, com link a partir de `/conta`, e está coberta por 25 passos de
teste com navegador e caixa de email de verdade. Uma correção saiu de lá: a
confirmação "a senha foi para…" usava o mesmo vermelho de erro do `.aviso.falta`,
e confirmação de sucesso em vermelho faz o dono achar que falhou e liberar a
mesma pessoa duas vezes. Agora tem estilo próprio (`.aviso.feito`, cinza com
visto).

### 2. O assunto do email escondia o que importava — corrigido

O assunto saía assim, com 102 caracteres:

```
#04003478 · Verificacao Ciclo Ltda — Painel de interface de sistema de pintura · Contrato PROP-2026-001
```

O Gmail corta por volta de 70 caracteres no computador e de 35 no celular. Como
"Proposta" e "Contrato" ficavam no fim, o cliente via **duas linhas idênticas** na
caixa de entrada e não sabia qual era o contrato sem abrir as duas.

Agora o tipo do documento vem na frente e o código vai pro fim, que é onde ele
serve — pra buscar, não pra ler:

```
Contrato PROP-2026-004 · Verificacao Ciclo Ltda — Painel de interface de sistema de pintura · #04003478
Proposta PROP-2026-004 · Verificacao Ciclo Ltda — Painel de interface de sistema de pintura · #04003478
```

Conferido na caixa do cliente depois da mudança, com os dois emails lado a lado.
Cortando em 35 caracteres, que é o que o celular mostra, sobra
`Contrato PROP-2026-004 · Verificaca…` contra `Proposta PROP-2026-004 · Verificaca…`:
dá pra separar sem abrir.

### 3. O pedido de orçamento não era guardado em lugar nenhum — corrigido

O formulário virava email pro Gmail do Mateus e acabava ali. Não existia nenhum
registro do pedido. Quem preencheu o formulário e entrou na conta duas semanas
depois via "nenhum projeto em andamento" — sem saber se o pedido tinha chegado,
o que tinha pedido, nem em que pé estava. Só restava perguntar no WhatsApp, que
é exatamente o que a conta existe pra evitar.

Agora todo pedido é registrado em `pedido:<empresa>:<data ISO>` e aparece na
conta em "Orçamentos que você pediu", com equipamento, código, data, prazo
pedido e estado. Dois detalhes que a implementação exigiu:

- A conta ainda não existe quando o pedido chega — é o pedido que a cria. Então
  o registro nasce com a chave no email e o `garantirEmpresa` move pra empresa
  quando ela nasce, junto com projeto e ficha. Sem essa linha, o histórico
  ficaria preso na chave antiga e a conta abriria vazia justamente no primeiro
  pedido, que é o único que o cliente já fez.
- Falhar ao registrar não pode derrubar o pedido. O email já saiu e o cliente já
  foi atendido: perder o histórico é ruim, perder o lead é pior.

### 4. A entrada da conta existia só numa linha do rodapé — corrigido

Quem já era cliente caía na home e tinha que rolar a página inteira pra achar
como entrar. Agora tem "Minha conta" no topo, a 24px do começo da página, e quem
já está logado vê "Meus projetos" apontando direto pra `/conta`.

### 5. As cores de cabo eram um campo de texto livre — corrigido

O cliente tinha que digitar `Fase R — preto` linha por linha, acertando o
travessão e o nome da cor. Quem preenche isso é eletricista no meio do dia,
muitas vezes no celular. Agora é uma linha por função (as três fases, neutro,
terra, comando CA, comando CC V+ e V−, e tensão externa) com a cor numa lista e
a amostra pintada do lado, pra conferir de relance.

Por baixo continua gerando o mesmo texto `Função — cor` num campo escondido:
resumo, WhatsApp, email, arquivo baixado e a ficha salva na conta não mudaram em
nada. Duas armadilhas tratadas:

- Cor de um preenchimento antigo que não está na paleta entra como opção
  própria. Sem isso o `select` cairia calado na primeira da lista e trocaria o
  padrão do cliente sem ele perceber.
- A ficha da conta chega por rede, depois da tela montada, e escrever em
  `.value` não dispara evento nenhum. O `_form.js` passou a emitir
  `formulario-aplicado`, e a tabela se remonta quando isso acontece — senão ela
  mostraria o padrão de fábrica com a ficha do cliente carregada por baixo.

### 6. Não havia como salvar o padrão como predefinição — corrigido

O `/padrao` salvava sozinho, mas sem nenhum ato explícito: não dava pra saber se
tinha ficado guardado. Agora tem "Salvar predefinições" no fim do formulário,
gravando nos dois lugares — no navegador (que faz o formulário de projeto vir
preenchido no mesmo aparelho) e na conta (que faz valer em qualquer aparelho e
nos projetos que ainda não tinham padrão). Sem login, avisa que ficou só no
navegador e o que fazer, em vez de dizer "erro".

### 7. Vários pedidos com o mesmo email trancavam o cliente pra fora — corrigido

Relatado pelo Mateus e reproduzido antes de qualquer mudança. Cada pedido novo
gerava uma senha nova e matava a anterior (é a proteção pra quando um estranho
digita o email de outra pessoa), mas nada dizia isso ao cliente. Os três emails
tinham o **mesmo assunto**:

```
pedido 1 → VJnunjmdzHJA   "Seu acesso — Borin Projetos Elétricos"
pedido 2 → ALDxyaAnq5yP   "Seu acesso — Borin Projetos Elétricos"
pedido 3 → 34yWHGJgxZag   "Seu acesso — Borin Projetos Elétricos"

senha 1 → 401 "email ou senha não conferem"
senha 2 → 401 "email ou senha não conferem"
senha 3 → 200

8 erros → 429 "muitas tentativas, 15 min" — e nem a senha certa passava
```

Quatro correções:

1. **A senha ficou simples de digitar:** `BORIN482913` no lugar de
   `HUzpXs5RTaab`. São seis dígitos e não quatro por conta do freio de login:
   quatro dígitos são 10 mil combinações e o freio solta 8 tentativas a cada 15
   minutos, o que abriria uma conta em menos de uma semana de tentativa
   automática. Seis dígitos são um milhão, e a mesma tentativa vai pra casa dos
   anos. O prefixo fixo não conta como segredo — serve pra reconhecer de onde
   veio e pra ditar por telefone.
2. **Senha de pedido anterior deixou de ser "senha errada".** O servidor guarda
   o hash das duas provisórias anteriores e responde *"essa senha era de um
   pedido anterior e já não vale, use a do email mais recente"* — e **não conta
   como tentativa**, porque quem digita uma senha que eu mandei recebeu um email
   de verdade, não está adivinhando. Era isso que trancava a conta.
3. **Assunto próprio no reenvio** ("Sua senha nova") e um aviso em vermelho
   dentro do email dizendo que substitui a anterior. Dois emails com o mesmo
   assunto são indistinguíveis na lista da caixa de entrada.
4. **Minúscula passa.** Quem digita `borin482913` no celular não errou a senha,
   errou o shift, e campo de senha não corrige sozinho. Vale só pra senha que o
   sistema gera; a que o cliente escolhe continua diferenciando maiúscula.

Também juntei os dois geradores de senha que existiam duplicados — um no
`acesso.js` e outro no `equipe.js`, com alfabetos diferentes. Mudar um não mudava
o outro, então a senha do lead e a do funcionário nunca eram iguais.

Depois de corrigido, o mesmo roteiro:

```
senha 1 e 2 → 401 com a explicação, sem contar tentativa
senha 3     → 200
9 tentativas com a senha antiga → NÃO trava; a senha certa entra logo depois
borin636055 em minúscula        → 200
chute de verdade                → trava na 9ª, como antes
```

Medido também o custo disso, porque cada senha antiga é uma derivação de PBKDF2
a mais e o Worker tem teto de CPU: pior caso (tudo falha) 851 ms e resposta
correta, sem erro de plataforma.

### 8. O cliente que volta não recebia nada — corrigido

Relatado pelo Mateus testando com o próprio email: *"fiz a solicitação, alterei
o email e não veio nem por WhatsApp nem por email"*. O pedido chegava normalmente
na caixa dele (conferido: três pedidos hoje, todos entregues em
`mateusborin73@gmail.com`). O que não chegava era a resposta ao **cliente**:

```js
if (antes && antes.estado === "ativa") return { estado: "ja_tinha" };
```

Conta ativa não ganha senha nova, e isso está certo — a senha é do cliente, o
sistema não deve trocar. Mas, sem senha pra mandar, a função saía sem mandar
**email nenhum**. Resultado: quem já tinha conta via a tela de "recebido" e
depois silêncio absoluto, sem saber se o pedido tinha chegado. Justamente o
cliente que volta, que é o melhor que existe.

Agora existe um email próprio pra esse caso — "Recebi seu pedido" — sem senha
nenhuma, apontando pra `/conta`, onde o pedido já aparece na lista.

Duas coisas que o teste também deixou claras e que não eram defeito:

- **O site não manda WhatsApp e nunca mandou.** O campo de canal só registra
  como o cliente prefere ser respondido; quem manda a mensagem é o Mateus. Os
  botões "Enviar pelo WhatsApp" das fichas abrem o WhatsApp com o texto pronto —
  não é envio automático. Confirmação automática por WhatsApp precisaria de uma
  API de WhatsApp, que não existe aqui.
- **O orçamento — valor e prazo — nunca sai do site.** É o Mateus que roda
  `comercial/orcamento.py`. O que o site manda sozinho é o acesso e, agora, a
  confirmação.

### 9. Os botões de rádio têm 13px

No celular os rádios de escolha de canal ficam com 13,3px. O mínimo recomendado
de alvo de toque é 24px. Os campos de texto estão certos (40 a 42px) e a página
não rola na horizontal. Já estava na lista da auditoria, continua pendente.

## O que estava errado no próprio teste

Três passos passavam sem provar nada. Vale registrar porque cada um escondia
exatamente aquilo que devia vigiar.

1. **`tecla.mjs` dava login por bom sem ninguém logado.** A comparação era
   `eu === (process.env.CAIXA || '')`. Rodando sem conta, virava `'' === ''`:
   verdadeiro. O passo de login era enfeite. Agora, sem conta, o teste falha e diz
   por quê — e o `com_conta.py` abre uma conta de verdade antes de chamar os `.mjs`
   que dependem de sessão.

2. **Os testes de admin batiam em `/api/admin/*`, que não existe.** As rotas de
   admin são as mesmas de `/api/acesso/*`; o que separa é o cabeçalho `Bearer`.
   Como `/api/admin/...` caía no 405 de método, todos respondiam "não autorizado"
   por acidente e a autenticação nunca era tocada. Agora batem nas rotas reais —
   `cliente`, `projeto`, `apagar`, `criar` — e o teste confirma os dois lados:
   401 sem o segredo, e a rota abrindo com ele no cabeçalho.

3. **O teste de injeção aceitava 429 como aprovado.** O limite de taxa respondia
   antes do Worker chegar a olhar os campos, e o passo dizia ok. Agora 429 é falha
   declarada: se o limite respondeu, o teste não provou nada.

Um quarto, já corrigido antes desta rodada: o extrator de senha exigia a senha
entre `>` e `<`, o que só existe na versão HTML do email. Quando o servidor de
teste devolvia a alternativa em texto puro, o teste dizia "senha não chegou" com o
email perfeitamente correto na caixa.

## Detalhe do que passou

**Segurança (`portas.py`)** — `/api/enviar` sem o segredo dá 401 e com o segredo
entrega; as quatro rotas de admin dão 401 sem o cabeçalho; segredo passado na URL
não vale (URL entra em log da Cloudflare, no histórico e no cabeçalho Referer);
sem cookie, `eu`, `equipe`, `ficha` e `projetos` não devolvem email nenhum; e a
validação de email e de WhatsApp é do servidor, não do navegador.

**Ciclo (`ciclo.py`)** — formulário enviado, senha chegando de
`site@borinprojetos.com.br` com os acentos intactos, login com a senha do email,
cadastro salvo, proposta com o contrato em PDF anexo, contrato preenchido pelo
cadastro sem nenhum `[campo]` sobrando, e o PDF baixado da caixa do cliente com
95 KB.

**Equipe (`equipe_teste.py`)** — o dono convida, o funcionário recebe a senha na
caixa dele e entra, vê a área da empresa e a ficha, e **não** consegue preencher
ficha nem liberar acesso. Removido, não entra mais.

**Conta pendente (`pend_teste.py`)** — quem digita o email de outra pessoa cria
uma conta *pendente*, não uma conta de verdade. O dono legítimo não é barrado:
recebe uma senha nova, a primeira deixa de valer, e a conta só vira ativa quando
ele troca a senha. Depois de ativa, pedido novo não troca mais a senha de ninguém.
