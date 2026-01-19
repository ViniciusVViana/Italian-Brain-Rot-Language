patterns_list = [
    # Comentários
    (r"saturnita.*", "COMENTARIO"),

    # Quebra de linha e espaços
    (r"\n", "QUEBRA DE LINHA"),
    (r"\t", "TABULACAO"),
    (r" ", "ESPACO"),

    # Palavras-chave
    (r"tralalero|tralala|porcodio|porcoala", "TIPO_DE_VARIAVEL"),
    (r"lirili|larila", "INICIO E FIM DE ESTRUTURA DE DECISAO"),
    (r"dunmadin", "INICIO DE LACO CONTADO"),
    (r"tung|sahur", "INICIO E FIM DE LACO DE REPETICAO"),
    (r"chimpanzini", "COMANDO DE SAIDA"),
    (r"batapim", "COMANDO DE ENTRADA"),
    (r"delimitare|finitini", "DELIMITADOR DE BLOCO"),
    (r"tripi|tropa", "VALOR BOOLEANO"),

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