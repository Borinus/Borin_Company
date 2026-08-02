# Como o site manda email pro cliente

> Comparação levantada em 01/08/2026 nas páginas oficiais de cada serviço. Cada ficha passou
> por um cético que foi conferir limite, exigência de cartão e tamanho de anexo na fonte.
>
> **Contexto:** até 01/08/2026 o site não conseguia escrever para o cliente — o destinatário
> estava fixo no email do Mateus. O código já foi arrumado (`site/worker/correio.js`), e
> trocar de transporte agora é uma variável de ambiente. Falta escolher qual.
>
> No código, `correio.js` já traz o caminho da Resend pronto: basta o secret `RESEND_API_KEY`.
> Para o caminho da Cloudflare, a variável é `ENVIO_ABERTO = "1"`.

---

# Envio de email do site — comparação

Tudo abaixo foi lido nas páginas oficiais em **01/08/2026**. Preço e limite mudam sem aviso — reconfira antes de assinar qualquer coisa.

## 1. Tabela

| Serviço | Custo por mês (no teu volume) | Limite grátis | Anexo PDF | Esforço pra ligar |
|---|---|---|---|---|
| **Cloudflare Email Sending** | **USD 5,00** (Workers Paid, mínimo por conta — não existe no Free) | Não tem para cliente. Grátis só para caixas tuas já verificadas. No pago: 3.000/mês inclusos | Sim, até 5 MiB no email inteiro (já contando o inchaço do base64) | Baixo. DNS já é Cloudflare, ela escreve SPF/DKIM sozinha. Mas exige cartão antes do primeiro email real |
| **Resend** | **USD 0,00** | 3.000/mês **e** 100/dia, 1 domínio verificado | Sim, até 40 MB pós-base64 | Médio-baixo. 3 registros no DNS (MX + SPF em `send`, DKIM em `resend._domainkey`), proxy desligado. 30–45 min |
| **SMTP2GO** | **USD 0,00** | 1.000/mês e 200/dia (25/hora até verificar o domínio) | Sim, até 50 MB. Aceita mandar a URL do PDF em vez do arquivo | Médio-baixo. 3 CNAMEs no DNS, proxy desligado. Sem aprovação manual. 30–45 min |
| **Postmark** | **USD 0,00** | 100/mês, sem limite diário, não expira | Sim, até 10 MB no email inteiro | Médio. Mesmo DNS **+ aprovação manual da conta**, até ~24h úteis, antes de conseguir escrever para cliente novo |

Duas coisas que valem para SMTP2GO e Postmark: nenhuma das duas aceita cadastro com Gmail — precisa de uma caixa `@borinprojetos.com.br` funcionando antes de abrir a conta. E nenhuma das duas pede cartão. Na Resend, a página oficial simplesmente **não diz** se pede cartão; fontes de terceiros dizem que não, mas isso não está escrito por eles — descobre no cadastro.

Descartadas e por quê: **Brevo** carimba "Sent with Brevo" em todo email do plano grátis (inaceitável numa proposta comercial). **Mailgun** sem cartão só envia para 5 endereços pré-autorizados — mata o caso de uso. **Amazon SES** nasce em sandbox, onde só escreve para endereço verificado, e exige assinatura SigV4 na mão dentro do Worker. **MailerSend** exige cartão. **ZeptoMail** não tem plano gratuito permanente, só um crédito de cortesia válido por 1 mês.

## 2. Recomendação

Vai de **Resend**. O argumento é o teu volume: menos de 50 emails/mês contra 3.000/mês dá margem de 60x, então o teto nunca vai te morder, e o custo é zero de verdade, não zero com prazo. A Cloudflare seria a escolha elegante — é binding nativo do Worker, sem chave de API, sem serviço de terceiro, e ela mesma escreve os registros de DNS — mas cobra USD 5/mês obrigatórios (o recurso não existe no Workers Free) e ainda está em **beta público**, o que significa que a API, o preço e os limites podem mudar sem aviso justamente no fluxo que é o rosto comercial do teu negócio. Pagar 5 dólares por mês por 50 emails, num beta, não se justifica. A SMTP2GO é a segunda melhor e tecnicamente é ótima — o recurso de mandar a URL do PDF em vez do arquivo evita gastar CPU do Worker convertendo 1 MB para base64 — mas perde para a Resend em documentação e em ergonomia de código, e ainda tem o entrave do cadastro com Gmail. A Postmark eu descarto como principal por dois motivos: 100 emails/mês são só ~33 orçamentos (confirmação + proposta + contrato = 3 emails por cliente), e a conta passa por aprovação humana antes de conseguir escrever para cliente novo — se descobrir isso no dia em que o primeiro cliente preencher o formulário, o email não sai. Vale abrir a conta dela depois, de graça, já aprovada, só como reserva. Sobre "mais uma senha, mais uma conta": é real, e é o único ponto em que a Cloudflare ganharia. A defesa contra isso não é evitar o serviço, é escrever o código de um jeito que trocar de fornecedor seja uma tarde de trabalho — o item 3 explica.

## 3. O que muda no código

**Resend / SMTP2GO / Postmark:** um `fetch()` POST dentro do Worker, com a chave num secret (`npx wrangler secret put RESEND_API_KEY`). Escreve **um** helper `enviarEmail(para, assunto, html, anexo?)` e os três fluxos chamam ele — trocar de fornecedor depois é mexer só dentro desse helper, o resto do site nem fica sabendo. O único cuidado técnico: no Worker não existe `Buffer`, então converter o PDF para base64 precisa ser em blocos sobre `Uint8Array`, senão estoura com arquivo de 1 MB.

**Cloudflare:** menos código ainda — declara `[[send_email]]` no `wrangler.toml` e chama `await env.EMAIL.send({...})`, sem chave, sem secret, sem chamada HTTP para fora. Em compensação, testar anexo obriga a usar binding remoto (`"remote": true`), porque o `wrangler dev` local não consegue serializar arquivo binário e dá erro.

Nos dois casos, dispara o email com `ctx.waitUntil(...)` para o formulário responder rápido ao cliente em vez de ficar esperando o envio. Trabalho total: uma tarde, e a maior parte é espera de DNS, não código.

## 4. A armadilha do DMARC p=reject

Teu domínio está em `p=reject`, o que significa que email com DKIM desalinhado é **rejeitado na borda do destinatário** — não cai no spam, não volta aviso, simplesmente não existe para o cliente, e você fica achando que ele te ignorou. Por isso: nunca dispare em produção antes de ver o domínio "Verified" no painel do provedor e de abrir um email de teste real (manda para um Gmail e para um Outlook) e conferir no cabeçalho `dkim=pass`, `spf=pass` e `dmarc=pass` com `header.from=borinprojetos.com.br` — e publique os registros na Cloudflare com o proxy **desligado** (nuvem cinza), porque registro proxiado quebra a verificação.
