# -*- coding: utf-8 -*-
from livewires import games
from livewires import colour
from mptd import mptd
from gamemenu import main_menu, build_menu, research_menu, upgrades_menu, special_menu
import pygame
import os, sys

PATHNAME=os.path.dirname(sys.argv[0])
FULLPATH=os.path.abspath(PATHNAME)
DATAPATH=os.path.join(FULLPATH,"data/")
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GAME_WIDTH = 800
GAME_HEIGHT = 600

class MptdScreen(games.Screen):
    def __init__(self, settings):
        games.Screen.__init__(self, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.set_background(pygame.image.load(DATAPATH + "background.png"))
        games.pygame.display.set_caption('MPTD | By Ghislain Lévêque')
        self.model = self.main_menu = self.build_menu = self.research_menu = self.upgrades_menu = self.special_menu = None
        self.blackboard = BlackBoard(self)
        self.model = mptd(self, settings)
        self.update_bb()

        self.main_menu = main_menu(None,self,None)
        self.build_menu = build_menu(None,self,None)
        self.research_menu = research_menu(None,self,None)
        self.research_menu_available = False
        self.upgrades_menu = upgrades_menu(None,self,None)
        self.upgrades_menu_available = False
        self.special_menu = special_menu(None,self,None)
        self.special_menu_available = False
        self.menu = self.build_menu

        self.tick_listeners = []

    def tick(self):
        self.model.tick()
        for listener in self.tick_listeners:
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

class BlackBoard(games.Object):
    def __init__(self, screen):
        surface = pygame.Surface((SCREEN_WIDTH - GAME_WIDTH,SCREEN_HEIGHT))
        self.font = pygame.font.Font(os.path.join(DATAPATH,"VeraBd.ttf"),16)
        games.Object.__init__(self, screen, 800, 20, surface)
        
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

    def update_bb(self, message = None):
        print "Update BB : %s" % message
        if message:
            self.message = message
        # Unless the game is initialized, don't go farther
        if not self.screen.model:
            return
        string = ""
        string += """MPTD\n\nVies :"""
        string += str(self.screen.model.castle.lifes)
        if self.screen.model.single_player:
            string += """\n\nProchaine vague :"""
            string += str(20 - self.screen.model.castle.get_badguys_ready())
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
        self.need_update = True
        
