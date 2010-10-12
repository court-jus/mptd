# -*- coding: utf-8 -*-
from livewires import games
import pygame
import os, sys

PATHNAME=os.path.dirname(sys.argv[0])
FULLPATH=os.path.abspath(PATHNAME)
DATAPATH=os.path.join(FULLPATH,"data/")
        
class bouton(games.Sprite):
    
    def __init__(self, dm, event_to_send, tlcorner, image_file, hidden = True):
        self.dm = dm
        self.tlcorner = tlcorner
        self.hiddentl = (-1000, -1000)
        self.text = ""
        self.event = event_to_send
        self.img = pygame.image.load(DATAPATH + image_file).convert_alpha()
        self.image =  pygame.Surface((100,120))
        self.update_text(self.text)
        super(bouton, self).__init__(dm, tlcorner[0], tlcorner[1], self.image)
        if hidden:
            self.hide()
        
    def update_img(self,img):
        self.img = pygame.image.load(DATAPATH + img).convert_alpha()
        
    def update_event(self,event):
        self.event = event
        
    def update_text(self,text):
        self.text = text
        self.image = pygame.Surface((100,120))
        self.image.blit(self.img,(0,0))
        self.font = pygame.font.Font(os.path.join(DATAPATH,"VeraBd.ttf"),12)
        lines = self.text.split("\n")
        h = 72
        for line in lines:
            (width,height) = self.font.size(line)
            #decal = (self.rect.width - width) / 2
            text = self.font.render(line,1,(255,255,255))
            #self.image.blit(text,(decal,h))
            h+=height

    def show(self):
        self.move_to(self.tlcorner)

    def hide(self):
        self._erase()
        self.move_to(self.hiddentl)
        
class bouton_menu(object):
    # (35,684)(104,684)
    y = 670
    
    def __init__(self, dm = None, parent = None, hidden = True):
        self.boutons = {}
        self.boutons_by_num = []
        self.dm = dm
        self.parent_menu = parent
        self.hidden = hidden
    
    def add_bouton(self,nom,bouton_img,event):
        x = 150 + 100 * len(self.boutons)
        bt = bouton(self.dm,event,(x,self.y),bouton_img)
        self.boutons [nom] = bt
        self.boutons_by_num.append(bt)
        if self.hidden:
            bt.hide()
        return bt
        
    def clic(self,event):
        pos = event[1][1]
        for bt_name in self.boutons:
            bt = self.boutons[bt_name]
            if bt._rect.collidepoint(pos):
                return (bt.event,bt)

    def show(self):
        self.hidden = False
        for bt in self.boutons.values():
            bt.show()
            
    def hide(self):
        self.hidden = True
        for bt in self.boutons.values():
            bt.hide()

class build_menu(bouton_menu):
    def __init__(self,dm = None, parent = None, hidden = True):
        super(build_menu, self).__init__(dm, parent, hidden)
        bt = self.add_bouton("bg_factory","bouton_B.png","build_badguy_factory")
        bt = self.add_bouton("labo","bouton_L.png","build_laboratory")
        bt = self.add_bouton("build_castle_defense","bouton_tw.png","build_castle_defense")
        bt = self.add_bouton("build_brouzouf_tower","bd_brouzouf_tw.png","build_brouzouf_tower")

class research_menu(bouton_menu):
    def __init__(self,dm = None, parent = None, hidden = True):
        super(research_menu, self).__init__(dm, parent, hidden)
        bt = self.add_bouton("research_defensive_castle","bouton_tw.png","research_defensive_castle")
        bt = self.add_bouton("research_special","bouton_S.png","research_special")
        bt = self.add_bouton("research_entry2","bouton_S.png","research_entry2")
        bt = self.add_bouton("research_entry3","bouton_S.png","research_entry3")
        bt = self.add_bouton("research_entry4","bouton_S.png","research_entry4")
        #self.dm.bulle.register(bt,self.dm.cm.game.castle.infobulle("defensive_castle"))

class upgrades_menu(bouton_menu):
    def __init__(self,dm = None, parent = None, hidden = True):
        super(upgrades_menu, self).__init__(dm, parent, hidden)
        bt = self.add_bouton("upgrade_bgspeed","bouton_S.png","upgrade_bgspeed")
        bt = self.add_bouton("upgrade_bglife","bouton_L.png","upgrade_bglife")
        bt = self.add_bouton("upgrade_bgbdspeed","bouton_B.png","upgrade_bgbdspeed")
        #bt = self.add_bouton("sell_badguys","brouzouf.png","sell_badguys")
        
class special_menu(bouton_menu):
    def __init__(self,dm = None, parent = None, hidden = True):
        super(special_menu, self).__init__(dm, parent, hidden)
        bt = self.add_bouton("special_wave_kamikaze","bouton_K.png","special_wave_kamikaze")
        bt = self.add_bouton("special_wave_para","bouton_P.png","special_wave_para")
        
class main_menu_bouton(bouton):
    
    def __init__(self, dm, event_to_send, tlcorner, image_file, hidden = True):
        super(main_menu_bouton, self).__init__(dm, event_to_send, tlcorner, image_file, hidden)
        self.image =  self.img
        
    def update_img(self,img):
        self.img = pygame.image.load(DATAPATH + img).convert_alpha()
        
    def update_event(self,event):
        self.event = event
        
class main_menu(bouton_menu):
    y = 640
    def __init__(self, dm = None, parent = None, hidden = True):
        super(main_menu, self).__init__(dm, parent, hidden)
        bt = self.add_bouton("construire","bmm_construire.png","construire")
        bt = self.add_bouton("rechercher","bmm_rechercher.png","rechercher")
        bt = self.add_bouton("ameliorer","bmm_ameliorer.png","ameliorer")
        bt = self.add_bouton("specialiser","bmm_special.png","specialiser")
        
    def add_bouton(self,nom,bouton_img,event):
        x = 60
        y = self.y + (len(self.boutons) + 1) * 30
        bt = main_menu_bouton(self.dm,event,(x,y),bouton_img)
        self.boutons [nom] = bt
        self.boutons_by_num.append(bt)
        return bt

