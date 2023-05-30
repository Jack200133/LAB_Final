
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
def analisisTokens(nombre_archivo, lista_producciones, tabla_accion, tabla_goto):
    pila_errores = []
    pila_analisis = [0]
    indice_input = 0
    token_actual, indice_input = current_tok(indice_input, nombre_archivo)
    token_actual = remove_quotes(token_actual)

    while True:
        estado_actual = pila_analisis[-1]

        # Ignorar tokens
        if token_actual in ignored:
            if has_next_token(indice_input, nombre_archivo):
                token_actual, indice_input = current_tok(indice_input, nombre_archivo)
                token_actual = remove_quotes(token_actual)
            else:
                token_actual = '$'
            continue

        accion = tabla_accion.loc[estado_actual, token_actual]

        if pd.isna(accion):
            print(CRED, 'Error: no se encontró ninguna acción para el estado {} y el token {}'.format(estado_actual, token_actual), CEND, '\n')
            pila_errores.append('\nError: no se encontró ninguna acción para el estado {} y el token {}'.format(estado_actual, token_actual))
            if has_next_token(indice_input, nombre_archivo):
                token_actual, indice_input = current_tok(indice_input, nombre_archivo)
                token_actual = remove_quotes(token_actual)
            else:
                token_actual = '$'
            continue

        if accion == 'ACEPTAR':
            if pila_errores:
                print(CRED, 'La cadena de entrada NO es válida.', CEND)
            else:
                print(CGREEM, 'La cadena de entrada es válida.', CEND)
            break
        elif accion.startswith('S'):
            siguiente_estado = int(accion[1:])
            pila_analisis.append(token_actual)
            pila_analisis.append(siguiente_estado)
            if has_next_token(indice_input, nombre_archivo):
                token_actual, indice_input = current_tok(indice_input, nombre_archivo)
                token_actual = remove_quotes(token_actual)
            else:
                token_actual = '$'
        elif accion.startswith('R'):
            numero_produccion = int(accion[1:])
            produccion = lista_producciones[numero_produccion]
            lhs, rhs = produccion

            num_simbolos = len(rhs)
            pila_analisis = pila_analisis[:-2 * num_simbolos]

            estado_actual = pila_analisis[-1]
            siguiente_estado = tabla_goto.loc[estado_actual, lhs]

            pila_analisis.append(lhs)
            pila_analisis.append(siguiente_estado)

ruta_archivo = 'input1.txt'

analisisTokens(ruta_archivo, production_list, action_table, goto_table)
