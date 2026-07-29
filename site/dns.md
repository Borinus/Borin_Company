# Registros de DNS — borinprojetos.com.br

Checklist da zona DNS. Preencha os valores conforme cada serviço for mostrando, e marque quando
estiver propagado. Onde editar: **registro.br → painel do domínio → Editar zona DNS**.

Se você transferir os nameservers para a Cloudflare, a edição passa a ser no painel dela — e aí os
registros do site entram sozinhos, sobrando só os de email para adicionar na mão.

---

## Email — Zoho Mail

### 1. Verificação de posse

| Tipo | Nome | Valor | Feito |
|---|---|---|---|
| TXT | `@` | *(o Zoho mostra na tela de verificação)* | [ ] |

### 2. Recebimento — registros MX

Prioridade menor = tentado primeiro. O Zoho mostra os hosts exatos na configuração.

| Tipo | Nome | Prioridade | Valor | Feito |
|---|---|---|---|---|
| MX | `@` | 10 | | [ ] |
| MX | `@` | 20 | | [ ] |
| MX | `@` | 50 | | [ ] |

### 3. Antisspam — SPF, DKIM e DMARC

**Não pule este bloco.** Sem ele, tua proposta cai no spam do cliente, o que é pior que não ter email
próprio. Só se descobre quando alguém diz que "não recebeu".

| Tipo | Nome | Valor | Feito |
|---|---|---|---|
| TXT (SPF) | `@` | `v=spf1 include:zoho.com ~all` | [ ] |
| TXT (DKIM) | `zoho._domainkey` | *(chave que o Zoho gera)* | [ ] |
| TXT (DMARC) | `_dmarc` | `v=DMARC1; p=none; rua=mailto:mateus@borinprojetos.com.br` | [ ] |

Comece o DMARC em `p=none`, que só monitora. Depois de algumas semanas sem problema, dá pra endurecer
para `p=quarantine`.

### 4. Contas a criar

- [ ] `mateus@borinprojetos.com.br` — a tua, para conversa com cliente
- [ ] `contato@borinprojetos.com.br` — a do site, caixa geral

Não crie mais que isso. Empresa de uma pessoa com seis endereços não engana ninguém.

---

## Site — Cloudflare Pages

| Tipo | Nome | Valor | Feito |
|---|---|---|---|
| CNAME | `@` | *(a Cloudflare mostra ao adicionar o domínio)* | [ ] |
| CNAME | `www` | *(idem)* | [ ] |

- [ ] Domínio adicionado em Workers & Pages → `borin` → Custom domains
- [ ] SSL ativo (a Cloudflare emite sozinha, leva alguns minutos)
- [ ] `borinprojetos.com.br` abre o site
- [ ] `www.borinprojetos.com.br` abre o site

---

## Conferir se funcionou

Depois da propagação — de minutos a algumas horas:

```bash
nslookup -type=mx borinprojetos.com.br
nslookup -type=txt borinprojetos.com.br
```

Teste de verdade do email: mande uma mensagem de `mateus@borinprojetos.com.br` para um Gmail seu.
Abra a mensagem recebida, vá em **Mostrar original** e confirme que aparece `SPF: PASS`,
`DKIM: PASS` e `DMARC: PASS`. Se algum falhar, o registro correspondente está errado ou ainda não
propagou.
