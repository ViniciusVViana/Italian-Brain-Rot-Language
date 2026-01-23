"""
Analisador Semântico - Percorre a árvore de derivação e valida regras semânticas
Implementado com funções puras, sem classes (consistente com léxico e sintático)
"""

from ..syntactic import DerivationNode

class SymbolEntry:
    def __init__(self, name: str, tipo: str, scope: int):
        self.name: str = name
        self.tipo: str = tipo
        self.scope: int = scope

class SemanticAnalyzer:
    def __init__(self):
        self.symbols: list[SymbolEntry] = []
        self.scope_stack: list[int] = [0]
        self.scope_id = 0
        self.errors: list[str] = []

    def error(self, message: str):
        self.errors.append(f"Erro semântico: {message}")

    def enter_scope(self):
        self.scope_id += 1
        self.scope_stack.append(self.scope_id)

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
        
    def declare(self, name: str, tipo: str):
        cur = self.scope_stack[-1]
        for s in self.symbols:
            if s.name == name and s.scope == cur:
                self.error(f"Variável {name} ja declarada no escopo {cur}")
                return
        self.symbols.append(SymbolEntry(name, tipo, cur))

    def lookup(self, name: str) -> SymbolEntry | None:
        for sc in reversed(self.scope_stack):
            for s in self.symbols:
                if s.name == name and s.scope == sc:
                    return s
        return None

    """API"""
    def analyse(self, root: DerivationNode):
        self.visit(root)
        if self.errors:
            #print("Erros semanticos encontrados:")
            for err in self.errors:
                print(f" - {err}")
        return self.errors

    """visitor"""
    def visit(self, node):
        if node is None:
            return None
        # anotar tipo no próprio nó (deixa pronto pro TAC)
        if not hasattr(node, "type"):
            node.type = None

        method = getattr(self, f"visit_{node.symbol}", self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for c in getattr(node, "children", []):
            self.visit(c)
        return getattr(node, "type", None)
    
    # ---------- regras por nó (conforme gramatica_util.py) ----------
    def visit_PROGRAMA(self, node):
        # PROGRAMA -> LISTA_DE_COMANDOS
        for c in node.children:
            self.visit(c)

    def visit_LISTA_DE_COMANDOS(self, node):
        for c in node.children:
            self.visit(c)

    def visit_COMANDO(self, node):
        for c in node.children:
            self.visit(c)

    # BLOCO é wrapper: BLOCO -> BLOCO_DECISAO | BLOCO_REPETICAO
    def visit_BLOCO(self, node):
        for c in node.children:
            self.visit(c)

    # BLOCO_DECISAO -> delimitare LISTA_DE_COMANDOS finitini
    def visit_BLOCO_DECISAO(self, node):
        self.enter_scope()
        for c in node.children:
            self.visit(c)
        self.exit_scope()

    # BLOCO_REPETICAO -> sahur LISTA_DE_COMANDOS sahur
    def visit_BLOCO_REPETICAO(self, node):
        self.enter_scope()
        for c in node.children:
            self.visit(c)
        self.exit_scope()

    # DECLARACAO -> TIPO_DE_VARIAVEL id ATRIBUICAO ;
    def visit_DECLARACAO(self, node):
        tipo = None
        name = None
        atrib_node = None

        # filhos esperados: [TIPO_DE_VARIAVEL, id, ATRIBUICAO, ;]
        for c in node.children:
            if c.symbol == "TIPO_DE_VARIAVEL":
                tipo = self.visit(c)  # retorna 'tralalero' etc.
            elif c.symbol == "id":
                name = c.lexeme if c.lexeme else c.symbol
            elif c.symbol == "ATRIBUICAO":
                atrib_node = c

        if tipo is None or name is None:
            self.error("Declaração mal formada (tipo ou id ausente)")
            return

        self.declare(name, tipo)

        # Se tem atribuição (= expr), checar tipo
        if atrib_node:
            rhs_type = self.visit(atrib_node)
            # atribuição vazia -> rhs_type None
            if rhs_type is not None and rhs_type != tipo:
                self.error(f"Atribuição incompatível em '{name}': {tipo} = {rhs_type}")

    def visit_TIPO_DE_VARIAVEL(self, node):
        # TIPO_DE_VARIAVEL -> tralalero | tralala | porcodio | porcoala
        if node.children:
            node.type = node.children[0].symbol
            return node.type
        return None

    # ENTRADA -> batapim id ;
    def visit_ENTRADA(self, node):
        # valida se id foi declarado
        for c in node.children:
            if c.symbol == "id":
                name = c.lexeme if c.lexeme else c.symbol
                if not self.lookup(name):
                    self.error(f"Variável '{name}' usada em batapim, mas não declarada")

    # SAIDA -> chimpanzini EXPRESSAO ;
    def visit_SAIDA(self, node):
        for c in node.children:
            if c.symbol == "EXPRESSAO":
                t = self.visit(c)
                if t is None:
                    self.error("Expressão inválida em chimpanzini (tipo indefinido)")

    # DECISAO -> lirili EXPRESSAO BLOCO [larila BLOCO|DECISAO]
    def visit_DECISAO(self, node):
        # acha a EXPRESSAO (condição)
        cond_type = None
        for c in node.children:
            if c.symbol == "EXPRESSAO":
                cond_type = self.visit(c)
                break

        if cond_type is not None and cond_type != "porcoala":
            self.error(f"Condição do lirili deve ser porcoala, recebido {cond_type}")

        # visita blocos/else
        for c in node.children:
            if c.symbol in ("BLOCO", "BLOCO_DECISAO", "BLOCO_REPETICAO", "DECISAO"):
                self.visit(c)

    # LACO_DE_REPETICAO -> tung EXPRESSAO BLOCO
    def visit_LACO_DE_REPETICAO(self, node):
        cond_type = None
        for c in node.children:
            if c.symbol == "EXPRESSAO":
                cond_type = self.visit(c)
                break
        if cond_type is not None and cond_type != "porcoala":
            self.error(f"Condição do tung deve ser porcoala, recebido {cond_type}")

        for c in node.children:
            if c.symbol == "BLOCO":
                self.visit(c)

    # ATRIBUICAO pode aparecer em 2 contextos na sua gramática:
    # 1) Em declaração: ATRIBUICAO -> '=' TERMO | '=' EXPRESSAO | ε
    # 2) Como comando: ATRIBUICAO -> TERMO '=' EXPRESSAO ';'
    def visit_ATRIBUICAO(self, node):
        # caso epsilon
        if len(node.children) == 0:
            return None

        # tenta detectar forma: '=' X
        if len(node.children) >= 2 and node.children[0].symbol == "=":
            return self.visit(node.children[1])

        # tenta detectar forma: TERMO '=' EXPRESSAO ';'
        # filhos típicos: [TERMO, '=', EXPRESSAO, ';']
        if len(node.children) >= 3 and node.children[1].symbol == "=":
            lhs_type = self.visit(node.children[0])
            rhs_type = self.visit(node.children[2])

            # lhs deve ser id declarado
            if node.children[0].children and node.children[0].children[0].symbol == "id":
                name = node.children[0].children[0].lexeme
                sym = self.lookup(name)
                if not sym:
                    self.error(f"Variável '{name}' não declarada (atribuição)")
                    return None
                lhs_type = sym.tipo

            if lhs_type is not None and rhs_type is not None and lhs_type != rhs_type:
                self.error(f"Atribuição incompatível: {lhs_type} = {rhs_type}")

            return lhs_type

        # fallback
        return self.generic_visit(node)

    # EXPRESSAO -> EXPRESSAO OPERADOR TERMO | TERMO
    def visit_EXPRESSAO(self, node):
        if len(node.children) == 1:
            node.type = self.visit(node.children[0])
            return node.type

        # padrão: [EXPRESSAO, OPERADOR, TERMO]
        left_type = self.visit(node.children[0])
        op_type = self.visit(node.children[1])  # 'arit'/'rel'/'log'
        right_type = self.visit(node.children[2])

        if op_type == "arit":
            if left_type != right_type:
                self.error("Tipos incompatíveis em operação aritmética")
            if left_type not in ("tralalero", "tralala"):
                self.error("Operação aritmética aplicada a tipo não numérico")
            node.type = left_type
            return node.type

        if op_type == "rel":
            # relacional retorna booleano
            if left_type != right_type:
                self.error("Comparação relacional entre tipos diferentes")
            node.type = "porcoala"
            return node.type

        if op_type == "log":
            # lógico exige booleano
            if left_type != "porcoala" or right_type != "porcoala":
                self.error("Operação lógica exige porcoala em ambos os lados")
            node.type = "porcoala"
            return node.type

        # se não souber operador, tenta manter
        node.type = left_type
        return node.type

    # OPERADOR -> OPERADOR_ARITMETICO | OPERADOR_RELACIONAL | OPERADOR_LOGICO
    def visit_OPERADOR(self, node):
        if not node.children:
            return None
        child = node.children[0].symbol
        if child == "OPERADOR_ARITMETICO":
            return "arit"
        if child == "OPERADOR_RELACIONAL":
            return "rel"
        if child == "OPERADOR_LOGICO":
            return "log"
        return None

    # TERMO -> id | valor_inteiro | valor_real | VALOR_BOOL | caractere | string
    def visit_TERMO(self, node):
        if not node.children:
            return None
        leaf = node.children[0]

        if leaf.symbol == "id":
            name = leaf.lexeme
            sym = self.lookup(name)
            if not sym:
                self.error(f"Variável '{name}' usada mas não declarada")
                node.type = None
                return None
            node.type = sym.tipo
            return node.type

        if leaf.symbol == "valor_inteiro":
            node.type = "tralalero"
            return node.type

        if leaf.symbol == "valor_real":
            node.type = "tralala"
            return node.type

        if leaf.symbol == "VALOR_BOOL":
            node.type = "porcoala"
            return node.type

        if leaf.symbol == "caractere":
            node.type = "porcodio"
            return node.type

        if leaf.symbol == "string":
            node.type = "string"
            return node.type

        return None

    def visit_VALOR_BOOL(self, node):
        # tripi|tropa
        node.type = "porcoala"
        return node.type
    
    def print_table(self):
        """
        Imprime a tabela de símbolos organizada por escopo
        """
        print("\n📋 Tabela de Símbolos")
        print("=" * 70)
        
        if not self.symbols:
            print("  (vazia)")
            print("=" * 70)
            return
        
        # Agrupa símbolos por escopo
        scopes = {}
        for sym in self.symbols:
            if sym.scope not in scopes:
                scopes[sym.scope] = []
            scopes[sym.scope].append(sym)
        
        # Imprime cada escopo
        for scope_id in sorted(scopes.keys()):
            scope_label = "global" if scope_id == 0 else f"local {scope_id}"
            print(f"\n  Escopo {scope_id} ({scope_label}):")
            for sym in scopes[scope_id]:
                print(f"    {sym.name:20} | tipo: {sym.tipo:15}")
        
        print("\n" + "=" * 70)