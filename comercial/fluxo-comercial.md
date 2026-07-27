# Fluxo comercial

> Do primeiro contato até o dinheiro na conta. Serve tanto pra você não esquecer etapa quanto pra
> eu saber em que ponto está cada cliente quando você me pedir alguma coisa.

---

## Infraestrutura mínima

Antes de prospectar o primeiro cliente, isso precisa existir. É o que separa "conhecido que faz
projeto" de "fornecedor".

### 1. Domínio

`borinprojetos.com.br` — R$ 40/ano direto no [registro.br](https://registro.br), mesmo preço na
renovação. **É o primeiro passo e trava tudo que vem depois**: sem domínio não existe email da
empresa.

### 2. Email profissional

Enviar proposta de Gmail pessoal derruba o preço antes de o cliente ler o valor.

| Opção | Custo | Observação |
|---|---|---|
| **Zoho Mail** | Plano gratuito aceita até 5 usuários | O caminho mais barato pra começar. Confira o armazenamento do plano gratuito na hora de assinar |
| **Google Workspace Business Starter** | R$ 32,72 por usuário/mês no anual | Preço promocional dos primeiros 12 meses; depois vai pro cheio. Vale se você já vive no ecossistema Google |

Recomendação: **Zoho no começo**. Migrar pro Google depois é simples e você não paga mensalidade
antes de faturar.

Endereços: `mateus@borinprojetos.com.br` para você, e `contato@borinprojetos.com.br` como caixa
geral. Não crie mais que isso — empresa de uma pessoa com seis emails engana ninguém.

**Assinatura de email:** conforme `marca/design-guide.md`. Logo, nome, função, cidade. Sem frase de
efeito, sem "enviado do meu iPhone", sem imagem pesada.

### 3. Assinatura de documento

Proposta e contrato assinados digitalmente. O [Assinador Gov.br](https://assinador.iti.br) é gratuito
e tem validade jurídica — dispensa contratar plataforma de assinatura no começo.

### 4. Formalização

Conversar com um contador antes de emitir a primeira nota. Pontos a resolver com ele:

- MEI, ME ou autônomo com RPA — qual enquadramento cabe no faturamento previsto e na atividade
- Qual CNAE cobre projeto e documentação técnica, e se a atividade é aceita no MEI
- Qual o teto de faturamento vigente do enquadramento escolhido
- Como emitir nota de serviço no município

Não chute nada disso. Enquadramento errado dá dor de cabeça retroativa.

---

## As etapas

### 1. Contato

Chega por indicação, LinkedIn ou porta. Responder em até 24h, sempre.

Nesse primeiro contato só se descobre três coisas:

- Que tipo de máquina ou processo é
- Se precisa só do painel ou também da instalação (Escopo A ou B)
- Qual o prazo que ele tem em mente

Se o prazo for impossível ou o serviço for fora do que você faz, dizer na hora. Perder rápido é
melhor que perder devagar.

### 2. Levantamento técnico

Preencher o `briefing.md` da pasta do cliente. Sem briefing preenchido não sai proposta — é ele que
protege você da discussão de escopo depois.

O que precisa estar respondido antes de precificar:

- Tensão de alimentação e tensão de comando
- CLP e hardware definidos, ou é você que especifica
- Quantidade estimada de I/Os
- Marcas obrigatórias ou restrições de componente
- Documentos que o cliente já tem: P&ID, layout, manual de equipamento, lista de I/O
- Existe projeto anterior? Em que formato
- Quem aprova tecnicamente do lado dele

### 3. Proposta

Enviar em até **3 dias úteis** depois do levantamento. Proposta que demora passa a impressão de
como vai ser o projeto.

Usar `comercial/modelo-proposta.md`. Sempre nomear o escopo (A ou B) e anexar o padrão de entrega.

Validade: 15 dias.

### 4. Acompanhamento

Se não responder em 5 dias úteis, uma mensagem curta perguntando se ficou dúvida no escopo. Uma só.
Depois disso, espera — insistência derruba preço.

### 5. Fechamento

- Contrato assinado pelos dois lados, digitalmente
- **Sinal de 40% na assinatura.** Projeto só entra na fila depois que o sinal cai
- Prazo começa a contar do sinal, não da assinatura

### 6. Execução

- Confirmar por escrito a data de entrega prevista
- Se aparecer algo que muda o escopo, avisar **na hora**, por escrito, com o impacto em prazo e preço. Nunca absorver calado
- Rodar o `padroes/checklist-conferencia.md` antes de qualquer envio, inclusive nas revisões

### 7. Entrega

- Enviar por link ou pasta compartilhada, com a nomenclatura do padrão de entrega
- Deixar claro quantas rodadas de revisão restam
- Aceite por escrito, ou automático após 10 dias corridos

### 8. Cobrança

- **60% restantes na entrega**, pagamento em até 15 dias
- Nota emitida junto com a entrega, não depois
- Atraso de 5 dias: uma cobrança educada por escrito. Atraso de 15: parar qualquer serviço em
  andamento pro mesmo cliente

### 9. Pós-entrega

Duas semanas depois, uma mensagem perguntando se o pessoal da montagem teve dificuldade com a
documentação. Serve pra melhorar o padrão e pra abrir a porta da indicação.

**Pedir indicação explicitamente.** Cliente satisfeito indica se for perguntado, e raramente indica
por conta própria.

---

## Onde procurar cliente

Conforme `analise-mercado.md`, o cliente inicial mais provável é a **integradora e o fabricante de
máquina da Serra**. Eles vivem de fila e terceirizam projeto quando entram várias máquinas juntas.

- Integradoras e fabricantes de máquina de Caxias, Bento, Farroupilha e Garibaldi
- Contatos de indicação — o canal mais forte hoje
- Fornecedores de componente (representantes de Weidmüller, Siemens, LAPP) sabem quem está com fila cheia
- LinkedIn: projetista e coordenador de engenharia dessas empresas

**Antes de prospectar:** resolver a questão de conflito de interesse com a FlowSistem. Você trabalha
lá, e algumas dessas empresas são concorrentes diretas. Ter clareza sobre isso antes evita um
problema que não se desfaz depois.
