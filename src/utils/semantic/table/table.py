from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

class SymbolType(Enum):
    """Tipos de dados suportados na linguagem"""
    INT = 'int'     # tralalero
    FLOAT = 'float' # tralala
    CHAR = 'char'   # porcodio
    BOOL = 'bool'   # porcoala

IBRL_TYPE_MAP = {
    'tralalero': SymbolType.INT,
    'tralala': SymbolType.FLOAT,
    'porcodio': SymbolType.CHAR,
    'porcoala': SymbolType.BOOL
}

@dataclass
class Symbol:
    name: str
    sym_type: SymbolType  # 'terminal' or 'non-terminal'
    line: int = None
    scope_level: int = None
    def __str__(self):
        return f"Symbol(name={self.name}, type={self.sym_type}, line={self.line})"
    
class SymbolTable:
    """Tabela de simbolos com suporte a escopos aninhados"""
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Pilha de escopos
        self.scope_level: int = 0
        self.errors: List[str] = []
        self.closed_scopes: List[Dict] = []  # Histórico de escopos encerrados

    def push_scope(self):
        """Entra em um novo escopo"""
        self.scopes.append({})
        self.scope_level += 1
    
    def pop_scope(self):
        """Sai do escopo atual e salva seu snapshot"""
        if len(self.scopes) > 1:
            closed_scope = self.scopes.pop()
            self.closed_scopes.append({
                'level': self.scope_level,
                'symbols': dict(closed_scope)
            })
            self.scope_level -= 1
        else:
            self.errors.append(f"❌ Tentativa de sair do escopo global")

    def declare(self, name: str, type: str, line: int) -> bool:
        """Declara uma nova variável no escopo atual"""
        current_scope = self.scopes[-1]
        
        # Verifica redeclaração no escopo corrente
        if name in current_scope:
            error_msg = f"❌ Erro semântico (linha {line}): Identificador '{name}' já declarado na linha {current_scope[name].line}"
            self.errors.append(error_msg)
            return False
        
        # Converte tipo IBRL para SymbolType
        sym_type = IBRL_TYPE_MAP.get(type)
        if not sym_type:
            error_msg = f"❌ Erro semântico (linha {line}): Tipo desconhecido '{type}'"
            self.errors.append(error_msg)
            return False
        
        # Cria e adiciona o símbolo
        symbol = Symbol(
            name=name,
            sym_type=sym_type,
            line=line,
            scope_level=self.scope_level
        )
        current_scope[name] = symbol
        return True
    
    def resolve(self, name: str) -> Optional[Symbol]:
        """Procura um símbolo da pilha no escopo atual"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def assign(self, name: str, value, line: int) -> bool:
        """Valida atribuição a uma variavel"""
        symbol = self.resolve(name)

        # Verifica se a variavel existe
        if not symbol:
            error_msg = f"❌ Erro semântico (linha {line}): Identificador '{name}' não declarado"
            self.errors.append(error_msg)
            return False
        
        # Valida compatibilidade de tipo (simplificado)
        if isinstance(value, SymbolType):
            if value != symbol.sym_type and not self.is_compatible(symbol.sym_type, value):
                error_msg = f"❌ Erro semântico (linha {line}): Tipo incompatível em atribuição a '{name}'. Esperado {symbol.sym_type.value}, recebido {value.value}"
                self.errors.append(error_msg)
                return False
            
        return True
    
    def __contains__(self, name: str) -> bool:
        """Verifica se um símbolo existe em qualquer escopo"""
        return self.resolve(name) is not None
    
    def is_compatible(self, expected: SymbolType, given: SymbolType) -> bool:
        """Verifica compatibilidade de tipos (pode incluir coerção)"""
        # Regras de coerção: int -> float
        if expected == SymbolType.FLOAT and given == SymbolType.INT:
            return True
        return False
    
    def get_all_symbols(self) -> List[Symbol]:
        """Retorna todos os símbolos do escopo atual"""
        return list(self.scopes[-1].values())
    
    def print_table(self):
        """Imprime a tabela de símbolos de forma formatada, incluindo escopos encerrados"""
        print("\n📋 Tabela de Símbolos")
        print("=" * 70)
        
        # Escopos ativos (ainda na pilha)
        for level, scope in enumerate(self.scopes):
            print(f"\n  Escopo {level} ({'global' if level == 0 else 'local'}) [ATIVO]:")
            if not scope:
                print(f"    (vazio)")
            else:
                for name, symbol in scope.items():
                    print(f"    {symbol.name:20} | tipo: {symbol.sym_type.value:8} | linha: {symbol.line}")
        
        # Escopos encerrados (histórico)
        if self.closed_scopes:
            print(f"\n  ─── Escopos Encerrados ───")
            for closed in self.closed_scopes:
                level = closed['level']
                symbols = closed['symbols']
                print(f"\n  Escopo {level} (local) [ENCERRADO]:")
                for name, symbol in symbols.items():
                    print(f"    {symbol.name:20} | tipo: {symbol.sym_type.value:8} | linha: {symbol.line}")
        
        print("\n" + "=" * 70)

    def print_errors(self):
        """Imprime todos os erros semânticos encontrados"""
        if not self.errors:
            print("\n✅ Nenhum erro semântico encontrado!")
        else:
            print("\n❌ Erros semânticos encontrados:")
            for error in self.errors:
                print(f"  {error}")