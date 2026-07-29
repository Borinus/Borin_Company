# DNS — borinprojetos.com.br

Domínio registrado em 28/07/2026, no CPF do Mateus. **Vence em 28/07/2027** — renovar ou estender
antes disso, senão o nome cai e leva junto o site e o email.

DNS administrado na **Cloudflare**, com os nameservers apontados a partir do registro.br.

---

## Etapa 1 — Nameservers

Passar a administração do DNS do registro.br para a Cloudflare. É o que destrava o Email Routing e
simplifica a publicação do site.

- [ ] Conta criada em [dash.cloudflare.com](https://dash.cloudflare.com)
- [ ] Domínio adicionado na Cloudflare, plano **Free**
- [ ] Anotar os dois nameservers que ela fornecer:

```
ns1: ________________________.ns.cloudflare.com
ns2: ________________________.ns.cloudflare.com
```

- [ ] No registro.br: painel do domínio → **Alterar servidores DNS** → substituir `a.auto.dns.br` e `b.auto.dns.br` pelos dois da Cloudflare
- [ ] Aguardar a Cloudflare confirmar (de minutos a algumas horas; ela manda email quando ativa)

> Esta é a única etapa que, se errada, tira o domínio do ar por algumas horas. Confira as duas
> linhas antes de salvar.

---

## Etapa 2 — Email (Cloudflare Email Routing, gratuito)

Recebe e encaminha. Não envia — ver `site/LEIA-ME.md` para o porquê e para o gatilho de migração.

- [ ] Cloudflare → domínio → **Email** → **Email Routing** → ativar
- [ ] Aceitar os registros MX e SPF que ela adiciona sozinha
- [ ] Endereço de destino: teu Gmail pessoal, confirmado pelo link que chega nele
- [ ] Criar `contato@borinprojetos.com.br` → encaminha pro Gmail
- [ ] Criar `mateus@borinprojetos.com.br` → encaminha pro Gmail
- [ ] Testar: mandar uma mensagem de outro endereço para `contato@` e ver se chega

**Não criar catch-all.** Endereço curinga vira ímã de spam.

---

## Etapa 3 — Site (Cloudflare Pages)

```bash
python site/publicar.py
npx wrangler pages deploy site/publico --project-name borin
```

- [ ] Deploy feito
- [ ] Workers & Pages → `borin` → **Custom domains** → adicionar `borinprojetos.com.br` e `www.borinprojetos.com.br`
- [ ] Com o DNS já na Cloudflare, os registros entram sozinhos
- [ ] SSL ativo (ela emite sozinha, leva alguns minutos)
- [ ] Os dois endereços abrem o site

---

## Etapa 4 — Quando migrar para o Zoho

Gatilho: **primeiro cliente real**. Aí o email precisa enviar com o domínio próprio.

- [ ] Assinar o Mail Lite: `https://mail.zoho.com/signup?type=org&plan=newMail5gb`
- [ ] Desativar o Email Routing da Cloudflare (os MX vão mudar de dono)
- [ ] Trocar os MX pelos do Zoho, na Cloudflare
- [ ] Adicionar SPF, DKIM e DMARC:

| Tipo | Nome | Valor |
|---|---|---|
| TXT (SPF) | `@` | `v=spf1 include:zoho.com ~all` |
| TXT (DKIM) | `zoho._domainkey` | *(chave gerada pelo Zoho)* |
| TXT (DMARC) | `_dmarc` | `v=DMARC1; p=none; rua=mailto:mateus@borinprojetos.com.br` |

Começar o DMARC em `p=none`, que só monitora. Depois de algumas semanas sem problema, endurecer para
`p=quarantine`.

**Não pule o SPF e o DKIM.** Sem eles a proposta cai no spam do cliente, e você só descobre quando
alguém diz que não recebeu.

---

## Conferir se funcionou

```bash
nslookup -type=ns borinprojetos.com.br
nslookup -type=mx borinprojetos.com.br
nslookup -type=txt borinprojetos.com.br
```

Depois de migrar para o Zoho, o teste de verdade: mandar uma mensagem de
`mateus@borinprojetos.com.br` para um Gmail seu, abrir **Mostrar original** e confirmar
`SPF: PASS`, `DKIM: PASS` e `DMARC: PASS`.
