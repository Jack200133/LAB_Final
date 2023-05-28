def get_terminals_and_non_terminals(productions):
    non_terminals = set(productions.keys())
    terminals = set()

    for non_terminal in non_terminals:
        for production in productions[non_terminal]:
            for symbol in production:
                if symbol not in non_terminals:
                    terminals.add(symbol)

    return terminals, non_terminals


def first_sets(productions):
    terminals, non_terminals = get_terminals_and_non_terminals(productions)
    first = {non_terminal: set() for non_terminal in non_terminals}

    changed = True
    while changed:
        changed = False
        for non_terminal in non_terminals:
            for production in productions[non_terminal]:
                for symbol in production:
                    # Para cada terminal en la producción, añadirlo al conjunto first
                    if symbol in terminals:
                        if symbol not in first[non_terminal]:
                            first[non_terminal].add(symbol)
                            changed = True
                        break
                    # Si el símbolo es un no terminal, añadir su conjunto first al conjunto first actual
                    else:
                        added = len(first[non_terminal])
                        first[non_terminal].update(first[symbol] - {None})
                        if len(first[non_terminal]) != added:
                            changed = True
                        # Si el símbolo actual puede generar la cadena vacía (None), continuar con el siguiente símbolo
                        if None not in first[symbol]:
                            break
                else:
                    if None not in first[non_terminal]:
                        first[non_terminal].add(None)
                        changed = True

    return first


def follow_sets(productions, first_sets):
    _, non_terminals = get_terminals_and_non_terminals(productions)
    follow = {non_terminal: set() for non_terminal in non_terminals}
    follow[next(iter(non_terminals))].add('$')

    changed = True
    while changed:
        changed = False
        for non_terminal in non_terminals:
            for production in productions[non_terminal]:
                for i, symbol in enumerate(production):
                    if symbol in non_terminals:
                        # Si no es el último símbolo de la producción, añadir el conjunto first del siguiente símbolo
                        if i + 1 < len(production):
                            next_symbol = production[i + 1]
                            if next_symbol in non_terminals:
                                added = len(follow[symbol])
                                follow[symbol].update(first_sets[next_symbol] - {None})
                                if len(follow[symbol]) != added:
                                    changed = True
                            # Si el siguiente símbolo es un terminal, añadirlo al conjunto follow
                            else:
                                if next_symbol not in follow[symbol]:
                                    follow[symbol].add(next_symbol)
                                    changed = True
                        # Si es el último símbolo de la producción, añadir el conjunto follow del no terminal actual
                        else:
                            added = len(follow[symbol])
                            follow[symbol].update(follow[non_terminal])
                            if len(follow[symbol]) != added:
                                changed = True

    return follow

