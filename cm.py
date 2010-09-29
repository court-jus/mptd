import pygame
from pygame.locals import *

control = None

class cm:
    """ This class implements a control manager """
    def __init__(self,keys,touches_boutons):
        self.listeners    =    []        # that will be the list of the listeners that we will send events to
        self.game = None
        self.current_clic_mode = None
        self.keys = keys
        self.touches_boutons = touches_boutons
            
        self.graphs = {
            "fps"   :   [],
            "ctps"  :   [],
            "listeners" : {},
            "draw_time": [],
            }

    def register(self,listener):
        """ Registers a new listener in the cm """
        self.graphs["listeners"][listener] = []
        self.listeners.append (listener)
        
    def unregister(self,listener):
        self.listeners.remove (listener)
    
    def register_game (self,game):
        """ registers the game that cm is related to """
        self.game = game
        self.register(game)

    def post (self, event):
        """ Receive an event and send it to the listeners """
        for listener in self.listeners:
            now = pygame.time.get_ticks()
            listener.notify(event)
            self.graphs["listeners"][listener].append((pygame.time.get_ticks() - now,event))
            
    def handle_pygame_events(self):
        for pgevent in pygame.event.get():
            ev = None
            if pgevent.type == QUIT:
                ev = ["quit_game",None]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["fullscreen"]:
                ev = ["toggle_fullscreen",None]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["quit"]:
                ev = ["quit_game",None]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["badguy"]:
                ev = ["send_badguys",None]
            
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["tower"]:
                self.current_clic_mode = "TOWER_CREATE"
                ev = ["mode_change","TOWER_CREATE"]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["upgrade"]:
                self.current_clic_mode = "TOWER_UPGRADE"
                ev = ["mode_change","TOWER_UPGRADE"]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["select"]:
                self.current_clic_mode = "SELECT"
                ev = ["mode_change","SELECT"]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["sell_tw"]:
                self.current_clic_mode = "TOWER_SELL"
                ev = ["mode_change","TOWER_SELL"]
                
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["construction"]:
                ev = ["menu_change","construction"]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["research"]:
                ev = ["menu_change","research"]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["upgrades"]:
                ev = ["menu_change","upgrades"]
            elif pgevent.type == KEYDOWN and pgevent.key == self.keys["special"]:
                ev = ["menu_change","special"]
            
            elif pgevent.type == MOUSEBUTTONDOWN and pgevent.button == 1:
                ev = ["clic",(self.current_clic_mode,pgevent.pos)]
            elif pgevent.type == MOUSEBUTTONDOWN and pgevent.button == 3:
                ev = ["rclic",None]
            elif pgevent.type == MOUSEMOTION:
                ev = ["mouse_move",pgevent.pos]
            elif pgevent.type == KEYDOWN:
                pgkey = pgevent.key
                if pgkey in self.touches_boutons:
                    for k in self.keys:
                        if self.keys[k] == pgkey:
                            ev = ["menu_bouton_pressed",int(k[6:])]
            if ev:
                self.post( ev )
