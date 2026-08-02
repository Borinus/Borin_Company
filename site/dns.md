# DNS — borinprojetos.com.br

Domínio registrado em 28/07/2026, no CPF do Mateus. **Vence em 28/07/2027** — renovar ou estender
antes disso, senão o nome cai e leva junto o site e o email.

DNS administrado na **Cloudflare**, com os nameservers apontados a partir do registro.br.

---

## Etapa 1 — Nameservers

Passar a administração do DNS do registro.br para a Cloudflare. É o que destrava o Email Routing e
simplifica a publicação do site.

- [x] Conta criada em [dash.cloudflare.com](https://dash.cloudflare.com) — conta `Mateusborin73@gmail.com`
- [x] Domínio adicionado na Cloudflare, plano **Free**
- [x] Nameservers atribuídos (29/07/2026):

```
ns1: duke.ns.cloudflare.com
ns2: lara.ns.cloudflare.com
```

- [x] No registro.br: alteração feita e aceita em 29/07/2026 — o painel já lista `duke` e `lara`
      como Servidor 1 e 2, em período de transição
- [x] **Delegação ativa em 29/07/2026.** O TLD `.br` e os resolvers públicos respondem
      `duke.ns.cloudflare.com` / `lara.ns.cloudflare.com`, e a Cloudflare confirmou a zona como
      ativa (*"Your domain is now protected by Cloudflare"*). Etapa 1 concluída.

> **Trava do registro.br em domínio novo — 29/07/2026.** Ao registrar, o domínio entra usando o DNS
> do próprio registro.br (`a.auto.dns.br`) e fica **bloqueado pra delegação externa por cerca de 2
> horas**. A mensagem no painel é: *"os servidores DNS do domínio se encontram em transição.
> Servidores DNS externos poderão ser delegados em seu domínio em aproximadamente 1h59m"*.
>
> Não é erro. É só esperar o prazo e refazer a alteração. Enquanto isso, a tela da Cloudflare fica
> em *"waiting for your registrar to propagate"* — ela espera indefinidamente e não precisa de ação.
>
> Depois do prazo, conferir com o comando no fim deste arquivo. O que tem que aparecer é `duke` e
> `lara`, não `a.auto.dns.br`.

> Esta é a única etapa que, se errada, tira o domínio do ar por algumas horas. Confira as duas
> linhas antes de salvar.

---

## Etapa 2 — Email (Cloudflare Email Routing, gratuito)

Recebe e encaminha. Não envia — ver `site/LEIA-ME.md` para o porquê e para o gatilho de migração.

- [x] Email Routing ativado em 29/07/2026
- [x] MX no ar e propagados: `route1/2/3.mx.cloudflare.net` (prio 53/41/56)
- [x] SPF trocado pela Cloudflare para `v=spf1 include:_spf.mx.cloudflare.net ~all`
- [x] DKIM adicionado pela Cloudflare (`cf2024-1._domainkey`)
- [x] Destino verificado: `mateusborin73@gmail.com` — auto-verificou por ser o email da própria
      conta Cloudflare, então não chegou link de confirmação. Está correto
- [x] `contato@borinprojetos.com.br` → encaminha pro Gmail
- [x] `mateus@borinprojetos.com.br` → encaminha pro Gmail
- [x] Catch-all mantida **desligada**
- [x] Testado em 29/07/2026: chegou, **mas caiu no Spam do Gmail**
- [ ] Criar o filtro no Gmail (abaixo) e testar de um endereço externo

### O encaminhamento cai no Spam — e por quê

Email Routing reenvia a mensagem mantendo o remetente original. O Gmail vê uma mensagem que diz vir
de `@gmail.com` (ou do domínio de quem mandou) chegando por um servidor da Cloudflare, que não está
no SPF daquele domínio. SPF falha, vai pro Spam. Isso é inerente a qualquer encaminhamento, e é
**pior no teste com o próprio endereço de destino**.

**Filtro no Gmail — fazer uma vez:**

1. Barra de pesquisa → ícone de opções → campo **Para**
2. Colar: `contato@borinprojetos.com.br OR mateus@borinprojetos.com.br`
3. **Criar filtro** → marcar **Nunca enviar para o Spam** e **Aplicar marcador** (`Borin`)

O cabeçalho `To:` original sobrevive ao encaminhamento, então o filtro pega qualquer remetente.

**Ao testar, nunca mande do próprio endereço de destino** — o resultado é sempre pessimista. Use
outro endereço.

Isso é remendo, não solução. A solução é a Etapa 4: caixa própria no Zoho, que entrega assinado com
DKIM do próprio domínio e não depende de encaminhamento.

> **Duas coisas aprendidas em 29/07/2026:**
>
> 1. Ao ativar, foi preciso apagar o registro `MX .` (nulo) que a Cloudflare cria por padrão em
>    domínio sem email. Era ele que causava *"Existing non-Cloudflare MX records conflict with Email
>    Routing"*.
> 2. O endereço de destino é **nível de conta** e exige a permissão `Email Routing Addresses`, que
>    não estava no token. As *regras* (`Email Routing Rules`) dá pra criar por API — mas só depois de
>    o destino existir e estar verificado, senão volta `code 2054: Destination address is not
>    verified`.

**Não criar catch-all.** Endereço curinga vira ímã de spam.

---

## Etapa 3 — Site (Cloudflare Pages)

```bash
python site/publicar.py
npx wrangler pages deploy site/publico --project-name borin --branch main
```

- [x] Projeto Pages `borin` criado e deploy feito em 29/07/2026 — `https://borin.pages.dev`
- [x] Custom domains adicionados: `borinprojetos.com.br` e `www.borinprojetos.com.br`, ambos `active`
- [x] CNAME dos dois criados apontando pra `borin.pages.dev`, proxied
- [x] SSL válido nos dois — verificado no edge (HTTP 200, 131 KB servidos)

> **Os registros NÃO entram sozinhos.** Adicionar o custom domain no projeto Pages deixa o status em
> `pending` indefinidamente até existir o CNAME na zona. Foi preciso criar os dois na mão
> (`CNAME borinprojetos.com.br -> borin.pages.dev`, proxied, e o mesmo para `www`).
>
> **Cache negativo local:** depois de publicar, a máquina do Mateus continuou dando "could not
> resolve host" por ter guardado o NXDOMAIN anterior — `ipconfig /flushdns` não resolveu porque o
> cache está no resolver da rede, não no Windows. O site já respondia normalmente pra fora. Para
> conferir sem depender do DNS local:
>
> ```bash
> curl -s -o /dev/null -w "%{http_code}\n" --resolve borinprojetos.com.br:443:104.21.42.71 https://borinprojetos.com.br
> ```

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
