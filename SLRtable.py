import pandas as pd
import numpy as np

def generate_parser_tables(estados, transiciones, producciones, conjuntos_siguiente, terminales, no_terminales):
    simbolo_inicio = list(producciones.keys())[0]
    terminales += ['$']

    tabla_accion = pd.DataFrame(index=range(len(estados)), columns=terminales, dtype=object)
    tabla_accion = tabla_accion.fillna(value=np.nan)

    tabla_goto = pd.DataFrame(index=range(len(estados)), columns=no_terminales, dtype=object)
    tabla_goto = tabla_goto.fillna(value=np.nan)

    lista_errores = []

    lista_producciones = []
    indice_producciones = {}
    for llave in producciones.keys():
        for valor in producciones[llave]:
            prod = (llave, tuple(valor))
            indice_producciones[prod] = len(lista_producciones)
            lista_producciones.append(prod)

    for idx, estado in enumerate(estados[:-1]):
        for elem in estado:
            if elem.production[0] == simbolo_inicio + "'" and elem.position == len(elem.production[1]):
                tabla_accion.loc[idx, '$'] = "ACEPTAR"
            elif elem.position == len(elem.production[1]):
                for simbolo in conjuntos_siguiente.get(elem.production[0], []):
                    prod = (elem.production[0], tuple(elem.production[1]))
                    if pd.notna(tabla_accion.loc[idx, simbolo]) and simbolo != '$':
                        lista_errores.append(f'Conflicto en [{idx},{simbolo}] = ({tabla_accion.loc[idx, simbolo]},r{indice_producciones.get(prod, -1)})')
                    else:
                        tabla_accion.loc[idx, simbolo] = f"R {indice_producciones.get(prod, -1)}"
        for trans in transiciones:
            if trans[0] == idx:
                if trans[1] in terminales:
                    if pd.notna(tabla_accion.loc[idx,trans[1]]) and trans[1] != '$':
                        lista_errores.append(f'Conflicto en [{idx},{trans[1]}] = ({tabla_accion.loc[idx, trans[1]]},s{trans[2]})')
                    elif trans[1] != '$':
                        tabla_accion.loc[idx, trans[1]] = f"S {trans[2]}"
                elif trans[1] in no_terminales:
                    if pd.notna(tabla_goto.loc[idx, trans[1]]):
                        lista_errores.append(f'Conflicto en [{idx},{trans[1]}] = ({tabla_goto.loc[idx, trans[1]]},s{trans[2]})')
                    tabla_goto.loc[idx, trans[1]] = trans[2]

    tabla_combinada = pd.concat([tabla_accion, tabla_goto], axis=1)
    tabla_combinada = tabla_combinada.drop(tabla_combinada.index[- 1])
    tabla_accion = tabla_accion.drop(tabla_accion.index[- 1])
    tabla_goto = tabla_goto.drop(tabla_goto.index[- 1])

    return tabla_combinada, lista_errores, lista_producciones, tabla_accion, tabla_goto
