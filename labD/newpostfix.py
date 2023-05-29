CEND = '\33[0m'
CRED = '\33[91m'
CYELLOW = '\33[93m'
CGREEM = '\33[92m'
CBLUE = '\33[94m'
class Nodo:

    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

def tree_stack(operator, stack,errors):
    new_node = Nodo(operator)
    has_error = False
    if operator in '*+?':
        if not stack:
            error = f"Operador {operator}: No esta aplicado a ningun simbolo."
            errors.append(error)
            has_error = True
        else:
            operador1 = stack.pop()
            if operator == '?':
                new_node.value = '|'
                new_node.left=operador1
                epsilon_node = Nodo('ε')
                new_node.right=epsilon_node
            else:
                new_node.left=operador1
    elif operator in '|.':
        if not stack or len(stack) == 1:
            error = f"Binary operator {operator} does not have the operators required."
            errors.append(error)
            has_error = True
            if len(stack) == 1:
                stack.pop()
        else:
            operador2 = stack.pop()
            operador1 = stack.pop()
            new_node.left=operador1
            new_node.right=operador2
    
    if not has_error:
        stack.append(new_node)
    return stack

# Tabla de símbolos operadores
non_symbols = ['|', '*','+', '?','.']
binarios = ['|']
precedence = {'|': 1, '+': 3, '?': 3, '*': 3, '.': 2}

def add_concat(regex):
    # Tamaño de la expresión regular
    l = len(regex)
    res = ''
    i =0
    while i < l:
        if i+1 < l:
            siguiente = regex[i+1]
            actual = regex[i]
            if i+2 < l:
                if actual == '\\':
                    actual += siguiente
                    siguiente = regex[i+2]
                    i += 1
            res += actual
            if(actual != "(" and siguiente != ")" and siguiente not in non_symbols and actual not in binarios):
                res += '.'
        else:
            res += regex[i]
        i += 1
    return res

def create_alphabet(regex):
    i = 0
    alphabet = []
    while i < len(regex):
        element = regex[i]
        if element == '\\':
            next = regex[i + 1]
            alphabet.append(element + next)
            i += 1
        elif element not in non_symbols and element not in '()':
            alphabet.append(element)
        i += 1

    alphabet = list(set(alphabet))
    return alphabet

def shunting_yard(expr):
    # Diccionario de precedencia de operadores
    

    #new_regex = expr.replace('?', '|ε')
    expr = add_concat(expr)
    expr = metacharacters(expr)
    real_alphabet = create_alphabet(expr)
    errors = verificacion_regex(expr)

    # Pila de operadores y cola de salida
    stack = []
    output = []
    resp = ''
    operator = "*+|?."
    i = 0

    while i < len(expr):
                element = expr[i]
                if element == '\\':
                    element += expr[i + 1]
                    i += 1
                if element in real_alphabet:
                    output.append(Nodo(element))
                    resp += element
                elif element == '(':
                    stack.append(element)
                elif element == ')':
                    while stack and stack[-1] != '(':
                        pop_element = stack.pop()
                        output = tree_stack(pop_element, output,errors)
                        resp += pop_element
                    if stack :
                        stack.pop()
                elif element in operator:
                    while stack and stack[-1] != '(' and precedence[element] <= precedence[stack[-1]]:
                        pop_element = stack.pop()
                        output = tree_stack(pop_element, output,errors)
                        resp += pop_element
                    
                    stack.append(element)
                i += 1
                
    while stack:
        pop_element = stack.pop()
        output = tree_stack(pop_element, output,errors)
        resp += pop_element

    if output:
        root = output.pop()
        #AST.set_root(root)
    return resp



def metacharacters(regex):
    deleteIdempotencia = ["*","+"]
    for symbol in deleteIdempotencia:
        end = ''
        espList = metahelper(regex)
        i =0
        for i in range(len(espList)):
            if espList[i] == symbol and end == symbol:
                end = symbol
                espList[i] = ''
            else:
                end = espList[i]
        regex = ''.join(espList)
    return regex
    
def metahelper(regex):
    newRegex = []
    i =0 
    while i < len(regex):
        element = regex[i]
        if element == '\\' and i+1 < len(regex) and regex[i+1] != '\\':
            newRegex.append(regex[i])
            newRegex.append(regex[i+1])
            i+=1
        else:
            newRegex.append(element)
        i+=1
    return newRegex

# Funcion para verificar que sea una expresion regular valida
def verificacion_regex(regex):
    # tabla de simbolos
    errors_log = []

    unitarios = ['*', '+', '?']
    binarios = ['|', '.']
    
    def verificacion_parentesis():
        stack =[]
        i =0 
        blanc = [""]
        for element in regex:
            if element == '(':
                stack.append(element)
                blanc.append("")
            elif element == ')':
                if not stack:
                    error = f"Parentesis desequilibrados en la posicion {i}, para la expresion {regex}"
                    errors_log.append(error)
                else:
                    stack.pop()
                    last = blanc.pop()
                    if not last:
                        error = f"Parentesis vacios en la posicion {i}, para la expresion {regex}"
                        errors_log.append(error)
            else:
                blanc[-1] += element
            i+=1
        if stack:
            error = f"Parentesis desequilibrados en la expresion {regex}"
            errors_log.append(error)
    
    def verificacion_dobleOperador():
        i =0 
        while i < len(regex):
            if i + 1 < len(regex):
                current = regex[i]
                next = regex[i + 1]
                if i + 2 < len(regex):
                    current += next
                    next = regex[i + 2]
                    i += 1
                if current in binarios and next in binarios:
                    error = f"Operador binario seguido de otro operador binario en la posicion {i} para la expresion {regex}"
                    errors_log.append(error)
                if current in binarios and next in unitarios:
                    error = f"Operador binario seguido de un operador unitario en la posicion {i} para la expresion {regex}"
                    errors_log.append(error)
            i += 1
    
    def verificacion_inicio_fin():
        if regex[0] in unitarios or regex[0] == ')' or regex[0] == binarios:
            error = f"Expresion mal formada: token no reconocido Inicio con un simbolo no valido, {regex[0]}"
            errors_log.append(error)
        if regex[-1] == '(' or regex[-1] == binarios:
            error = f"Expresion mal formada: token no reconocido Final con un simbolo no valido, {regex[-1]}"
            errors_log.append(error)
    verificacion_parentesis()
    verificacion_dobleOperador()
    verificacion_inicio_fin()
    
    return errors_log
            
