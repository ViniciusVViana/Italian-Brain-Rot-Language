from utils import lex
from utils import augment_grammar, compute_first_follow, build_slr_table, derv
import sys
import os

__version__ = "1.0.0"

def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python main.py <argumento(s)>")

    if sys.argv[1] in ("-v", "--version"):
        print(f"versão {__version__}")
        return

    archive = sys.argv[1]
    flag = sys.argv[2] if len(sys.argv) > 2 else "c"

    lex(archive, flag)

    if not os.path.exists("data/slr_table.csv"):
        ff_set = compute_first_follow(gramatica)
        augmented_grammar = augment_grammar(gramatica)
        build_slr_table(augmented_grammar, ff_set)
    else:
        print("Arquivo data/slr_table.csv já existe. ✅\n")

    with open(sys.argv[1], 'r') as file:
        token_list = [line.strip() for line in file if line.strip()]

    derv(token_list)



if __name__ == "__main__":
    main()