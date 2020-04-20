"""
EXEMPLE POUR UN RESEAU INITIALISE A "initialise_reseau(5,[4],3)"

                0                                          0
                                    0
                0
                                    0
--> ENTREE      0   SORTIE/ENTREE        SORTIE/ENTREE     0     SORTIE -->
                                    0
                0
                                    0
                0                                          0


5 entrees
[4] extra_layers; ex: [4,3,5]
3 sortie
[-1,1] intervalle des bias voulus
[-3,3] intervalle des poids voulus

Je veux cree ce reseau:
Individu = Neurones(5, [4], 3, [-1,1], [3,3])

Pour explorer ce reseau - c'est a dire j'entre les valeurs d'entree (sous forme d'une liste avec autant de valeurs que de neurones a l'entree) pour en recuperer la sortie (sous forme d'une liste avec autant de valeurs que de neurones en sortie)
On utilise Individu.explore_reseau(entree)
On recoit la liste en sortie

"""

### NEURONES ###

# Imports
from math import *
import random

# Fonctions externes à la classe

def random_liste(longueur,intervalle):
    """
    Renvoie une liste de len longueur (entier) de valeurs au hasard dans l'intervalle intervalle (liste de deux elements)
    """
    liste = []
    for i in range(longueur):
        liste.append(random.uniform(intervalle[0],intervalle[1]))
    return liste


def sigmoide(valeurs_entree,poids,bias):
    """
    Renvoie pour une entree donnee (liste), la decision (i.e. la sortie: un entier) d'un neurone en fonction de ses poids (liste) et de son bias (entier)
    """
    compteur=0
    for i in range(len(valeurs_entree)):
        compteur += valeurs_entree[i] * poids[i]
    return 1 / (1 + exp(- compteur - bias))

def neurone_aleatoire(entree, extra_layers, sortie, intervalle_bias, intervalle_poids):
        #On crée les listes des poids et des bias
        #On crée la structure du réseau stockée dans la variable interne 'reseau'
        reseau=[entree]+extra_layers+[sortie]
        poids_neurones_reseau = []
        bias_neurones_reseau = []
        for rangee in range(len(reseau)-1):
            bias_neurones_rangee = random_liste(reseau[rangee+1], intervalle_bias)
            poids_neurones_rangee = []
            for neurone in range(reseau[rangee+1]): #Les neurones de la 1ère rangée n'ont pas de poids
                poids_d_un_neurone = random_liste(reseau[rangee], intervalle_poids)  #Un poids != pour chaque entrée
                poids_neurones_rangee.append(poids_d_un_neurone)
            poids_neurones_reseau.append(poids_neurones_rangee)
            bias_neurones_reseau.append(bias_neurones_rangee)
        return Neurones(entree, extra_layers, sortie, poids_neurones_reseau, bias_neurones_reseau)
        
### Classe Neurones ###

class Neurones:
    """
    5 entrees:
    -entree : nombre de neurones dans la premiere rangee (entier)
    -extra_layers : liste de nombres de neurones pour chaque sous-couche (liste d'entiers)
    -sortie : nombre de neurones a la sortie (entier)
    -intervalle_bias : donne l'intervalle des valeurs des bias voulus (liste de deux entiers (valeur min et valeur max))
    -intervalle_poids : donne l'intervalles des valeurs des poids voulus (liste de deux entiers (valeur min et valeur max))
    """
    def __init__(self, entree, extra_layers, sortie, poids, bias):
        self.poids = poids
        self.bias = bias
        extra_layers = extra_layers.copy()
       #On crée la structure du réseau stockée dans la variable interne 'reseau'
        extra_layers.append(sortie) # L'entrée fait partie du réseau
        extra_layers.insert(0,entree) # La sortie aussi
        
        self.reseau = extra_layers
      
  
    def explore_rangee_neurone(self, valeurs_entree, rangee):
        #Renvoie l'ensemble des sorties pour une entree (liste) donnee en fonction de la liste de chacun des poids (ie liste de liste) et de leur bias (liste)
        sortie = []
        for neurone in range(len(self.poids[rangee])):
            #Pour chaque neurone on prend une decision
            sortie.append(sigmoide(valeurs_entree,self.poids[rangee][neurone],self.bias[rangee][neurone]))
        return sortie
    
    def explore_reseau(self, valeurs_entree):
        for rangee in range(len(self.reseau)-1):
            valeurs_entree = self.explore_rangee_neurone(valeurs_entree, rangee)
        return valeurs_entree #Valeurs_entree sont initialement les valeurs qui rentrent dans les neurones - mais qui deviennent ensuite la sortie de ces neurones - et donc la nouvelle entree des neurones qui suivent

#Exemple
# 
# Individu = neurone_aleatoire(5,[4,3],2,[-3,3],[-5,5])
# 
# print("Le reseau est de la forme:", Individu.reseau, "\n"*2, "Les poids sont:", Individu.poids, "\n"*2, "Les bias sont:", Individu.bias, "\n"*2)
# 
# print("La sortie est:", Individu.explore_reseau([1,1,1,1,1]))
