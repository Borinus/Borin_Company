# Enquadramento: MEI, CNAE e nota fiscal

> Pesquisa em fontes oficiais rodada em 01/08/2026. Sete frentes independentes; cada
> afirmação passou por um cético que tentou derrubá-la antes de entrar aqui.
> **23 sobreviveram, 5 foram descartadas.**
>
> **Isto não substitui contador nem advogado.** Serve pra você chegar na conversa sabendo
> a pergunta certa. Onde está escrito "checar", é porque não deu pra confirmar em fonte
> primária — trate como pista, não como fato.

---

# Enquadramento do CNPJ — o que a pesquisa fechou

## 1. Resposta em uma frase

**Não cobre.** O CNAE 3321-0/00 descreve *instalação e montagem física* de máquinas e equipamentos industriais, e no MEI ele corresponde à ocupação "INSTALADOR(A) DE MÁQUINAS E EQUIPAMENTOS INDUSTRIAIS INDEPENDENTE" — atividade de campo, que você declaradamente não exerce.

## 2. O que isso significa na prática hoje

O código em si é válido. Ele consta da Tabela A do Anexo XI da Resolução CGSN nº 140/2018 (versão consolidada gerada em 16/10/2025, já posterior às Resoluções CGSN 182 e 183, ambas de 26/09/2025), com ISS = S e ICMS = N. Ninguém vai te desenquadrar por o código ter saído da lista — ele não saiu.

O problema é outro, e é maior: **o que você vende não tem ocupação MEI nenhuma.** Rodando busca no texto integral do Anexo XI (43 páginas, ~471 ocupações), não existe nenhuma ocupação com "PROJETISTA", "DESENHISTA" ou "ENGENH". Os CNAEs 7119-7/03 (desenho técnico) e 7112-0/00 (serviços de engenharia) não constam do anexo. E o Manual do Desenquadramento do SIMEI da Receita (versão Abril/2025, item 4.3) é explícito: "considere sempre a descrição do campo 'ocupação' (primeira coluna), nunca a descrição da subclasse CNAE (terceira coluna)".

Traduzindo: **a correção não é trocar de CNAE dentro do MEI. Não existe CNAE certo disponível no MEI.** A correção é sair do MEI.

Sobre emitir a primeira nota: tecnicamente você consegue. Mas cada nota de projeto emitida sob esse CNPJ é faturamento fora da ocupação declarada. A obrigação de comunicar o desenquadramento por "atividade econômica vedada" nasce no momento em que você começa a prestar o serviço, não quando alguém te pega — prazo até o último dia útil do mês seguinte, multa de R$ 50,00 (LC 123/2006, art. 36-A). A multa é irrelevante. O que importa é o cenário do item 8 do mesmo Manual: se o fisco entender que você nunca exerceu a ocupação de instalador e abriu o MEI já para vender projeto, o desenquadramento é feito de ofício e **retroage à data de ingresso no regime — 18/03/2026** — e todo o faturamento é recalculado como ME no Simples. Nesse caso não dá para desfazer pelo aplicativo, só por processo administrativo protocolado no ente que registrou o evento (e Caxias tem competência para registrar, porque o serviço é de ISS).

Dois números que mudam o planejamento:

- **Seu teto em 2026 não é R$ 81.000.** CNPJ aberto em 18/03/2026 → limite proporcional de R$ 6.750 × 10 meses = **R$ 67.500** (LC 123/2006, art. 18-A, §2º). Estourar isso em até 20% (ou seja, até R$ 81.000) gera DAS complementar e desenquadramento em 01/01/2027; passar de R$ 81.000 desenquadra retroativo a 18/03/2026. Com ticket médio de R$ 6.700, são ~10 projetos.
- **Não conte com aumento de teto.** Os R$ 110 mil / R$ 140 mil que estão na página do gov.br são o PLP 186/2026, que em 01/08/2026 estava "aguardando despacho do Presidente da Câmara". O PLP 108/2021 tem urgência aprovada mas votação adiada para o segundo semestre. Nada virou lei.

Sobre ISS em Caxias: a tabela da Secretaria da Receita Municipal (atualizada em 27/07/2026, compilação da Tabela 02 da LC municipal 701/2022) traz 4% tanto para o item 32.01 quanto para todo o bloco 07. Mas a OBS 1 da própria tabela diz que essas alíquotas se aplicam a pessoas jurídicas **não** optantes pelo Simples Nacional/MEI — então elas não são a tua conta hoje, e continuam não sendo se você virar ME no Simples. Só passam a valer fora do Simples.

## 3. O que fazer, em ordem

1. **Levantar quantas notas já saíram sob esse CNPJ e com que descrição.** Se for zero ou quase, você está no melhor momento possível para corrigir — 4 meses de CNPJ.
2. **Parar de fechar contrato novo até definir o enquadramento.** Especialmente qualquer coisa acima de R$ 15.000, que sozinha empurra o acumulado para perto do limite.
3. **Montar a planilha de acumulado do ano.** Marcar R$ 67.500 como linha vermelha de 2026, não R$ 81.000.
4. **Abrir o Emissor Nacional (nfse.gov.br/EmissorNacional) com o teu CNPJ e ver quais códigos de serviço aparecem.** É o teste mais barato que existe: se só aparecer código de instalação, isso já responde sozinho a pergunta de campo. Leva cinco minutos.
5. **Levar tudo isso para o contador com a pergunta certa** (ver seção 4). A pergunta não é "qual CNAE eu incluo" — é "como eu migro para ME no Simples e o que faço com o período já faturado".
6. **Revisar o texto comercial e o modelo de contrato.** A Lei 5.194/1966, art. 15, declara nulos de pleno direito os contratos referentes a qualquer ramo da engenharia, "inclusive a elaboração de projeto", firmados com quem não é legalmente habilitado — e o art. 6º, alíneas "a" e "e", alcança pessoa jurídica, não só pessoa física. Num projeto de R$ 15.000 com cliente que decide não pagar, o teu próprio contrato vira defesa dele. Vale reescrever para descrever o entregável (documentação técnica, diagramas, listas, conferência) sem se apresentar como responsável técnico e sem "Engenharia" em lugar nenhum.

## 4. O que depende de contador ou da prefeitura — não decido por você

**Para o contador:**
- Migração MEI → ME no Simples Nacional: rito, custo na JUCISRS, prazo, e o que acontece com as notas já emitidas (retificação? cancelamento? deixa como está?).
- Qual CNAE adotar. Atenção: **7119-7/03 não é resposta óbvia.** A nota do IBGE para 7119-7/03 cobre só "desenho técnico especializado"; elaboração e gestão de projeto de engenharia elétrica, além de conferência e revisão de projeto, aparecem nominalmente em 7112-0/00. A escolha entre os dois é decisão regulatória (7112-0/00 puxa registro no CREA) somada a decisão fiscal, e não é minha. **Checar.**
- Enquadramento no Anexo III ou V do Simples e o fator R — muda a alíquota efetiva e portanto a tua precificação. **Não verificado, checar.**
- Se cabe comunicar o desenquadramento espontaneamente agora (efeito só do mês seguinte) em vez de esperar desenquadramento de ofício (risco de retroagir a 18/03/2026).

**Para a Prefeitura de Caxias do Sul (Secretaria da Receita Municipal):**
- Em qual item da lista da LC 116/2003 eles enquadram o serviço. Há pelo menos três candidatos e a escolha não é sua: 7.03 (elaboração de anteprojetos, projetos básicos e executivos para trabalhos de engenharia), 31.01 (serviços técnicos em edificações, eletrônica, **eletrotécnica**, mecânica, telecomunicações e congêneres) e 32.01 (serviços de desenhos técnicos). O 31.01 é o classicamente aplicado a técnico/projetista em eletrotécnica e costuma ser esquecido. **Checar** — pedir por protocolo escrito, não por telefone.
- Se o município exige inscrição municipal, alvará ou cadastro econômico prévio do MEI antes de emitir NFS-e. **Não confirmado, checar.**

**Para o CRT-RS (Conselho Regional dos Técnicos Industriais):**
- "Legalmente habilitado" não é sinônimo de engenheiro com CREA. A Lei 5.524/1968 (art. 2º, V) e o Decreto 90.922/1985 (art. 4º, V e §2º) reconhecem ao técnico industrial de nível médio a responsabilidade por elaboração de projetos compatíveis com sua formação — o §2º fala expressamente em projetar instalações elétricas até 800 kVA e exercer atividade de desenhista da especialidade. Desde a Lei 13.639/2018 esse registro é no CFT/CRT, não no CREA. Isso é uma porta que existe, mas depende de você ter (ou obter) diploma técnico. **Checar direto com o CRT-RS.**

## 5. Em aberto — não consegui confirmar

- **Se existe alguma via de registro no CFT/CRT por comprovação de experiência**, sem diploma técnico. Assumi que não, mas não verifiquei as resoluções do CFT. **Checar.**
- **Se o Emissor Nacional bloqueia tecnicamente código de serviço divergente do CNAE.** Fontes de contabilidade afirmam que sim; norma oficial dizendo isso eu não achei. Por isso o passo 4 acima é teste prático, não pesquisa.
- **Se a Resolução CGSN 183/2025 excluiu ocupações do Anexo XI com efeito em 01/01/2026.** Circula uma lista de 13 atividades desenquadradas; a de instalador de máquinas não está nela, e o PDF que li é posterior à 183 — mas não li o anexo da 183 em fonte primária. O portal normas.receita.fazenda.gov.br esteve fora do ar. Não muda a conclusão (o problema é ausência de ocupação de projetista, não exclusão do 3321-0/00).
- **Resolução CONFEA 1.156, de 24/10/2025**, revogou os arts. 8º e 9º da Resolução 218/1973 (atribuições do engenheiro eletricista). Não consegui ler o que entrou no lugar. Se alguém te mostrar a Res. 218/1973 citando o art. 8º como argumento, esse artigo não está mais em vigor. **Checar.**
- **Efeito da nulidade do art. 15 da Lei 5.194/1966 sobre serviço já executado e não pago** (se cabe cobrança por enriquecimento sem causa). Não achei julgado. **Checar com advogado se algum cliente travar pagamento.**
- **Impacto da LC 214/2025 (IBS/CBS) sobre o DAS do MEI a partir de 2027.** Há indicação de valores fixos novos, não confirmada em fonte primária. **Checar.**

## Armadilhas que você provavelmente acreditaria

- **"Meu CNAE está na lista do MEI, então está tudo certo."** Está na lista — e isso não te protege. A lista é de *ocupações*, e a tua é "instalador".
- **"É só incluir o CNAE de projeto."** Não dá. Nenhum CNAE de projeto ou desenho técnico está no Anexo XI.
- **"O teto é R$ 81 mil."** Em 2026, para você, é R$ 67.500.
- **"O governo já aumentou o teto para R$ 110 mil."** A página do gov.br diz "será reajustado progressivamente em duas etapas automáticas" sem nunca escrever a palavra "projeto de lei". É PLP 186/2026, em tramitação.
