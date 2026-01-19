patterns_list = [
    # Comentários
    (r"saturnita.*", "COMENTARIO"),

    # Quebra de linha e espaços
    (r"\n", "QUEBRA_DE_LINHA"),
    (r"\t", "TABULACAO"),
    (r" ", "ESPACO"),

    # Palavras-chave
    (r"tralalero|tralala|porcodio|porcoala", "TIPO_DE_VARIAVEL"),
    (r"lirili|larila", "INICIO_E_FIM_DE_ESTRUTURA_DE_DECISAO"),
    (r"dunmadin", "INICIO_DE_LACO_CONTADO"),
    (r"tung|sahur", "INICIO_E_FIM_DE_LACO_DE_REPETICAO"),
    (r"chimpanzini", "COMANDO_DE_SAIDA"),
    (r"batapim", "COMANDO_DE_ENTRADA"),
    (r"delimitare|finitini", "DELIMITADOR_DE_BLOCO"),
    (r"tripi|tropa", "VALOR_BOOLEANO"),

    # Identificadores (após palavras-chave)
    (r"[a-z][a-zA-Z0-9]*", "id"),

    # Literais
    (r"\d+\.\d+", "valor_real"),
    (r"\d+", "valor_inteiro"),
    (r"\".*?\"", "string"),
    (r"'.*?'", "caractere"),

    # Operadores
    (r"\+|\-|\*|\/|\%", "OPERADOR_ARITMETICO"),
    (r"==|!=|>=|<=|>|<", "OPERADOR_RELACIONAL"),
    (r"\&\&|\|\|", "OPERADOR_LOGICO"),
    (r"=", "ATRIBUICAO"),
    (r";", "FIM_DE_INSTRUCAO"),

    # Captura qualquer outro caractere (erro léxico)
    (r".", "TOKEN_INVALIDO"),
]