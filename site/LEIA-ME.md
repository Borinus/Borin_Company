# Site

Landing page da Borin. Autocontida: não busca fonte, script nem imagem de lugar nenhum — a Inter vai
embutida em base64, com subset de 70 KB para os quatro pesos. Abre por `file://`, sobe em qualquer
hospedagem e funciona offline.

## Como mexer

O arquivo que você edita é o `_pagina.html`. O `index.html` é **gerado** — não edite ele direto,
porque a próxima montagem sobrescreve.

```
python site/gerar-fontes.py    # 1. subset da Inter -> fontes.css  (só precisa rodar de novo se mudar a fonte)
python site/montar.py          # 2. injeta as fontes -> index.html
```

## Antes de publicar — o que falta preencher

- [ ] **WhatsApp**: trocar `+55 (54) 0 0000-0000` e o link `wa.me/55SEUNUMERO` pelo teu número real
- [ ] **Email**: `contato@borinprojetos.com.br` só funciona depois do passo de email abaixo
- [ ] Reler os textos e ajustar o que não soar como você

**O que não tem no site, de propósito:** depoimento de cliente, logo de empresa atendida, número de
projetos entregues. Nada disso existe ainda sob a marca Borin, e inventar é o tipo de coisa que
destrói confiança justamente com o comprador técnico, que confere. O site vende o que é verdade
hoje: o pacote de entrega, o rigor da conferência e o plano de instalação. Quando tiver cliente e
autorização para citar, a gente acrescenta.

---

## Passo 1 — Domínio

Sem isso não existe nem site nem email da empresa.

1. Acesse [registro.br](https://registro.br) e crie a conta com teu CPF
2. Registre **`borinprojetos.com.br`** — R$ 40/ano, mesmo preço na renovação
3. Pode pagar 3 ou 5 anos de uma vez e esquecer o assunto

Estava livre na última verificação (28/07/2026). Domínio livre não fica reservado.

---

## Passo 2 — Email

### A decisão (29/07/2026)

**Agora: Cloudflare Email Routing, gratuito. Quando entrar o primeiro cliente: Zoho Mail Lite, pago.**

O Zoho tinha um plano gratuito com domínio próprio, mas em julho de 2026 **a porta de entrada dele
sumiu** — o plano é citado no FAQ, e não há mais botão de inscrição na página de preços, na do
Workplace nem na principal. Só sobraram Mail Lite, Mail Premium e o teste de 15 dias.

O Email Routing da Cloudflare é gratuito e **só recebe e encaminha**: cria `contato@` no domínio e
joga o que chega no Gmail. Serve pra receber contato do site sem custo nenhum.

**A limitação que importa:** ao *responder*, o cliente vê o teu Gmail, ou o aviso *"via gmail.com"* se
você configurar o "enviar como". Para primeiro contato, tudo bem. Para negociar proposta, não.

Por isso o gatilho está definido: **no primeiro cliente real, assinar o Zoho Mail Lite** — cerca de
US$ 1 por usuário/mês no anual, com IMAP e envio assinado com DKIM no próprio domínio.
Link direto que funciona: `https://mail.zoho.com/signup?type=org&plan=newMail5gb`

### Pré-requisito

O Email Routing exige o domínio **hospedado na Cloudflare** — ou seja, apontar os nameservers do
registro.br para ela. Isso é conveniente: o site também fica lá, e DNS, site e email passam a ser
administrados num painel só.

1. Criar conta em [zoho.com/mail](https://www.zoho.com/pt-br/mail/) e escolher o plano gratuito
2. Adicionar o domínio `borinprojetos.com.br`
3. O Zoho vai pedir para **verificar a posse do domínio** com um registro TXT — copie o valor que
   ele mostrar
4. No registro.br, abrir o painel do domínio → **Editar zona DNS** → adicionar o TXT
5. Voltar no Zoho e confirmar a verificação
6. Ainda na zona DNS do registro.br, adicionar os **registros MX** que o Zoho indicar. São eles que
   fazem o email chegar
7. Adicionar também os registros **SPF e DKIM** que o Zoho fornece — sem eles teu email cai na caixa
   de spam do cliente, que é pior que não ter email
8. Criar as contas: `mateus@borinprojetos.com.br` e `contato@borinprojetos.com.br`

A propagação de DNS leva de alguns minutos a algumas horas.

**Assinatura de email:** conforme `marca/design-guide.md` — logo, nome, função, cidade. Use o
`marca/png/borin-completo.png` em 140px de largura. Sem frase de efeito e sem imagem pesada.

---

## Passo 3 — Publicar o site

**Cloudflare Pages** é a recomendação: gratuito, SSL incluso, domínio próprio sem custo, e aguenta
tráfego muito acima do que um site institucional precisa.

```bash
npx wrangler pages deploy site --project-name borin
```

Na primeira vez ele pede login pelo navegador. Depois, no painel da Cloudflare:

1. **Workers & Pages** → o projeto `borin` → **Custom domains**
2. Adicionar `borinprojetos.com.br` e `www.borinprojetos.com.br`
3. A Cloudflare mostra os registros de DNS a criar no registro.br — ou, se você transferir os
   nameservers do domínio para a Cloudflare, ela cuida disso sozinha

Alternativas equivalentes: Vercel (`vercel --prod`) ou Netlify. GitHub Pages não serve aqui, porque
o repositório é privado e a publicação exigiria plano pago.

---

## Depois que estiver no ar

- [ ] Testar o formulário de contato — hoje o site usa `mailto:` e link de WhatsApp, sem formulário. Se quiser formulário de verdade, precisa de um backend simples (um Worker da Cloudflare resolve)
- [ ] Cadastrar o site no Google Search Console
- [ ] Colocar o endereço na assinatura de email e na proposta
- [ ] Perfil no LinkedIn apontando pro site — é onde está o comprador técnico das integradoras
