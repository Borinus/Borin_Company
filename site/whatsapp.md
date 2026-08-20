# WhatsApp Cloud API — o que já está montado

> Levantado em 20/08/2026, depois de meia hora perdida com envio que retornava
> sucesso e não entregava. Está aqui para isso não se repetir.

## Os dados

| Item | Valor |
|---|---|
| Número de envio | `+55 54 9951-7183` |
| Phone Number ID | `1209216718946878` |
| WhatsApp Business Account ID | `902961082438081` |
| App | Borin Site — `1020386860773883` |
| Portfólio | Borin Projetos Elétricos |
| Webhook | `https://borinprojetos.com.br/api/zap` |
| Qualidade | GREEN · pagamento cadastrado |

O token é permanente, gerado pelo utilizador de sistema **`site`** no
Business Settings. Não expira. Vive em secret do worker e no `.env` de quem
mais precisar — **nunca versionado**.

## As três armadilhas

### 1. Texto livre não entrega fora da janela de 24 horas

Mensagem `type: "text"` só funciona até 24 h depois de o cliente ter escrito.
Fora disso a API **responde 200 com `wamid` e descarta a mensagem depois** — a
falha só aparece no webhook de status, nunca na resposta do envio.

**Sempre usar `type: "template"`** para qualquer mensagem que o sistema inicia.

### 2. O nome do template não é o que está no código

`zap.js` traz `env.ZAP_TEMPLATE || "pedido_recebido"`, mas o `wrangler.toml`
define `ZAP_TEMPLATE = "pedido_recebido_botoes"`. O padrão do código **não
existe** na conta. Usar o nome do padrão devolve erro 132001.

Para listar o que existe de verdade:

```bash
curl.exe -s "https://graph.facebook.com/v21.0/902961082438081/message_templates?access_token=TOKEN&fields=name,status,language"
```

### 3. O nono dígito some

Envio para `5554996642003` volta com `wa_id: 555496642003`. O WhatsApp
normaliza número brasileiro tirando o 9. **O webhook usa a forma curta.**
Quem comparar número recebido com número cadastrado tem que tratar as duas.

## Erros da Meta que importam

| Código | O que é |
|---|---|
| 131047 | Fora da janela de 24 h — precisa de template |
| 132001 | Template não existe ou não aprovado |
| 132000 | Número errado de parâmetros no template |
| 131026 | Destino não tem WhatsApp |
| 190 | Token inválido ou expirado |

Sempre logar o código. Sem ele, investigar vira adivinhação — foi o que
aconteceu em 20/08.

## Para um segundo projeto usar o mesmo número

Não precisa de app novo nem de número novo. Copiar as credenciais e criar um
template próprio, porque o `pedido_recebido_botoes` é texto de orçamento e não
serve para notificação interna.

Template sugerido para automação, categoria **Utilidade**:

```
Nome:   status_geracao
Idioma: pt_BR
Corpo:  Geração do projeto {{1}} concluída na volta {{2}}. Resultado: {{3}}.
```

Criar em **business.facebook.com/wa/manage/message-templates**. Utilidade
aprova em minutos e custa menos que Marketing.
