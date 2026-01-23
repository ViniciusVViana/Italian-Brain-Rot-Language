import re
import sys

from .pattern_util import patterns_list

# ========== Análise Léxica ==========
# Função que realiza a análise léxica do arquivo de entrada
def lex_anal(arch : str) -> list:
    tokens = []
    line = 1
    while arch:
        for pattern, desc in patterns_list:
            match = re.match(pattern, arch)
            if match:
                tokens.append((match.group(0), desc, line))
                if tokens[-1][0] == "\n":
                    line += 1
                arch = arch[match.end():]
                break
    return tokens

def lex(archive : str):
    
    with open(archive, "r", encoding="utf-8") as file:
        fl = file.read()

    tokens = lex_anal(fl)
        
    if tokens:
        print("Tokens encontrados:")
        for token in tokens:
            val = token[0]
            if val == "\n":
                val = "\\n"
            elif val == "\t":
                val = "\\t"
            elif val == " ":
                val = "' '"
            print(f"[ \033[34m{val}\033[0m  -  \033[32m{token[1]}\033[0m  -  \033[35mLinha {token[2]}\033[0m ]")

    return tokens