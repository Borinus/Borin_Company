# Site

**No ar em [borinprojetos.com.br](https://borinprojetos.com.br).** Cloudflare Pages, domínio na
Cloudflare, email pelo Email Routing.

Páginas autocontidas: não buscam fonte, script nem imagem de lugar nenhum — a Inter vai embutida em
base64, com subset para os quatro pesos. Abrem por `file://` e funcionam offline.

---

## As páginas

| Rota | Template que você edita | Indexada | O que é |
|---|---|---|---|
| `/` | `_pagina.html` | sim | A página de venda |
| `/orcamento` | `_orcamento.html` | sim | 11 campos, pré-contrato |
| `/enviado` | `_enviado.html` | não | Confirmação pós-envio |
| `/padrao` | `_padrao.html` | não | Padrão do cliente, uma vez por cliente |
| `/projeto` | **gerado** — veja abaixo | não | Ficha técnica, uma por projeto |
| erro 404 | `_404.html` | não | Sem ela o Pages devolve a home com HTTP 200 |

**Edite sempre o arquivo com underscore.** Os `.html` sem underscore são gerados e a próxima
montagem sobrescreve.

`/padrao` e `/projeto` são pós-contrato: ficam fora do `robots.txt` e não têm link no site.

---

## Como montar e publicar

```bash
python site/publicar.py            # monta e prepara, sem subir
python site/publicar.py --deploy   # monta, confere e sobe
```

**Build e deploy são o mesmo comando de propósito.** Quando eram separados, um build que falhava era
seguido de um deploy que subia pasta vazia — e o wrangler dizia "sucesso". Agora o site é montado
numa pasta nova e só troca com a `publico/` no fim; se qualquer coisa falhar, o que está no ar
continua valendo.

O script aborta com `NAO PUBLIQUE` se faltar página ou se alguma sair pequena demais.

> **Se der `nao consegui trocar a pasta`:** tem processo com a `site/publico/` aberta, normalmente um
> `python -m http.server` de teste. Feche e rode de novo.

Scripts auxiliares, que rodam sozinhos quando precisa:

| Comando | Quando rodar |
|---|---|
| `python site/gerar-fontes.py` | só se trocar a fonte |
| `python site/gerar-og.py` | se mudar a marca ou os prazos do cartão de link |
| `python site/gerar-ficha.py` | não precisa — o `publicar.py` já chama |

Página nova: crie o `_nome.html` com o marcador `/* FONTES */` no `<style>` e acrescente o par em
`PAGINAS`, no `montar.py` **e** no `publicar.py`.

---

## A ficha do projeto é gerada

`/projeto` não se edita direto. Ela nasce de **`ficha-campos.json`**, que é o de/para entre o que o
cliente lê e o nome técnico que o gerador consome:

```json
{ "rotulo": "5 A — painel pequeno e médio", "macro": "FONTE_24V_5A" }
```

Mudar `rotulo` é seguro. Mudar `macro` só se o nome existir na biblioteca — a origem dos nomes é
`CONFERENCIAS/_eplan_gerador/FICHA_APP.yaml` e `docs_banco/MACROS_BIBLIOTECA.xlsx`.

A mensagem que chega em você leva os dois: `Chave geral: Trifásica [CHGERAL_TRI]`.

**A ficha também vira documento.** O botão *Gerar ficha para assinar* troca o formulário por um
documento com declaração e campo de assinatura, que o cliente salva em PDF pelo navegador. É o
**Anexo II do contrato** — é contra ela que a cláusula 5 compara todo pedido posterior.

---

## Os formulários

Nenhum deles tem página de obrigado com formulário tradicional: o JavaScript monta um texto e envia.

**`/orcamento` manda pro servidor.** Um Worker em `site/worker/` recebe o pedido em
`borinprojetos.com.br/api/*` e envia por email usando o binding nativo do Cloudflare — sem conta de
terceiro, sem chave de API, sem custo. Depois disso o cliente cai em `/enviado`.

```bash
cd site/worker && npx wrangler deploy
```

O assunto do email leva o código do projeto na frente (`#04003478 · Empresa — equipamento`), senão o
Gmail agrupa tudo numa conversa só.

**`/padrao` e `/projeto` NÃO mandam pro servidor**, de propósito: carregam o padrão interno e o
desenho da máquina do cliente, e o site promete sigilo. Saem por WhatsApp ou arquivo. Ligar essas
duas no Worker exige reescrever o bloco de sigilo da home junto.

Os campos marcados com `data-perfil` ficam no `localStorage` do navegador do cliente, pra ele não
repreencher no próximo pedido.

---

## Testar

```bash
python site/testar-fluxo.py     # o fluxo do orçamento, no site no ar
python site/teste-completo.py   # o fluxo inteiro + 5 emails de relatório
```

Os dois sobem uma página de teste temporária, dirigem um navegador de verdade contra o site
publicado, verificam cada etapa e removem a página no fim. **Rode antes de dizer que está pronto.**

Duas armadilhas que já geraram diagnóstico errado:

- **Cache de borda** serve versão antiga. Fure com uma query aleatória: `/pagina?c=123`
- **Git Bash corrompe acento** em `curl --data`. Escreva o JSON num arquivo UTF-8 e use
  `--data-binary @arquivo`

---

## O que falta

- [ ] **Token do Cloudflare Web Analytics** no `.env` como `BORIN_ANALYTICS_TOKEN`. Sem ele o site
      sobe igual, só não mede nada — e sem medir não dá pra decidir o que mudar
- [ ] **Tela intermediária** depois do orçamento: usar o padrão Borin ou montar o próprio
- [ ] **Frase de escopo negativo** no hero — *"Não monto painel, não vendo componente e não falo com
      o seu cliente"*. O ICP é integrador; sem isso o site lê como concorrente
- [ ] **Filtro no Gmail** pra `contato@` e `mateus@` nunca caírem no spam

**O que não tem no site, de propósito:** depoimento, logo de cliente e número de projetos entregues.
Nada disso existe ainda sob a marca Borin, e inventar destrói confiança justamente com o comprador
técnico, que confere. O site vende o que é verdade hoje.
