import pygame, os
from pygame.locals import *
import pygame_dm

pygame.init()

key_name = {
                "fullscreen":   "Plein ecran",
                "quit"      :   "Quitter",
                "badguy"    :   "Envoyer les mechants",
                "tower"     :   "Construire une tour",
                "upgrade"   :   "Ameliorer une tour",
                "select"    :   "Selectionner",
                "sell_tw"   :   "Vendre une tour",
                "construction" : "Menu construction",
                "research" : "Menu recherches",
                "upgrades" : "Menu amelioration des mechants",
                "special"  : "Menu special",
                "bouton1"  : "Bouton de menu  1",
                "bouton2"  : "Bouton de menu  2",
                "bouton3"  : "Bouton de menu  3",
                "bouton4"  : "Bouton de menu  4",
                "bouton5"  : "Bouton de menu  5",
                "bouton6"  : "Bouton de menu  6",
                "bouton7"  : "Bouton de menu  7",
                "bouton8"  : "Bouton de menu  8",
                "bouton9"  : "Bouton de menu  9",
                "bouton10"  : "Bouton de menu 10",
                "menu_down" : "Menu principal : descendre",
                "menu_up" : "Menu principal : monter",
                "menu_select" : "Menu principal : valider",
}

class Menu(object):
    def __init__(self, keys, screen):
        self.bg_img = None
        self.bg_color = (0,0,0)
        self.text_color = (255,255,255)
        self.hl_color = (255,0,0)
        self.keys = keys
        self.items = []
        self.selected_item = 1
        self.screen = screen
        self.font = pygame.font.Font(os.path.join(pygame_dm.DATAPATH,"VeraBd.ttf"),16)
        self.event = None

class menu:
    def __init__(self,keys):
        self.bg_img = None
        self.bg_color = (0,0,0)
        self.text_color = (255,255,255)
        self.hl_color = (255,0,0)
        self.keys = keys
        self.items = []
        self.selected_item = 1
        self.display = pygame.display.set_mode((pygame_dm.SCREEN_WIDTH,pygame_dm.SCREEN_HEIGHT))
        pygame.display.set_caption( 'MultiPlayerTowerDefense' )
        self.window = pygame.display.get_surface()
        self.font = pygame.font.Font(os.path.join(pygame_dm.DATAPATH,"VeraBd.ttf"),16)
        self.need_update = True
        self.event = None
        
    def show(self):
        self.window.fill(self.bg_color)
        if self.bg_img:
            self.background = pygame.image.load(pygame_dm.DATAPATH + self.bg_img)
            self.window.blit(self.background,(0,0))
        h = 10
        for i in range(len(self.items)):
            item = self.items[i]
            text = item.text
            if item.event:
                if item.event[0].split(" ")[0] == "toggle":
                    text += " : "
                    if item.event[1][item.event[0].split(" ")[1]]:
                        text += "OUI"
                    else:
                        text += "NON"
            color = self.text_color
            (width, height) = self.font.size(text)
            decal = (pygame_dm.SCREEN_WIDTH - width) / 2
            if i == self.selected_item:
                color = self.hl_color
            self.window.blit(self.font.render(text,1,color),(decal,h))
            h += height + 10
	pygame.display.update()
        
    def add_item(self,item):
        self.items.append(item)
        self.need_update = True
        
    def select_next(self):
        self.selected_item += 1
        if self.selected_item >= len(self.items):
            self.selected_item = 1
        self.need_update = True
        
    def select_prev(self):
        self.selected_item -= 1
        if self.selected_item < 1:
            self.selected_item = len(self.items) - 1
        self.need_update = True
        
    def activate_selection(self):
        self.event = self.items[self.selected_item].event
    
    def mainloop(self):
        self.show()
        self.running = True
        while self.running:
            pygame.time.wait(0)
            self.show()
            for pgevent in pygame.event.get():
                if pgevent.type == QUIT or (pgevent.type == KEYDOWN and pgevent.key == self.keys["quit"]):
                    self.event = ("quit",None)
                    self.running = False
                elif pgevent.type == KEYDOWN and pgevent.key == self.keys["menu_down"]:
                    self.select_next()
                elif pgevent.type == KEYDOWN and pgevent.key == self.keys["menu_up"]:
                    self.select_prev()
                elif pgevent.type == KEYDOWN and pgevent.key == self.keys["menu_select"]:
                    self.activate_selection()
            if self.event and self.event[0] == "quit":
                self.running = False
            elif self.event and self.event[0] == "solo":
                self.running = False
            elif self.event and self.event[0] == "multi":
                self.running = False
            elif self.event:
                order = self.event[0].split(" ")
                if order [0] == "input":
                    le_menu = input_field(order[1],self.keys,self.event[1][order[1]])
                    reponse = le_menu.mainloop()
                    print "saisie de",order[1],":",reponse
                    self.event[1][order[1]] = reponse
                    self.event = None
                elif order [0] == "keyconf":
                    field = keyconf_field(order[1],self.keys,self.keys[order[1]])
                    reponse = field.mainloop()
                    if reponse:
                        self.keys[order[1]] = reponse
                    self.event = None
                elif order [0] == "toggle":
                    print "basculement de",order[1]
                    self.event[1][order[1]] = not self.event[1][order[1]]
                    self.event = None
                elif order [0] == "menu":
                    le_menu = self.event [1]
                    self.event = None
                    le_menu.mainloop()
        return self.event
        

class item:
    def __init__(self,text,event):
        self.text = text
        self.event = event

class input_field(menu):
    def __init__(self,titre,keys,default=None):
        menu.__init__(self,keys)
        self.titre = "Saisir la valeur de : " + titre
        self.default = default
        self.value = str(self.default)
    
    def show(self):
        self.window.fill(self.bg_color)
        if self.bg_img:
            self.background = pygame.image.load(pygame_dm.DATAPATH + self.bg_img)
            self.window.blit(self.background,(0,0))
        h = 72
        color = self.text_color
        item = self.titre
        (width, height) = self.font.size(item)
        decal = (pygame_dm.SCREEN_WIDTH - width) / 2
        self.window.blit(self.font.render(item,1,color),(decal,h))
        h += height + 10
        item = self.value
        (width, height) = self.font.size(item)
        decal = (pygame_dm.SCREEN_WIDTH - width) / 2
        self.window.blit(self.font.render(item,1,color),(decal,h))
        h += height + 10
	pygame.display.update()
        
    def mainloop(self):
        self.show()
        self.running = True
        while self.running:
            pygame.time.wait(0)
            self.show()
            for pgevent in pygame.event.get():
                if pgevent.type == QUIT or (pgevent.type == KEYDOWN and (pgevent.key == self.keys["quit"] or pgevent.key == self.keys["menu_select"] or pgevent.key == K_KP_ENTER)):
                    self.event = None
                    self.running = False
                elif pgevent.type == KEYDOWN and pgevent.key == K_BACKSPACE:
                    self.value = self.value[:len(self.value) - 1]
                elif pgevent.type == KEYDOWN:
                    self.value += pgevent.unicode
        return self.value
                
class keyconf_field(menu):
    def __init__(self,titre,keys,default):
        menu.__init__(self,keys)
        self.titre = "Tapper sur la touche pour " + key_name[titre] + " echap pour annuler"
        self.value = default

    def show(self):
        self.window.fill(self.bg_color)
        if self.bg_img:
            self.background = pygame.image.load(pygame_dm.DATAPATH + self.bg_img)
            self.window.blit(self.background,(0,0))
        h = 72
        color = self.text_color
        item = self.titre
        (width, height) = self.font.size(item)
        decal = (pygame_dm.SCREEN_WIDTH - width) / 2
        self.window.blit(self.font.render(item,1,color),(decal,h))
        h += height + 10
	pygame.display.update()
        
    def mainloop(self):
        self.show()
        self.running = True
        while self.running:
            pygame.time.wait(0)
            self.show()
            for pgevent in pygame.event.get():
                if pgevent.type == QUIT or (pgevent.type == KEYDOWN and pgevent.key == K_ESCAPE):
                    self.running = False
                elif pgevent.type == KEYDOWN:
                    self.value = pgevent.key
                    self.running = False
        return self.value
