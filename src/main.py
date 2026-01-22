from utils import lex
from utils import augment_grammar, compute_first_follow, build_slr_table, derv, gramatica
from utils import analyze_semantic
from utils.semantic.tac import generate_tac_from_tree
import sys
import os

__version__ = "1.0.0"

def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python main.py <argumento(s)>")

    if sys.argv[1] in ("-v", "--version"):
        print(f"versão {__version__}")
        return

    archive : str = sys.argv[1]
    flag : str = sys.argv[2] if len(sys.argv) > 2 else "c"

    token_list : list = lex(archive, flag)

    if not os.path.exists("data/slr_table.csv"):
        ff_set = compute_first_follow(gramatica)
        augmented_grammar = augment_grammar(gramatica)
        build_slr_table(augmented_grammar, ff_set)
    else:
        print("Arquivo data/slr_table.csv já existe. ✅\n")

    derivation_tree = derv(token_list)

    # semantica
    if derivation_tree:
        semantic_ok, symbol_table = analyze_semantic(derivation_tree)
        if not semantic_ok:
            sys.exit(1)

        # Geração de código intermediário (TAC)
        tac_generator = generate_tac_from_tree(derivation_tree, symbol_table)

        # Salva o código TAC em um arquivo
        output_file = os.path.splitext(archive)[0] + "_tac.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in tac_generator.get_code():
                f.write(line + '\n')
        print(f"\n✅ Código TAC salvo em: {output_file}")

    #symbol_table.print_table()



if __name__ == "__main__":
    main()