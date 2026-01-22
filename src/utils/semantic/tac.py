"""
Gerador de Código Intermediário de 3 Endereços (Three Address Code - TAC)
Percorre a árvore de derivação após análise semântica e gera código intermediário
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class OpType(Enum):
    """Tipos de operações suportadas"""
    # Operações binárias
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    EQ = '=='
    NEQ = '!='
    LT = '<'
    GT = '>'
    LEQ = '<='
    GEQ = '>='
    AND = '&&'
    OR = '||'
    # Operações unárias
    NEG = '-'      # negação aritmética
    NOT = '!'      # negação lógica
    # Desvios
    GOTO = 'goto'
    IF_GOTO = 'if_goto'
    # Chamadas
    INPUT = 'input'
    OUTPUT = 'output'

@dataclass
class TACInstruction:
    """Uma instrução de 3 endereços"""
    op: OpType           # Operação
    arg1: Optional[str]  # Primeiro operando (variável ou constante)
    arg2: Optional[str]  # Segundo operando (variável ou constante)
    result: Optional[str] # Resultado/destino
    label: Optional[str] = None  # Rótulo (para desvios)
    
    def __str__(self):
        """Representação em string da instrução"""
        if self.op == OpType.GOTO:
            return f"goto {self.label}"
        elif self.op == OpType.IF_GOTO:
            return f"if {self.arg1} goto {self.label}"
        elif self.op == OpType.INPUT:
            return f"{self.result} = input()"
        elif self.op == OpType.OUTPUT:
            return f"output({self.arg1})"
        elif self.arg2 is None:  # Operação unária
            return f"{self.result} = {self.op.value} {self.arg1}"
        else:  # Operação binária
            return f"{self.result} = {self.arg1} {self.op.value} {self.arg2}"

class TACGenerator:
    """Gerador de código de 3 endereços"""
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_count = 0  # Contador para gerar temporários t1, t2, etc
        self.label_count = 0 # Contador para gerar rótulos L1, L2, etc
        self.symbol_table = None
    
    def new_temp(self) -> str:
        """Gera um novo identificador temporário"""
        self.temp_count += 1
        return f"t{self.temp_count}"
    
    def new_label(self) -> str:
        """Gera um novo rótulo"""
        self.label_count += 1
        return f"L{self.label_count}"
    
    def emit(self, op: OpType, arg1: str = None, arg2: str = None, 
             result: str = None, label: str = None) -> str:
        """Emite uma instrução TAC e retorna o resultado"""
        instr = TACInstruction(op, arg1, arg2, result, label)
        self.instructions.append(instr)
        return result
    
    def emit_unary_op(self, op: OpType, operand: str) -> str:
        """Emite operação unária: result = op operand"""
        result = self.new_temp()
        self.emit(op, operand, None, result)
        return result
    
    def emit_binary_op(self, op: OpType, left: str, right: str) -> str:
        """Emite operação binária: result = left op right"""
        result = self.new_temp()
        self.emit(op, left, right, result)
        return result
    
    def emit_assignment(self, var: str, value: str):
        """Emite atribuição: var = value"""
        # Se value é um temporário ou constante, copia para var
        self.emit(OpType.ADD, value, "0", var)  # x = y + 0 é equivalente a x = y
    
    def emit_goto(self, label: str):
        """Emite desvio incondicional"""
        self.emit(OpType.GOTO, None, None, None, label)
    
    def emit_if_goto(self, condition: str, label: str):
        """Emite desvio condicional: if condition goto label"""
        self.emit(OpType.IF_GOTO, condition, None, None, label)
    
    def emit_input(self) -> str:
        """Emite leitura: result = input()"""
        result = self.new_temp()
        self.emit(OpType.INPUT, None, None, result)
        return result
    
    def emit_output(self, var: str):
        """Emite saída: output(var)"""
        self.emit(OpType.OUTPUT, var, None, None)
    
    def print_code(self):
        """Imprime o código de 3 endereços formatado"""
        print("\n📝 Código Intermediário de 3 Endereços")
        print("=" * 70)
        for i, instr in enumerate(self.instructions, 1):
            print(f"{i:3d}. {instr}")
        print("=" * 70)
    
    def get_code(self) -> List[str]:
        """Retorna código como lista de strings"""
        return [str(instr) for instr in self.instructions]


# Instância global para usar em seman.py
_tac_generator = None

def init_tac_generator():
    """Inicializa o gerador TAC"""
    global _tac_generator
    _tac_generator = TACGenerator()
    return _tac_generator

def get_tac_generator() -> TACGenerator:
    """Retorna o gerador TAC"""
    global _tac_generator
    if _tac_generator is None:
        _tac_generator = TACGenerator()
    return _tac_generator

def generate_tac_from_tree(derivation_tree, symbol_table) -> TACGenerator:
    """
    Função principal para gerar TAC a partir da árvore de derivação
    
    Args:
        derivation_tree: DerivationTree do parser
        symbol_table: SymbolTable da análise semântica
    
    Returns:
        TACGenerator com código intermediário gerado
    """
    global _tac_generator
    
    _tac_generator = TACGenerator()
    _tac_generator.symbol_table = symbol_table
    
    print("\n🔨 Gerando código intermediário de 3 endereços...")
    print("=" * 70)
    
    if derivation_tree.root:
        _visit_for_tac(derivation_tree.root)
    else:
        print("❌ Árvore de derivação vazia!")
    
    _tac_generator.print_code()
    
    return _tac_generator


def _visit_for_tac(node) -> str:
    """
    Percorre a árvore e gera TAC recursivamente
    Retorna o "endereço" (variável ou temporário) do resultado
    """
    tac = get_tac_generator()
    
    if not node:
        return None
    
    symbol = node.symbol
    
    # Processa diferentes tipos de nós
    if symbol == "PROGRAMA":
        for child in node.children:
            _visit_for_tac(child)

    elif symbol in ("LISTA_DE_COMANDOS", "COMANDO"):
        # Percorre sequência de comandos
        for child in node.children:
            _visit_for_tac(child)
    
    elif symbol == "DECLARACAO":
        # DECLARACAO -> TIPO ID
        # Não gera código para declaração
        pass
    
    elif symbol in ("BLOCO", "BLOCO_DECISAO", "BLOCO_REPETICAO"):
        for child in node.children:
            _visit_for_tac(child)
    
    elif symbol == "ATRIBUICAO":
        # ATRIBUICAO produzida pela gramática: TERMO = EXPRESSAO ;
        # ou variações com = TERMO / = EXPRESSAO. Vamos extrair id e expressão.
        var_name = _extract_identifier(node)

        # Procura o nó da expressão ou termo à direita do '='
        expr_node = None
        for child in reversed(node.children):
            if getattr(child, "symbol", None) in ("EXPRESSAO", "TERMO"):
                expr_node = child
                break
        if expr_node is None and node.children:
            expr_node = node.children[-1]

        expr_result = _visit_for_tac(expr_node) if expr_node else None

        if var_name and expr_result:
            tac.emit_assignment(var_name, expr_result)
    
    elif symbol == "EXPRESSAO":
        # Processa expressão e retorna seu resultado
        return _visit_expression_for_tac(node)
    
    elif symbol == "ENTRADA":
        # ENTRADA -> leia ID
        if len(node.children) >= 2:
            var_node = node.children[1]
            var_name = var_node.lexeme
            temp = tac.emit_input()
            tac.emit_assignment(var_name, temp)
    
    elif symbol == "SAIDA":
        # SAIDA -> escreva EXPRESSAO
        if len(node.children) >= 2:
            expr_node = node.children[1]
            expr_result = _visit_for_tac(expr_node)
            if expr_result:
                tac.emit_output(expr_result)
    
    elif symbol == "DECISAO":
        # DECISAO -> se ( EXPRESSAO ) BLOCO
        # ou se ( EXPRESSAO ) BLOCO senao BLOCO
        label_else = tac.new_label()
        label_end = tac.new_label()
        
        # Testa condição
        if len(node.children) >= 3:
            cond_node = node.children[2]
            cond_result = _visit_for_tac(cond_node)
            
            # if not condition goto else
            tac.emit_if_goto(f"!{cond_result}", label_else)
            
            # Bloco if
            if len(node.children) >= 5:
                block_node = node.children[4]
                _visit_for_tac(block_node)
            
            tac.emit_goto(label_end)
            
            # Rótulo else
            # Processa senao se existir
            found_senao = False
            for child in node.children:
                if child.symbol == "senao" if hasattr(child, 'symbol') else child.lexeme == "senao":
                    found_senao = True
                    break
            
            if found_senao and len(node.children) >= 8:
                # Bloco else
                block_else = node.children[7]
                _visit_for_tac(block_else)
        
        # Rótulo fim
    
    elif symbol == "LACO_DE_REPETICAO":
        # LACO -> tung ( EXPRESSAO ) BLOCO
        label_loop = tac.new_label()
        label_end = tac.new_label()
        
        # Início do loop
        # Emite rótulo (não é instrução, apenas marca posição)
        
        # Testa condição
        if len(node.children) >= 3:
            cond_node = node.children[2]
            cond_result = _visit_for_tac(cond_node)
            
            # if not condition goto end
            tac.emit_if_goto(f"!{cond_result}", label_end)
            
            # Bloco loop
            if len(node.children) >= 5:
                block_node = node.children[4]
                _visit_for_tac(block_node)
            
            # Volta ao início
            tac.emit_goto(label_loop)
    
    return None


def _visit_expression_for_tac(node) -> str:
    """Processa EXPRESSAO e retorna seu resultado (variável ou temporário)"""
    tac = get_tac_generator()
    
    if not node or not hasattr(node, 'children'):
        return None
    
    # Se é um terminal (ID, número)
    if node.is_terminal:
        return node.lexeme
    
    # Se tem apenas um filho, retorna o resultado dele
    if len(node.children) == 1:
        return _visit_expression_for_tac(node.children[0])
    
    # Se tem 3 filhos: esquerda operador direita
    if len(node.children) >= 3:
        left = _visit_expression_for_tac(node.children[0])
        right = _visit_expression_for_tac(node.children[2])
        
        # Extrai o operador
        op_node = node.children[1]
        op_str = op_node.lexeme if hasattr(op_node, 'lexeme') else str(op_node.symbol)
        
        # Mapeia operador para OpType
        op_map = {
            '+': OpType.ADD,
            '-': OpType.SUB,
            '*': OpType.MUL,
            '/': OpType.DIV,
            '%': OpType.MOD,
            '==': OpType.EQ,
            '!=': OpType.NEQ,
            '<': OpType.LT,
            '>': OpType.GT,
            '<=': OpType.LEQ,
            '>=': OpType.GEQ,
            '&&': OpType.AND,
            '||': OpType.OR,
        }
        
        op = op_map.get(op_str)
        if op:
            return tac.emit_binary_op(op, left, right)
    
    # Se tem 2 filhos: operador unário
    if len(node.children) == 2:
        op_node = node.children[0]
        operand = _visit_expression_for_tac(node.children[1])
        
        op_str = op_node.lexeme if hasattr(op_node, 'lexeme') else str(op_node.symbol)
        op_map = {
            '-': OpType.NEG,
            '!': OpType.NOT,
        }
        
        op = op_map.get(op_str)
        if op:
            return tac.emit_unary_op(op, operand)
    
    return None


def _extract_identifier(node) -> str:
    """Busca o primeiro identificador (terminal 'id') na subárvore"""
    if not node:
        return None
    if getattr(node, "is_terminal", False) and getattr(node, "symbol", None) == "id":
        return node.lexeme
    if hasattr(node, "children"):
        for child in node.children:
            found = _extract_identifier(child)
            if found:
                return found
    return None
