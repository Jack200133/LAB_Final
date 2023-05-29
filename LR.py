class LR0Item:
    def __init__(self, production, position,derived=False):
        self.production = (production[0], tuple(production[1]))
        self.position = position
        self.derived = derived

    def __repr__(self):
        return f'{self.production[0]} -> {" ".join(self.production[1][:self.position]) + "•" + " ".join(self.production[1][self.position:])}'

    def __eq__(self, other):
        return self.production == other.production and self.position == other.position

    def __hash__(self):
        return hash((self.production, self.position))

def closure(items, productions, order):
    new_items = []
    for item in items:
        if item not in new_items:
            new_items.append(item)
    changed = True
    while changed:
        changed = False
        for item in list(new_items):
            if item.position < len(item.production[1]) and item.production[1][item.position] in productions:
                non_terminal = item.production[1][item.position]
                for production in productions[non_terminal]:
                    new_item = LR0Item((non_terminal, production), 0)
                    if new_item not in new_items:
                        index = next((i for i, p in enumerate(order) if p == non_terminal), len(order))
                        new_items.insert(index, new_item)
                        changed = True
    return new_items

def goto(items, symbol, productions, order):
    new_state = []
    for item in items:
        if item.position < len(item.production[1]) and item.production[1][item.position] == symbol:
            new_item = LR0Item(item.production, item.position + 1)
            if new_item not in new_state:
                index = next((i for i, p in enumerate(order) if p == symbol), len(order))
                new_state.insert(index, new_item)
    return closure(new_state, productions, order)

def canonical_collection(productions, non_terminals, terminals):
    order = non_terminals + terminals
    items = LR0Item((list(productions.keys())[0]+'\'', [list(productions.keys())[0]]), 0)
    states = [closure([items], productions, order)]
    stack = [states[0]]
    transitions = set()

    while stack:
        state = stack.pop()
        symbols = [sym for item in state for sym in item.production[1][item.position:item.position + 1]]
        # Separar los símbolos en no terminales y terminales
        non_terminal_symbols = [sym for sym in symbols if sym in non_terminals]
        terminal_symbols = [sym for sym in symbols if sym in terminals]
        # Procesar las transiciones para los no terminales en el orden dado
        for symbol in non_terminal_symbols:
            next_state = goto(state, symbol, productions, order)
            if not next_state:
                continue
            if next_state not in states:
                states.append(next_state)
                stack.append(next_state)
            transitions.add((states.index(state), symbol, states.index(next_state)))
        # Procesar las transiciones para los terminales en el orden dado
        for symbol in terminal_symbols:
            next_state = goto(state, symbol, productions, order)
            if not next_state:
                continue
            if next_state not in states:
                states.append(next_state)
                stack.append(next_state)
            transitions.add((states.index(state), symbol, states.index(next_state)))

    accept_state = len(states)
    for i,state in enumerate(states):
        for item in state:
            if item.production[0] == list(productions.keys())[0]+'\'' and item.position == len(item.production[1]) and item.derived == False:
                transitions.add((i,'$',accept_state))
                break
    states.append(set())

    return states, list(transitions)
