#Convertir a AFN to a AFD
import json

#Función para obtener el AFN generado
def openJson():
    with open('AFN.json', 'r') as json_file:
	    return json.load(json_file)

#Funcion el eClosure de cada estado
def eClosures(state):
    temp =[]
    closures = []
    for i in state:
        # Condición para verificar si el estado ya está en temp para asegurarnos de no repetir un estado en la cerradura
        if i not in temp:
            #Guarda el primer estado para el cierre y lo utiliza para obtener todos las cerraduras posibles
            temp.append(i)
            closures.append(i)

    while len(temp) != 0:
        states =  temp.pop()
        # Ciclo utilizado para obtener solo los datos de la función de transición
        for j in afn['transition_function']:
            # Obtener cada valor de la lista obtenida en el ciclo for
            first = j[0]
            second = j[1]
            third = j[2]
            # Obtener todas las transiciones ε con el estado
            if second == 'ε' and  first == states:
                # Condición para verificar si el estado ya está guardado
                if third not in closures:
                    temp.append(third)
                    closures.append(third)

    # Ordenar la lista de estados
   
    closures.sort()

    return closures


#Funcion para convertir el AFN a AFD
def convertToAFD(file):
    afd ={}

    s1 = eClosures(['S1'])
    temp1 =[s1[:]]
    states =[s1[:]]

    rechazos = []
    
    transition = []
    transitionB = []
    finalStates = []

    #Obtener los valores del AFN
    alphabet = file ['letters']
    final_state = file['final_states']
    transitions = file ['transition_function']

    while len(temp1) != 0:
        #Obtener el primer valor de la lista
        temp_state = temp1.pop()
        #Ciclo para obtener cada valor del alfabeto
        subset = []
        start = []
        start.extend(temp_state[:])

        # Se calcula la cerradura de cada estado
        closure = eClosures(start)
        for i in alphabet:
            move = []
            #Ciclo para obtener cada valor de la función de transición
            for j in transitions:
                # Valores de cada transicion first = inicial, second = letra de transicion, third = final
                first = j[0]
                second = j[1]
                third = j[2]
                #Ciclo para obtener cada valor de la cerradura
                for k in closure :
                    # Verifica si el estado inicial de la transición es igual al estado inicial de la cerradura
                    # y si la letra de la transición es igual a la letra del alfabeto
                    if first == k and second == i:
                        # Si el estado no esta en la lista de estados, se agrega
                        #if third not in start:
                        move.append(third)


            subset = eClosures(move)
           # subset = n_states

            if subset != start:
                
                # Condicion para verificar si el estado ya está en temp1 para asegurarnos de no repetir un estado en la cerradura
                if subset not in states:
                    if subset not in temp1:
                        # Guarda el primer estado para el cierre y lo utiliza para obtener todos las cerraduras posibles
                        states.append(subset[:])
                        temp1.append(subset[:])

                # Se agrega la transición al AFD
                transition.append((start, i, subset))
                transitionB.append(("S"+str(states.index(start)+1), i, "S"+str(states.index(subset)+1)))
            else:
                if move != []:
                    transition.append((start, i, subset))
                    transitionB.append(("S"+str(states.index(start)+1), i, "S"+str(states.index(subset)+1)))

                

    #Convierte la lista de estados finales en un string
    final_state = ' '.join ([str(item) for item in file['final_states']])

    # Ciclo para obtener cada valor de la lista de estados
    for i in states:
        # Busca si el estado final está en la lista de estados
        if final_state in i:
            # Si el estado final está en la lista de estados, se agrega a la lista de estados finales
            finalStates.append(i)

    #Datos del AFD
    afd['alphabet'] = alphabet
    afd['start_state'] = s1
    afd['states'] = states
    afd['final_states'] = finalStates
    afd['transition'] = transition

    afd['start_stateB'] = ["S"+str(states.index(s1)+1)]
    afd['statesB'] = ["S"+str(states.index(i)+1) for i in states]
    afd['final_statesB'] = ["S"+str(states.index(i)+1) for i in finalStates]
    afd['transitionB'] = transitionB


    return  afd

#Funcion para guardar el AFD en un archivo json
def output_afd(afd):
    with open('AFD.json', 'w') as file:
        json.dump(afd, file, indent=4)

def generate_afd(afn_data):
    global afn
    afn = afn_data
    afd = convertToAFD(afn)
    #output_afd(afd)
    return afd
