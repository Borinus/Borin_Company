# Perfil de Padrão do Cliente

> **Preenchido uma vez, vale para todos os projetos daquele cliente.**
>
> É o que separa o que muda a cada projeto (máquina, I/Os, prazo) do que nunca muda (marcas, cores,
> normas, códigos). Sem isso, a mesma discussão se repete em todo pedido.
>
> Copie este arquivo para `clientes/[nome-cliente]/perfil-padrao.md` e preencha junto com o cliente.

---

**Cliente:**
**Responsável técnico:**
**Preenchido em:**
**Revisão:**

---

## 1. Elétrica básica

| Item | Definição |
|---|---|
| Tensão de alimentação | |
| Tensão de comando | |
| Frequência | |
| Esquema de aterramento | TN-C · TN-S · TT · IT |
| Corrente de curto-circuito presumida (Icc) | |
| Tensão de sinal | |

## 2. Normas e obrigatoriedades

Marcar o que é **sempre** exigido, para não perguntar de novo a cada projeto.

| Item | Sempre? | Observação |
|---|---|---|
| NR-12 | [ ] | |
| NR-10 / prontuário | [ ] | |
| Botão de emergência no painel | [ ] | |
| Botoeira de emergência em campo | [ ] | |
| Relé de segurança | [ ] | marca preferida: |
| Cortina de luz / scanner | [ ] | |
| Seccionadora com bloqueio | [ ] | |
| Sinaleiro de painel energizado | [ ] | |
| Idioma da documentação | | |
| Norma de tag adotada | | IEC 81346 ou padrão próprio |

## 3. Cores de cabo

| Função | Cor |
|---|---|
| Fase R / S / T | |
| Neutro | |
| Terra | |
| 24 VCC | |
| 0 VCC | |
| Sinal 24 VCC | |
| Comando CA | |
| Interbloqueio / tensão externa | |

**Seção padrão quando não especificada no diagrama:**

## 4. Marcas por família de componente

O cliente escolhe uma vez. Em projeto novo, só se avisa quando fugir do padrão.

| Família | Marca padrão | Alternativa aceita | Proibida |
|---|---|---|---|
| Bornes | | | |
| Disjuntores | | | |
| Contatores | | | |
| Relés e bases | | | |
| Fonte 24 VCC | | | |
| CLP e módulos de I/O | | | |
| IHM | | | |
| Inversor de frequência | | | |
| Servo / motion | | | |
| Botoeiras e sinaleiros | | | |
| Sensores | | | |
| Cabos | | | |
| Conectores de campo | | | |
| Quadro / estrutura | | | |
| Climatização e ventilação | | | |
| Rede e switches | | | |

## 5. Painel — construção

| Item | Definição |
|---|---|
| Fabricante do quadro | |
| Material da estrutura | |
| Grau de proteção padrão | |
| Cor RAL | |
| Tipo de pintura | |
| Fixação | soleira · suporte · parede |
| Entrada e saída de cabos | superior · inferior |
| Lado de acesso | traseiro · lateral · frontal |
| Temperatura ambiente de projeto | |
| Acessórios sempre presentes | porta-documentos, tomada, iluminação, ventilador… |

## 6. Identificação

| Item | Definição |
|---|---|
| Padrão de tag de dispositivo | |
| Padrão de tag de cabo | |
| Padrão de numeração de fio | |
| Fios 24 V e 0 V levam tag? | |
| Impressora de etiquetas | |
| Modelo de etiqueta — fio | |
| Modelo de etiqueta — cabo | |
| Modelo de etiqueta — borne | |
| Modelo de etiqueta — dispositivo | |

## 7. De/para de códigos

O item mais trabalhoso de montar e o que mais economiza tempo depois. Uma linha por material que o
cliente já tem cadastrado no ERP.

| Código ERP do cliente | Descrição no ERP | Fabricante | Referência do fabricante | Família |
|---|---|---|---|---|
| | | | | |

**Sistema ERP do cliente:**
**Quem mantém o cadastro do lado dele:**

> Manter também como planilha em `clientes/[nome]/de-para-erp.xlsx` — em projeto grande, esta tabela
> passa de mil linhas e é ela que faz a lista de materiais sair pronta para compra.

## 8. Entrega

| Item | Definição |
|---|---|
| Formatos exigidos | PDF · Excel · DWG · CAD elétrico |
| Nomenclatura de arquivo do cliente | |
| Onde entregar | link, pasta compartilhada, portal |
| Quem aprova tecnicamente | |
| Prazo padrão de aprovação | |
| Quantas vias impressas, se houver | |

## 9. Observações e exceções

Regras que não couberam acima, e casos em que o cliente abre exceção ao próprio padrão.

---

## Como usar

**No primeiro contato**, pergunte se o cliente já tem padrão documentado. As três situações:

1. **Tem padrão e entrega documentado** — transcrever para este arquivo, confirmar e seguir
2. **Tem padrão na cabeça, não no papel** — uma reunião de uma hora resolve a maior parte
3. **Não tem padrão** — é serviço à parte, cobrado: uma ou duas reuniões de definição, e a entrega é
   este documento preenchido. Vale por si só, mesmo que ele nunca contrate outro projeto

**Depois de preenchido**, todo projeto daquele cliente começa daqui. O checklist do projeto passa a
perguntar só o que muda: qual máquina, quantos I/Os, qual prazo.

**Revisar** quando o cliente trocar de marca, de ERP ou de norma. Toda mudança sobe a revisão no topo.
