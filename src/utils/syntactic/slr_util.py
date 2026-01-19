""" Modulo com funções que criaram a tabela SLR(1) de análise sintática. """

from .gramatica_util import ALL_TERMINALS, ALL_NONTERMINALS, EPS, ENDMARK
import csv, os
from collections import defaultdict
import pprint

# Função para criar pasta data
def ensure_data_folder() -> None:
    """Garante que a pasta 'data' existe"""
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Pasta 'data' criada ✅")

def augment_grammar(grammar: dict) -> dict:
    """
    Aumenta a gramática adicionando uma nova produção S' -> S
    
    :param grammar: dicionário da gramática original
    :return: gramática aumentada
    """
    start_symbol = list(grammar.keys())[0]
    augmented = {"S'": [[start_symbol]]}
    augmented.update(grammar)
    return augmented

def compute_lr0_items(grammar: dict) -> dict:
    """
    Computa os itens LR(0) para cada produção da gramática
    
    :param grammar: dicionário da gramática
    :return: dicionário com todos os itens LR(0)
    """
    items = {}
    item_id = 0
    
    for lhs, productions in grammar.items():
        for production in productions:
            # Cria itens com ponto em todas as posições possíveis
            for dot_pos in range(len(production) + 1):
                before_dot = production[:dot_pos]
                after_dot = production[dot_pos:]
                
                item = (lhs, tuple(before_dot), tuple(after_dot))
                items[item_id] = item
                item_id += 1
    
    return items

def closure(items: set, grammar: dict) -> set:
    """
    Computa o fechamento de um conjunto de itens LR(0)
    
    :param items: conjunto de itens LR(0)
    :param grammar: dicionário da gramática
    :return: fechamento do conjunto de itens
    """
    closure_set = set(items)
    added = True
    
    while added:
        added = False
        new_items = set()
        
        for item in closure_set:
            lhs, before_dot, after_dot = item
            
            # Se há símbolos após o ponto e o primeiro é não-terminal
            if after_dot and after_dot[0] in ALL_NONTERMINALS:
                next_symbol = after_dot[0]
                
                # Adiciona todos os itens A -> •α para cada produção A -> α
                if next_symbol in grammar:
                    for production in grammar[next_symbol]:
                        new_item = (next_symbol, (), tuple(production))
                        if new_item not in closure_set:
                            new_items.add(new_item)
                            added = True
        
        closure_set.update(new_items)
    
    return closure_set

def goto(items: set, symbol: str, grammar: dict) -> set:
    """
    Computa a função GOTO para um conjunto de itens e um símbolo
    
    :param items: conjunto de itens LR(0)
    :param symbol: símbolo da gramática
    :param grammar: dicionário da gramática
    :return: conjunto GOTO(items, symbol)
    """
    goto_set = set()
    
    for item in items:
        lhs, before_dot, after_dot = item
        
        # Se o símbolo após o ponto é o símbolo desejado
        if after_dot and after_dot[0] == symbol:
            # Move o ponto uma posição para a direita
            new_before = before_dot + (after_dot[0],)
            new_after = after_dot[1:]
            new_item = (lhs, new_before, new_after)
            goto_set.add(new_item)
    
    return closure(goto_set, grammar) if goto_set else set()

def compute_lr0_states(grammar: dict) -> tuple:
    """
    Computa todos os estados LR(0) da gramática
    
    :param grammar: dicionário da gramática aumentada
    :return: tupla contendo (estados, transições)
    """
    # Estado inicial: fechamento de [S' -> •S]
    start_symbol = list(grammar.keys())[1]  # Segundo símbolo (primeiro após S')
    start_item = ("S'", (), (start_symbol,))  # S' -> •S
    initial_state = closure({start_item}, grammar)
    
    states = [initial_state]
    transitions = {}
    state_map = {frozenset(initial_state): 0}
    
    i = 0
    while i < len(states):
        current_state = states[i]
        
        # Para cada símbolo da gramática
        all_symbols = set()
        for item in current_state:
            lhs, before_dot, after_dot = item
            if after_dot:
                all_symbols.add(after_dot[0])
        
        for symbol in all_symbols:
            next_state = goto(current_state, symbol, grammar)
            
            if next_state:
                next_state_frozen = frozenset(next_state)
                
                if next_state_frozen not in state_map:
                    state_map[next_state_frozen] = len(states)
                    states.append(next_state)
                
                transitions[(i, symbol)] = state_map[next_state_frozen]
        
        i += 1
    
    return states, transitions

def save_slr_table(table: dict, filename: str = "slr_table.csv") -> None:
    """
    Salva a tabela SLR(1) em um arquivo CSV
    
    :param table: tabela SLR(1)
    :param filename: nome do arquivo
    """
    ensure_data_folder()  # Cria a pasta se não existir
    filepath = os.path.join("data", filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Cabeçalho
        terminals = sorted(ALL_TERMINALS) + [ENDMARK]
        nonterminals = sorted(ALL_NONTERMINALS)
        header = ['State'] + [t for t in terminals] + [nt for nt in nonterminals]
        writer.writerow(header)
        
        # Estados
        max_state = max(max(table['action'].keys(), default=-1), max(table['goto'].keys(), default=-1))
        
        for state in range(max_state + 1):
            row = [state]
            
            # Colunas ACTION
            for terminal in terminals:
                action = table['action'][state].get(terminal, '')
                row.append(action)
            
            # Colunas GOTO
            for nt in nonterminals:
                goto = table['goto'][state].get(nt, '')
                row.append(goto)
            
            writer.writerow(row)
    
    print(f"Tabela SLR(1) salva em 'data/{filename}' ✅")

def build_slr_table(grammar: dict, first_follow: dict, debug: bool = False) -> None:
    """
    Constrói a tabela de análise SLR(1) e salva em um arquivo CSV

    :param grammar: dicionário da gramática
    :param first_follow: dicionários FIRST e FOLLOW
    :param debug: habilita a saída de depuração
    :return: None
    """
    slr_file_path = os.path.join("data", "slr_table.csv")
    if os.path.exists(slr_file_path):
        print("\tO arquivo data/slr_table.csv já existe. ✅")
        return

    states, transitions = compute_lr0_states(grammar)
    
    # Inicializa a tabela
    table = {
        'action': defaultdict(dict),
        'goto': defaultdict(dict)
    }
    
    # Enumera as produções ORIGINAIS (sem S') para os números das reduções
    original_grammar = {k: v for k, v in grammar.items() if k != "S'"}
    productions = []
    for lhs, prods in original_grammar.items():
        for prod in prods:
            productions.append((lhs, prod))
    
    if debug: print(f"Debug: Encontradas {len(productions)} produções para redução:")
    for i, (lhs, prod) in enumerate(productions):
        if debug: print(f"  {i}: {lhs} -> {prod}")

    # Preenche a tabela
    for state_num, state in enumerate(states):
        if debug: print(f"\nDebug: Analisando Estado {state_num}:")
        for item in state:
            lhs, before_dot, after_dot = item
            if debug: print(f"  Item: {lhs} -> {list(before_dot)} • {list(after_dot)}")
            
            # Shift: A -> α•aβ onde a é terminal
            if after_dot and after_dot[0] in ALL_TERMINALS:
                terminal = after_dot[0]
                if (state_num, terminal) in transitions:
                    next_state = transitions[(state_num, terminal)]
                    table['action'][state_num][terminal] = f's{next_state}'
                    if debug: print(f"    Shift {terminal} -> Estado {next_state}")
            # Reduce: A -> α• onde A ≠ S' (item completo)
            elif not after_dot and lhs != "S'":
                try:
                    prod_num = productions.index((lhs, list(before_dot)))
                    if debug: print(f"    Item de redução encontrado: {lhs} -> {list(before_dot)} (produção {prod_num})")
                    
                    # Para cada símbolo no FOLLOW(A)
                    if lhs in first_follow:
                        follow_set = first_follow[lhs]['follow']
                        if debug: print(f"    FOLLOW({lhs}) = {follow_set}")
                        
                        for symbol in follow_set:
                            if debug: print(f"        Considerando símbolo de FOLLOW: {symbol}")
                            if symbol in ALL_TERMINALS or symbol == ENDMARK:
                                table['action'][state_num][symbol] = f'r{prod_num}'
                                if debug: print(f"    Redução r{prod_num} em {symbol}")
                    else:
                        if debug: print(f"    ERRO: {lhs} não encontrado em first_follow!")
                        
                except ValueError as e:
                    if debug: print(f"    ERRO: Produção {lhs} -> {list(before_dot)} não encontrada nas produções!")
                    if debug: print(f"    Produções disponíveis: {productions}")

            # Accept: S' -> S•
            elif not after_dot and lhs == "S'":
                table['action'][state_num][ENDMARK] = 'acc'
                if debug: print(f"    Accept em {ENDMARK}")

        # GOTO para não-terminais
        for nt in ALL_NONTERMINALS:
            if (state_num, nt) in transitions:
                next_state = transitions[(state_num, nt)]
                table['goto'][state_num][nt] = next_state
                if debug: print(f"    GOTO {nt} -> Estado {next_state}")

    # linha da action que tenham redução devem ser preenchidas com redução por completo
    # ALL_TERMINALS é um `set`, não suportando concatenação com lista. Convertemos
    # para uma lista ordenada para garantir comportamento determinístico.
    for state in table['action']:
        for terminal in sorted(ALL_TERMINALS) + [ENDMARK]:
            value = table['action'][state].get(terminal, '')
            # Se já existe um shift (por exemplo 's3'), não sobrescrevemos
            if isinstance(value, str) and value.startswith('s'):
                continue
            if isinstance(value, str) and value.startswith('r'):
                reduct = value
                for t in sorted(ALL_TERMINALS) + [ENDMARK]:
                    if t not in table['action'][state]:
                        table['action'][state][t] = reduct
                continue
            if terminal not in table['action'][state]:
                table['action'][state][terminal] = 'error'

    print("\nTabela SLR(1) construída com sucesso. ✅")
    save_slr_table(table)