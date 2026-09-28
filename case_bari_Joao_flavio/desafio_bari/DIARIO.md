# Diário de bordo — João Flávio

Comecei no domingo, 27/09, às 14:30 e terminei na segunda, 28/09, à 2:24.

## a) Registro de uso de IA

**Ferramentas e para quê**

- **Cursor:** para escrever partes do código em que eu tinha dificuldade e para estilizar o relatório em
  HTML/CSS, buscando um resultado simples, porém agradável aos olhos.
- **Claude:** usei como uma conversa ao longo do projeto. Ele me ajudou a montar o script do RPA e o
  extrator dos laudos e, no final, fiz uma avaliação de tudo o que havíamos construído para ver se estava
  de fato bom. Eu ia jogando ideias e ele respondia quais usar e como usá-las, por exemplo: fazer o
  relatório em HTML dentro do próprio script Python(também utilizei para fazer uma base do read.me e metodologia, 
  corrigindo erros ortográficos e entre outros).

**Situações concretas em que a IA me deu algo inadequado e o que fiz a respeito**

- Nos meus projetos procuro seguir as regras de clean code, e acredito que as IAs acabam esquecendo
  delas. Para manter o código mais fácil de entender e seguir as boas práticas, precisei pedir ajustes ao
  que veio pronto. Por exemplo: `tratar_dados` tinha umas 80 linhas fazendo tudo; agora são 8 funções
  pequenas (uma por problema de dado) e uma que só as chama em ordem.

## b) O que aprendi do zero

Eu não estava acostumado a usar a biblioteca `logging` para registrar eventos, erros e o fluxo de
execução. Confesso que, agora que a conheço, vou parar de escrever `print()` para ver se o código
funciona do jeito certo (só funcionar já é ótimo também).

Demorei cerca de 45/50 minutos para aprender o necessario para realizar o script e os métodos que
 eu usei para aprender também foram recomendações do claude(sites e vídeos).

Também aprendi bastante sobre matemática aplicada à economia.

## c) Autocrítica

**O que na minha entrega eu sei que está fraco**

Minha semana foi corrida e isso atrapalhou um pouco o projeto. Teve momentos em que eu usava a IA e
depois lembrava que sabia fazer o que havia pedido. Mesmo assim, acredito que o resultado reflete bem o
meu fluxo de trabalho, por mais que a IA tenha me ajudado em algumas partes.

**O que eu faria com mais 40 horas**

Muitas coisas: talvez uma aplicação que já enviasse os relatórios para algum e-mail, ou estilizar o
relatório do funil para algo mais parecido com a identidade visual da Bari.

**Perguntas que eu gostaria de ter feito ao time de negócios antes de começar**

- Qual é a data de corte da extração? Sem ela, não dá para saber quais propostas ainda estão em andamento.
- Como a "conversão" é definida: contratadas sobre todas as entradas, ou só sobre propostas encerradas?
- Qual é a diferença entre "Sem retorno" e "Desistiu"?
