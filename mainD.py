import re
import json
from yalex import *

from labD.AFN import generate_afn, add_new_initial_state, merge_automata
from labD.AFD import generate_afd
from labD.AFMini import build_miniAFD
from labD.newpostfix import shunting_yard
from labD.newSimul import simularAFD
from labD.draw import draw_afn


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
tokens,errorStack = build_tokens(file_content, regex,errorStack,fin+1)

if errorStack:
    print(CRED,"Error stack:")
    for error in errorStack:
        print(error)
    print(CEND)
    exit()

megarex =""
# ARMAR MEGAAUTOMATA CON LOS REGEX Y AFNS
i = 0
tokens_states ={}
regexAFN = {}
for item in tokens:
    if len(item) == 3:
        # Generar AFN para cada regex
        key = item[0]
        value = item[2]
        afn = {}
        reg = shunting_yard(value)
        megarex += value + '|'
        print('\33[93m',key,'REGEX: ',value,'\33[94m')
        print('\33[93m',key,'POSTFIX: ',reg,'\33[94m')
        afn = generate_afn(reg,0)
        afd = generate_afd(afn)
        mini = build_miniAFD(afd,i)
        i =int(mini['start_states'][0][1:]) + 4
        regexAFN[key] = mini
        tokens_states[tuple(mini['final_states'])] = key
automata_list = list(regexAFN.values())
reg = shunting_yard(megarex.rstrip('|'))
print(tokens_states)

# Unir todos los autómatas en la lista
merged_automaton = automata_list[0]
for i in range(1, len(automata_list)):
    merged_automaton = merge_automata(merged_automaton, automata_list[i])

# Agregar el nuevo estado inicial 's0' con transiciones epsilon a los estados iniciales
initial_states = [automaton["start_states"][0] for automaton in automata_list]
final_automaton = add_new_initial_state(merged_automaton, initial_states)

draw_afn(final_automaton["states"], final_automaton["transition_function"], final_automaton["start_states"], final_automaton["final_states"], "final_automatonD")
print(final_automaton["transition_function"])
import pickle

final_bits = pickle.dumps(final_automaton)
tokens_bits = pickle.dumps(tokens_states)

with open('pickle/final_automatonD.pickle', 'wb') as f:
    f.write(final_bits)

with open('pickle/tokens_statesD.pickle', 'wb') as f:
    f.write(tokens_bits)

with open('pickle/tokensD.pickle', 'wb') as f:
    f.write(pickle.dumps(tokens))

imports = '''
import pickle
from labD.newSimul import simularAFD
'''

code = '''

CEND = '\\33[0m'
CRED = '\\33[91m'
CYELLOW = '\\33[93m'
CGREEM = '\\33[92m'
CBLUE = '\\33[94m'

#cargar bites del automata
with open('pickle/final_automatonD.pickle', 'rb') as f:
    final_automaton = pickle.load(f)

with open('pickle/tokens_statesD.pickle', 'rb') as f:
    tokens_states = pickle.load(f)

with open('pickle/tokensD.pickle', 'rb') as f:
    tokens = pickle.load(f)

print(CYELLOW)
#textInput = input('Ingrese el Archivo a resolver:\\n ')

def Content(file):
    with open("input/"+file, 'r') as f:
        return f.read()


print(CGREEM)

space_map = {
        '\s': 'サ',
        '\\t': 'ラ',
        '\\n': 'ナ',
        '"': 'ハ',
        "'": 'ワ',
        '`':'カ',
    }


input_w = 0
def current_tok(input_w,file):
    input_content = Content(file)
    accepted_word = ''
    accepted_priority = float('inf')
    current_word = ''
    line_count = 1
    while input_w < len(input_content):
        inputO = input_content[input_w]
        if inputO in space_map.keys() or inputO == ' ':
            if inputO == ' ':
                inputO = '\s'
            inputO = space_map[inputO]
        current_word += inputO

        accepted_now, new_state, new_priority = simularAFD(current_word,final_automaton["transition_function"],tokens_states,tokens)

        if accepted_now:

            accepted_word = current_word
            accepted_priority = new_priority
            input_w += 1
        else:
            banda = False
            for token in tokens:
                if token[0] == accepted_word:
                    banda = True
                    exec(token[1])
                    input_w += 1
                    current_word = ''
                    accepted_word = ''
                    accepted_priority = float('inf')
                    
                    return token[1],input_w
                    break
            if not banda:
                found_token = False
                if accepted_priority != float('inf'):
                    if accepted_word == 'ナ':
                                line_count += 1
                    accepted_word = tokens[accepted_priority][0]
                    

                for token in tokens:
                    if token[0] == accepted_word:
                        found_token = True
                        exec(token[1])
                        return token[1],input_w
                        break
                    elif token[0] == current_word:
                        found_token = True
                        exec(token[1])
                        input_w += 1
                        return token[1],input_w
                        break

                if found_token:
                    current_word = ''
                    accepted_word = ''
                    accepted_priority = float('inf')
                else:
                    errorS = current_word if len(accepted_word) == 0 else accepted_word
                    print(CRED, 'Error en el caracter:', errorS, ", en la línea:", line_count, CGREEM, '\\n')
                    input_w += 1
                    current_word = ''
                    accepted_word = ''
                    accepted_priority = float('inf')
    if current_word != "":
        banda = False
        for token in tokens:
            if token[0] == accepted_word:
                banda = True
                exec(token[1])
                input_w += 1
                current_word = ''
                accepted_word = ''
                accepted_priority = float('inf')
                return token[1],input_w
                break
        if not banda:
            found_token = False
            if accepted_priority != float('inf'):
                accepted_word = tokens[accepted_priority][0]
            for token in tokens:
                if token[0] == accepted_word:
                    found_token = True
                    exec(token[1])
                    if accepted_word == 'ナ':
                        line_count += 1
                    return token[1],input_w
                    break
                elif token[0] == current_word:
                    found_token = True
                    exec(token[1])
                    input_w += 1
                    return token[1],input_w
                    break
            if found_token:
                current_word = ''
                accepted_word = ''
                accepted_priority = float('inf')       
            else:
                errorS = current_word if len(accepted_word) == 0 else accepted_word
                print(CRED, 'Error en el caracter:', errorS, ", en la línea:", line_count, CGREEM, '\\n')
                input_w += 1
                current_word = '' 
                accepted_word = ''
                accepted_priority = float('inf')

def has_next_token(input_W,file):
    input_content = Content(file)
    return input_W < len(input_content)
'''
with open("labD/newSimul.py", "r") as f:
    simularAFDFILE = f.read()

with open('compilado.py', 'w',encoding="utf-8") as archivo:
    archivo.write(header_result)
    archivo.write(imports)
    #archivo.write(simularAFDFILE)
    archivo.write(code)
    archivo.write(trailer_result)