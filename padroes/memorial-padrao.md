# Memorial descritivo — respostas padrão

> Os seis blocos do memorial (`padrao-entrega.md`) com **as respostas que não mudam já preenchidas**.
>
> Pra que isso serve: o memorial tem cerca de 45 campos, e uns 33 deles são a mesma coisa em todo
> painel. Redecidir a cada projeto é onde entra divergência entre um projeto e o seguinte — e
> divergência entre projetos é o que faz o cliente perguntar qual dos dois está certo.
>
> **Fixo** = transcreve igual. **Do projeto** = muda a cada trabalho, e a coluna diz de onde sai o valor.
>
> Escrito em 05/08/2026, a partir de `padroes/padrao-entrega.md`.

---

## 1. Características técnicas

| Campo | | Valor |
|---|---|---|
| Cliente | do projeto | razão social do contratante, do contrato |
| Tensão nominal | do projeto | da alimentação disponível no cliente |
| Frequência | **fixo** | 60 Hz |
| Tensão de comando | do projeto | tipicamente 24 VCC; 220 VCA quando o cliente exige |
| Corrente nominal | do projeto | da capa, tem que bater com a proteção geral |
| Corrente de curto-circuito (Icc) | do projeto | **pergunta pro cliente, não estime.** Define a capacidade de interrupção dos disjuntores |
| Normas aplicáveis | **fixo** | IEC 60204-1 · IEC 61082 · IEC 81346 · NFPA 79 · NR-10 · NR-12 |
| Forma de montagem | do projeto | conforme IEC 61439 |
| Painel testado | do projeto | marcar conforme o combinado no escopo |
| Esquema de aterramento | do projeto | TN-S é o comum em indústria; confirmar com o cliente antes de marcar |

> **Icc é o único campo desta folha que não dá pra chutar.** Ele decide a capacidade de interrupção
> de todo disjuntor do painel. Errar pra baixo é o defeito que só aparece no dia do curto.

---

## 2. Estrutura

| Campo | | Valor |
|---|---|---|
| Fornecedor | do projeto | do layout / da lista de materiais |
| Dimensões (A × L × P) | do projeto | tem que bater com o design térmico e com o layout |
| Material | do projeto | aço carbono no padrão; inox em ambiente corrosivo ou de lavagem |
| Grau de proteção | do projeto | IP54 abrigado, IP65 exposto — confirmar com o ambiente do bloco 3 |
| Cor RAL | **fixo** | RAL 7032 salvo pedido do cliente |
| Tipo de pintura | **fixo** | pintura eletrostática a pó |
| Placa de montagem | do projeto | dimensão tem que bater com o layout |
| Fixação | do projeto | autoportante, de parede ou embutido |
| Entrada e saída de cabos | do projeto | inferior no padrão; superior quando o piso é lavado |
| Lado de acesso | do projeto | frontal, ou frontal e traseiro |
| Acessórios | do projeto | iluminação interna, tomada de serviço, bolsa de documentos |

---

## 3. Condições de serviço

| Campo | | Valor |
|---|---|---|
| Temperatura ambiente máxima | **fixo** | **35 °C** — é o valor que o cálculo térmico usa |
| Temperatura interna admissível | **fixo** | **50 °C** |
| Ambiente da instalação | do projeto | marcar área classificada, corrosivo, úmido ou próximo do mar |
| Local | do projeto | abrigado ou ao tempo |
| Temperatura de sala | do projeto | só quando o painel fica em sala elétrica climatizada |

> Os 35 °C não são enfeite: mudar esse número muda o ΔT admissível, e o ΔT decide se o painel
> precisa de ventilação forçada ou climatizador. Se o cliente disser que a área passa de 35 °C,
> **refaz o cálculo antes de fechar o layout**, não depois.

---

## 4. Condutores

| Campo | | Valor |
|---|---|---|
| Isolação de comando | **fixo** | 750 V, PVC flexível |
| Isolação de potência | do projeto | conforme a tensão e a bitola do circuito |
| Seção padrão de comando | **fixo** | **0,5 mm²** quando não especificada no diagrama |
| Barramento | do projeto | só quando houver; declarar material e seção |

### Tabela de cores por função

| Função | Cor |
|---|---|
| Fase R (L1), S (L2), T (L3) | preto |
| Neutro | azul claro |
| Terra (PE) | verde/amarelo |
| Comando CA | vermelho |
| Comando CC — V+ (24 VCC) | vermelho |
| Comando CC — V− (0 VCC, comum) | **⚠ ver a divergência abaixo** |
| Sinal 24 VCC | cinza |
| Tensão externa (não desliga na seccionadora) | laranja |

> ### ⚠ Divergência a resolver — o 0 VCC tem duas cores no teu próprio material
>
> Achado em 05/08/2026, comparando os dois lugares onde a regra está escrita:
>
> | Onde | O que diz o 0 VCC |
> |---|---|
> | `padroes/padrao-entrega.md`, linha 247 | **marrom** |
> | `site/_padrao.html`, tabela `CORES_LINHAS` — a que o **cliente preenche** no orçamento | **azul** |
>
> As duas convivem hoje porque nenhum projeto saiu ainda. No dia em que sair, o cliente vai ter
> aprovado "azul" no formulário e recebido "marrom" no memorial — e quem vai descobrir é o
> eletricista, com o painel montado.
>
> Tem mais duas diferenças menores na mesma comparação: o `padrao-entrega.md` tem **sinal 24 VCC
> cinza** e o formulário não; o formulário tem **tensão externa laranja** e o `padrao-entrega.md`
> não. Os dois valores são bons — só precisam existir nos dois lugares.
>
> **Decisão tua, não minha.** Escolhe a cor do 0 VCC e eu acerto os dois arquivos de uma vez.
> Enquanto não escolher, este campo fica marcado assim de propósito: memorial com campo em branco
> alguém preenche; memorial com campo errado ninguém percebe.

---

## 5. Identificação

| Campo | | Valor |
|---|---|---|
| Dispositivos | **fixo** | letra identificadora + contador, conforme **IEC 81346** |
| Fios | **fixo** | tag em luva, exceto 24 V e 0 V |
| Exceção do 24 V / 0 V | **fixo** | não levam tag nem luva — são identificados **pela cor** |
| Bornes | **fixo** | régua X0, X1, X2… numeradas na ordem do diagrama |

---

## 6. Observações

Bloco de exceções. O que costuma entrar:

- Fios de 24 V e 0 V identificados pela cor, sem tag nem luva
- Circuito alimentado por tensão externa que **não desliga na seccionadora geral** — identificar em
  laranja e sinalizar na porta
- Componente fornecido pelo cliente, quando houver, com a responsabilidade de especificação dele
- Ponto do escopo que ficou de fora por decisão registrada na proposta

> Bloco vazio é bandeira vermelha na conferência. Projeto sem nenhuma exceção é raro — quase sempre
> significa que a exceção existe e não foi escrita.

---

## O que ainda falta pra este memorial virar folha de projeto

Isto aqui é o **conteúdo**. A folha em si precisa ser montada no CAD, e depende de estar na máquina:

- [ ] Folha de memorial com os seis blocos, campos e caixas de seleção
- [ ] Marcador de logo do cliente no carimbo — pronto em `marca/png/placeholder-logo-cliente.png`
- [ ] Decidir a cor do 0 VCC e acertar os dois arquivos
