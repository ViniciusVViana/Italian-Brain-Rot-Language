""" Modulo para computar os conjuntos FIRST e FOLLOW de uma gramática livre de contexto (CFG) e salvar os resultados em um arquivo CSV. """

from utils import ALL_NONTERMINALS, ALL_TERMINALS, EPS, ENDMARK

import csv, os

# Função para criar pasta data
def ensure_data_folder():
    """Garante que a pasta 'data' existe"""
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Pasta 'data' criada ✅")

def compute_first(prod_list:list, grammar:dict) -> set:
    """
    computa o conjunto FIRST para uma produção

    :param prod_list: lista de produções (cada produção é uma lista de símbolos)
    :return: conjunto FIRST como um set
    """
    result_set = set()
    for prod in prod_list:
        if prod[0] in ALL_TERMINALS:
            result_set.add(prod[0])
        elif prod[0] == EPS:
            result_set.add(EPS)
        elif prod[0] == 'EXPRESSAO':
            continue
        elif prod[0] in ALL_NONTERMINALS:
            result_set.update(compute_first(grammar[prod[0]], grammar))
    return result_set

def compute_follow(key:str, grammar:dict, first_sets:dict, follow_sets:dict) -> set:
    """
    computa o conjunto FOLLOW para uma produção

    :param key: o não-terminal para o qual estamos computando o conjunto FOLLOW
    :param grammar: dicionário representando a gramática
    :param first_sets: dicionário com os conjuntos FIRST de cada não-terminal
    :param follow_sets: dicionário com os conjuntos FOLLOW de cada não-terminal
    :return: conjunto FOLLOW como um set
    """
    follow = follow_sets[key]
    for A, productions in grammar.items():
        for production in productions:
            for i, B in enumerate(production):
                if B == key:
                    if i + 1 < len(production):
                        beta = production[i + 1]
                        if beta in ALL_TERMINALS:
                            follow.add(beta)
                        elif beta in ALL_NONTERMINALS:
                            follow.update(x for x in first_sets[beta] if x != EPS)
                            if EPS in first_sets[beta]:
                                follow.update(follow_sets[A])
                    else:
                        if A != key:
                            follow.update(follow_sets[A])
    return follow


def compute_first_follow(grammar: dict) -> dict:
    """
    computa os conjuntos FIRST e FOLLOW para a gramática fornecida e salva conjunto em um arquivo .csv

    :param grammar: dicionário representando a gramática
    :return: dict com conjuntos FIRST e FOLLOW
    """
    # Garante que a pasta data existe
    ensure_data_folder()
    
    ff_file_path = os.path.join("data", "first_follow.csv")
    
    # Verifica se o arquivo first_follow.csv já existe
    if os.path.exists(ff_file_path):
        print("O arquivo data/first_follow.csv já existe.")
        with open(ff_file_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            ff_set = {row["non_terminal"]: {
                "first": set(item.strip().strip("'\"") for item in row["first"].strip("{}").split(", ") if item.strip()) if row["first"] else set(),
                "follow": set(item.strip().strip("'\"") for item in row["follow"].strip("{}").split(", ") if item.strip()) if row["follow"] else set()
            } for row in reader}
            print("Arquivo lido com sucesso. ✅\n")
        return ff_set

    first = {nt: set() for nt in grammar}
    for key in grammar:
        first[key] = compute_first(grammar[key], grammar)

    follow = {nt: set() for nt in grammar}
    for key in grammar:
        if key == list(grammar.keys())[0]:  # Supondo que o primeiro não-terminal é o inicial
            follow[key].add(ENDMARK)  # Adiciona o marcador de fim de entrada ao FOLLOW do símbolo inicial
        else:
            follow[key] = compute_follow(key, grammar, first, follow)
    
    # junta em first e follow em um único dicionario
    ff_set = {nt: {"first": first[nt], "follow": follow[nt]} for nt in grammar}

    # escreve em um arquivo .csv na pasta data
    with open(ff_file_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["non_terminal", "first", "follow"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for nt, sets in ff_set.items():
            writer.writerow({"non_terminal": nt, "first": sets["first"], "follow": sets["follow"]})

    print("Arquivo data/first_follow.csv criado e salvo com sucesso. ✅\n")
    return ff_set