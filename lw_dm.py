# -*- coding: utf-8 -*-
from livewires import games
from livewires import colour
from mptd import mptd
from gamemenu import main_menu, build_menu, research_menu, upgrades_menu, special_menu
import pygame
import os, sys
import objects

PATHNAME=os.path.dirname(sys.argv[0])
FULLPATH=os.path.abspath(PATHNAME)
DATAPATH=os.path.join(FULLPATH,"data/")
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GAME_WIDTH = 800
GAME_HEIGHT = 600

class MptdScreen(games.Screen):
    def __init__(self, settings):
        super(MptdScreen, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.shadow = None
        self.set_background(pygame.image.load(DATAPATH + "background.png"))
        games.pygame.display.set_caption('MPTD | By Ghislain Lévêque')
        self.model = self.main_menu = self.build_menu = self.research_menu = self.upgrades_menu = self.special_menu = None
        self.blackboard = BlackBoard(self)
        self.model = mptd(self, settings)
        self.update_bb()

        self.menu = None
        self.main_menu = main_menu(self)
        self.build_menu = build_menu(self)
        self.research_menu = research_menu(self)
        self.upgrades_menu = upgrades_menu(self)
        self.special_menu = special_menu(self)
        self.research_menu_available = self.upgrades_menu_available = self.special_menu_available = False
        self.main_menu.show()
        self.select_menu(self.build_menu)
        self.model.castle.update_boutons_text(True)

        self.tick_listeners = []

    def select_menu(self, new_menu):
        print "sleect menu",new_menu
        if self.menu:
            self.menu.hide()
        self.menu = new_menu
        self.menu.show()

    def tick(self):
        self.model.tick()
        for listener in self.tick_listeners:
            if hasattr(listener, '_gone') and listener._gone == 1:
                self.tick_listeners.remove(listener)
            else:
                listener.update()

    def handle_events (self):
        if not self.model:
            return
        return self.model.cm.handle_pygame_events()
        events = pygame.event.get ()
        for event in events:
            if event.type == QUIT:
                self.quit ()
            elif event.type == KEYDOWN:
                self.keypress (event.key)
            elif event.type == MOUSEBUTTONUP:
                self.mouse_up (event.pos, event.button-1)
            elif event.type == MOUSEBUTTONDOWN:
                self.mouse_down (event.pos, event.button-1)

    def update_bb(self, message = None):
        self.blackboard.update_bb(message)

    def create_badguy(self):
        bg = objects.badguy(self,self.model.cm)
        self.tick_listeners.append(bg)
        return bg
    
    def create_tower(self, twclass):
        tw = twclass(self,self.model.cm)
        self.update_bb()
        self.tick_listeners.append(tw)
        return tw

    def create_bullet(self,tower,badguy):
    	bul = objects.bullet(self,tower,badguy)
        bul.speed = badguy.speed * 2
        bul.power = tower.power
        bul.visual_coord = tower.visual_coord[:]
        self.tick_listeners.append(bul)
        return bul

    def create_gauge(self,init_value,final_value,stuff):
        attach_point = stuff
        if not attach_point:
            attach_point = (GAME_WIDTH/2,GAME_HEIGHT/2)
        g = objects.gauge(self, init_value, final_value, attach_point)
        self.need_update = True
        return g

    def remove_shadow(self):
        if not self.shadow:
            return
        self.shadow.kill()
        self.shadow = None
    
    def notify(self, event):
        if event[0] != "mouse_move":
            print "notify event",event
        if event [0] == "toggle_fullscreen":
            pygame.display.toggle_fullscreen()
        elif event [0] == "badguy_count_update":
            self.update_bb()
        elif event [0] == "level_up":
            self.update_bb()
        elif event [0] == "clic":
            ev = self.menu.clic(event)
            if ev:
                print "current menu sent",ev
                self.model.cm.post(ev)
            ev = self.main_menu.clic(event)
            if ev:
                print "main menu sent",ev
                self.model.cm.post(ev)
        elif event [0] == "mode_change":
            if event [1] == "TOWER_CREATE":
                # TODO mouse cursor self.mouse_cursor.set_tc()
                if not self.shadow:
                    self.shadow = objects.shadow(self, self.model.cm)
                self.blackboard.update_mode('CREATE')
            elif event [1] == "TOWER_UPGRADE":
                # TODO mouse cursor self.mouse_cursor.set_tu()
                self.remove_shadow()
                self.blackboard.update_mode('UPGRADE')
            elif event [1] == "SELECT" :
                # TODO mouse cursor self.mouse_cursor.set_select()
                self.remove_shadow()
                self.blackboard.update_mode('SELECT')
            elif event [1] == "TOWER_SELL" :
                # TODO mouse cursor self.mouse_cursor.set_sell()
                self.remove_shadow()
                self.blackboard.update_mode('SELL')
        elif (event [0] == "menu_change" and event [1] == "construction") or event [0] == "construire":
            #self.model.cm.post(("mode_change","TOWER_CREATE"))
            self.select_menu(self.build_menu)
        elif ((event [0] == "menu_change" and event [1] == "research") or event [0] == "rechercher") and self.research_menu_available:
            #self.model.cm.post(("mode_change","SELECT"))
            self.select_menu(self.research_menu)
        elif ((event [0] == "menu_change" and event [1] == "upgrades") or event [0] == "ameliorer") and self.upgrades_menu_available:
            #self.model.cm.post(("mode_change","TOWER_UPGRADE"))
            self.select_menu(self.upgrades_menu)
        elif ((event [0] == "menu_change" and event [1] == "special") or event [0] == "specialiser") and self.special_menu_available:
            #self.model.cm.post(("mode_change","TOWER_SELL"))
            self.select_menu(self.special_menu)
        return
        if False:
            pass
        #elif event [0] == "mouse_move":
            #found = None
            #for bulle_sprite in self.bulle.sprites:
                #if bulle_sprite[0] in self.menu.boutons:
                    #if bulle_sprite[0].rect.collidepoint(event [1]):
                        #self.bulle.update_text(bulle_sprite[1],event[1])
                        #found = True
            #if not found:
                #self.bulle.hide()
        elif event [0] == "menu_bouton_pressed":
            if event [1] <= (len(self.menu.boutons)):
                btnum = event [1] - 1
                bt = self.menu.boutons_by_num[btnum]
                self.model.cm.post((bt.event,bt))
        elif event [0] == "select_stuff":
            stuff = event [1]
            if stuff and hasattr(stuff,"selectable"):
                if self.selected_stuff:
                    self.selected_stuff.image = self.selected_stuff.image_save.copy()
                    self.selected_stuff.selected = False
                stuff.selected = True
                stuff.image.fill((255,0,0))
                stuff.image.blit(stuff.image_save,(0,0))
                self.selected_stuff = stuff
                self.update_bb(str(stuff.get_info()))

    def debug(self, *args, **kwargs):
        print "DEBUG",args,kwargs

class BlackBoard(games.Object):
    def __init__(self, screen):
        surface = pygame.Surface((SCREEN_WIDTH - GAME_WIDTH,SCREEN_HEIGHT))
        self.font = pygame.font.Font(os.path.join(DATAPATH,"VeraBd.ttf"),16)
        self.mode = 'MPTD'
        super(BlackBoard, self).__init__(screen, 800, 20, surface)
        
    def update_text(self,text):
        lines = text.split("\n")
        #self._surface.fill( (0,0,0) )
        surface = pygame.Surface((SCREEN_WIDTH - GAME_WIDTH,SCREEN_HEIGHT))
        self._erase()
        h = 10
        height = self.font.get_height()
        for line in lines:
            test_text = self.font.render(line,1,(255,255,255))
            surface.blit(test_text,(10,h))
            h += height
        self.replace_image(surface)

    def update_mode(self, mode):
        self.mode = mode
        self.update_bb()

    def update_bb(self, message = None):
        if message:
            self.message = message
        elif message is not None:
            self.message = ""
        # Unless the game is initialized, don't go farther
        if not self.screen.model:
            return
        string = ""
        string += """%s\n\nVies :""" % (self.mode,)
        string += str(self.screen.model.castle.lifes)
        if self.screen.model.single_player:
            string += """\n\nProchaine vague :"""
        else:
            string += """\n\nMechants prets :"""
        string += str(self.screen.model.castle.get_badguys_ready())
        string += """\n\nBrouzoufs :"""
        string += str(self.screen.model.castle.money)
        string += """\n\nVictimes :"""
        string += str(self.screen.model.level - 1)
        if self.message:
            string += """\n\n""" + self.message
        if self.screen.model.enemy_info and len(self.screen.model.enemy_info) > 0:
            string += "\n\nInfo Ennemi :"
            for info_name in self.screen.model.enemy_info:
                string += "\n" + info_name + " : " + str(self.screen.model.enemy_info[info_name])
        self.update_text(string);
        
