import pandas as pd
import numpy as np

def generate_slr_tables(states, transitions, productions, first_sets, follow_sets,non_terminals,terminals):
    start_symbol = list(productions.keys())[0]  # Símbolo de inicio
    terminals = terminals + ['$']  # Añadir el símbolo de dolar ($)
    # Crear tabla de ACCION y tabla de GOTO inicialmente vacías
    action_table = pd.DataFrame(index=range(len(states)), columns=terminals, dtype=object)
    action_table = action_table.fillna(value=np.nan)

    goto_table = pd.DataFrame(index=range(len(states)), columns=non_terminals, dtype=object)  # Quitar el símbolo de dolar ($)
    goto_table = goto_table.fillna(value=np.nan)

    errorList =[]
    # Crear una lista de producciones y un diccionario para mapear las producciones a su índice correspondiente
    production_list = []
    production_index = {}
    for key in productions.keys():
        for value in productions[key]:
            prod = (key, tuple(value))
            production_index[prod] = len(production_list)
            production_list.append(prod)

    # Rellenar las tablas
    for i, state in enumerate(states[:-1]):
        for item in state:
            # caso especial para la reducción [S' -> S·]
            if item.production[0] == start_symbol + "'" and item.position == len(item.production[1]):
                action_table.loc[i, '$'] = "ACCEPT"
            elif item.position == len(item.production[1]):  # caso para [A -> α·]
                for symbol in follow_sets.get(item.production[0], []):
                    prod = (item.production[0], tuple(item.production[1]))
                    if pd.notna(action_table.loc[i, symbol]) and symbol != '$':
                        errorList.append(f'1 Conflict in [{i},{symbol}] = ({action_table.loc[i, symbol]},r{production_index.get(prod, -1)})')
                    else:
                        action_table.loc[i, symbol] = f"R {production_index.get(prod, -1)}"
        for trans in transitions:
            if trans[0] == i:
                if trans[1] in terminals:  # caso para [A → α·aβ]
                    if pd.notna(action_table.loc[i,trans[1]]) and trans[1] != '$':
                        errorList.append(f'2 Conflict in [{i},{trans[1]}] = ({action_table.loc[i, trans[1]]},s{trans[2]})')
                    elif trans[1] != '$':
                        action_table.loc[i, trans[1]] = f"S {trans[2]}"
                elif trans[1] in non_terminals:  # caso para ir_A
                    if pd.notna(goto_table.loc[i, trans[1]]):
                        errorList.append(f'3 Conflict in [{i},{trans[1]}] = ({goto_table.loc[i, trans[1]]},s{trans[2]})')
                    goto_table.loc[i, trans[1]] = trans[2]

    # Reemplazar NaNs por " "
    action_table = action_table.fillna("-")
    goto_table = goto_table.fillna("-")

    # Combina las tablas de acción y GOTO en una tabla
    combined_table = pd.concat([action_table, goto_table], axis=1)
    combined_table = combined_table.drop(combined_table.index[- 1])

    return combined_table, errorList
