""" Modulo que define a gramática da linguagem e conjuntos de símbolos terminais e não-terminais. """

EPS = "ε"
ENDMARK = "$"

gramatica = {
    'PROGRAMA': [
        ['LISTA_DE_COMANDOS'] # 1
    ],
    'LISTA_DE_COMANDOS': [
        ['COMANDO', 'LISTA_DE_COMANDOS'], # 2
        ['COMANDO'] # 3
    ],
    'COMANDO': [
        ['DECLARACAO'], # 4
        ['ENTRADA'], # 5
        ['SAIDA'], # 6
        ['DECISAO'], # 7
        ['LACO_CONTADO'], # 8
        ['LACO_DE_REPETICAO'], # 9
        ['ATRIBUICAO'], # 10
        ['COMENTARIO'] # 11
    ],
    'DECLARACAO': [
        ['TIPO_DE_VARIAVEL', 'id', ';'], # 12
        ['TIPO_DE_VARIAVEL', 'id', 'ATRIBUICAO', ';'], # 12
    ],
    'ATRIBUICAO': [
        ['=', 'TERMO'], # 13
        ['=', 'EXPRESSAO'], # 14
        ['TERMO', '=', 'EXPRESSAO', ';'], # 15
    ],
    'EXPRESSAO': [
        ['EXPRESSAO', 'OPERADOR', 'TERMO'], # 17
        ['TERMO'] # 18
    ],
    'OPERADOR': [
        ['OPERADOR_ARITMETICO'], # 19
        ['OPERADOR_RELACIONAL'], # 20
        ['OPERADOR_LOGICO'] # 21
    ],
    'ENTRADA': [
        ['batapim', 'id', ';'] # 22
    ],
    'SAIDA': [
        ['chimpanzini', 'EXPRESSAO', ';'] # 23
    ],
    'DECISAO': [
        ['lirili', 'EXPRESSAO', 'BLOCO'], # 24
        ['lirili', 'EXPRESSAO', 'BLOCO', 'larila', 'BLOCO'],  # 25
        ['lirili', 'EXPRESSAO', 'BLOCO', 'larila', 'DECISAO'],  # 26
    ],
    'LACO_CONTADO': [
        ['dunmadin', '(', 'DECLARACAO', ';', 'EXPRESSAO', ';', 'EXPRESSAO', ')', 'BLOCO'] # 27
    ],
    'LACO_DE_REPETICAO': [
        ['tung', 'EXPRESSAO', 'BLOCO'] # 28
    ],
    'BLOCO': [
        ['BLOCO_DECISAO'], # 29
        ['BLOCO_REPETICAO'] # 30
    ],
    'BLOCO_REPETICAO': [
        ['sahur', 'LISTA_DE_COMANDOS', 'sahur'] # 31
    ],
    'BLOCO_DECISAO': [
        ['delimitare', 'LISTA_DE_COMANDOS', 'finitini'], # 32
    ],
    'COMENTARIO': [
        ['saturnita', 'TERMO'] # 33
    ],
    'TIPO_DE_VARIAVEL': [
        ['tralalero'], # 34
        ['tralala'], # 35
        ['porcodio'], # 36
        ['porcoala'] # 37
    ],
    'OPERADOR_ARITMETICO': [
        ['+'], # 38
        ['-'], # 39
        ['*'], # 40
        ['/'], # 41
        ['%'] # 42
    ],
    'OPERADOR_RELACIONAL': [
        ['=='], # 43
        ['!='], # 44
        ['>'], # 45
        ['<'], # 46
        ['<='], # 47
        ['>='] # 48
    ],
    'OPERADOR_LOGICO': [
        ['&&'], # 49
        ['||'] # 50
    ],
    'TERMO': [
        ['id'], # 51
        ['valor_inteiro'], # 52
        ['valor_real'], # 53
        ['VALOR_BOOL'], # 54
        ['caractere'], # 55
        ['string'] # 56
    ],
    'VALOR_BOOL': [
        ['tripi'], # 57
        ['tropa'] # 58
    ]
}

ALL_NONTERMINALS = set(gramatica.keys())
ALL_TERMINALS = set(sym for prod in gramatica.values() for prod_aux in prod for sym in prod_aux if sym not in ALL_NONTERMINALS and sym != EPS)