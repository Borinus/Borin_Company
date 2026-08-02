# Revisão do contrato — pauta para o advogado

> Levantada em 02/08/2026 por quatro leituras independentes (nulidade, lacuna, ambiguidade
> e o lado do cliente), cada achado atacado por um cético que foi conferir o trecho no
> arquivo. **16 achados, nenhum derrubado.**
>
> A seção *O que eu conserto agora* JÁ FOI APLICADA no `modelo-contrato.md`. Ela fica aqui
> como registro do que mudou e por quê. As outras três seções são para levar à conversa.

---

## O que eu conserto agora

Tudo abaixo é edição de texto no `comercial/modelo-contrato.md`. Marquei em cada item se toca o gerador.

**1. Cláusula 19 — hoje ela permite o cliente cancelar e pedir os 40% de volta**

O critério é "páginas emitidas". Emissão é evento: pode haver três semanas de levantamento e arquitetura de diagrama com zero página emitida. Nesse ponto o proporcional é zero, e como a parcela inicial é "compensada", a leitura literal é devolução de R$ 2.680 no ticket típico, com o trabalho quase todo feito. Substituir a cláusula inteira:

> **19.** Qualquer das partes encerra o contrato com aviso escrito de 15 dias. Encerrado ou interrompido o contrato por qualquer causa, iniciada a execução, é devido a BORIN o valor proporcional ao serviço executado até a data, apurado pelas páginas emitidas ou em elaboração e pelos demais documentos e levantamentos já produzidos, aplicado o preço por página da cláusula 13; a parcela inicial não é restituída e serve de crédito contra esse valor. Quitado o saldo, o CLIENTE recebe o que estiver pronto, identificado como emissão parcial e não apta à fabricação, à montagem ou à energização.

Ganhos, em ordem: a métrica passa a alcançar o trabalho em elaboração; a entrada vira piso e não teto móvel; a entrega fica condicionada à quitação (hoje o cliente cancela, não paga e leva o material); e o "aplicado o preço por página da cláusula 13" deixa pré-fixado, por escrito e pelas duas partes, quanto vale o trabalho — o que serve de aritmética pronta se um dia a discussão virar quanto se deve, e não se se deve. Não toca o gerador.

**2. Cláusula 3 — tira a promessa de "funcionar"**

"Em condições de ser usada na fabricação e na montagem" e "o compromisso dele é a documentação funcionar" são padrões abertos, sem parâmetro, e mais largos que o gatilho da cláusula 8. Cliente adversário nunca pede "revisão": ele diz que "não está em condições de ser usada" porque o montador reclamou. A cláusula 3 dá correção gratuita e ilimitada sem ele ter de apontar divergência com nada. Substituir:

> **3.** BORIN responde pela documentação que elabora: ela é entregue coerente com a Ficha Técnica, com o escopo contratado e com o Padrão de Entrega, e consistente entre suas próprias folhas, cabendo ao CLIENTE a verificação e a aprovação técnica da cláusula 4. Divergência, erro ou omissão em relação a essas referências — apontada por escrito durante a execução ou ao longo da garantia da cláusula 15, inclusive quando aparecer na fabricação, na montagem ou na partida do equipamento — BORIN corrige sem custo, sem limite de acionamentos e sem consumir rodada, na forma da cláusula 8. Pedido que não decorra dessas referências é revisão, na forma da cláusula 9, ou alteração de escopo, na forma da cláusula 11.

A frase do "funcionar" não some do negócio: ela vai pra proposta e pro site, onde vende sem obrigar. Não toca o gerador.

**3. Cláusula 8 — quem aponta erro tem que dizer com o que ele diverge**

A cláusula 11 já põe o ônus em você (apontar o campo alterado). Ninguém põe ônus no cliente pra alegar erro. Acrescentar as duas frases finais:

> **8.** Divergência entre a documentação entregue e o escopo contratado ou as premissas da Ficha Técnica é erro de BORIN: ele corrige sem custo, sem limite de acionamentos e sem consumir rodada. Ao apontar erro, o CLIENTE indica por email o item da documentação e o ponto do escopo ou da Ficha Técnica com que ele diverge. Pedido sem essa indicação segue como revisão da cláusula 9; BORIN o executa e comunica o enquadramento por email, e devolve a rodada se a divergência for demonstrada depois.

Isso impede a trava: o trabalho anda, a rodada conta, a emissão segue, o relógio do aceite volta a correr — e continua justo pro cliente que estava certo, porque a rodada volta. Não toca o gerador.

**4. Cláusula 17 — a licença hoje trava a venda do teu cliente**

"O CLIENTE usa e modifica a documentação neste projeto" não diz se a metalúrgica pode entregar o dossiê a quem compra a máquina, usar na segunda unidade igual, ou usar na manutenção dez anos depois. Quem monta série lê isso como "vou pagar de novo por cada unidade" e negocia o preço todo pra baixo, ou o jurídico dele pede cessão total de direitos. Substituir:

> **17.** Pago o preço, o CLIENTE recebe licença definitiva, irrevogável, sem prazo e sem exclusividade para usar, reproduzir e modificar a documentação na fabricação, montagem, operação e manutenção do equipamento do Quadro Resumo, inclusive em unidades adicionais do mesmo equipamento que ele fabricar. A licença acompanha o equipamento: o CLIENTE pode entregar a documentação, inclusive alterada, ao comprador, ao proprietário e a quem faça a manutenção, que a usam para a mesma finalidade. A licença não alcança a venda da documentação como produto em si, separada do equipamento. O arquivo-fonte não integra a entrega; BORIN o arquiva por 5 anos e pode fornecê-lo por preço adicional. BORIN segue livre para reusar seus próprios padrões e seu banco de artigos.

E uma frase no fim da 18, senão o sigilo contradiz a licença — o cliente-alvo entrega o dossiê ao comprador da máquina no curso normal do negócio dele:

> O sigilo não impede o CLIENTE de entregar a documentação nos termos da cláusula 17.

Você continua vendendo separado o que interessa: arquivo-fonte e revisão nova. Não toca o gerador — só não usar colchetes no texto novo, que o regex pinta de vermelho.

**5. Emails — seis cláusulas dependem deles e o contrato não fixa nenhum**

A cláusula 20 manda usar "os endereços da assinatura", e não existe endereço nenhum no recorte que vira contrato: o bloco de assinatura do PDF é montado pelo `contrato.py` com nome, cargo, razão social e CNPJ. Pior que isso: a 20 diz que "aceite só vale por email", o que contradiz de frente os outros dois caminhos da cláusula 12 (conduta e decurso, que por definição não são email). A defesa do cliente cabe numa linha: aceite só vale por email, não há endereços, não houve email, logo não houve aceite — e caem os três caminhos juntos.

Nova linha no Quadro Resumo, depois de **Anexos**:

> `| **Emails oficiais** | CLIENTE: [email], aos cuidados de [nome do representante] · BORIN: contato@borinprojetos.com.br |`

Cláusula 12 inteira:

> **12.** A documentação é entregue por link ou pasta compartilhada, com aviso por email ao endereço oficial do CLIENTE, e considera-se entregue na data do envio desse email. A entrega é aceita por email; por conduta, como pedido de compra pela lista de materiais ou início da montagem; ou por decurso, se passarem 10 dias úteis da entrega sem manifestação do CLIENTE e mais 5 dias úteis após novo aviso de BORIN. Reemissão decorrente de rodada de revisão reabre o prazo apenas quanto ao que foi alterado. O aceite encerra as rodadas e vence a parcela final.

Cláusula 20 inteira (já com a conservação e os sucessores, que hoje faltam e que a versão longa tinha):

> **20.** Alteração deste contrato, aditivo e aceite expresso só valem por email, nos endereços oficiais do Quadro Resumo, ressalvados o aceite por conduta e por decurso da cláusula 12. Comunicação enviada a esses endereços presume-se recebida no primeiro dia útil seguinte ao envio, independentemente de confirmação de leitura, e cabe a cada parte avisar por escrito a mudança de endereço ou de interlocutor. Acerto verbal não muda preço, prazo nem escopo. Este contrato não cria vínculo empregatício, societário nem de exclusividade, e nenhuma das partes o cede sem concordância escrita da outra. A invalidade de uma disposição não afeta as demais, que seguem em vigor, e este contrato obriga as partes e seus sucessores.

**Aviso de gerador, aqui sim.** O rótulo `**Emails oficiais**` é novo e não está no dicionário `linhas` do `contrato.py` (206-227), então a linha passa intacta — é justamente o que a gente quer. Os tokens `[email]` e `[nome do representante]` já são substituídos no dicionário `campos` (248-250), hoje código morto, que volta a ter uso. O email da Borin tem que ir **literal**, porque o `replace` de `[email]` é global e transformaria os dois no email do cliente. E **não** colocar o email dentro da linha `**CONTRATANTE:**` do topo: essa linha é reconstruída inteira pela f-string das linhas 258-264 e o email sumiria calado justamente nos contratos preenchidos — pra fazer lá seria preciso mexer no Python.

**6. Cláusula 7 — você trabalha sozinho e o contrato não admite que você pare**

Só existe suspensão por causa do cliente. Doença, cirurgia, sinistro, queda longa de energia ou internet: nada para o relógio da multa de 0,5% ao dia. O art. 393 do Código Civil ajuda por lei, mas doença do próprio prestador em obrigação personalíssima costuma ser lida como risco da atividade, e aí vira discussão. Escrever converte discussão em regra. Acrescentar ao **fim** da 7:

> Nenhuma das partes responde por atraso decorrente de caso fortuito ou força maior, nos termos do art. 393 do Código Civil, aí compreendidos evento climático extremo, sinistro, interrupção prolongada de energia ou de telecomunicações, ato de autoridade e impedimento temporário de BORIN por motivo de saúde comprovado. A parte afetada avisa a outra por escrito em até 2 dias úteis e o prazo fica suspenso pelo mesmo número de dias, sem multa. Persistindo o evento por mais de 20 dias corridos, qualquer das partes pode encerrar o contrato sem multa, na forma da cláusula 19.

É bilateral e não assusta: o cliente também quer isso pra um incêndio na fábrica dele. Acrescentar no fim, nunca criar cláusula nova no meio — a 3 remete às cláusulas 8 e 15 por número.

**7. Cláusula 5 — proibir menção de autoria empurra o engenheiro do cliente pra uma declaração falsa**

Hoje ela diz que o cliente não te apresenta "a terceiros como responsável técnico ou autor do projeto". O engenheiro dele vai assinar ART sobre desenhos que não elaborou e o contrato o proíbe de dizer quem elaborou — e a cláusula 4 já manda teu nome impresso no campo de elaboração, então a proibição não protege nada e contradiz a 4. É a cláusula com maior chance de travar a assinatura por objeção do corpo técnico, não do jurídico. Substituir o final da 5:

> Em qualquer dos casos, ajuste exigido por critério técnico desse profissional é alteração de escopo. O CLIENTE não apresenta BORIN como responsável técnico pelo equipamento ou pela instalação, nem o indica como responsável ou corresponsável em ART. A indicação de BORIN no campo de elaboração da documentação, na forma da cláusula 4, é permitida e não configura descumprimento desta cláusula.

Você perde o que não protegia e mantém o que protege. Não toca o gerador.

**8. Cláusula 4 — tirar a autodeclaração negativa, e só ela**

"sem título profissional e sem registro em conselho" não produz efeito contratual nenhum e entrega ao jurídico do cliente, por escrito e no documento que vai ser assinado, o gancho pra exigir declaração de habilitação legal e cláusula de indenidade como condição de assinar. O resto da cláusula é a melhor defesa do contrato e fica:

> **4.** A verificação e a aprovação técnica final, antes de fabricar, montar, instalar ou energizar, cabem ao CLIENTE, por seu corpo técnico ou por profissional legalmente habilitado que ele designar. Os campos de verificação, aprovação e responsabilidade técnica são entregues em branco, para preenchimento por esse profissional; no campo de elaboração consta o nome de BORIN. BORIN não assume a responsabilidade técnica pelo equipamento ou pela instalação e não responde por decisão tomada pelo CLIENTE ou por terceiro, nem por execução, material ou montagem que divirjam da documentação entregue.

**Isso só vale com a compensação, senão vira ocultação:** a informação de que você é projetista, sem registro em conselho e sem emitir ART, tem que estar por escrito **antes** da assinatura, na proposta ou no email que a acompanha. Lá ela cumpre a mesma função de boa-fé, mata alegação futura de erro ou dolo, e não fica dentro do documento que o setor de compras encaminha pro jurídico. Não toca o gerador.

**9. Cláusulas 1 e 6 — a Ficha Técnica é anexo e entrega posterior ao mesmo tempo**

O Quadro Resumo lista a Ficha como Anexo II e a cláusula 1 diz que os anexos integram o contrato — anexo é documento que existe e se rubrica na assinatura. Mas a cláusula 7 a trata como documento a ser recebido depois, e é desse recebimento que sai o termo inicial do prazo e, portanto, da tua multa de 0,5% ao dia. Três edições:

Célula de anexos (mantendo a numeração, que o `contrato.py` referencia como "Anexo III" na linha 214):
> `I — Proposta · II — Ficha Técnica, confirmada na forma da cláusula 6 · III — Padrão de Entrega`

Fim da cláusula 1:
> Enquanto a Ficha Técnica não for confirmada, prevalecem o Quadro Resumo e o Padrão de Entrega.

Fim da cláusula 6:
> Considera-se completa a Ficha Técnica emitida por BORIN em PDF datado, com todos os campos preenchidos, e confirmada pelo CLIENTE por email. A partir da confirmação ela é a versão vigente, e só muda por aditivo na forma da cláusula 11.

A linha **Anexos** não está no dicionário de substituição, então trocar o texto dela é seguro. Mexer nos rótulos **Objeto**, **Escopo**, **Proposta**, **Preço total**, **Prazo de entrega** ou nos dois contadores de `[N]` quebra o gerador.

**10. Faxina — três coisas que não são cláusula mas custam caro**

- `padroes/padrao-entrega.md` linha 226 diz "Aceite. Confirmação escrita do cliente, ou automático após **10 dias corridos**". O contrato diz 10 dias **úteis** mais 5 após aviso. São duas regras de aceite tácito dentro do mesmo pacote assinado, e a cláusula 1 só ordena a prevalência entre os anexos, não do corpo sobre eles. Alinhar o anexo com a nova cláusula 12.
- As seções internas do arquivo (linhas 144-188) citam cláusulas 2, 3, 4.3, 5.1, 5.3, 5.4, 6.2, 6.3, 6.4, 7.3 e 2.2 — numeração de uma versão que não existe mais. Isso não vai pro PDF do cliente, mas é o mapa que você vai levar ao advogado; ele nota em 30 segundos e você paga hora pra ouvir que a numeração não bate.
- A "Pergunta para o advogado" nº 2 diz "registro de técnico em eletrotécnica **no CREA**". Está errado desde 2018: técnico industrial registra no CFT/CRT, pela Lei 13.639/2018.

*Uma coisa que eu deliberadamente não escrevi:* cláusula dizendo "se este contrato for declarado nulo, permanece devida a remuneração". Parece esperta e é contraproducente — cai junto com o contrato pelo mesmo motivo que ele cairia, não te dá direito nenhum que os arts. 182 e 884 do CC já não deem, e planta no comprador exatamente a dúvida que o resto do documento foi escrito pra não levantar. Isso é pergunta pro advogado, não cláusula.

---

## O que perguntar ao advogado

1. Eu sou projetista sem CREA e vendo elaboração de diagrama elétrico de painel, com os campos de responsabilidade técnica entregues em branco e a aprovação técnica a cargo do engenheiro do cliente — o art. 15 da Lei 5.194/1966 torna esse contrato nulo, e se tornar, eu ainda recebo pelo serviço já entregue e o teto de responsabilidade da cláusula 16 sobrevive, ou eu caio em responsabilidade extracontratual sem teto e sobre o meu patrimônio pessoal?
2. Se eu tirar diploma de técnico em eletrotécnica e me registrar no CRT-RS (Lei 5.524/1968 e Decreto 90.922/1985, art. 4º, V e §2º, que fala em instalação elétrica até 800 kVA), isso resolve o art. 15 pro meu escopo, e o MEI 65.749.097 também precisa se registrar como pessoa jurídica no conselho?
3. Elaboração de projeto elétrico é obrigação de meio ou de resultado no RS, e se for de resultado por natureza, adianta alguma coisa eu suavizar a redação da cláusula 3 ou eu deveria gastar o esforço todo no teto da cláusula 16?
4. O aceite tácito da cláusula 12 — 10 dias úteis de silêncio mais 5 após novo aviso, com presunção de recebimento por email — basta pra vencer a parcela de 60% num contrato entre empresas, ou eu preciso de notificação por AR antes de o silêncio produzir aceite?
5. Na rescisão, é melhor eu escrever que a entrada não é restituível e que o proporcional se mede por página, ou ficar em silêncio e cair no art. 623 do Código Civil, que me daria despesas mais lucro dos serviços feitos — e escrever "não restituível" pode ser reduzido pelo juiz como cláusula penal excessiva se o cliente desistir na primeira semana (art. 413)?
6. A cláusula 5, que proíbe o cliente de me apresentar como responsável técnico e de me incluir em ART, pode ser lida como ajuste de ocultação ou simulação (art. 167 do CC) e piorar a minha posição em vez de melhorar?

As seis perguntas que já estão no arquivo (teto de responsabilidade, arras dos arts. 417 a 420, foro depois da Lei 14.879/2024, garantia de 12 meses) continuam boas — leve as duas listas, só corrija a numeração das cláusulas antes.

---

## O que ele NÃO deve ceder

- **O teto da cláusula 16 (valor do contrato) e a exclusão de lucros cessantes.** Sem isso, um erro num painel de R$ 6.700 pode responder por uma linha de produção parada. É a única coisa que dimensiona o risco ao tamanho do negócio.
- **A cláusula 4 inteira, agora sem a autodeclaração.** É a espinha dorsal: quem verifica e aprova é o cliente. Ceder aqui é assumir responsabilidade técnica por escrito.
- **A lista de exclusões da cláusula 2** (ART, CLP, IHM, supervisório, montagem, comissionamento, execução, compra de material, visita, arquivo-fonte). Cada item que sair da lista vira trabalho de graça na primeira reunião.
- **Cessão total de direitos patrimoniais, se o jurídico dele propuser no lugar da nova cláusula 17.** A licença ampla já dá ao cliente tudo que ele precisa pra fabricar, revender e manter; cessão entrega padrão, banco de artigos e o direito de te tirar do próprio trabalho.
- **Os 40% como condição para iniciar e a retenção da cláusula 14.** Sem isso você financia o cliente e fica sem instrumento nenhum de cobrança até o fim.
- **A janela de 5 dias da cláusula 10.** É o que impede o cliente mandar um ajuste por dia e nunca fechar uma rodada.
- **Declaração de que você "é legalmente habilitado" ou indenidade ampla por autuação de conselho, se pedirem em troca de assinar.** Declaração de habilitação que você não tem é pior que o problema que ela tenta resolver — leve isso ao advogado antes de assinar qualquer versão dessa frase.

---

## O que segue em aberto

- **Você tem ou não diploma de curso técnico (eletrotécnica, eletromecânica, automação)?** É o fato mais barato de confirmar e o de maior consequência: com ele, o registro no CRT-RS vira a prioridade número 1 do negócio e o contrato deve ser reescrito (a cláusula 4 passa a ter responsabilidade técnica anotada, a 5 troca ART por TRT no que couber). Sem ele, o registro é impossível hoje e a pergunta vira "vale 1,5 a 2 anos de curso técnico?", que é decisão de negócio, não de advogado. Existe ainda disputa institucional aberta entre CONFEA/CREA e CFT sobre os limites de atribuição do técnico — registro reduz muito o risco, não o zera.
- **A Ficha Técnica ainda não existe como documento.** A cláusula 6 nova promete "PDF datado, confirmado por email", e o sistema não produz isso: o `site/worker/acesso.js` grava com `env.CLIENTES.put("ficha:" + email + ":" + tipo, ...)`, que sobrescreve a mesma chave. Não há versão congelada nem no papel nem no banco, e o timestamp pode ser empurrado pra frente pelo próprio cliente reabrindo a ficha. Enquanto isso não for resolvido (emitir PDF e versionar a chave com timestamp), a cláusula 11 é inoperável — você não consegue provar qual campo mudou — e tudo desce pra correção gratuita da 8.
- **Se a não-restituição da entrada é piso incondicional ou escalonado.** Decisão comercial sua, com a ressalva jurídica da pergunta 5.
- **Se a licença cobre unidades adicionais do mesmo equipamento.** Eu incluí porque você não tem como fiscalizar e porque cobrar por unidade é exatamente o que faz o comprador de série achar que vai pagar de novo — mas é escolha de preço, não de direito.
- **O CNAE em branco no `comercial/formalizacao.md`.** Se o contrato disser uma coisa e a nota fiscal disser outra, quem vale é a nota. Isso é conversa de contador, não de advogado, e é rápida.
- **Código morto no `comercial/contrato.py`.** As linhas 280-282 e 286-290 fazem replace de `"**CONTRATANTE** — [Nome do representante], [cargo]"` e `"[Razão social] — CNPJ [número] — [email]"`, strings que não existem mais no modelo — restos de uma versão que tinha bloco de assinatura em markdown. Com a proposta do item 5 acima elas continuam mortas e podem ser removidas. Só não remova achando que isso resolve o email: quem resolve é a linha nova do Quadro Resumo.