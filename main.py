
from yapl import *
from yalex import *

CEND = '\33[0m'
CRED = '\33[91m'
CYELLOW = '\33[93m'
CGREEM = '\33[92m'
CBLUE = '\33[94m'

with open('yalex/lex1.yal', 'r') as f:
    # Leer todas las líneas del archivo
    yalex_content = f.read()


header_result = ''
regex = {}
simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"

# Llamando a las funciones en orden
file_content = yalex_content

header_result, trailer_result, file_content,i = build_header_and_trailer(file_content)
file_content = clean_comments(file_content)
file_content = replace_quotation_mark(file_content)
regex,errorStack,fin = build_regex(file_content,i)
LEXtokens,errorStack = build_tokens(file_content, regex,errorStack,fin+1)

tokens, productions_dict,errorStack,ignored = parse_yalp_file('yapar/lex1.yalp',errorStack)
if errorStack:
    print(CRED,"Error stack:")
    for error in errorStack:
        print(error)
    print(CEND)
    exit()

gooTokens = []

for token in tokens:
    for lex_token in LEXtokens:
        evald = evalToken(lex_token)
        if token == evald:
            gooTokens.append(token)
    if token not in gooTokens:
        errorStack.append(f"Token {token} no definido en el YALEX")

if (len(gooTokens) + len(ignored)) < len(LEXtokens):
    errorStack.append("Faltaron Definir tokens en el YAPAR")


if errorStack:
    print(CRED,"Error stack:")
    for error in errorStack:
        print(error)
    print(CEND)
    exit()

converted_productions = convert_productions(productions_dict)

nonTerminals = list(productions_dict.keys())
Terminals = tokens
states, transitions = canonical_collection(converted_productions,nonTerminals,Terminals)


visualize_lr0(states, transitions)

def convert_productions(productions):
    converted_productions = {}
    for key, value in productions.items():
        converted_productions[key] = [prod.split() for prod in value]
    return converted_productions

converted_prod = convert_productions(productions_dict)
first = first_sets(converted_prod)
follow = follow_sets(converted_prod, first)


from slr_table import generate_slr_tables


combined_table,errorList,production_list,action_table, goto_table = generate_slr_tables(states, transitions, converted_prod, first, follow,nonTerminals,Terminals)

if errorList:
    print(CRED,"Error stack:")
    for error in errorList:
        print(error)
    print(CEND)
    # exit()

print(CYELLOW,"SLR table:",CGREEM)
print(combined_table)

from compilado import current_tok,has_next_token
import pandas as pd


def remove_quotes(token):
    if token[0] == "'" and token[-1] == "'":
        return token[1:-1]
    return token

def parse_slr(file_name, action_table, goto_table, production_list):
    error_stack = []
    parse_stack = [0]  # Pila inicial con el estado 0
    input_index = 0  # Índice para rastrear el token actual en input_tokens
    current_token, input_index = current_tok(input_index, file_name)
    current_token = remove_quotes(current_token)
    while True:
        if current_token in ignored:
            if has_next_token(input_index, file_name):
                current_token, input_index = current_tok(input_index, file_name)
                current_token = remove_quotes(current_token)
            else:
                current_token = '$'
            continue
        current_state = parse_stack[-1]
        
        action = action_table.loc[current_state, current_token]

        # Comprobar si el estado actual y el token actual tienen una acción válida
        if pd.isna(action):
            print(CRED,'Error: no se encontró ninguna acción para el estado {} y el token {}'.format(current_state,current_token),CEND,'\n')
            error_stack.append('\nError: no se encontró ninguna acción para el estado {} y el token {}'.format(current_state,current_token))
            if has_next_token(input_index, file_name):
                current_token, input_index = current_tok(input_index, file_name)
                current_token = remove_quotes(current_token)
            else:
                current_token = '$'
            continue

        print(CGREEM,"ESTADO :", current_state,CEND)
        print(CYELLOW,"TOKEN  :", current_token,CEND)
        print(CBLUE,"ACCION :", action,CEND,'\n')

        if action.startswith('S'):
            # Desplazamiento (shift)
            next_state = int(action[1:])
            parse_stack.append(current_token)
            parse_stack.append(next_state)
            # Obteniendo el token actual
            if has_next_token(input_index, file_name):
                current_token, input_index = current_tok(input_index, file_name)
                current_token = remove_quotes(current_token)
            else:
                current_token = '$'

        elif action.startswith('R'):
            # Reducción (reduce)
            production_num = int(action[1:])
            production = production_list[production_num]
            lhs, rhs = production

            # Desapilar símbolos
            num_symbols = len(rhs)
            parse_stack = parse_stack[:-2 * num_symbols]

            # Obtener el estado actual después de la reducción
            current_state = parse_stack[-1]
            next_state = goto_table.loc[current_state, lhs]

            parse_stack.append(lhs)
            parse_stack.append(next_state)
        elif action == 'ACCEPT':
            # Análisis completado
            if error_stack:
                print(CRED,'La cadena de entrada NO es válida.',CEND)
            else:
                print(CGREEM,'La cadena de entrada es válida.',CEND)
            break

# file_path = input("\nQue archivo de texto deseamos evaluar? -> ")
#file_path = 'input1.txt'
#parse_slr(file_path, action_table, goto_table, production_list)



import pickle

with open('pickle/action_table.pickle', 'wb') as f:
    f.write(pickle.dumps(action_table))

with open('pickle/goto_table.pickle', 'wb') as f:
    f.write(pickle.dumps(goto_table))

with open('pickle/production_list.pickle', 'wb') as f:
    f.write(pickle.dumps(production_list))

with open('pickle/ignored.pickle', 'wb') as f:
    f.write(pickle.dumps(ignored))

imports = '''
from compilado import current_tok,has_next_token
import pandas as pd
import pickle
'''

code = '''
CEND = '\\33[0m'
CRED = '\\33[91m'
CYELLOW = '\\33[93m'
CGREEM = '\\33[92m'
CBLUE = '\\33[94m'

#cargar bites del automata
with open('pickle/action_table.pickle', 'rb') as f:
    action_table = pickle.load(f)

with open('pickle/goto_table.pickle', 'rb') as f:
    goto_table = pickle.load(f)

with open('pickle/production_list.pickle', 'rb') as f:
    production_list = pickle.load(f)

with open('pickle/ignored.pickle', 'rb') as f:
    ignored = pickle.load(f)

def remove_quotes(token):
    if token[0] == "'" and token[-1] == "'":
        return token[1:-1]
    return token

def parse_slr(file_name, action_table, goto_table, production_list):
    error_stack = []
    parse_stack = [0]  # Pila inicial con el estado 0
    input_index = 0  # Índice para rastrear el token actual en input_tokens
    current_token, input_index = current_tok(input_index, file_name)
    current_token = remove_quotes(current_token)
    while True:
        if current_token in ignored:
            if has_next_token(input_index, file_name):
                current_token, input_index = current_tok(input_index, file_name)
                current_token = remove_quotes(current_token)
            else:
                current_token = '$'
            continue
        current_state = parse_stack[-1]
        
        action = action_table.loc[current_state, current_token]

        # Comprobar si el estado actual y el token actual tienen una acción válida
        if pd.isna(action):
            print(CRED,'Error: no se encontró ninguna acción para el estado {} y el token {}'.format(current_state,current_token),CEND,'\\n')
            error_stack.append('\\nError: no se encontró ninguna acción para el estado {} y el token {}'.format(current_state,current_token))
            if has_next_token(input_index, file_name):
                current_token, input_index = current_tok(input_index, file_name)
                current_token = remove_quotes(current_token)
            else:
                current_token = '$'
            continue

        print(CGREEM,"ESTADO :", current_state,CEND)
        print(CYELLOW,"TOKEN  :", current_token,CEND)
        print(CBLUE,"ACCION :", action,CEND,'\\n')

        if action.startswith('S'):
            # Desplazamiento (shift)
            next_state = int(action[1:])
            parse_stack.append(current_token)
            parse_stack.append(next_state)
            # Obteniendo el token actual
            if has_next_token(input_index, file_name):
                current_token, input_index = current_tok(input_index, file_name)
                current_token = remove_quotes(current_token)
            else:
                current_token = '$'

        elif action.startswith('R'):
            # Reducción (reduce)
            production_num = int(action[1:])
            production = production_list[production_num]
            lhs, rhs = production

            # Desapilar símbolos
            num_symbols = len(rhs)
            parse_stack = parse_stack[:-2 * num_symbols]

            # Obtener el estado actual después de la reducción
            current_state = parse_stack[-1]
            next_state = goto_table.loc[current_state, lhs]

            parse_stack.append(lhs)
            parse_stack.append(next_state)
        elif action == 'ACCEPT':
            # Análisis completado
            if error_stack:
                print(CRED,'La cadena de entrada NO es válida.',CEND)
            else:
                print(CGREEM,'La cadena de entrada es válida.',CEND)
            break
file_path = 'input1.txt'

parse_slr(file_path, action_table, goto_table, production_list)

'''

with open('SLRparse.py', 'w',encoding="utf-8") as archivo:
    archivo.write(imports)
    archivo.write(code)