"""
Modulo para funções relacionadas à derivação de cadeias em uma gramática livre de contexto (CFG).
"""
import pprint, csv
from .gramatica_util import gramatica, ENDMARK, EPS, ALL_NONTERMINALS

class DerivationNode:
    """Classe para representar um nó na árvore de derivação"""
    def __init__(self, symbol, lexeme=None, state=None, depth=0, parent=None, line=None):
        self.symbol = symbol
        self.lexeme = lexeme  # Para terminais, armazena o valor original
        self.state = state
        self.line = line  # Linha do código-fonte
        self.depth = depth
        self.parent = parent
        self.children = []
        self.is_terminal = symbol not in gramatica and symbol not in ALL_NONTERMINALS
    
    def add_child(self, child_node):
        """Adiciona um filho ao nó"""
        child_node.parent = self
        self.children.append(child_node)
    
    def __str__(self):
        if self.lexeme and self.lexeme != self.symbol:
            return f"{self.symbol}('{self.lexeme}')"
        return self.symbol

class DerivationTree:
    """Classe para gerenciar a árvore de derivação bottom-up"""
    def __init__(self):
        self.root = None
        self.node_stack = []  # Pilha de nós correspondente à pilha do parser
        self.all_nodes = []   # Todos os nós criados
    def shift_terminal(self, symbol, lexeme=None, state=None, line=None):
        """Cria nó terminal durante SHIFT"""
        terminal_node = DerivationNode(symbol, lexeme, state, line=line)
        self.node_stack.append(terminal_node)
        self.all_nodes.append(terminal_node)
        return terminal_node
    def reduce_production(self, lhs, rhs, new_state=None):
        """Cria nó não-terminal durante REDUCE, conectando aos filhos"""
        # Remove os nós filhos da pilha (correspondente aos símbolos da produção)
        children_nodes = []
        if rhs != ['ε']:  # Se não é produção vazia
            # Remove tantos nós quantos símbolos na produção
            for _ in range(len(rhs)):
                if self.node_stack:
                    children_nodes.append(self.node_stack.pop())
        # Inverte a ordem dos filhos (foram removidos em ordem reversa)
        children_nodes.reverse()
        # Cria o nó não-terminal
        parent_node = DerivationNode(lhs, state=new_state)
        # Conecta os filhos ao pai
        for child in children_nodes:
            parent_node.add_child(child)
        # Adiciona o novo nó à pilha
        self.node_stack.append(parent_node)
        self.all_nodes.append(parent_node)
        # Se chegamos ao símbolo inicial, esta é a raiz
        if lhs == 'PROGRAMA' or (len(self.node_stack) == 1 and not any(n.parent for n in self.node_stack)):
            self.root = parent_node
        
        return parent_node
    
    def print_tree_format(self):
        """Imprime a árvore no formato de diretório"""
        if not self.root:
            # Se não há raiz definida, usa o último nó da pilha
            if self.node_stack:
                self.root = self.node_stack[-1]
            else:
                print("❌ Árvore vazia")
                return
        print("📊 Árvore de Derivação (Bottom-Up):")
        print("=" * 60)
        self._print_node(self.root, "", True, True)
        print("=" * 60)
    
    def _print_node(self, node, prefix, is_last, is_root):
        """Função auxiliar para imprimir um nó com formatação de árvore"""
        # Mostra o símbolo e, se for terminal, o lexema
        display_text = str(node)
        if is_root:
            print(f"{display_text}")
        else:
            connector = "└───" if is_last else "├───"
            print(f"{prefix}{connector}{display_text}")
        # Prepara o prefixo para os filhos
        if not is_root:
            child_prefix = prefix + ("    " if is_last else "│   ")
        else:
            child_prefix = ""
        # Imprime os filhos
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            self._print_node(child, child_prefix, is_last_child, False)
    
    def print_bottom_up_steps(self):
        """Imprime os passos da derivação bottom-up"""
        print("\n📝 Passos da Análise Bottom-Up:")
        #print("-" * 50)
        # Coleta terminais na ordem que foram processados
        terminals = [node for node in self.all_nodes if node.is_terminal]
        non_terminals = [node for node in self.all_nodes if not node.is_terminal]
        print("1️⃣ Terminais reconhecidos (SHIFT):")
        for i, terminal in enumerate(terminals):
            lexeme_part = f" <- '{terminal.lexeme}'" if terminal.lexeme else ""
            print(f"   {i+1}: {terminal.symbol}{lexeme_part}")
        print("\n2️⃣ Reduções aplicadas (REDUCE):")
        for i, nt in enumerate(non_terminals):
            children_symbols = [str(child) for child in nt.children]
            if children_symbols:
                print(f"   {i+1}: {nt.symbol} -> {' '.join(children_symbols)}")
            else:
                print(f"   {i+1}: {nt.symbol} -> ε")

def read_tuples(tuples_list: list) -> tuple[list, list]:
    """Converte uma lista de strings de tokens em uma lista de tuplas (tipo, valor), desconsiderando espaços e comentários."""
    # remove comentario, quebra de linha, espaços linhas vazias
    tuples_list = [
        token for token in tuples_list 
        if token[1] != "ESPACO" 
        and token[1] != "QUEBRA_DE_LINHA" 
        and token[1] != "COMENTARIO"
        and token[1] != " "
    ]

    token_tuples = [(token[1], token[0]) for token in tuples_list]

    line_list = [token[2] for token in tuples_list]

    for i, token in enumerate(token_tuples):
        if token[0] != "id" and token[0] != "valor_inteiro" and token[0] != "valor_real" and token[0] != "string":
            token_tuples[i] = (token[1], token[1])
    return token_tuples, line_list

def read_slr_table() -> dict:
    slr_dict = {}
    try:
        with open("data/slr_table.csv", 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            column_names = headers[1:]  # Exclui 'State'
            for col_name in column_names:
                slr_dict[col_name] = []
            for row in reader:
                values = row[1:]    # Valores das outras colunas
                for i, col_name in enumerate(column_names):
                    if i < len(values):
                        slr_dict[col_name].append(values[i])
                    else:
                        slr_dict[col_name].append('')
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: data/slr_table.csv")
        return {}
    except Exception as e:
        print(f"❌ Erro ao ler arquivo SLR: {e}")
        return {}
    return slr_dict

def parse(token_tuples: list, line_list: list, slr_dict: dict) -> tuple[bool, list, DerivationTree, list]:
    """Função para analisar uma lista de tuplas de tokens usando um dicionário SLR."""
    stack = [ENDMARK, 0]  # Pilha de estados e símbolos
    input_tokens = token_tuples + [(ENDMARK, ENDMARK)]  # Adiciona marcador de fim
    prods = [prod for prods in gramatica.values() for prod in prods]  # Lista de produções
    current_token_info = input_tokens.pop(0)  # (tipo, lexema)
    current_token = current_token_info[0]
    current_lexeme = current_token_info[1] if len(current_token_info) > 1 else current_token_info[0]
    # Inicializa a árvore de derivação bottom-up
    derivation_tree = DerivationTree()
    step_count = 0
    error_list = []
    # Proteção adicional: se ficarmos repetindo o mesmo erro (mesmo estado+token)
    # muitas vezes, interrompemos para evitar loop infinito.
    last_error_key = None
    error_streak = 0
    ERROR_STREAK_LIMIT = 1000

    while True:
        step_count += 1
        # Limite de segurança: verificar imediatamente para que 'continue'
        # dentro do loop não permita ultrapassar o limite.
        if step_count > 1000:
            print("❌ Muitos passos, parando por segurança")
            break
        top = stack[-1]  # Topo da pilha (estado atual)
        action = slr_dict.get(current_token, [])[int(top)] if current_token in slr_dict else ''
        print(f"Step {step_count}: state: {top}, current_token: {current_token}, action: {action}")
        if not action:
            print(f"❌ Erro: Ação inválida para estado {top} e token '{current_token}'")
            return False, stack, derivation_tree
        if action.startswith("e"): # ERROR
            # os erros devem ser armazenados em uma lista para serem exibidos no final
            print(f"❌ Erro de sintaxe: entrada inesperada '{current_token}' na linha {line_list[0]}")
            # armazena o erro na lista, junto com informação de que linha o erro é
            error_list.append(f"Erro de sintaxe: entrada inesperada '{current_token}' na {line_list[0]}")
            current_token = input_tokens.pop(0) if input_tokens else (ENDMARK, ENDMARK)
            current_token = current_token[0] if isinstance(current_token, tuple) else current_token
            current_lexeme = current_token[1] if isinstance(current_token, tuple) and len(current_token) > 1 else current_token
            # Proteção contra ficar preso repetindo o mesmo par (estado,token)
            error_key = (top, current_token)
            if error_key == last_error_key:
                error_streak += 1
            else:
                last_error_key = error_key
                error_streak = 1
            if error_streak >= ERROR_STREAK_LIMIT:
                print(f"❌ Loop de erro detectado: estado {top} e token '{current_token}' repetidos {error_streak} vezes. Interrompendo.")
                error_list.append(f"Loop de erro detectado em estado {top} com token '{current_token}'")
                break
            if len(line_list) > 1:
                line_list.pop(0)
            continue
        elif action.startswith("s"):  # SHIFT
            next_state = int(action[1:])
            stack.append(current_token)
            stack.append(next_state)
            # 🔧 CORREÇÃO: Adiciona terminal à árvore bottom-up com linha
            current_line = int(line_list[0]) if line_list and line_list[0] else 0
            derivation_tree.shift_terminal(current_token, current_lexeme, next_state, line=current_line)
            print(f"   SHIFT: Empilhado '{current_token}' ('{current_lexeme}') e estado {next_state}")
            # Avança para o próximo token
            if input_tokens:
                current_token_info = input_tokens.pop(0)
                current_token = current_token_info[0]
                current_lexeme = current_token_info[1] if len(current_token_info) > 1 else current_token_info[0]
            if len(line_list) > 0:
                line_list.pop(0)
        elif action.startswith("r"):  # REDUCE
            num_prod = int(action[1:])  # Produção a ser aplicada
            production = prods[num_prod]
            num_symbols = len(production) * 2  # Número de elementos a remover da pilha
            # Encontra o não-terminal da produção
            nt_prod = None
            for nt in gramatica:
                if production in gramatica[nt]:
                    nt_prod = nt
                    break
            print(f"   REDUCE: Aplicando produção {num_prod}: {nt_prod} -> {' '.join(production)}")
            print(f"   Removendo {num_symbols} elementos da pilha")
            # Remove os símbolos da produção da pilha
            for _ in range(num_symbols):
                if len(stack) > 2:  # Mantém pelo menos $ e estado inicial
                    stack.pop()
            # Adiciona o não-terminal da produção
            stack.append(nt_prod)
            # Calcula novo estado via GOTO
            goto_state = slr_dict.get(nt_prod, [])[int(stack[-2])] if nt_prod in slr_dict else ''
            if goto_state:
                new_state = int(goto_state)
                stack.append(new_state)
                # 🔧 CORREÇÃO: Cria nó não-terminal conectando aos filhos
                derivation_tree.reduce_production(nt_prod, production, new_state)
                print(f"   Empilhado não-terminal '{nt_prod}' e estado {new_state}")
            else:
                print(f"❌ Erro: GOTO não encontrado para '{nt_prod}' no estado {stack[-2]}")
                return False, stack, derivation_tree, error_list
        elif action == "acc":  # ACCEPT
            print("✅ Cadeia aceita!")
            return True, stack, derivation_tree, error_list
        print(f"   Pilha atual: {stack}")
        print(f"   Próximo token: {current_token}")
        print("-" * 60)
        # (cheque de segurança movido para o início do loop)
    return False, stack, derivation_tree, error_list

def save_derivation_tree(tree: DerivationTree, filename: str = "data/derivation_tree.txt"):
    """Salva a árvore de derivação em um arquivo"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Árvore de Derivação Sintática (Bottom-Up)\n")
            f.write("=" * 60 + "\n")
            
            if tree.root:
                tree._write_node_to_file(tree.root, "", True, True, f)
            else:
                f.write("Árvore vazia ou incompleta\n")
            f.write("=" * 60 + "\n")
        print("=" * 60)
        print(f"💾 Árvore bottom-up salva em: {filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar árvore: {e}")

def _write_node_to_file(tree, node, prefix, is_last, is_root, file):
    """Escreve um nó no arquivo com formatação de árvore"""
    display_text = str(node)
    if is_root:
        file.write(f"{display_text}\n")
    else:
        connector = "└───" if is_last else "├───"
        file.write(f"{prefix}{connector}{display_text}\n")
    if not is_root:
        child_prefix = prefix + ("    " if is_last else "│   ")
    else:
        child_prefix = ""
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        tree._write_node_to_file(child, child_prefix, is_last_child, False, file)

# Adiciona o método à classe
DerivationTree._write_node_to_file = _write_node_to_file

def derv(token_list: list) -> DerivationTree | None:
    """Função principal de derivação"""
    print("🔄 Iniciando análise sintática bottom-up...")
    # Transforma token_list em tuplas (tipo, valor)
    token_tuples, line_list = read_tuples(token_list)
    #pprint.pprint(token_tuples)
    print(f"✅ {len(token_tuples)} tokens processados")
    # Carrega tabela SLR
    slr_dict = read_slr_table()
    if not slr_dict:
        print("❌ Erro ao carregar tabela SLR")
        return None
    print("✅ Tabela SLR carregada")
    print("=" * 60)
    # Executa análise
    success, final_stack, derivation_tree, errors = parse(token_tuples, line_list, slr_dict)
    print("=" * 60)
    if success:
        print("🎉 ANÁLISE SINTÁTICA CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("Erros encontrados durante a análise (se houver):")
        if errors:
            for err in errors:
                print(f" - {err}")
        else:
            print(" Nenhum erro encontrado.")
        # Salva a árvore em arquivo
        save_derivation_tree(derivation_tree)
    else:
        print("❌ ANÁLISE SINTÁTICA FALHOU!")
        print("\nErros encontrados durante a análise (se houver):")
        if errors:
            for err in errors:
                print(f" - {err}")
        else:
            print(" Nenhum erro encontrado.")
        print("Árvore parcial construída:")
        derivation_tree.print_tree_format()
    print("=" * 60)
    return derivation_tree