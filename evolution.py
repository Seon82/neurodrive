''' 
Mode d'emploi:
Appeler la fonction:
evoluer_neurones(entree, probabilite_crossover, probabilite_mutation_bias, probabilite_mutation_poids, intervalle_poids, intervalle_bias, elitisme)

entree :          une liste de 2-listes de la forme: [[individuA,distanceA],[individuB,distanceB],...]
intervalle_poids: 2-liste de la forme [poids_min,poids_max]
intervalle_bias:  2-liste de la forme [bias_min,bias_max]

'''

### FONCTIONS GÉNÉTIQUES ###
from math import *
import random
from neurones import *


def extraire(entree): # Extrait la liste des individus et des distances de [[individuA,distanceA],[individuB,distanceB],...]
    liste_individus, liste_fitness = [], []
    for elmt in entree:
        liste_individus.append(elmt[0])
        liste_fitness.append(elmt[1])
    return liste_individus, liste_fitness
    
            
def normaliser(liste_fitness): # Prend la liste des fitness brutes et renvoie la liste des fitness normalisées
    somme = sum(liste_fitness)
    return [i/somme for i in liste_fitness] 
    
def cumulees_croissantes(liste_fitness_normalisee): # Renvoie la listes des probas cumulées croissantes
    liste_fitness_cumulees = list()
    somme = 0
    for elmt in liste_fitness_normalisee:
        somme += elmt
        liste_fitness_cumulees.append(somme)
    return liste_fitness_cumulees
    
    
def selectionner_parent(liste_individus, liste_fitness_cumulees): # Fitness Proportionate Selection
    nb_alea = random.random()
    i = 0
    while liste_fitness_cumulees[i] <= nb_alea:
        i+=1
    return liste_individus[i]
        
        
def crossover(parentA, parentB): # Réalise un crossover (1 point de coupure) et renvoie 2 listes
    n = len(parentA)
    point_coupure = random.randint(1,n-1)
    individuA= parentA[:point_coupure] + parentB[point_coupure:]
    individuB= parentB[:point_coupure] + parentA[point_coupure:]
    return individuA, individuB
    
def muter(liste, probabilite_mutation, intervalle): # ATTENTION modifie directement la liste passée en argument
    a = liste.copy()
    for i in range(len(liste)):
        if random.random() < probabilite_mutation:
            liste[i] = random.uniform(intervalle[0], intervalle[1])


def evoluer_bias(IndividuA, IndividuB, probabilite_mutation, intervalle_bias): # Renvoie les bias évolués de 2 nouveaux individus
    nouveaux_bias_1 = list()
    nouveaux_bias_2 = list()
    biasA=IndividuA.bias
    biasB=IndividuB.bias
    for i in range(len(IndividuA.bias)):
        couche_bias_evoluee_1, couche_bias_evoluee_2 = crossover(biasA[i],biasB[i]) # Crossover
        muter(couche_bias_evoluee_1, probabilite_mutation, intervalle_bias) # Mutation
        muter(couche_bias_evoluee_2, probabilite_mutation, intervalle_bias)
        nouveaux_bias_1.append(couche_bias_evoluee_1)
        nouveaux_bias_2.append(couche_bias_evoluee_2)
    return nouveaux_bias_1, nouveaux_bias_2

def evoluer_poids(IndividuA, IndividuB, probabilite_mutation, intervalle_poids): # Renvoie les poids évolués de 2 nouveaux individus
    nouveaux_poids_1 = list()
    nouveaux_poids_2 = list()
    poidsA = IndividuA.poids
    poidsB = IndividuB.poids
    for num_couche in range(len(poidsA)):
        couche_poids_evoluee_1 = list()
        couche_poids_evoluee_2 = list()
        for i in range(len(poidsA[num_couche])):
            poids_evolues_1, poids_evolues_2 = crossover(poidsA[num_couche][i], poidsB[num_couche][i]) # Crossover
            muter(poids_evolues_1, probabilite_mutation, intervalle_poids) # Mutation
            muter(poids_evolues_2, probabilite_mutation, intervalle_poids)
            couche_poids_evoluee_1.append(poids_evolues_1)
            couche_poids_evoluee_2.append(poids_evolues_2)
        nouveaux_poids_1.append(couche_poids_evoluee_1)
        nouveaux_poids_2.append(couche_poids_evoluee_2)
    return nouveaux_poids_1, nouveaux_poids_2

def evoluer_neurones(entree, probabilite_crossover, probabilite_mutation_bias, probabilite_mutation_poids, intervalle_poids, intervalle_bias, elitisme):
    ''' Entrée: [[individuA,distanceA],[individuB,distanceB],...]
        intervalle_poids: 2-liste de la forme [poids_min,poids_max]
        intervalle_bias: 2-liste de la forme [bias_min,bias_max]'''
    liste_individus, liste_fitness = extraire(entree)
    N = len(liste_individus) # Taille de la population
    N_nouvelle_gen = 0
    nouvelle_gen = list()
    structure = liste_individus[0].reseau
    nb_entrees = structure[0]
    nb_sorties = structure[-1]
    extra_layers = list(structure[1:-1])
    liste_fitness_normalisee = normaliser(liste_fitness)
    liste_fitness_cumulees = cumulees_croissantes(liste_fitness_normalisee)

    if elitisme:
        # Elitisme
        nouvelle_gen.append(liste_individus[liste_fitness.index(max(liste_fitness))])
        #print('max', max(liste_fitness), 'fdsf', liste_fitness.index(max(liste_fitness)))
        #print(nouvelle_gen[0].bias)
        N_nouvelle_gen+=1
    
    while N_nouvelle_gen < N: # Crossover

        if random.random()>=probabilite_crossover or N_nouvelle_gen == N-1: # On garde constante la taille de la population
            individu = selectionner_parent(liste_individus, liste_fitness_cumulees) #On prend copie directement l'individu
            nouvelle_gen.append(individu)
            N_nouvelle_gen+=1

        else:
            parentA = selectionner_parent(liste_individus, liste_fitness_cumulees) # Sélection
            parentB = selectionner_parent(liste_individus, liste_fitness_cumulees)

            poidsA, poidsB = evoluer_poids(parentA, parentB, probabilite_mutation_poids, intervalle_poids) # Evolution des poids
            biasA, biasB = evoluer_bias(parentA, parentB, probabilite_mutation_bias, intervalle_bias) # Evolution des bias
            individuA = Neurones(nb_entrees, extra_layers, nb_sorties, poidsA, biasA)
            individuB = Neurones(nb_entrees, extra_layers, nb_sorties, poidsB, biasB)
            nouvelle_gen.append(individuA)
            nouvelle_gen.append(individuB)
            N_nouvelle_gen+=2
    return nouvelle_gen

if __name__ == "__main__":
    #TEST
    from neurones import *
    n = 10
    intervalle_poids = [-1,1]
    intervalle_bias = [-1,1]
    probabilite_mutation = 0.00001
    probabilite_crossover = 0.7
    ma_pop = list()
    for i in range(n):
        ma_pop.append(neurone_aleatoire(5,[4,3],2,intervalle_bias, intervalle_poids))  

    entree=list()
    for elmt in ma_pop:
        entree.append([elmt,random.randint(1,30)])

    pop_evoluee = evoluer_neurones(entree, probabilite_crossover, probabilite_mutation, probabilite_mutation, intervalle_poids, intervalle_bias, True)

    for i in range(len(pop_evoluee)):
        Individu2 = pop_evoluee[i]
        Individu1 = ma_pop[i]
        print("La sortie est:", Individu1.explore_reseau([1,1,1,1,1]))
        print("La sortie est:", Individu2.explore_reseau([1,1,1,1,1]))
        print()
