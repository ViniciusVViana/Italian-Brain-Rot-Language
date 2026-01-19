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
                # verificar se a variavel ja foi declarada
                if match.group(0) in [token[0] for token in tokens] and desc == "id" and tokens[-2][1] == "TIPO_DE_VARIAVEL":
                    raise NameError(f"Erro léxico: Identificador '{match.group(0)}' já declarado na linha {line}.")
                tokens.append((match.group(0), desc, line))
                if tokens[-1][0] == "\n":
                    line += 1
                arch = arch[match.end():]
                break
    return tokens

def lex(archive : str, flag : str ="c"):
    
    with open(archive, "r", encoding="utf-8") as file:
        fl = file.read()

    tokens = lex_anal(fl)

    if flag == "f":
        archive_name = archive.split("\\")[-1].split(".")[0] + "_out.txt"
        with open(f"saida/{archive_name}", "w", encoding="utf-8") as out_file:
            if not tokens:
                out_file.write("Nenhum token encontrado.\n")
            else:
                for token in tokens:
                    val = token[0]
                    if val == "\n":
                        val = "\\n"
                    elif val == "\t":
                        val = "\\t"
                    elif val == " ":
                        val = "' '"
                    out_file.write(f"[ {val}  -  {token[1]}  -  Linha {token[2]} ]\n")
        print(f"Tokens escritos em {archive_name} no diretório saida.")
        
    else:
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