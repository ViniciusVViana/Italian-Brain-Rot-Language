from ..syntactic import DerivationNode

class TACGenerator:
    """Gerador de Código de 3 Endereços (Three Address Code)"""
    
    def __init__(self):
        self.instructions: list[str] = []
        self.temp_count = 0
        self.label_count = 0
        self.symbols = None  # Referência à tabela de símbolos
    
    def new_temp(self) -> str:
        """Gera novo temporário: t1, t2, t3..."""
        self.temp_count += 1
        return f"t{self.temp_count}"
    
    def new_label(self) -> str:
        """Gera novo rótulo: L1, L2, L3..."""
        self.label_count += 1
        return f"L{self.label_count}"
    
    def emit(self, instruction: str):
        """Emite uma instrução TAC"""
        self.instructions.append(instruction)
        print(f"  {len(self.instructions):3d}. {instruction}")
    
    def generate(self, root: DerivationNode, symbols_from_analyzer) -> list[str]:
        """Gera código TAC a partir da árvore"""
        self.symbols = symbols_from_analyzer
        
        print("\n🔨 Gerando Código de 3 Endereços")
        print("=" * 70)
        
        self.visit(root)
        
        print("=" * 70)
        return self.instructions
    
    def visit(self, node):
        """Despachador Visitor - mesma ideia da análise semântica"""
        if node is None:
            return None
        
        method = getattr(self, f"visit_{node.symbol}", self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Fallback: visita filhos"""
        result = None
        for c in getattr(node, "children", []):
            result = self.visit(c)
        return result
    
    # ===== MÉTODOS PARA CADA TIPO DE NÓ =====
    
    def visit_PROGRAMA(self, node):
        for c in node.children:
            self.visit(c)
    
    def visit_LISTA_DE_COMANDOS(self, node):
        for c in node.children:
            self.visit(c)
    
    def visit_COMANDO(self, node):
        for c in node.children:
            self.visit(c)
    
    def visit_DECLARACAO(self, node):
        """
        DECLARACAO -> TIPO_DE_VARIAVEL id [ATRIBUICAO] ;
        Se tem atribuição, processa ela
        """
        var_name = None
        atrib_node = None
        
        # Extrai nome e atribuição
        for c in node.children:
            if c.symbol == "id":
                var_name = c.lexeme
            elif c.symbol == "ATRIBUICAO":
                atrib_node = c
        
        # Se tem atribuição inicial, processa
        if atrib_node and var_name:
            # ATRIBUICAO em contexto de DECLARACAO é: '=' EXPRESSAO | '=' TERMO
            expr_value = None
            for c in atrib_node.children:
                if c.symbol in ("EXPRESSAO", "TERMO"):
                    expr_value = self.visit(c)
                    break
            
            if expr_value:
                self.emit(f"{var_name} = {expr_value}")
    
    def visit_ATRIBUICAO(self, node):
        """ATRIBUICAO -> TERMO '=' EXPRESSAO ';'"""
        # Extrai identificador (lhs)
        var_name = None
        expr_value = None
        
        for i, c in enumerate(node.children):
            if c.symbol == "TERMO" and i == 0:
                # Primeiro TERMO é a variável
                if c.children and c.children[0].symbol == "id":
                    var_name = c.children[0].lexeme
            elif c.symbol == "EXPRESSAO":
                # Visita a expressão e retorna seu valor
                expr_value = self.visit(c)
        
        if var_name and expr_value:
            self.emit(f"{var_name} = {expr_value}")
        
        return var_name
    
    def visit_EXPRESSAO(self, node):
        """EXPRESSAO -> EXPRESSAO OPERADOR TERMO | TERMO"""
        
        if len(node.children) == 1:
            # Simples: apenas um TERMO
            return self.visit(node.children[0])
        
        elif len(node.children) == 3:
            # Binária: EXPRESSAO OPERADOR TERMO
            left = self.visit(node.children[0])      # Expressão esquerda
            op = self._extract_operator(node.children[1])  # Operador
            right = self.visit(node.children[2])     # TERMO direita
            
            # Gera temporário para o resultado
            result = self.new_temp()
            self.emit(f"{result} = {left} {op} {right}")
            return result
        
        return None
    
    def visit_TERMO(self, node):
        """TERMO -> id | valor_inteiro | valor_real | ..."""
        if not node.children:
            return None
        
        leaf = node.children[0]
        
        if leaf.symbol == "id":
            return leaf.lexeme
        elif leaf.symbol == "valor_inteiro":
            return leaf.lexeme
        elif leaf.symbol == "valor_real":
            return leaf.lexeme
        elif leaf.symbol in ("tripi", "tropa"):
            return "true" if leaf.symbol == "tripi" else "false"
        elif leaf.symbol == "caractere":
            return f"'{leaf.lexeme}'"
        elif leaf.symbol == "string":
            return f'"{leaf.lexeme}"'
        
        return leaf.lexeme
    
    def visit_ENTRADA(self, node):
        """ENTRADA -> batapim id ;"""
        for c in node.children:
            if c.symbol == "id":
                var = c.lexeme
                temp = self.new_temp()
                self.emit(f"{temp} = input()")
                self.emit(f"{var} = {temp}")
    
    def visit_SAIDA(self, node):
        """SAIDA -> chimpanzini EXPRESSAO ;"""
        for c in node.children:
            if c.symbol == "EXPRESSAO":
                expr = self.visit(c)
                self.emit(f"output({expr})")
    
    def visit_DECISAO(self, node):
        """DECISAO -> lirili EXPRESSAO BLOCO [larila BLOCO]"""
        label_else = self.new_label()
        label_end = self.new_label()
        
        # Avalia condição
        cond = None
        for c in node.children:
            if c.symbol == "EXPRESSAO":
                cond = self.visit(c)
                break
        
        # if not cond goto else
        self.emit(f"if_not {cond} goto {label_else}")
        
        # Bloco then
        for c in node.children:
            if c.symbol in ("BLOCO", "BLOCO_DECISAO"):
                self.visit(c)
                break
        
        self.emit(f"goto {label_end}")
        
        # Rótulo else
        self.emit(f"{label_else}:")
        
        # Bloco else (se existir)
        blocks = [c for c in node.children 
                 if c.symbol in ("BLOCO", "BLOCO_DECISAO")]
        if len(blocks) > 1:
            self.visit(blocks[1])
        
        # Rótulo fim
        self.emit(f"{label_end}:")
    
    def visit_LACO_DE_REPETICAO(self, node):
        """LACO_DE_REPETICAO -> tung EXPRESSAO BLOCO"""
        label_loop = self.new_label()
        label_end = self.new_label()
        
        # Rótulo início do loop
        self.emit(f"{label_loop}:")
        
        # Condição
        cond = None
        for c in node.children:
            if c.symbol == "EXPRESSAO":
                cond = self.visit(c)
                break
        
        # if not cond goto end
        self.emit(f"if_not {cond} goto {label_end}")
        
        # Corpo do loop
        for c in node.children:
            if c.symbol in ("BLOCO", "BLOCO_REPETICAO"):
                self.visit(c)
                break
        
        # Volta ao início
        self.emit(f"goto {label_loop}")
        
        # Rótulo fim
        self.emit(f"{label_end}:")
    
    def visit_BLOCO(self, node):
        for c in node.children:
            self.visit(c)
    
    def visit_BLOCO_DECISAO(self, node):
        for c in node.children:
            self.visit(c)
    
    def visit_BLOCO_REPETICAO(self, node):
        for c in node.children:
            self.visit(c)
    
    def _extract_operator(self, op_node) -> str:
        """Extrai o símbolo do operador"""
        if op_node.children:
            child = op_node.children[0]
            if child.children:
                return child.children[0].lexeme
        return "?"