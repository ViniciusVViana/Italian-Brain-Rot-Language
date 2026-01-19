# Analisador Semantico e Gerador de Código

- [x] Analisador Léxico
- [ ] Analisador Sintatico
- [ ] Analisador Semantico
- [ ] Gerador de Código


# Analisador Sintatico
- Adicionar tabela de simbolos

# AnalisadorLexico-IBR
Linguagem desenvolvida para a matéria de compiladores, ela é baseada nos Brainrots italianos onde basicamente alteramos as palavras comuns de um programa para o nome de alguns Brainrots italianos.
## Especificações da linguagem
### Tipos de dados
|Tipo|IBR|
|---|---|
|inteiro|tralalero|
|float|tralala
|caracter|porcodio|
|boolean|porcoala|
### Operadores
|Tipo do operador|Símbolos|Exemplos|
|---|---|---|
Aritméticos|+,-,*,/,%| a + b, x * 2
Relacionais| ==, !=, >, <, <=, >=| a == b, x >= 10
Lógicos| && (e), \|\|(ou)|
### Identificadores
- Devem começar com uma letra minúscula.
- Podem conter letras (maiúsculas e minúsculas) e números.
- Não pode haver espaços ou separadores no meio do identificador.

    |Exemplo|Válido|
    |---|---|
    |variavel1|sim|
    |contador|sim|
    |resultadoFinal|sim|
    |1variavel|não|
    |Resultado|não|
### Comando de entrada e saída
|Comando IBR|Descrição|
|---|---|
batapim|Lê dados de entrada
chimpanzini|Imprimi dados na saída
### Estruturas de controle
|Estrutura|IBR|Descrição
|---|---|---|
Decisão (if)|lirili|Executa um bloco de código se a condição for verdadeira.
Laço contado (for)|dunmadin|Repete um bloco de código um número específico de vezes.
Repetição (while)|tung ... sahur|Repete um bloco de código enquanto condição for verdadeira.
### Palavras reservadas
Palavra reservada|Função
---|---
tralalero|Declaração de inteiro
tralala|Declaração de ponto flutuante
porcodio|Declaração de caractere
porcoala|Declaração de booleano
lirili|Inicio de estrutura de decisão
larila|Fim de estrura de decisão
dunmadun|Início de laço contado
tung|Início de laço de repetição
sahur|Fim de laço de repetição
chimpanzini|Comando de sapida
batapim|Comando de entrada
delimitare|Início de delimitador de bloco
finitini|Fim de delimitador de bloco
saturnita| Comentário
tripi|Valor booleano verdadeiro
tropa|Valor booleano falso
## Análise léxica
### Expressões regulares para tokens
Token|Expressão regula|Exemplo
---|---|---
Identificador|\[a-z][a-zA-Z0-9]^*^|variavel1, contador
Número inteiro|\[0-9]^+^|123, 45
Número decimal|\[0-9]^+^.\[0-9]^+^|3,14, 2.71
String|[a-zA-Z]+|(teste!)
Caractere|\[a-zA-z]|A, b, C, d
Booleano|tripi, tropa
Operador|[operador](https://github.com/ViniciusVViana/AnalisadorLexico-IBRL?tab=readme-ov-file#Operadores)|+, -, *, /
Comentário|saturnita|saturnita comentação
Delimitador| delimitare, finitini
## Exemplos de código
### Calculadora simples
    tralelero a = 10;
    tralelero b = 5;
    tralelero resultado = a + b;
    chimpanzini "Resultado da soma: ";
    chimpanzini resultado;
### Estrutura de decisão
    tralelero idade = 20;

    lirili idade >= 18 delimitare
        chimpanzini "Maior de idade";
    finitini
    larila
        chimpanzini "Menor de idade";
    finitini
### Laço de repetição
    tralelero contador = 0;
    tung contador < 5 sahur
        chimpanzini "Contador: ";
        chimpanzini contador;
        contador = contador + 1;
    sahur
# Preparação para execução do analisador léxico
Para rodar o analisador crie o ambiente virtual para poder instalar todos os requisitos necessários:
```
python -m venv venv
```
E para ativar o ambiente rode o seguinte script:
```
.\venv\Script\activate
```
E então instalar os requisitos:
```
pip install requirements.txt
```

# Como utilizar o analisador léxico (IBRL)
## Usando o arquivo fonte
Com o arquivo ```main.py``` e os arquivos de exemplo com a seguinte extensão ```.ibr``` ja instalados em seu computador execute o seguinte comando para realizar a análise léxica:
- lembre-se que deve você estar dentro do diretório.
```
python main.py nome_do_arquivo.ibr
```
Após a execução aparece no seu terminal algo parecido com isso:
![](./.img/carbon.png)
## Usando executavel
Baixe e execute o instalador, então no terminal execute o seguinte comando:
```
LexAnalyzer nome_do_arquivo.ibr
```
