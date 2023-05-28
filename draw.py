from graphviz import Digraph

from graphviz import Digraph

def visualize_lr0(states, transitions):
    dot = Digraph("LR0", format='png')
    dot.attr(rankdir="LR")
    dot.attr('node', shape='rectangle')

    for i, state in enumerate(states):
        if i == len(states) - 1:  # Estado de aceptación
            label = 'ACEPTAR'
        else:
            non_derived = []
            derived = []
            for item in state:
                if item.derived:
                    derived.append(str(item))
                else:
                    non_derived.append(str(item))

            label = 'I' + str(i) + '\n-----------\n'
            label += '\n'.join(non_derived) + '\n-----------\n' + '\n'.join(derived)

        dot.node(str(i), label=label)

    for t in transitions:
        dot.edge(str(t[0]), str(t[2]), label=t[1])

        # Generar y guardar el gráfico como imagen PNG
    dot.render("lr0_automaton", cleanup=True)
    print("Gráfico del autómata LR(0) generado como 'lr0_automaton.png'")

