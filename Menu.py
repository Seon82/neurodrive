from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.factory import Factory
from kivy.core.window import Window
import os
import pickle
Window.clearcolor = (1,1,1,1)

parametres = {"taille_pop":50,"proba crossing_over":0.7,"proba poids":0.001,"proba bias":0.001,"elitisme":True}

Builder.load_string("""

<MenuPrincipal>:
    title: "Neurodrive"
    canvas.before:
        Rectangle:
            source: "./Images/background.png"
            pos: self.pos
            size: self.size
    FloatLayout:
        Image:
            source: "./Images/image_titre_1.png"
            size_hint: 0.95,1
            pos_hint: {"x":0.02,"y":.32}
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        BoxLayout:
            orientation: "vertical"
            spacing: '5dp'
            size_hint: 0.6,0.6
            Label
            Button:
                text: "Nouvelle simulation"
                font_size:'25sp'
                on_press:
                    root.manager.transition.direction = 'left'
                    root.manager.current = 'options'
            Button:
                text: "Charger une simulation"
                font_size:'25sp'
                on_press:
                    root.manager.transition.direction = 'left'
                    root.manager.current = 'fichier'
            Button:
                text: "En savoir plus"
                font_size:'25sp'
                on_press:
                    root.manager.transition.direction = 'left'
                    root.manager.current = 'infos'

<MenuOuvrirFichier>:
    canvas.before:
        Color:
            rgba: 0.43,0.43,0.43,0.7
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        Label:
            text: "Veuillez choisir le fichier à ouvrir."
            size_hint:1,0.3
        FileChooserIconView:
            id: filechooser
            rootpath: root.path
        GridLayout:
            rows: 1
            cols: 2
            size_hint: 1,0.15
            Button:
                text: "Retour"
                on_press: 
                    root.manager.transition.direction = 'right'
                    root.manager.current = 'principal'
            Button:
                text: "Ouvrir"
                on_release:
                    root.load()


<MenuOptions>:

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: "Veuillez choisir les paramètres de la simulation."
            color: 0,0,0,1
            size_hint: 1,0.2
        Label:
            size_hint: 1,0.2
        GridLayout:
            cols: 2
            spacing: '8dp'
            row_force_default: True
            row_default_height: 40
        
            Label:
                text: "Taille de la population"
                color: 0,0,0,1
            TextInput:
                name: "taille_pop"
                text: "50"
                width: 62
                size_hint_x: None
                multiline: False
                on_text:
                    root.get_info(self)
                
            Label:
                text: "Probabilité de crossing-over"
                color: 0,0,0,1
            TextInput:
                name: "proba crossing_over"
                text: "0.7"
                width: 62
                size_hint_x: None
                multiline: False
                on_text:
                    root.get_info(self)
            Label:
                text: "Probabilité de mutation sur les poids"
                color: 0,0,0,1
            TextInput:
                name: "proba poids"
                text: "0.001"
                width: 62 
                size_hint_x: None
                multiline: False
                on_text:
                    root.get_info(self)
            Label:
                text: "Probabilité de mutation sur les seuils"
                color: 0,0,0,1
            TextInput:
                name: "proba bias"
                text: "0.001"
                width: 62
                size_hint_x: None
                multiline: False
                on_text:
                    root.get_info(self)
            Label:
                text: "Élitisme"
                color: 0,0,0,1
            Switch:
                name: "elitisme"
                width: 62   
                size_hint_x: None
                active: True
                on_active:
                    root.get_info(self)
            Label
            Label

        GridLayout:
            rows: 1
            cols: 2
            size_hint: 1,0.22
            Button:
                text: "Retour"
                on_press: 
                    root.manager.transition.direction = 'right'
                    root.manager.current = 'principal'
            Button:
                text: "Lancer la simulation"
                on_press:
                    root.close()

<MenuInfos>:
    BoxLayout:
        orientation: 'vertical'
        TextInput:
            text: "Programmé par Dylan Sechet, Alexis Roux et Benjamin Boucher."
            readonly: True
        Button:
            size_hint: 1,0.1
            text: "Retour"
            on_press: 
                root.manager.transition.direction = 'right'
                root.manager.current = 'principal'

""")

class MenuPrincipal(Screen):
    pass

class MenuOuvrirFichier(Screen):
    path = os.getcwd()+"\\Sauvegardes"
    
    def load(self):
        path = self.ids.filechooser.selection
        sauvegarde = open("Lien menu_simulation","wb")
        pickle.dump(path[0], sauvegarde)
        sauvegarde.close()
        App.get_running_app().stop()
        Window.close()
        os.system("neurodrive.py")
    
class MenuOptions(Screen):
    global parametres
   
    def get_info(self, caller):
        if caller.name == "elitisme":
            parametres["elitisme"] = caller.active
        elif caller.name == "taille_pop":
            parametres["taille_pop"] = int(caller.text)
        else:
            parametres[caller.name]= float(caller.text)
    
    def close(self):
        sauvegarde = open("Lien menu_simulation","wb")
        pickle.dump(parametres, sauvegarde)
        sauvegarde.close()
        App.get_running_app().stop()
        Window.close()
        os.system("neurodrive.py")
        

class MenuInfos(Screen):
    pass
    
sm = ScreenManager()
sm.add_widget(MenuPrincipal(name='principal'))
sm.add_widget(MenuOuvrirFichier(name='fichier'))
sm.add_widget(MenuOptions(name='options'))
sm.add_widget(MenuInfos(name='infos'))

class NeurodriveApp(App):
    def build(self):
        return sm

NeurodriveApp().run()