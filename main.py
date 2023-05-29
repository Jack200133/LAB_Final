
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


combined_table,errorList,production_list = generate_slr_tables(states, transitions, converted_prod, first, follow,nonTerminals,Terminals)

if errorList:
    print(CRED,"Error stack:")
    for error in errorList:
        print(error)
    print(CEND)
    # exit()

print("\nACTION table:")
print(combined_table)
def remove_quotes(token):
    if token[0] == "'" and token[-1] == "'":
        return token[1:-1]
    return token

# Use the function before using the token in the analysis
token = remove_quotes(token)

from compilado import current_token,has_next_token
import pandas as pd

inicio = 0
file = 'input1.txt'
def parse_lr(input_file, combined_table, states, transitions, production_list):
    # Initiate
    stack = [0]
    index = 0
    error_list = []
    parse_result = []
    
    file = input_file
    while has_next_token(index, file):
        token, new_index = current_token(index, file)
        token = remove_quotes(token)  # Remove extra quotes
        index = new_index
        if token not in ignored:
            while True:
                state = stack[-1]
                action = combined_table.loc[state, token]
                
                if pd.isna(action):
                    error_list.append(f"Unexpected token '{token}' at index {index}.")
                    break
                
                if action == "ACCEPT":
                    parse_result.append("ACCEPT")
                    break
                
                elif action.startswith("S"):
                    next_state = int(action.split()[1])
                    stack.append(next_state)
                    break
                
                elif action.startswith("R"):
                    production_index = int(action.split()[1])
                    production = production_list[production_index]  # Get the corresponding production
                    A, β = production
                    
                    # Pop |β| states
                    for _ in range(len(β)):
                        if stack:
                            stack.pop()
                        else:
                            error_list.append(f"Unexpected end of stack when processing token '{token}' at index {index}.")
                            break
                    
                    # Let state t now be on the top of the stack
                    t = stack[-1] if stack else None
                    if t is not None:
                        # Push goto[t, A] onto the stack
                        goto = combined_table.loc[t, A]
                        if pd.notna(goto):
                            stack.append(int(goto))
                        else:
                            error_list.append(f"Error: GOTO[{t},{A}] is undefined.")
                            break
                    else:
                        error_list.append(f"Error: Stack is empty when trying to GOTO[{A}].")
                        break
                        
                    # Output the production
                    parse_result.append(production)
                    
                else:
                    error_list.append(f"Unexpected action '{action}' for token '{token}' at index {index}.")
                    break
            
    return parse_result, error_list

parse_result, error_list =  parse_lr(file, combined_table, states, transitions, production_list)
if error_list:
    print("\nErrors encountered:")
    for err in error_list:
        print(err)

print("\nParse result:")
for prod in parse_result:
    print(prod)