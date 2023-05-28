from LR import canonical_collection
from LL import first_sets,follow_sets
from draw import visualize_lr0

import re

def read_yalp_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

def split_sections(content):
    errorStack = []
    tokens_section = None
    productions_section = None
    sections = content.split('%%')
    if len(sections)!= 2:
        errorStack.append("Error: No se encuentra la división '%%' entre las secciones de tokens y producciones.")
    else:
        tokens_section = sections[0]
        productions_section = sections[1]
    return tokens_section, productions_section,errorStack

def process_tokens_section(content):
    tokens = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith("%token"):
            line_tokens = line[len("%token"):].strip().split(' ')
            tokens.extend(line_tokens)
    return tokens

def process_productions_section(content):
    productions = {}
    #content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # Eliminar comentarios
    lines = content.split('\n')
    current_production = None
    production_rules = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith(':'):
            if current_production:
                productions[current_production] = production_rules
                production_rules = []
            current_production = line[:-1]
        elif line.endswith(';'):
            line = line[:-1]
            if line != "":
                production_rules.append(line)
            productions[current_production] = production_rules
            production_rules = []
            current_production = None
        else:
            if (line.startswith('|') or line.startswith('->')) and current_production:
                line = line.strip().split('|')
                for item in line: 
                    if item.strip() != "":
                        production_rules.append(item.strip())

            elif ('|' in line) and current_production:
                line = line.strip()
                production_rules.extend(line.split('|'))
            else:
                production_rules.append(line)
    return productions


def validate_yalp(tokens_section, productions_section, tokens, productions):
    error_stack = []

    # Verificar si existe la división '%%'
    if not tokens_section or not productions_section:
        error_stack.append("Error: No se encuentra la división '%%' entre las secciones de tokens y producciones.")

    # Verificar si tiene el símbolo '%' antes de la declaración de tokens
    lines = tokens_section.split('\n')
    for line in lines:
        if not line.startswith("%token") and not line.startswith("IGNORE") and line.strip():
            error_stack.append(f"Error: No se encuentra el símbolo '%' antes de la declaración de tokens en la línea '{line.strip()}'.")
            break

    # Verificar si una producción tiene el mismo nombre que un token
    for token in tokens:
        if token in productions:
            error_stack.append(f"Error: La producción '{token}' tiene el mismo nombre que un token.")
            break

    return error_stack


def parse_yalp_file(filename,error_stack):
    content = read_yalp_file(filename)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # Eliminar comentarios
    tokens_section, productions_section,divisionError = split_sections(content)
    tokens = None
    productions = None
    if(divisionError):
        error_stack.extend(divisionError)
    else:
        tokens = process_tokens_section(tokens_section)
        productions = process_productions_section(productions_section)

        error_stack.extend(validate_yalp(tokens_section, productions_section, tokens, productions))

    return tokens, productions,error_stack

def convert_productions(productions_dict):
    converted_productions = {}
    for key, value in productions_dict.items():
        converted_productions[key] = [rule.split() for rule in value]
    return converted_productions

