import json

def hopcroft_minimization(afd):
    P = [set(afd["final_statesB"]), set(afd["statesB"]) - set(afd["final_statesB"])]
    W = [set(afd["final_statesB"])]

    def find_group(state, P):
        for group in P:
            if state in group:
                return group
        return None

    while W:
        A = W.pop(0)
        for symbol in afd["alphabet"]:
            X = set()
            for transition in afd["transitionB"]:
                if transition[1] == symbol and transition[2] in A:
                    X.add(transition[0])

            if not X:
                continue

            for Y in P.copy():
                if not Y.intersection(X):
                    continue

                Y_minus_X = Y - X
                P.remove(Y)
                P.extend([Y.intersection(X), Y_minus_X])

                if Y in W:
                    W.remove(Y)
                    W.extend([Y.intersection(X), Y_minus_X])
                else:
                    smaller_group = Y_minus_X if len(Y_minus_X) < len(Y.intersection(X)) else Y.intersection(X)
                    if smaller_group:
                        W.append(smaller_group)

    return P

def remove_dead_states(afd):
    reachable_states = set(afd["start_stateB"])

    def find_new_reachable_states(state, reachable_states):
        for transition in afd["transitionB"]:
            if transition[0] == state:
                reachable_states.add(transition[2])

    prev_reachable_states_count = 0
    while prev_reachable_states_count != len(reachable_states):
        prev_reachable_states_count = len(reachable_states)
        for state in list(reachable_states):
            find_new_reachable_states(state, reachable_states)

    afd["statesB"] = list(reachable_states)
    afd["final_statesB"] = [s for s in afd["final_statesB"] if s in reachable_states]
    afd["transitionB"] = [t for t in afd["transitionB"] if t[0] in reachable_states and t[2] in reachable_states]


def build_miniAFD(afd,start):
    remove_dead_states(afd)
    minimized_partitions = hopcroft_minimization(afd)
    minimized_partitions = [p for p in minimized_partitions if p]

    state_mapping = {}
    for i, partition in enumerate(minimized_partitions):
        for state in partition:
            state_mapping[state] = f"S{i + 1+int(start)}"

    miniAFD = {
        "letters": afd["alphabet"],
        "start_states": [state_mapping[afd["start_stateB"][0]]],
        "states": [],
        "final_states": [],
        "transition_function": [],
    }

   

    for final_state in afd["final_statesB"]:
        if final_state in state_mapping:
            mapped_final_state = state_mapping[final_state]
            if mapped_final_state not in miniAFD["final_states"]:
                miniAFD["final_states"].append(mapped_final_state)

    
    processed_transitions = set()
    for transition in afd["transitionB"]:
        old_from, symbol, old_to = transition
        new_from, new_to = state_mapping[old_from], state_mapping[old_to]
        if (new_from, symbol) not in processed_transitions:
            processed_transitions.add((new_from, symbol))
            miniAFD["transition_function"].append([new_from, symbol, new_to])
    
    cleanStates =[]
    for state in state_mapping.values():
        for ini, simbol, fin in miniAFD["transition_function"]:
            if ini == state:
                if state not in cleanStates:
                    cleanStates.append(state)
                break

    miniAFD["states"] = cleanStates

    cleanTransitions = []

    for ini, simbol, fin in miniAFD["transition_function"]:
        if ini in cleanStates and fin in cleanStates:
            cleanTransitions.append([ini, simbol, fin])

    miniAFD["transition_function"] = cleanTransitions

    return miniAFD
