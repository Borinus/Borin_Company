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

## Passo 2 — Email profissional

### Por que não o Cloudflare

O Email Routing da Cloudflare é gratuito e cria endereços no teu domínio, mas **só recebe e
encaminha** — envio é outro produto, e está em beta. Dá pra contornar configurando "enviar como" no
Gmail via SMTP dele, só que aí o Gmail assina com o domínio dele e o cliente vê *"via gmail.com"* na
proposta, além dos limites de envio do Gmail.

Use a Cloudflare para **site e DNS**, onde ela é imbatível, e o Zoho para email. Os dois convivem: os
registros MX do Zoho ficam na mesma zona DNS.

### Zoho Mail

O plano gratuito do **Zoho Mail** aceita até 5 usuários com domínio próprio, envia e recebe, e assina
com DKIM no teu domínio. É o caminho mais barato para começar, e migrar para o Google Workspace
depois é simples.

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
