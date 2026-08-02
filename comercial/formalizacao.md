# Formalização da empresa

> Burocracia de operar e crescer. O que já existe, o que vai estourar, e o que decidir antes.
>
> **Nada aqui substitui o contador.** Teto, alíquota e regra de desenquadramento mudam por ano. O
> valor deste documento é você chegar na conversa sabendo o que perguntar.
>
> Última revisão: 29/07/2026.

---

## Situação atual

| | |
|---|---|
| CNPJ | **65.749.097/0001-85** |
| Razão social | `65.749.097 MATEUS BORIN` (formato padrão de MEI) |
| Nome fantasia | Borin Projetos Elétricos |
| Enquadramento | **MEI**, no Simples, porte Micro Empresa |
| Aberto em | 18/03/2026 — situação **ATIVA** |
| Endereço da sede | Rua Rivadávia de Azambuja Guimarães 331, Nossa Senhora da Saúde, Caxias do Sul / RS, CEP 95044-080 |
| CNAE principal | **3321-0/00** — Instalação de máquinas e equipamentos industriais |
| CNAE secundário | **nenhum** |
| CREA | Não se aplica. A atividade é desenho e documentação técnica |
| Sócio em conversa | Tem empresa própria no **Simples Nacional** |

> Dados conferidos direto no cadastro da Receita em 01/08/2026 (via BrasilAPI), não de memória.
> O endereço acima é o que vai na qualificação do CONTRATADO no contrato — está no `.env`
> como `BORIN_ENDERECO` e entra sozinho no PDF gerado por `comercial/contrato.py`.

### Decisão sobre o CNAE (01/08/2026)

O CNAE registrado é de *instalação* de máquinas; o que se vende é *elaboração de projeto e
documentação técnica*. São atividades diferentes.

**Decisão do Mateus: fica como está.** Um amigo dele opera MEI com esse mesmo CNAE, mesmo perfil
de cliente pequeno, e as notas passam. Abre ME mais adiante, depois de uns 5 projetos.

### O que a pesquisa em fonte oficial acrescentou (01/08/2026)

Detalhe completo em `comercial/enquadramento.md`. O que muda a leitura da decisão acima:

- **O CNAE 3321-0/00 continua válido no MEI.** Não foi removido. Consta da Tabela A do Anexo XI da
  Resolução CGSN 140/2018, versão consolidada de 16/10/2025. Essa parte da premissa está certa.
- **Mas não existe CNAE de projeto disponível no MEI.** Buscando as ~471 ocupações do Anexo XI
  inteiro, nenhuma contém "projetista", "desenhista" ou "engenh". Os CNAEs 7119-7/03 e 7112-0/00
  não estão lá. Ou seja: **"incluir o CNAE certo" não é uma opção** — a correção seria sair do MEI.
- **O que conta é a ocupação, não a descrição do CNAE.** Manual do Desenquadramento do SIMEI
  (Receita, abril/2025, item 4.3): *"considere sempre a descrição do campo 'ocupação', nunca a
  descrição da subclasse CNAE"*. A ocupação registrada é INSTALADOR DE MÁQUINAS E EQUIPAMENTOS
  INDUSTRIAIS INDEPENDENTE.
- **O risco não é a multa.** A multa por não comunicar desenquadramento é R$ 50 (LC 123/2006,
  art. 36-A). O que pesa é o item 8 do mesmo Manual: se o fisco entender que a ocupação de
  instalador nunca foi exercida, o desenquadramento é de ofício e **retroage a 18/03/2026**, com
  todo o faturamento recalculado como ME — e só se desfaz por processo administrativo.

**Teste de cinco minutos, antes de qualquer conversa com contador:** abrir o Emissor Nacional
(`nfse.gov.br/EmissorNacional`) com o CNPJ e ver quais códigos de serviço aparecem. Se só vier
código de instalação, a pergunta se responde sozinha, de graça, sem depender de opinião.

**Três coisas para perguntar ao amigo** — elas decidem se o precedente dele transfere:
ele é MEI ou já é ME; ele instala alguma coisa de fato ou só projeta; e se já emitiu nota para
cliente que retém ISS.

### O ponto jurídico que afeta o contrato

A Lei 5.194/1966, art. 15, declara **nulos de pleno direito** os contratos referentes a qualquer
ramo da engenharia, "inclusive a elaboração de projeto", firmados com quem não é legalmente
habilitado — e o art. 6º alcança pessoa jurídica, não só física. Num projeto de R$ 15 mil com
cliente que decide não pagar, o próprio contrato pode virar defesa dele.

Isso reforça o que `modelo-contrato.md` já faz: descrever o entregável (documentação técnica,
diagramas, listas, conferência), sem se apresentar como responsável técnico e sem a palavra
"Engenharia" em lugar nenhum. Vale revisar com advogado com esse artigo na mão.

**Porta que existe e não estava no radar:** "legalmente habilitado" não é sinônimo de engenheiro
com CREA. A Lei 5.524/1968 e o Decreto 90.922/1985 (art. 4º, V e §2º) reconhecem ao **técnico
industrial** a responsabilidade por projeto compatível com a formação — o §2º cita expressamente
projetar instalações elétricas até 800 kVA. O registro é no CFT/CRT desde a Lei 13.639/2018.
Depende de diploma técnico. **Vale uma ligação para o CRT-RS.**

**Detalhe que aparece em todo documento:** a razão social do MEI é o número do CNPJ mais o nome —
`65.749.097 MATEUS BORIN`. É isso que vai na nota fiscal e na qualificação das partes do contrato.
**Borin Projetos Elétricos** é nome fantasia: usa no papel, no site, na assinatura e no carimbo, mas
não substitui a razão social em documento formal. Já preenchido em `modelo-contrato.md`.

MEI está certo para começar: custo fixo baixo, DAS mensal de valor único, nota de serviço simples.
O problema não é hoje — é o teto.

---

## O teto do MEI vai estourar, e a conta diz quando

| | |
|---|---|
| Teto do MEI, ano cheio | **R$ 81.000/ano** → R$ 6.750/mês. Confirmado na LC 123/2006, art. 18-A §1º |
| **Teu teto em 2026** | **R$ 67.500** — proporcional, veja abaixo |
| Faturamento necessário para a meta | **R$ 8.940/mês** → R$ 107.280/ano |
| Excedente projetado | ~**32% acima do teto cheio** |

> **O teto de 2026 não é R$ 81 mil.** O CNPJ abriu em 18/03/2026, e no ano de início a lei
> manda multiplicar R$ 6.750 pelos meses até dezembro — 10 meses, contando março inteiro
> (LC 123/2006, art. 18-A, §2º). Dá **R$ 67.500**. Passar disso em até 20% (ou seja, até
> R$ 81.000) gera DAS complementar e desenquadramento em 01/01/2027. Passar de R$ 81.000
> desenquadra **retroativo a 18/03/2026**, com tudo recalculado como ME.
>
> E não conte com aumento: os R$ 110 mil / R$ 140 mil que aparecem na página do gov.br são
> o PLP 186/2026, ainda em tramitação em 01/08/2026. Não virou lei.

Pela tabela de `precificacao.md`, **um Escopo A grande (R$ 8.200) ou um B grande (R$ 11.700) já
estoura o mês.** Não é cenário distante: é o primeiro projeto grande.

### Plano do Mateus (29/07/2026)

Seguir no MEI por enquanto e **abrir o Simples depois de faturar um pouco**, quando o teto se
aproximar. Parceria com o sócio segue **verbal, sem papel**, por decisão dele.

### O ajuste de timing que esse plano precisa

A regra de desenquadramento tem dois patamares — confirmar com o contador, mas a lógica é esta:

- **Excedeu até 20%** — no teu caso de 2026, entre R$ 67.500 e R$ 81.000 → paga DAS complementar e
  sai do MEI em 1º de janeiro de 2027
- **Excedeu mais de 20%** — acima de R$ 81.000 → sai **retroativo a 18/03/2026**, data de abertura do
  CNPJ, com todo o faturamento do período recalculado como ME

Ou seja: *"abro o Simples quando passar"* funciona se a migração acontecer **antes** de cruzar a
linha. Se cruzar primeiro e abrir depois, o retroativo já foi gerado — e pela projeção de
R$ 8.940/mês o excedente seria de ~32%, dentro do segundo patamar.

**Regra prática: quando o faturamento acumulado do ano chegar em ~R$ 55 mil, começar a abrir o
Simples.** Aí sobra um projeto grande de folga para o processo correr sem pressa. Em 2026 a linha
de corte é R$ 67.500, não R$ 81 mil — esperar chegar nela é apertado, passar dela é caro.

### Por que o gatilho é valor acumulado, e não número de projetos

O plano de "abrir ME depois de uns 5 projetos" fecha — mas com **menos folga do que parecia**,
porque o teto de 2026 é R$ 67.500 e não R$ 81 mil:

| 5 projetos | Acumulado | Do teto de 2026 (R$ 67.500) |
|---|---|---|
| 5 × Escopo A pequeno (R$ 3.500) | R$ 17.500 | 26% |
| 5 × típico (R$ 6.700) | R$ 33.500 | 50% |
| 5 × Escopo B grande (R$ 11.700) | R$ 58.500 | **87%** |

**Seis Escopo B grandes já dão R$ 70.200 e passam do limite de 2026.** Contar projeto não serve de
controle, porque o mesmo "5 projetos" pode ser R$ 17 mil ou R$ 58 mil. Contar dinheiro serve.

**Gatilho corrigido: R$ 55 mil acumulados** — não R$ 65 mil. Os R$ 65 mil foram calculados contra o
teto errado; contra R$ 67.500 eles deixam só dois mil e quinhentos de folga, o que não dá tempo de
abrir empresa. R$ 55 mil deixa um projeto grande inteiro de margem.

- [ ] Anotar o faturamento acumulado do ano a cada nota emitida — controle simples, uma linha por nota
- [ ] Gatilho: acumulado ≥ R$ 55 mil → procurar contador e iniciar a abertura do Simples
- [x] Teto e regra de excedente confirmados em fonte oficial — ver `enquadramento.md`
- [ ] Abrir o Emissor Nacional e ver quais códigos de serviço aparecem para o CNPJ (5 minutos)

---

## MEI e sociedade não convivem

Regra a confirmar com o contador, mas é conhecida: **MEI não pode ser sócio, titular ou administrador
de outra empresa.** Se for, perde a condição de MEI.

Hoje isso não é problema: **a parceria é verbal, sem participação societária no papel** — decisão do
Mateus em 29/07/2026. O MEI está preservado.

Vira problema no dia em que a sociedade for formalizada. Três cenários:

| Arranjo | O que acontece com o MEI |
|---|---|
| Ele só **indica** cliente e você fatura pelo seu MEI | MEI mantido. Mais simples de todos |
| Você entra como **sócio** na empresa dele | **Perde o MEI.** Vira sócio de ME no Simples |
| Ele fatura pelo Simples dele e te paga | MEI mantido, mas ver a seção abaixo |

Ou seja: virar sócio de fato não é só uma decisão de relacionamento — **desenquadra teu MEI
automaticamente.** Antes de assinar qualquer coisa societária, essa conta precisa estar feita.

---

## Faturar pelo Simples do sócio — o que ninguém avisa

É arranjo comum e resolve o teto no curto prazo. Mas tem uma consequência estrutural que não é
tributária:

**Se a nota sai do CNPJ dele, o cliente é dele.** Contratualmente, quem presta o serviço é a empresa
que fatura. Você aparece como subcontratado. Isso significa:

- O histórico de faturamento e a referência comercial ficam na empresa dele, não na sua
- Se a parceria acabar, os clientes têm relação formal com ele
- O seu portfólio próprio não se constrói — e portfólio é o que você não tem hoje

A alíquota efetiva também muda: a receita entra na faixa do Simples **dele**, que pode ser maior que a
sua por já ter faturamento acumulado.

**Não é motivo para descartar** — resolve um problema real de teto. É motivo para decidir consciente,
e para pelo menos alternar: projeto que vem por indicação dele fatura por ele; cliente que você
originar fatura pelo seu CNPJ. Assim você constrói histórico próprio em paralelo.

- [ ] Definir a regra de quem fatura o quê, antes do primeiro projeto
- [ ] Perguntar ao contador o impacto de faixa no Simples dele

---

## Simples Nacional — quando migrar, o Anexo decide a alíquota

Vale para quando sair do MEI. Serviço de desenho técnico cai no **Anexo III ou no Anexo V**, e quem
decide é o **Fator R**:

```
Fator R  =  folha de pagamento dos últimos 12 meses  ÷  faturamento dos últimos 12 meses
```

| Fator R | Anexo | Alíquota inicial |
|---|---|---|
| **≥ 28%** | Anexo III | cerca de **6%** |
| < 28% | Anexo V | cerca de **15,5%** |

Numa empresa de uma pessoa, "folha" inclui o **pró-labore** — o que você formalmente paga a si mesmo.
Pagar pró-labore suficiente para bater 28% derruba a alíquota de ~15,5% para ~6%. Em R$ 8.940/mês, a
diferença bruta é da ordem de **R$ 850/mês**.

**Perguntas ao contador:**

1. Minha atividade cai no Anexo III ou V?
2. Qual pró-labore mensal me mantém com Fator R acima de 28%?
3. O encargo desse pró-labore (INSS patronal, INSS do sócio, IRPF) é menor que a economia de
   alíquota? Compensa líquido?
4. Como o Fator R é apurado no primeiro ano, sem histórico de 12 meses?

A pergunta 3 é a única que importa. As outras três só existem para chegar nela.

---

## Nota fiscal de serviço

Serviço é tributado pelo município. Caxias do Sul emite **NFS-e** por sistema próprio da prefeitura.

- [ ] Confirmar acesso ao sistema de NFS-e e a alíquota de ISS da atividade
- [ ] Confirmar se o ISS é retido pelo cliente ou pago por você — muda o que entra na conta
- [ ] Emitir a primeira nota **junto com o contador**, para aprender o caminho

O fluxo comercial já define: **nota emitida junto com a entrega, nunca depois.**

---

## Custo fixo mensal

| Item | Hoje (MEI) | Depois (ME) |
|---|---|---|
| DAS / Simples | DAS fixo mensal | 6% ou 15,5% do faturamento |
| Contador | opcional no MEI | R$ 300 a 500/mês |
| Domínio | R$ 3,33/mês | igual |
| Email | R$ 0 (Cloudflare) | Zoho Mail Lite, ~US$ 1/mês |
| Licença de CAD | R$ 0 | R$ 0 até entrar outra pessoa |

A precificação atual (`precificacao.md`) assume **R$ 400/mês de contador e 6% de imposto** — cenário
de ME no Anexo III. **Enquanto for MEI, o custo real é menor e a margem é maior que a tabela diz.**
Não baixe o preço por causa disso: a folga é temporária e vira custo no desenquadramento.

---

## Ordem de execução

1. [x] CNPJ aberto — MEI
2. [x] CNAE decidido: segue no 3321-0/00 enquanto o cliente for pequeno. Revisar ao entrar
       cliente grande, ou junto com a migração para ME
3. [x] Estratégia definida: MEI agora, Simples depois de uns 5 projetos
4. [ ] **Conta bancária PJ**, separada da pessoal. Sem exceção
5. [ ] Acesso ao sistema de NFS-e de Caxias e primeira nota de teste
6. [ ] Controle do faturamento acumulado do ano — uma linha por nota emitida
7. [ ] Ao bater ~R$ 55 mil acumulados: iniciar a abertura do Simples
8. [ ] Definir a regra de quem fatura (seu MEI x Simples do sócio) antes do primeiro projeto
9. [ ] Revisar `comercial/modelo-contrato.md` com advogado antes do primeiro contrato

O passo 3 não é preciosismo. Misturar conta pessoal e da empresa inviabiliza saber se o negócio dá
lucro, e é o erro mais comum em negócio de uma pessoa.

---

## Conflito de interesse com a FlowSistem

Burocracia também, e a de maior custo se der errado.

Você presta serviço na FlowSistem e vai prospectar integradoras e fabricantes de máquina da Serra —
alguns concorrentes diretos dela. E o sistema de geração que sustenta sua margem roda hoje sobre a
instalação e os dados da empresa.

1. **Cliente.** Pode atender empresa que compete com a FlowSistem? Se houver algo escrito ou
   combinado, precisa ser lido antes
2. **Ativo.** O código é seu; dados, biblioteca de macros e projetos são deles — já registrado em
   `CONFERENCIAS/AGENTS.md`. Levar o sistema para cliente próprio é levar o código limpo
3. **Tempo.** Projeto próprio é noite e fim de semana. No dia em que ocupar horário de trabalho,
   deixa de ser paralelo

- [ ] Ler o contrato com a FlowSistem: exclusividade, não-concorrência, propriedade intelectual
- [ ] Decidir se a conversa será aberta com eles — e registrar a decisão

Não existe resposta certa, mas existe resposta informada. Ler o contrato é o mínimo.
