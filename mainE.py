
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
# productions = [(nt, rule) for nt, rules in productions_dict.items() for rule in rules]
print("----------------------")
print(converted_productions)
print("----------------------")

nonTerminals = list(productions_dict.keys())
Terminals = tokens
print(converted_productions)
states, transitions = canonical_collection(converted_productions,nonTerminals,Terminals)

print('Estados:')
for i, state in enumerate(states):
    print(f'{i}: {state}')

print('Transiciones:')
for transition in transitions:
    print(transition)
# Ejemplo de uso:

visualize_lr0(states, transitions)

# print("\n------------LL----------\n\n")

def convert_productions(productions):
    converted_productions = {}
    for key, value in productions.items():
        converted_productions[key] = [prod.split() for prod in value]
    return converted_productions

# print(productions_dict)
converted_prod = convert_productions(productions_dict)
first = first_sets(converted_prod)
follow = follow_sets(converted_prod, first)


from SLRtable import generate_slr_tables


combined_table,errorList = generate_slr_tables(states, transitions, converted_prod, first, follow,nonTerminals,Terminals)

if errorList:
    print(CRED,"Error stack:")
    for error in errorList:
        print(error)
    print(CEND)
    # exit()

print("\nACTION table:")
print(combined_table)

