# Auditoria do site — 01/08/2026

> Rodada em produção: seis frentes independentes baixaram as páginas com curl e leram o HTML
> cru. Cada achado passou por um cético que tentou reproduzir e derrubar antes de entrar aqui.
> **25 confirmados, 7 derrubados.**
>
> Complementa o teste de funil que dirigiu o navegador de verdade (formulário preenchido campo
> a campo, botão clicado): esse caminho, do clique até a `/enviado`, funciona.

---

# Auditoria do site — borinprojetos.com.br

## QUEBRA

**1. O Worker não consegue mandar email para cliente nenhum no plano atual**
Onde: Cloudflare Email Service — tabela de preço lista "Outbound emails (Email Sending)" como *Not available* no Workers Free; hoje o site só funciona porque manda para o `mateusborin73@gmail.com`, que é destino verificado (grátis em qualquer plano).
Conserto: assinar Workers Paid (US$ 5/mês, 3.000 emails inclusos) e onboardar `borinprojetos.com.br` em Email Sending. Sem isso, nenhum email sai para o lead — só para você.

## ERRA

**2. Dois rastreadores de terceiro, nenhuma política de privacidade**
Onde: `/` e `/orcamento` — Microsoft Clarity (gravação de sessão, id `xvrvwys25k`) mais o beacon da Cloudflare; "privacidade", "cookie", "LGPD" e "termos" aparecem 0 vezes no HTML das duas páginas e não existe página de política em nenhuma URL (todas 404). O `/orcamento` grava sessão em cima de um formulário com empresa, nome, email e WhatsApp.
Conserto: publicar `/privacidade` com o que é coletado e por quem, linkar no rodapé das duas páginas. Agrava porque a home vende sigilo na seção "Condições comerciais".

**3. Qualquer um afoga tua caixa de entrada com pedido falso**
Onde: `POST /api/enviar` e `POST /api/orcamento` — sem auth, sem captcha, sem rate limit; 25 POSTs seguidos passaram sem um 429. A única defesa é o campo-isca `website`, que script direto nem carrega. O `Reply-To` também vem do que o remetente digitou.
Conserto: rate limit por IP na rota (regra de Rate Limiting da Cloudflare já resolve) e Turnstile no formulário.

**4. O segredo de administrador viaja na query string**
Onde: `GET /api/acesso/cliente?email=...&segredo=...` — mesmo segredo lê conta e fichas de qualquer cliente, cria conta e grava projeto. Query string entra em log da Cloudflare, histórico e header `Referer`. Esse endpoint não tem nem a trava por email que o `/entrar` tem.
Conserto: mover o segredo para header `Authorization` e colocar freio de tentativa.

**5. Login sem `<form>`: apertar Enter não entra**
Onde: `/entrar` — zero ocorrências de `<form>` no HTML, botão `type="button"`, nenhum handler de tecla.
Conserto: envolver os campos num `<form>` com botão `type="submit"`. Também conserta o salvamento de senha do gerenciador do navegador.

**6. Todos os campos do formulário em 14px — iOS dá zoom em cada um**
Onde: `/orcamento` — `input[type=text|email|tel], select, textarea { font-size: var(--fs-small) }` com `--fs-small: 0.875rem`. Medido no viewport de iPhone: 14px nos 9 campos de texto.
Conserto: `font-size: max(16px, var(--fs-small))` nos campos. Abaixo de 16px o Safari dá zoom e não desfaz.

**7. O campo de data ficou fora do CSS**
Onde: `/orcamento`, `<input type="date" id="prazo">` — o seletor lista `text, email, tel, select, textarea` e não inclui `date`. Medido: 21px de altura contra 37px dos vizinhos, borda `2px inset`, fonte monospace 13.33px, fundo branco no modo escuro.
Conserto: incluir `input[type="date"]` no seletor.

**8. `robots.txt` bloqueia páginas que têm `noindex`**
Onde: `/robots.txt` com `Disallow: /enviado`, `/padrao`, `/projeto`, `/entrar`, `/conta`, `/cadastro` — todas essas têm `<meta name="robots" content="noindex">` no HTML. O crawler que obedece o Disallow não baixa a página e nunca lê o noindex.
Conserto: tirar o Disallow dessas rotas e deixar o `noindex` fazer o trabalho.

**9. Em `/padrao` e `/projeto` o envio pode não chegar na `/enviado`**
Onde: `enviar()` faz `if (guardou) { location.href = destinoEnvio() }`, e `guardarEnvio()` retorna `false` no catch quando `sessionStorage.setItem` lança (navegador embutido do Instagram/LinkedIn/WhatsApp, armazenamento bloqueado). A `/enviado` é a única marca de conversão que Clarity e Cloudflare conseguem contar.
Conserto: redirecionar sempre, fora do condicional — é o que o `/orcamento` já faz em `solicitar()`.

## MELHORA

**10. Email nunca validado no formato**
Onde: `/orcamento` — `validar()` só testa `!v('email')` (vazio), e como o botão é `type="button"` dentro de `<form onsubmit="return false;">`, a validação nativa do `type="email"` nunca roda. "joao@" passa. O worker confirma: `email.includes("@") ? email : null` — sem "@" o Reply-To não é setado. Mesmo caso no telefone quando o canal é WhatsApp.
Conserto: regex de email e mínimo de dígitos no fone dentro de `validar()`.

**11. Enter no formulário de orçamento não faz nada**
Onde: `/orcamento` — zero `type="submit"` no HTML e 9 campos de texto, então não existe submissão implícita. Quem preenche no teclado aperta Enter e acha que enviou.
Conserto: trocar o botão principal para `type="submit"` e chamar `solicitar()` no `onsubmit`.

**12. Link de email da home é 404 e mostra "[email protected]"**
Onde: `/`, seção contato — o Cloudflare reescreveu o `mailto:` para `/cdn-cgi/l/email-protection#...`, que responde 404 (confirmado agora). Só vira mailto real se o JS decodificador rodar. E não protege nada: o mesmo endereço está em texto puro no JSON-LD da própria página.
Conserto: desligar Scrape Shield > Email Address Obfuscation no painel do domínio.

**13. Botões mortos no `/entrar` e nenhum jeito de trocar a senha depois**
Onde: o bloco `cxDentro` ("Trocar a senha" / "Sair") só aparece se `dentro()` for chamada, e `dentro(` aparece uma única vez no arquivo — a própria declaração. `carregar()` só redireciona ou mostra `cxEntrar`. O `cxTrocar` só abre pelo caminho `senha_provisoria`, uma vez. O `/conta` não tem link de trocar senha.
Conserto: remover o bloco morto e colocar "Trocar a senha" no `/conta`.

**14. Qualquer um trava a conta de um cliente por 15 min só sabendo o email**
Onde: `POST /api/acesso/entrar` — o freio conta por email, sem componente de IP. Nove pedidos anônimos bloqueiam o endereço. Não existe recuperação de senha automática, então o cliente travado não tem saída.
Conserto: contar por IP+email em vez de só email.

**15. `color-scheme` não declarado**
Onde: `/` e `/orcamento` — há `@media (prefers-color-scheme: dark)` e overrides `data-theme`, mas nenhuma declaração `color-scheme` (confirmado: as únicas ocorrências no HTML são dentro de `prefers-color-scheme`). Radios saem como círculos brancos no modo escuro, calendário abre claro, scrollbar clara. É a causa raiz do item 7.
Conserto: `:root { color-scheme: light dark; }` mais o par nos overrides.

**16. `/orcamento` pode ser embutida em iframe de terceiro**
Onde: cabeçalhos da resposta — sem `Content-Security-Policy` (`frame-ancestors`) e sem `X-Frame-Options`. A página HTML ainda volta com `Access-Control-Allow-Origin: *`.
Conserto: `X-Frame-Options: SAMEORIGIN` (ou CSP `frame-ancestors 'self'`) e tirar o CORS aberto do documento HTML.

**17. Botões "ver os 9" / "ver os 5" sem estado para leitor de tela**
Onde: `/`, seção pacote — `<button class="link-expandir" data-abre="pdf">` sem `aria-expanded` nem `aria-controls`; a função `fechar()` só faz `classList.toggle('fechada')` e troca o texto.
Conserto: `aria-expanded` + `aria-controls` apontando para o `id` da `<ul>`, atualizados dentro de `fechar()`.

**18. Alvo de toque de 17px no "← Início" do orçamento**
Onde: `/orcamento` — `.voltar` mede 59x17px no celular, abaixo do mínimo 24x24 do WCAG. Mesmo caso nos `.link-acao` ("Ver e editar" / "Apagar", 16px). A home já resolveu isso com `min-height: 2.75rem` em todos os alvos; o CSS do formulário não recebeu.
Conserto: aplicar o mesmo `min-height: 2.75rem` no CSS do formulário.

**19. Meta description com 165 caracteres**
Onde: `/`, linha 6 — o corte do Google (~155-160) cai justo em "Caxias do Sul, RS", que é o sinal de SEO local mais valioso da página.
Conserto: enxugar para ~150 caracteres ou puxar a cidade para antes do meio da frase.

**20. Tag do Clarity no último byte da página**
Onde: `/`, `/orcamento` e `/enviado` — o snippet é o último elemento, em 99,9% do HTML. A home tem 168 KB de HTML, então o Clarity só inicializa depois de todo esse parse e visita que sai rápido não é registrada.
Conserto: mover o snippet para logo depois das metas do topo, como a doc do Clarity pede.

## Sobre o email

O Worker hoje **não consegue** escrever para o cliente: o binding em `wrangler.toml` tem `destination_address = "mateusborin73@gmail.com"`, e esse campo trava o destino no runtime — o `send()` rejeita qualquer outro `to`, não adianta mudar o código.
Não é problema de "destino verificado": depois de onboardar um domínio de envio, a Cloudflare libera envio para qualquer destinatário na hora. Os comentários no `wrangler.toml` (linha 12) e no `index.js` (linha 9) descrevem o mundo antigo, só-Email-Routing.
O bloqueio real é plano: Email Sending é *Not available* no Workers Free.
Caminho: Workers Paid (US$ 5/mês) → onboardar `borinprojetos.com.br` em Email Sending → trocar `destination_address` por `allowed_destination_addresses` (lista branca) ou tirar a restrição, e usar `allowed_sender_addresses` para fixar o remetente.
Custo efetivo: US$ 5/mês; os 3.000 emails inclusos nunca vão ser atingidos no teu volume.
