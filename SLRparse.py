
from compilado import current_tok,has_next_token
import pandas as pd
import pickle

CEND = '\33[0m'
CRED = '\33[91m'
CYELLOW = '\33[93m'
CGREEM = '\33[92m'
CBLUE = '\33[94m'

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
file_path = 'input1.txt'

parse_slr(file_path, action_table, goto_table, production_list)

