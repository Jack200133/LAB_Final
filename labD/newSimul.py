import numpy as np
import pandas as pd

CEND = '\33[0m'
CRED = '\33[91m'
CYELLOW = '\33[93m'
CGREEM = '\33[92m'
CBLUE = '\33[94m'


# Funcion de trancision de un estado a otro
def transition(q, a, tabla):
    x = tabla[(tabla['q'] == q) & (tabla['a'] == a)]['d(q,a)']
    if (len(x) == 0):
        return []
    return x.values

# Funcion que regresa el estado final dado un estado inicial y una palabra
def final_state(q, w, tabla):
    n = len(w)
    if n == 0:
        return [q]
    else:
        a = w[0]
        possible_states = transition(q, a, tabla)
        final_states = []

        for state in possible_states:
            final_states.extend(final_state(state, w[1:], tabla))

        return final_states



# Funcion que imprime la derivacion de la palabra
def derivation(q, w, tabla):
    n = len(w)
    if (n == 0):
        return print('\33[92m({},{})\33[93m => \33[94m{}'.format(q,'',q))
    else: 
        a = (w[0])
        qq = transition(q, a, tabla)
        x = derivation(qq, w[1:],tabla)
        return print('\33[92m({},{})\33[93m => \33[94m({},{})'.format(q,w,qq,w[1:]))

def accepted(q, w, F, tab, token_hierarchy):
    final_states = final_state(q, w, tab)
    min_priority = float('inf')
    min_priority_state = None

    for x in final_states:
        transitions = tab[tab['q'] == x]

        if x in F:
            token = F[x]
            priority = token_hierarchy[token]
            if priority < min_priority:
                min_priority = priority
                min_priority_state = x
        elif len(transitions) > 0:
            for index, row in transitions.iterrows():
                next_state = row['d(q,a)']
                if next_state in F:
                    token = F[next_state]
                    priority = token_hierarchy[token]
                else:
                    token = None
                    priority = float('inf')

                if priority <= min_priority:
                    min_priority = priority
                    min_priority_state = x

    if min_priority_state is not None:
        return True, min_priority_state, min_priority

    return False, None, None




def simularAFD(w, transacciones, estados_finales, tokens):
    token_hierarchy = {token[0]: index for index, token in enumerate(tokens)}

    estados_finales_dict = {}
    for k, v in estados_finales.items():
        for estado in k:
            estados_finales_dict[estado] = v

    table = np.array(transacciones)
    tab = pd.DataFrame(data=table, columns=['q', 'a', 'd(q,a)'])
    return accepted('S0', w, estados_finales_dict, tab, token_hierarchy)
