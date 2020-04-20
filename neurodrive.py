from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, texture
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior


from neurones import *
from evolution import *

from math import cos,sin,pi
from random import *
import matplotlib.image as img
import numpy as np
import os
import time

parametres = {"taille_pop":50,"proba crossing_over":0.7,"proba poids":0.001,"proba bias":0.001,"elitisme":True}


import pickle
sauvegarde = open("Lien menu_simulation",'rb')
contenu = pickle.load(sauvegarde)
sauvegarde.close()
if type(contenu)==str:
    sauvegarde = open(contenu,'rb')
    contenu = pickle.load(sauvegarde)
    sauvegarde.close()
    generation_importee = True,contenu
else:
    parametres = contenu
    generation_importee = (False,)

class PlayPause(ToggleButtonBehavior, Image):
    def __init__(self,**kwargs):
        super(PlayPause, self).__init__(**kwargs)
        self.source="./Images/Bouton_pause.png"
    def clic(self, caller):
        global en_pause
        if caller.state=="down":
            self.source = "./Images/Bouton_play.png"
            en_pause = True
        else:
            self.source="./Images/Bouton_pause.png"
            en_pause = False


class Voiture(Widget):
    """
    Petite voiture qui s'affiche à l'écran et sert de "réceptacle" à un réseau de neurone pour évoluer:
    Paramètres fixés au début d'une génération:
        neurones : un réseau de neurones : objet de type Neurones
        color : une couleur aléatoire : 4-liste rgba de floats compris entre 0 et 1
        size : composé de x et y : dimension de la voiture sous forme de liste de 2 entiers
    Paramètres évoluant pendant une simulation:
        vitesse : vitesse linéraire de la voiture : float strictement supérieur à 1
        theta : angle de la voiture : float compris entre 0 et 2*pi
        distanceReel : distance totale parcourue par la voiture au cours de cette génération
        distance : partie entière de distanceReel permettant d'afficher la distance sur les voitures en cas de besoin
        aX : accélération linéaire de la voiture : sortie du réseau de neurone : float compris entre 0 et 1
        aAng : vitesse angulaire de la voiture : sortie du réseau de neurone : float compris entre 0 et 1
        vie : booléen servant à vérifier si la voiture est toujours en vie (si elle s'est prise un mur ou pas encore)
        capteur : état des cinq capteurs de distance au mur dans cinq direections devant la voiture : 5-liste de floats compris entre 0 et 1
    """
    size_x = NumericProperty(50)
    size_y = NumericProperty(25)
    size = ReferenceListProperty(size_x,size_y)
    neurones = []
    theta = NumericProperty (0)
    distanceReel = 0
    distance = NumericProperty (0.001)
    vitesse = 2
    aX = 0.5
    aAng = 0.5
    vie = True
    r,g,b,a = NumericProperty(1),NumericProperty(1),NumericProperty(1),NumericProperty(1)
    color = ReferenceListProperty (r,g,b,a)
    capteurs = [0,0,0,0,0]

    def reinitialise(self):
        """
        Remet à l'état initial tout les paramètres de la voiture après une génération pour relancer la suivante
        """
        self.theta = 0
        self.pos = 50,70
        self.distanceReel = 0
        self.distance = 0.001
        self.vitesse = 2
        self.aX = 0.5
        self.aAng = 0.5
        self.vie = True

    def acceleration_lineaire(self,aX):
        """
        Calcule la nouvelle vitesse de la voiture à partir de son accélération linéaire
        """
        if self.vitesse >= 2:
            self.vitesse *= 1+ (aX-.5)/50

    def vitesse_angulaire(self,aAng):
        """
        Calcule le nouvel angle de la voiture à partir de sa vitesse angulaire
        """
        self.theta += (aAng/10-0.05)*8.5*(1-exp(-self.vitesse/20))
        self.theta %= 2*pi

    def calcul_distance(self):
        """
        Rajoute à la distance totale parcourue par la voiture la distance qu'elle a parcouru pendant la dernière itération
        """
        self.distanceReel += self.vitesse/10
        self.distance = self.distanceReel//1

    def avance(self):
        """
        Fait avancer la voiture et vérifie si elle meurt ou pas:
            -commence par vérifier l'état des capteurs
            -calcule sa nouvelle accélération linéaire et sa nouvelle vitesse angulaire à partir des capteurs grâce au réseau de neurones
            -calcule sa nouvelle vitesse
            -calcule son nouvel angle
            -avance en modifiant sa position grâce à sa vitesse et son angle
            -actualise la distance totale parcourue
        """
        self.test_mur()
        self.aX,self.aAng = self.neurone()
        self.acceleration_lineaire(self.aX)
        self.vitesse_angulaire(self.aAng)
        self.pos = (self.vitesse*cos(self.theta)+self.pos[0],self.vitesse*sin(self.theta)+self.pos[1])
        self.calcul_distance()
        

    def test_mur(self):
        """
        Calcule l'état des capteurs devant la voiture
            -commence par situer le centre de l'arrête avant de la voiture comme point de référence pour les capteurs
            -pour chaque capteur, teste cran par cran dans chaque direction si le capteur se trouve dans un mur ou pas jusqu'à recontrer un mur
            -teste si le point de référence se trouve lui-même dans un mur pour savoir si la voiture meurt ou pas
        """
        global circuit,width,height
        x,y = self.pos
        x_dec = self.size_x*cos(self.theta)
        y_dec = self.size_y//2 + self.size_x*sin(self.theta)
        x += x_dec
        y += y_dec
        for i in range(5):
            j = 0
            actif = True
            while actif and j < 100:
                j+=1
                x_capteur = x + j*cos((self.theta - pi/2 + i*pi/4)%(2*pi))
                y_capteur = y + j*sin((self.theta - pi/2 + i*pi/4)%(2*pi))
                try:
                    if circuit[height-int(y_capteur),int(x_capteur)]:
                        actif = False
                except:
                    actif = False
            self.capteurs[i]=j/100
        try:
            if circuit[height-int(y),int(x)]:
                self.vie = False
        except:
            self.vie = False
        
    def neurone(self):
        """
        Fait appel au réseau de neurones pour calculer les nouveaux paramètres à partir de l'état des capteurs
        """
        aX,aAng = self.neurones.explore_reseau(self.capteurs)
        return aX,aAng


class NeurodriveGame(Widget):
    """
    Gère l'écran principal, son affichage graphique, l'enchaînement des évènements et la liste et l'évolution des voitures
    Constantes:
        intervalle_poids : intervalle dans lequel les poids du réeau de neurone sont chosis
        intervalle_bias : intervalle dans lequel les seuils du réeau de neurone sont chosis
        probabilite_mutation : probabilité de changer chaque poids ou seuil du réseau de neurone lors de l'évolution
        probabilite_crossover : probabilté de générer un nouvel individu en croisant deux anciens individus lors de l'évolution
        nombre_voitures : nombre de voitures affichées à l'écran lors de la simulation
    Variable:
        generation : numéro de la génération de voiture entrain de tourner à l'écran
    """
    global parametres
    global en_pause

    generation = NumericProperty (1)
    intervalle_poids = [-5,5]
    intervalle_bias = [-5,5]
    probabilite_mutation_poids = parametres["proba poids"]
    probabilite_mutation_seuils = parametres["proba bias"]
    probabilite_crossover = parametres["proba crossing_over"]
    nombre_voitures = parametres["taille_pop"]
    elitisme = parametres["elitisme"]
    
        
    

    en_pause = False
    var_changer_circuit = [False, str()]
 
 
    def init_voiture(self,reseaux_evolues):
        """
        Initialise les générations de voitures au début de la simulation:
            population : liste des voitures
            -si population est vide, cela veut dire qu'on est à la première génération, les voitures sont initialisées aléatoiremnt
            -sinon:
                -on parcourt la liste des sous-widgets du widget principal (liste des voitures en l'occurence)
                -on attribue à chaque voiture un réseau de neurone de la liste des réseaux évolués juste avant
                -on attribue au meilleur individu de la génération la couleur verte et une couleur aléatoire aux autres voitures
                -on réinitialise les autres paramètres des voitures
        """
        if reseaux_evolues == []:
            for i in range (self.nombre_voitures):
                self.add_widget(Voiture())
        i = 0
        for child in self.children:
            if type(child) == Voiture :
                if reseaux_evolues == []:
                    reseau = neurone_aleatoire(5,[4,3],2,self.intervalle_bias,self.intervalle_poids)
                else:
                    reseau = reseaux_evolues[i]
                color = random(),random(),random(),1
                if i==0:
                    color = 0.3,1,0,1
                child.neurones = reseau
                child.color = color
                child.reinitialise()
            i += 1
            
            if self.var_changer_circuit[0]: # Changement de circuit
                self.var_changer_circuit[0] = False
                texte = self.var_changer_circuit[1]
                global circuit
                nb_image = 0
                if texte == "Circuit basique":
                    nb_image = 1
                elif texte == "Circuit desert":
                    nb_image = 2
                elif texte == "Circuit neige":
                    nb_image = 3
                circuit = img.imread('./Circuits/Circuit_'+str(nb_image) +'.png')
                circuit = circuit[:,:,0]
                self.ids.image_fond.source = './Circuits/Circuit_couleur_'+str(nb_image) +'.png'
                
                
    def update(self, dt):
        """
        Fonction principale appelée à intervalle régulier pour faire avancer la simulation :
            -fait avancer les voitures
            -fait évoluer les voitures si elles sont toutes arrêtées
        """
        if not en_pause:
            reste_course = 0
            for child in self.children:
                if type(child) == Voiture :
                    if child.vie:
                        child.avance()
                        reste_course += 1
    
            if reste_course == 0:
                self.evolue()

    def evolue(self):
        """
        Fait évoluer les voitures:
            -récupère les scores de chaque voiture et les associe à leur réseau de neurone
            -fait évoluer les voitures et récupère la nouvelle population
            -initialise la génération suivante à partir des nouveaux réseaux de neurones
        """
        resultat = []
        for child in self.children:
            if type(child) == Voiture :
                resultat.append([child.neurones,
                                 child.distance])
        reseaux_evolues = evoluer_neurones(resultat,
                                       self.probabilite_crossover,
                                       self.probabilite_mutation_seuils,
                                       self.probabilite_mutation_poids,
                                       self.intervalle_bias,
                                       self.intervalle_poids,
                                       self.elitisme)
        self.generation += 1
        self.init_voiture(reseaux_evolues)
    
    def changer_circuit(self, texte):
        self.var_changer_circuit = [True, texte]
    
    def sauvegarder(self):
        MsgSave().open()
    
    def quit(self):
        App.get_running_app().stop()
        Window.close()
        os.system("Menu.py")
        
class MsgSave(Popup):
    global game
    jour = time.strftime('%d.%m.%Y %Hh%M')
    texte_defaut = jour
    
    def enregistrer_sauvegarde(self, nom_fichier):
        resultat = []
        for child in game.children:
            if type(child) == Voiture:
                resultat.append(child.neurones)
        sauvegarde = {"parametres": parametres, "population": resultat, "generation": game.generation}
        fichier_ouvert = open("./Sauvegardes/" + nom_fichier,'wb')
        pickle.dump(sauvegarde, fichier_ouvert)
        fichier_ouvert.close()
        self.dismiss()
        
    
class NeurodriveApp(App):
    """
    Application principale:
        -crée la fenêtre et le jeu
        -initialise la population vide
        -appelle la fonction update à intervalle régulier
    """
    def build(self):
        global game
        global generation_importee
        
        if generation_importee[0]:  # Règle les paramètres si des données sauvegardées ont été ouvertes
            contenu = generation_importee[1]
            parametres = contenu["parametres"]
        
        game = NeurodriveGame()
        
        if generation_importee[0]:   
        # Ajoute les voitures sauvegardées si des données sauvegardées ont été ouvertes
            game.generation = contenu["generation"]
            for reseau in contenu["population"]:
                ma_voiture = Voiture()
                ma_voiture.neurones = reseau
                ma_voiture.color = random(),random(),random(),1
                ma_voiture.reinitialise()
                game.add_widget(ma_voiture)
        else:
            game.init_voiture([])
            
        Clock.schedule_interval(game.update, 1.0 / 600.0)
        return game

##======CORPS DU PROGRAMME=======##

"""
Génère le circuit sous forme de matrice contenant des 0 et des 1 à partir d'une image et règle la taille de l'écran
"""
circuit = img.imread('./Circuits/Circuit_1.png')
height,width,_ = circuit.shape
circuit = circuit[:,:,0]
   
Config.set('graphics', 'width', str(width)) 
Config.set('graphics', 'height', str(height))
Config.set('graphics', 'resizable', 0)

from kivy.core.window import Window

"""
Lance la simulation
"""
NeurodriveApp().run()