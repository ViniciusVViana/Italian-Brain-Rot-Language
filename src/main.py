from pathlib import Path
from utils import lex
from utils import augment_grammar, compute_first_follow, build_slr_table, derv, gramatica
from utils import SemanticAnalyzer, TACGenerator, generate_asm_from_tac
import sys
import os
import subprocess

__version__ = "1.0.0"

def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: ibr <argumento(s)>")

    if sys.argv[1] in ("-v", "--version"):
        print(f"versão {__version__}")
        return

    archive : str = sys.argv[1]
    output_archive : str = sys.argv[2] if len(sys.argv) > 2 else "program.exe"

    """ANALISE LÉXICA"""
    token_list : list = lex(archive)

    """ANALISE SINTÁTICA"""
    ff_set = compute_first_follow(gramatica)
    augmented_grammar = augment_grammar(gramatica)
    slr = build_slr_table(augmented_grammar, ff_set)

    derivation_tree = derv(token_list, slr)

    #derivation_tree.print_tree_format()

    """ANALISE SEMÂNTICA E GERAÇÃO DE CÓDIGO INTERMEDIÁRIO (TAC)"""
    sem = SemanticAnalyzer()

    sem_errors = sem.analyse(derivation_tree.root)

    if not sem_errors:
        tac_gen = TACGenerator()
        tac_code = tac_gen.generate(derivation_tree.root, sem.symbols)
        asm_path = generate_asm_from_tac(tac_code, Path("out.s"))
        subprocess.run(["gcc", "out.s", "-o", output_archive])
        subprocess.run(["rm", "out.s"])

if __name__ == "__main__":
    main()