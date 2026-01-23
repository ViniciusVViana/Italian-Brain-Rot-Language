from .lexical import lex
from .syntactic import compute_first_follow, augment_grammar, build_slr_table, derv, gramatica
from .semantic import SemanticAnalyzer, TACGenerator, generate_asm_from_tac