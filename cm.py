# -*- coding: utf-8 -*-

from pygame.locals import *

control = None

class cm:
    """ This class implements a control manager """
    def __init__(self,keys,touches_boutons):
        self.listeners    =    []        # that will be the list of the listeners that we will send events to
        self.emitters     =    []        # objects that can "spawn" events
        self.game = None
        self.current_clic_mode = None
        self.keys = keys
        self.touches_boutons = touches_boutons
            
    def register_emitter(self, emitter):
        self.emitters.append(emitter)

    def register(self,listener):
        """ Registers a new listener in the cm """
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
            listener.notify(event)
            
    def handle_events(self):
        for emitter in self.emitters:
            for event in emitter.handle_events():
                ev = None
                if event.type == QUIT:
                    ev = ["quit_game",None]
                elif event.type == KEYDOWN and event.key == self.keys["fullscreen"]:
                    ev = ["toggle_fullscreen",None]
                elif event.type == KEYDOWN and event.key == self.keys["quit"]:
                    ev = ["quit_game",None]
                elif event.type == KEYDOWN and event.key == self.keys["badguy"]:
                    ev = ["send_badguys",None]
                
                elif event.type == KEYDOWN and event.key == self.keys["tower"]:
                    self.current_clic_mode = "TOWER_CREATE"
                    ev = ["mode_change","TOWER_CREATE"]
                elif event.type == KEYDOWN and event.key == self.keys["upgrade"]:
                    self.current_clic_mode = "TOWER_UPGRADE"
                    ev = ["mode_change","TOWER_UPGRADE"]
                elif event.type == KEYDOWN and event.key == self.keys["select"]:
                    self.current_clic_mode = "SELECT"
                    ev = ["mode_change","SELECT"]
                elif event.type == KEYDOWN and event.key == self.keys["sell_tw"]:
                    self.current_clic_mode = "TOWER_SELL"
                    ev = ["mode_change","TOWER_SELL"]
                    
                elif event.type == KEYDOWN and event.key == self.keys["construction"]:
                    ev = ["menu_change","construction"]
                elif event.type == KEYDOWN and event.key == self.keys["research"]:
                    ev = ["menu_change","research"]
                elif event.type == KEYDOWN and event.key == self.keys["upgrades"]:
                    ev = ["menu_change","upgrades"]
                elif event.type == KEYDOWN and event.key == self.keys["special"]:
                    ev = ["menu_change","special"]
                
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    ev = ["clic",(self.current_clic_mode,event.pos)]
                elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                    ev = ["rclic",None]
                elif event.type == MOUSEMOTION:
                    ev = ["mouse_move",event.pos]
                elif event.type == KEYDOWN:
                    pgkey = event.key
                    if pgkey in self.touches_boutons:
                        for k in self.keys:
                            if self.keys[k] == pgkey:
                                ev = ["menu_bouton_pressed",int(k[6:])]
                if ev:
                    self.post( ev )
