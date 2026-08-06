# Contexto da Empresa — Mateus Borin

**Nome:** Mateus Borin
**Negócio:** Borin Projetos Elétricos
**O que faz:** projeto elétrico industrial completo, do início ao fim — diagramas, listas de materiais, tags, I/Os e padronização, usando CAD elétrico
**Perfil:** freelancer
**Atende clientes:** sim (externos)
**Equipe:** solo — sem sócio, equipe ou terceirizado
**Ferramentas:** CAD elétrico, Excel, Claude Code. Também usa Python e Node.js em automações pontuais. LOGO! Soft Comfort V8 (Siemens) no aprendizado de CLP
**Principais entregas:** projeto elétrico completo em CAD elétrico, diagramas, lista de materiais, lista de tags e I/Os, padronização de projeto, conferência/revisão de projeto, planilhas técnicas de apoio

## Contexto adicional

**Nome da marca:** Borin Projetos Elétricos (definido em 26/07/2026). Marca gráfica prevista:
monograma `BRN` ou a assinatura `BORIN` em caixa alta, peso alto, monocromática, com o descritor
"projetos elétricos industriais" em corpo menor embaixo.

**Domínio:** `borinprojetos.com.br` estava livre em 26/07/2026 e é o alvo de registro
(`borin.com.br` está ocupado).

**Por que nome próprio e não marca abstrata:** foram avaliadas duas rodadas de nomes abstratos e
termos técnicos (Fasor, Farad, Gauss, Neper, Estator, Entreferro, Quadratura, Prumo). Fasor chegou a
ser escolhido e foi descartado por já existirem quatro empresas do mesmo ramo com esse nome
(Fasor Engenharia, Fasor Serviços Elétricos, Fasor Tecnologia, Fasor Eletricidade). A conclusão foi
que nome abstrato exige construir reconhecimento do zero, e o canal de venda dele é indicação — onde
o nome próprio já carrega o lastro. Não reabrir essa discussão sem motivo novo.

**Formação e habilitação:** Mateus é **projetista**, não engenheiro eletricista — cursa Engenharia
Civil na FSG. O tipo de trabalho que ele vende (projeto e documentação técnica de sistemas elétricos
industriais) não exige ART nem engenheiro para assinar. Consequências práticas:
- Não usar a palavra "Engenharia" no nome, material ou assinatura — é termo com registro no CREA
- Posicionar como projetista / projeto e documentação técnica, nunca como serviço de engenharia
- Se um cliente exigir ART (obra ou máquina sob NR-12), precisa de engenheiro eletricista parceiro para assinar — ainda não tem esse parceiro mapeado

**Situação atual:** trabalha como terceiro na FlowSistem (Caxias do Sul/RS), fabricante de sistemas de
pintura industrial (dosagem e aplicação de fluidos). É o projetista elétrico único da empresa e está
implantando o padrão CAD elétrico lá. O negócio próprio é paralelo e está sendo estruturado agora.

**Público-alvo:** em aberto — pode ser integrador/fabricante de máquina, indústria direta ou escritório
de engenharia. Os primeiros clientes devem vir por indicação de contatos.

**Domínio técnico:** pintura industrial (Promix/Graco, Viscon, HotSpray, aplicação eletrostática,
pintura robotizada), painéis de controle elétrico, automação industrial. Clientes já atendidos via
empresa: John Deere, Meritor.

**Nível:** avançado em CAD elétrico (cria projetos completos e define padrão). Iniciante em programação de CLP.

**Normas que usa como base:** IEC 81346 (tags), IEC 61082 (documentos), NFPA 79 (fios),
IEC 60204-1 (cores).

**Padrões técnicos já definidos (herdados do trabalho de padronização):**
- Cores de cabo: potência preto, neutro azul claro, PE verde/amarelo, 24VCC vermelho, comando cinza, 0VCC marrom
- Proteção CLP: fusível 2A (CPU/fonte), fusível 1A por módulo de I/O
- Demais: disjuntor para fonte, tomada, ar-condicionado e ventilador; DJM para inversor e RFF
- Filosofia de banco de dados: enxuto, poucos artigos, alta repetição

**Formação:** cursa Bacharelado em Engenharia Civil na FSG (Caxias do Sul/RS).

**Serviço futuro:** programação de CLP, quando dominar a parte de programação.

**Ativo próprio — sistema de automação EPLAN:** desenvolveu por conta própria um sistema que gera
projeto elétrico a partir de uma ficha preenchida e confere o resultado contra o padrão da empresa
(macros, colagem, numeração, relatórios, PDF e listas; conferência de tags, cabos, bornes, BOM e
corrente). É ferramenta dele: usa no dia a dia na FlowSistem, onde presta serviço, e leva pra onde
for. Fica em `CONFERENCIAS/` no workspace.

**Ganho medido: cerca de 8x mais rápido na execução** que o processo manual usado por integradoras,
escritórios e fabricantes grandes — e mais assertivo, porque o gerador confere o próprio resultado.
Isso é a vantagem competitiva central do negócio, não um detalhe técnico. Consequências que valem
pra qualquer conversa comercial:

- **Preço nunca se calcula pela hora dele.** Precificação é por valor de mercado (o que o projeto
  custa feito à mão). O 8x é margem, prazo e capacidade — nunca desconto. Detalhe em
  `comercial/precificacao.md`
- **Nunca abrir hora na proposta.** Preço fechado por escopo, sempre. Se o cliente souber que o
  projeto levou 9h, a conversa vira sobre a hora e ele perde
- A trava do negócio deixou de ser capacidade e passou a ser demanda — o gargalo é quantos clientes
  chegam, não quanto ele consegue produzir
- É base de um segundo serviço vendável: padronização e automação de CAD elétrico pra quem já tem
  EPLAN (concorrente direto identificado: EPLAN eBuild)

**Licença:** o sistema automatiza o EPLAN, não substitui — precisa do EPLAN rodando do outro lado
(`garantir_eplan.py`, jobs em C# contra a Eplan.EplApi). O que ele dispensa é o módulo pago de
automação (eBuild/Cogineer), e isso é argumento comercial legítimo. **Decisão de 29/07/2026:
começar sem custo de licença própria.** Revisar quando entrar outra pessoa no trabalho — aí a
licença vira necessária e toda a precificação sobe.

Cuidado ao citar: o código é dele, os dados dentro da pasta são da FlowSistem — nunca mostrar
projeto real como portfólio sem autorização.
