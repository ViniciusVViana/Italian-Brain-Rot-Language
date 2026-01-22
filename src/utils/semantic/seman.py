"""
Analisador Semântico - Percorre a árvore de derivação e valida regras semânticas
Implementado com funções puras, sem classes (consistente com léxico e sintático)
"""

from .table import SymbolTable, SymbolType, IBRL_TYPE_MAP

_symbol_table = None
_errors = []

def analyze_semantic(derivation_tree):
    """
    Função principal de análise semântica - percorre a árvore de derivação
    
    Args:
        derivation_tree: DerivationTree do parser sintático
        
    Returns:
        tuple: (bool, SymbolTable) - (sucesso, tabela de símbolos)
    """
    global _symbol_table, _errors
    
    _symbol_table = SymbolTable()
    _errors = []
    
    print("\n🔍 Iniciando análise semântica...")
    print("=" * 70)
    
    if derivation_tree.root:
        _visit_node(derivation_tree.root)
    else:
        print("❌ Árvore de derivação vazia!")
        return False, _symbol_table
    
    # Exibe resultados
    _symbol_table.print_table()
    _symbol_table.print_errors()
    
    has_errors = len(_symbol_table.errors) > 0
    
    if not has_errors:
        print("\n✅ Análise semântica concluída com sucesso!")
    else:
        print(f"\n❌ Análise semântica falhou com {len(_symbol_table.errors)} erro(s)")
    
    print("=" * 70)
    return not has_errors, _symbol_table


def _visit_node(node):
    """Visita recursivamente cada nó da árvore e executa ações semânticas"""
    
    symbol = node.symbol
    
    # Ações semânticas baseadas no não-terminal
    if symbol == "DECLARACAO":
        _handle_declaration(node)
    
    elif symbol in ("BLOCO_DECISAO", "BLOCO_REPETICAO"):
        _handle_block(node)
    
    elif symbol == "ATRIBUICAO":
        _handle_assignment(node)
    
    elif symbol == "EXPRESSAO":
        _handle_expression(node)
    
    elif symbol == "ENTRADA":
        _handle_input(node)
    
    elif symbol == "SAIDA":
        _handle_output(node)
    
    elif symbol == "DECISAO":
        _handle_decision(node)
    
    elif symbol in ("LACO_DE_REPETICAO", "LACO_CONTADO"):
        _handle_loop(node)
    
    # Continua percorrendo filhos para outros nós
    else:
        for child in node.children:
            _visit_node(child)


def _handle_declaration(node):
    """
    DECLARACAO -> TIPO_DE_VARIAVEL id ;
    DECLARACAO -> TIPO_DE_VARIAVEL id ATRIBUICAO ;
    """
    children = node.children
    
    if len(children) < 3:
        return
    
    tipo_node = children[0]
    id_node = children[1]
    
    # Pega o lexema do tipo
    if tipo_node.children and len(tipo_node.children) > 0:
        tipo_lexeme = tipo_node.children[0].lexeme
    else:
        tipo_lexeme = tipo_node.lexeme
    
    var_name = id_node.lexeme
    line = _extract_line(id_node)
    
    # Declara na tabela de símbolos
    success = _symbol_table.declare(var_name, tipo_lexeme, line)
    
    if success:
        print(f"  ✓ Variável '{var_name}' declarada como {tipo_lexeme} (linha {line})")
    
    # Se houver atribuição inicial, valida
    if len(children) >= 4 and children[2].symbol == "ATRIBUICAO":
        _visit_node(children[2])


def _handle_block(node):
    """Entra em novo escopo, visita filhos, sai do escopo"""
    print(f"  → Entrando em escopo ({node.symbol})")
    _symbol_table.push_scope()
    
    for child in node.children:
        if child.symbol not in ("delimitare", "finitini", "sahur"):
            _visit_node(child)
    
    _symbol_table.pop_scope()
    print(f"  ← Saindo de escopo")


def _handle_assignment(node):
    """
    ATRIBUICAO -> = TERMO
    ATRIBUICAO -> = EXPRESSAO
    ATRIBUICAO -> TERMO = EXPRESSAO ;
    """
    children = node.children
    
    if len(children) < 2:
        return
    
    if children[0].symbol == "=":
        return
    
    if len(children) >= 3 and children[1].lexeme == "=":
        var_node = children[0]
        expr_node = children[2]
        
        var_name = _extract_id_from_termo(var_node)
        if not var_name:
            return
        
        line = _extract_line(var_node)
        
        symbol = _symbol_table.resolve(var_name)
        if not symbol:
            error_msg = f"❌ Erro semântico (linha {line}): Variável '{var_name}' não declarada"
            _symbol_table.errors.append(error_msg)
            print(f"  {error_msg}")
            return
        
        expr_type = _handle_expression(expr_node)
        
        if expr_type and expr_type != symbol.sym_type:
            if not _symbol_table._is_compatible(symbol.sym_type, expr_type):
                error_msg = f"❌ Erro semântico (linha {line}): Atribuição incompatível. '{var_name}' é {symbol.sym_type.value}, mas expressão é {expr_type.value}"
                _symbol_table.errors.append(error_msg)
                print(f"  {error_msg}")
            else:
                print(f"  ⚠️  Coerção de tipo: {expr_type.value} → {symbol.sym_type.value}")
        else:
            print(f"  ✓ Atribuição válida para '{var_name}' (linha {line})")


def _handle_expression(node):
    """
    Infere o tipo de uma expressão recursivamente
    Returns: SymbolType ou None
    """
    children = node.children
    
    if not children:
        return None
    
    # EXPRESSAO -> TERMO
    if len(children) == 1 and children[0].symbol == "TERMO":
        return _get_termo_type(children[0])
    
    # EXPRESSAO -> EXPRESSAO OPERADOR TERMO
    if len(children) == 3:
        left_type = _handle_expression(children[0])
        operator_node = children[1]
        right_type = _get_termo_type(children[2])
        
        return _validate_operation(left_type, operator_node, right_type)
    
    return None


def _get_termo_type(termo_node):
    """Infere o tipo de um TERMO"""
    if not termo_node.children:
        return None
    
    child = termo_node.children[0]
    
    if child.symbol == "id":
        var_name = child.lexeme
        symbol = _symbol_table.resolve(var_name)
        return symbol.sym_type if symbol else None
    
    if child.symbol == "valor_inteiro":
        return SymbolType.INT
    elif child.symbol == "valor_real":
        return SymbolType.FLOAT
    elif child.symbol == "caractere":
        return SymbolType.CHAR
    elif child.symbol == "VALOR_BOOL":
        return SymbolType.BOOL
    
    return None


def _validate_operation(left_type, operator_node, right_type):
    """Valida operação entre dois tipos e retorna o tipo resultante"""
    if not left_type or not right_type:
        return None
    
    if not operator_node.children:
        return None
    
    op_type_node = operator_node.children[0]
    op_symbol = op_type_node.symbol
    
    # OPERADORES ARITMÉTICOS
    if op_symbol == "OPERADOR_ARITMETICO":
        if left_type in (SymbolType.INT, SymbolType.FLOAT) and right_type in (SymbolType.INT, SymbolType.FLOAT):
            return SymbolType.FLOAT if (left_type == SymbolType.FLOAT or right_type == SymbolType.FLOAT) else SymbolType.INT
        else:
            _symbol_table.errors.append(f"❌ Operador aritmético requer tipos numéricos, recebeu {left_type.value} e {right_type.value}")
            return None
    
    # OPERADORES RELACIONAIS
    elif op_symbol == "OPERADOR_RELACIONAL":
        if left_type == right_type or _symbol_table._is_compatible(left_type, right_type):
            return SymbolType.BOOL
        else:
            _symbol_table.errors.append(f"❌ Operador relacional requer tipos compatíveis, recebeu {left_type.value} e {right_type.value}")
            return SymbolType.BOOL
    
    # OPERADORES LÓGICOS
    elif op_symbol == "OPERADOR_LOGICO":
        if left_type == SymbolType.BOOL and right_type == SymbolType.BOOL:
            return SymbolType.BOOL
        else:
            _symbol_table.errors.append(f"❌ Operador lógico requer booleanos, recebeu {left_type.value} e {right_type.value}")
            return SymbolType.BOOL
    
    return None


def _handle_input(node):
    """ENTRADA -> batapim id ;"""
    if len(node.children) >= 2:
        id_node = node.children[1]
        var_name = id_node.lexeme
        line = _extract_line(id_node)
        
        if var_name not in _symbol_table:
            error_msg = f"❌ Erro semântico (linha {line}): Leitura em variável '{var_name}' não declarada"
            _symbol_table.errors.append(error_msg)
            print(f"  {error_msg}")
        else:
            print(f"  ✓ Entrada válida para '{var_name}'")


def _handle_output(node):
    """SAIDA -> chimpanzini EXPRESSAO ;"""
    if len(node.children) >= 2:
        expr_node = node.children[1]
        expr_type = _handle_expression(expr_node)
        print(f"  ✓ Saída válida (tipo: {expr_type.value if expr_type else 'desconhecido'})")


def _handle_decision(node):
    """DECISAO -> lirili EXPRESSAO BLOCO ..."""
    if len(node.children) >= 2:
        expr_node = node.children[1]
        expr_type = _handle_expression(expr_node)
        
        if expr_type and expr_type != SymbolType.BOOL:
            error_msg = f"❌ Erro semântico: Condição de decisão deve ser booleana, recebeu {expr_type.value}"
            _symbol_table.errors.append(error_msg)
            print(f"  {error_msg}")
    
    for child in node.children:
        if child.symbol in ("BLOCO", "BLOCO_DECISAO", "BLOCO_REPETICAO", "DECISAO"):
            _visit_node(child)


def _handle_loop(node):
    """LACO_DE_REPETICAO -> tung EXPRESSAO BLOCO"""
    if len(node.children) >= 2:
        expr_node = node.children[1]
        expr_type = _handle_expression(expr_node)
        
        if expr_type and expr_type != SymbolType.BOOL:
            error_msg = f"❌ Erro semântico: Condição de laço deve ser booleana, recebeu {expr_type.value}"
            _symbol_table.errors.append(error_msg)
            print(f"  {error_msg}")
    
    for child in node.children:
        if child.symbol in ("BLOCO", "BLOCO_DECISAO", "BLOCO_REPETICAO"):
            _visit_node(child)


# ===== FUNÇÕES AUXILIARES =====

def _extract_id_from_termo(termo_node):
    """Extrai o identificador de um nó TERMO"""
    if termo_node.children and termo_node.children[0].symbol == "id":
        return termo_node.children[0].lexeme
    return None


def _extract_line(node):
    """Extrai número de linha de um nó - verifica atributo 'line' ou busca em filhos terminais"""
    # Primeiro tenta usar o atributo 'line' armazenado no nó
    if hasattr(node, 'line') and node.line is not None and node.line != 0:
        return node.line
    
    # Se não encontrou, busca recursivamente nos filhos (especialmente terminais)
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            line = _extract_line(child)
            if line and line != 0:
                return line
    
    # Se ainda não encontrou, retorna 0
    return 0