
import pickle
from labD.newSimul import simularAFD


CEND = '\33[0m'
CRED = '\33[91m'
CYELLOW = '\33[93m'
CGREEM = '\33[92m'
CBLUE = '\33[94m'

#cargar bites del automata
with open('final_automatonD.pickle', 'rb') as f:
    final_automaton = pickle.load(f)

with open('tokens_statesD.pickle', 'rb') as f:
    tokens_states = pickle.load(f)

with open('tokensD.pickle', 'rb') as f:
    tokens = pickle.load(f)

print(CYELLOW)
#textInput = input('Ingrese el Archivo a resolver:\n ')

def Content(file):
    with open("input/"+file, 'r') as f:
        return f.read()


print(CGREEM)

space_map = {
        '\s': 'サ',
        '\t': 'ラ',
        '\n': 'ナ',
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
                    print(CRED,errorS, current_word, accepted_word)
                    print(CRED, '1Error en el caracter:', errorS, ", en la línea:", line_count, CGREEM, '\n')
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
                print(CRED, '2Error en el caracter:', errorS, ", en la línea:", line_count, CGREEM, '\n')
                input_w += 1
                current_word = '' 
                accepted_word = ''
                accepted_priority = float('inf')

def has_next_token(input_W,file):
    input_content = Content(file)
    return input_W < len(input_content)
