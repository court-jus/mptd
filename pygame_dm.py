import os, sys, threading, time
import pygame
import pygame.font
from pygame.locals import *
import objects

PATHNAME=os.path.dirname(sys.argv[0])
FULLPATH=os.path.abspath(PATHNAME)
DATAPATH=os.path.join(FULLPATH,"data/")
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GAME_WIDTH = 800
GAME_HEIGHT = 600
TARGET_FPS = 100

TOP_MARGIN = 25
LEFT_MARGIN = 25

COLORBULLE = (253,248,118)

# targets for towers
TAR_NORMAL = 0

class badguy_sprite(pygame.sprite.Sprite):
    def __init__(self,badguy,group = None):
        pygame.sprite.Sprite.__init__(self,group)
        self.model = badguy
        
class tower_sprite(pygame.sprite.Sprite):
    images = [
        ["tower.png"],
        ["tower.png"],
        ["tower.png"],
        ["tower.png"],
        ["tower.png"],
        ["tower.png"],
        ["tower.png"],
    ]
    def __init__(self,tower,group = None):
        pygame.sprite.Sprite.__init__(self,group)
        self.model = tower
        
class bullet_sprite(pygame.sprite.Sprite):
    def __init__(self,bullet,group = None):
        pygame.sprite.Sprite.__init__(self,group)
        self.model = bullet
        
class bouton(pygame.sprite.Sprite):
    
    def __init__(self, dm, event_to_send, tlcorner, image_file, group = None):
        pygame.sprite.Sprite.__init__(self,group)
        self.dm = dm
        self.text = ""
        self.event = event_to_send
        self.img = pygame.image.load(DATAPATH + image_file).convert_alpha()
        self.tlcorner = tlcorner
        self.image =  pygame.Surface((100,120))
        self.rect = self.image.get_rect()
        self.update_text(self.text)
        
    def update_img(self,img):
        self.img = pygame.image.load(DATAPATH + img).convert_alpha()
        
    def update_event(self,event):
        self.event = event
        
    def update_text(self,text):
        self.text = text
        self.image = pygame.Surface((100,120))
        self.rect = self.image.get_rect()
        self.rect.left = self.tlcorner[0]
        self.rect.top = self.tlcorner[1]
        self.image.blit(self.img,(0,0))
        self.font = pygame.font.Font(os.path.join(DATAPATH,"VeraBd.ttf"),12)
        lines = self.text.split("\n")
        h = 72
        for line in lines:
            (width,height) = self.font.size(line)
            decal = (self.rect.width - width) / 2
            text = self.font.render(line,1,(255,255,255))
            self.image.blit(text,(decal,h))
            h+=height
        self.dm.need_update = True
        
class bouton_menu:
    # (35,684)(104,684)
    y = 0
    
    def __init__(self, group = None, dm = None, parent = None):
        self.boutons = {}
        self.boutons_by_num = []
        self.dm = dm
        self.group = group
        self.parent_menu = parent
    
    def add_bouton(self,nom,bouton_img,event):
        x = 80 + 100 * len(self.boutons)
        bt = bouton(self.dm,event,(x,self.y),bouton_img,self.group)
        self.boutons [nom] = bt
        self.boutons_by_num.append(bt)
        return bt
        
    def clic(self,event):
        pos = event[1][1]
        for bt_name in self.boutons:
            bt = self.boutons[bt_name]
            if bt.rect.collidepoint(pos):
                return (bt.event,bt)
            
class build_menu(bouton_menu):
    y = 610
    def __init__(self,group = None, dm = None, parent = None):
        bouton_menu.__init__(self,group,dm,parent)
        bt = self.add_bouton("bg_factory","bouton_B.png","build_badguy_factory")
        bt = self.add_bouton("labo","bouton_L.png","build_laboratory")
        bt = self.add_bouton("build_castle_defense","bouton_tw.png","build_castle_defense")
        bt = self.add_bouton("build_brouzouf_tower","bd_brouzouf_tw.png","build_brouzouf_tower")

class research_menu(bouton_menu):
    y = 610
    def __init__(self,group = None, dm = None, parent = None):
        bouton_menu.__init__(self,group,dm,parent)
        bt = self.add_bouton("research_defensive_castle","bouton_tw.png","research_defensive_castle")
        bt = self.add_bouton("research_special","bouton_S.png","research_special")
        bt = self.add_bouton("research_entry2","bouton_S.png","research_entry2")
        bt = self.add_bouton("research_entry3","bouton_S.png","research_entry3")
        bt = self.add_bouton("research_entry4","bouton_S.png","research_entry4")
        #self.dm.bulle.register(bt,self.dm.cm.game.castle.infobulle("defensive_castle"))

class upgrades_menu(bouton_menu):
    y = 610
    def __init__(self,group = None, dm = None, parent = None):
        bouton_menu.__init__(self,group,dm,parent)
        bt = self.add_bouton("upgrade_bgspeed","bouton_S.png","upgrade_bgspeed")
        bt = self.add_bouton("upgrade_bglife","bouton_L.png","upgrade_bglife")
        bt = self.add_bouton("upgrade_bgbdspeed","bouton_B.png","upgrade_bgbdspeed")
        #bt = self.add_bouton("sell_badguys","brouzouf.png","sell_badguys")
        
class special_menu(bouton_menu):
    y = 610
    def __init__(self,group = None, dm = None, parent = None):
        bouton_menu.__init__(self,group,dm,parent)
        bt = self.add_bouton("special_wave_kamikaze","bouton_K.png","special_wave_kamikaze")
        bt = self.add_bouton("special_wave_para","bouton_P.png","special_wave_para")
        
class main_menu_bouton(bouton):
    
    def __init__(self, dm, event_to_send, tlcorner, image_file, group = None):
    #self, dm, event_to_send, tlcorner, image_file, group = None
        bouton.__init__(self,dm,event_to_send,tlcorner,image_file,group)
        self.image =  self.img
        self.rect = self.image.get_rect()
        self.rect.left = self.tlcorner[0]
        self.rect.top  = self.tlcorner[1]
        
    def update_img(self,img):
        self.img = pygame.image.load(DATAPATH + img).convert_alpha()
        
    def update_event(self,event):
        self.event = event
        
class main_menu(bouton_menu):
    y = 600
    def __init__(self,group = None, dm = None, parent = None):
        bouton_menu.__init__(self,group,dm,parent)
        bt = self.add_bouton("construire","bmm_construire.png","construire")
        bt = self.add_bouton("rechercher","bmm_rechercher.png","rechercher")
        bt = self.add_bouton("ameliorer","bmm_ameliorer.png","ameliorer")
        bt = self.add_bouton("specialiser","bmm_special.png","specialiser")
        
    def add_bouton(self,nom,bouton_img,event):
        x = 1
        y = self.y + (len(self.boutons) + 1) * 30
        bt = main_menu_bouton(self.dm,event,(x,y),bouton_img,self.group)
        self.boutons [nom] = bt
        self.boutons_by_num.append(bt)
        return bt


class mouse_cursor:
    #pygame.mouse.set_cursor(*pygame.cursors.arrow)
    #pygame.mouse.set_cursor(*pygame.cursors.diamond)
    #pygame.mouse.set_cursor(*pygame.cursors.broken_x)
    #pygame.mouse.set_cursor(*pygame.cursors.tri_left)
    #pygame.mouse.set_cursor(*pygame.cursors.tri_right)    
    tc = pygame.cursors.load_xbm("data/mouse_tc.xbm","data/mouse_tc_m.xbm")
    br = pygame.cursors.load_xbm("data/mouse_br.xbm","data/mouse_br_m.xbm")
    tu = pygame.cursors.load_xbm("data/mouse_tu.xbm","data/mouse_tu_m.xbm")

    def __init__ (self, group = None):
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        
    def set_tc(self):
        pygame.mouse.set_cursor(*self.tc)
    
    def set_tu(self):
        pygame.mouse.set_cursor(*self.tu)
        
    def set_select(self):
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)
        
    def set_sell(self):
        pygame.mouse.set_cursor(*self.br)
        
class blackboard(pygame.sprite.Sprite):
    def __init__(self,group = None):
        pygame.sprite.Sprite.__init__(self,group)
        self.image = pygame.Surface((SCREEN_WIDTH - GAME_WIDTH,SCREEN_HEIGHT))
        self.font = pygame.font.Font(os.path.join(DATAPATH,"VeraBd.ttf"),16)
        self.rect = self.image.get_rect()
        self.rect.center = (GAME_WIDTH + (SCREEN_WIDTH - GAME_WIDTH) / 2 , SCREEN_HEIGHT / 2)
        
    def update_text(self,text):
        lines = text.split("\n")
        self.image.fill( (0,0,0) )
        h = 10
        height = self.font.get_height()
        for line in lines:
            test_text = self.font.render(line,1,(255,255,255))
            self.image.blit(test_text,(10,h))
            h += height
            
class gauge(pygame.sprite.Sprite):
    def __init__(self,init_value,final_value,sprite_or_center,group = None):
        pygame.sprite.Sprite.__init__(self,group)
        if isinstance(sprite_or_center,pygame.sprite.Sprite):
            width = sprite_or_center.rect.width * 90/100
            center = sprite_or_center.rect.center
        else:
            width = 30
            center = sprite_or_center
        self.image = pygame.Surface((width, 4))
        self.rect= self.image.get_rect()
        
        self.rect.center = center
        self.image.fill((0,0,0))
        self.ini_val = init_value
        self.fin_val = final_value
        self.update_gauge(init_value)
        
    def update_gauge(self,value):
        w = (value - self.ini_val) * self.rect.width / (self.fin_val - self.ini_val)
        rect = pygame.Rect((1,1),(w,2))
        self.image.fill((0,0,0))
        self.image.fill((255,0,0), rect)
        
class infobulle(pygame.sprite.Sprite):
    def __init__(self,group = None):
        pygame.sprite.Sprite.__init__(self,group)
        self.sprites = []
        self.text = "Passez la souris sur les elements pour avoir de l'aide"
        self.font = pygame.font.Font(os.path.join(DATAPATH,"VeraBd.ttf"),12)
        self.image = pygame.Surface((10,10))
        self.image.fill(COLORBULLE)
        self.rect = self.image.get_rect()
        
    def update_text(self,text,pos):
        self.text = text
        width = 0
        lines = text.split("\n")
        for line in lines:
            test = self.font.size(line)
            if test[0] > width:
                width = test[0]
        h = 0
        height = self.font.get_height()
        self.image = pygame.Surface((width,len(lines) * height))
        self.image.fill( COLORBULLE )
        for line in lines:
            txt = self.font.render(line,1,(0,0,0))
            self.image.blit(txt,(0,h))
            h += height
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        
    def hide(self):
        self.rect.center = (2000,2000)
        
    def register(self,sprite,text):
        self.sprites.append([sprite,text])
        
class pygame_dm:#(threading.Thread):
    def __init__(self, control, fullscreen = False, single_player = False):
        #threading.Thread.__init__(self)
        #self._stopevent = threading.Event()
        
        self.display = mydisplay(self)
        
        self.cm = control
        self.cm.register(self)
        #self.stuff    =    []        # that will be the list of the stuff we will have to display
        self.boutons = []
        self.need_update =      True
        self.debuging  = True
        self.single_player = single_player
        pygame.init ()

        if fullscreen:
            flags = pygame.FULLSCREEN
        else:
            flags = 0
        self.window = pygame.display.set_mode( (SCREEN_WIDTH,SCREEN_HEIGHT),flags)
        pygame.display.set_caption( 'MultiPlayerTowerDefense' )
        self.background = pygame.image.load(DATAPATH + "background.png")
        #self.background.fill( (0,0,0) )
        pygame.display.get_surface().blit(self.background,(0,0))
        pygame.display.update()

        self.topsprites = pygame.sprite.RenderUpdates()
        self.frontsprites = pygame.sprite.RenderUpdates()
        self.towersprites = pygame.sprite.RenderUpdates()
        self.badguysprites = pygame.sprite.RenderUpdates()
        self.backsprites  = pygame.sprite.RenderUpdates()
        self.bmsprites  = pygame.sprite.RenderUpdates() # sprites for the build menu
        self.rmsprites  = pygame.sprite.RenderUpdates() # sprites for the research menu
        self.umsprites  = pygame.sprite.RenderUpdates() # sprites for the upgrades_menu
        self.mmsprites =  pygame.sprite.RenderUpdates() # sprites for the main_menu
        self.smsprites =  pygame.sprite.RenderUpdates() # sprites for the special_menu
        
        self.mouse_cursor = mouse_cursor()
        self.selected_stuff = None
        self.bb = blackboard(self.backsprites)
        self.message = "begin !"
        
        #self.bulle = infobulle(self.topsprites)
        #self.bulle.hide()
        
        self.main_menu = main_menu(self.mmsprites,self,None)
        self.build_menu = build_menu(self.bmsprites,self,None)
        self.research_menu = research_menu(self.rmsprites,self,None)
        self.research_menu_available = False
        self.upgrades_menu = upgrades_menu(self.umsprites,self,None)
        self.upgrades_menu_available = False
        self.special_menu = special_menu(self.smsprites,self,None)
        self.special_menu_available = False
        self.menu = self.build_menu
        
        #self.display.start()
        
        
    def update_bb(self,message = None):
        if message:
            self.message = message
        string = ""
        string += """MPTD\n\nVies :"""
        string += str(self.cm.game.castle.lifes)
        if self.single_player:
            string += """\n\nProchaine vague :"""
            string += str(20 - self.cm.game.castle.get_badguys_ready())
        else:
            string += """\n\nMechants prets :"""
            string += str(self.cm.game.castle.get_badguys_ready())
        string += """\n\nBrouzoufs :"""
        string += str(self.cm.game.castle.money)
	#if self.cm.game.single_player:
        string += """\n\nVictimes :"""
        string += str(self.cm.game.level - 1)
        if self.message:
            string += """\n\n""" + self.message
        if self.cm.game.enemy_info and len(self.cm.game.enemy_info) > 0:
            string += "\n\nInfo Ennemi :"
            for info_name in self.cm.game.enemy_info:
                string += "\n" + info_name + " : " + str(self.cm.game.enemy_info[info_name])
        self.bb.update_text(string);
        self.need_update = True
        

    def notify(self,event):
        if event [0] == "quit_game":
            pygame.display.quit()
        elif event [0] == "toggle_fullscreen":
            pygame.display.toggle_fullscreen()
        elif (event [0] == "menu_change" and event [1] == "construction") or event [0] == "construire":
            #self.cm.post(("mode_change","TOWER_CREATE"))
            self.menu = self.build_menu
            self.need_update = True
        elif ((event [0] == "menu_change" and event [1] == "research") or event [0] == "rechercher") and self.research_menu_available:
            #self.cm.post(("mode_change","SELECT"))
            self.menu = self.research_menu
            self.need_update = True
        elif ((event [0] == "menu_change" and event [1] == "upgrades") or event [0] == "ameliorer") and self.upgrades_menu_available:
            #self.cm.post(("mode_change","TOWER_UPGRADE"))
            self.menu = self.upgrades_menu
            self.need_update = True
        elif ((event [0] == "menu_change" and event [1] == "special") or event [0] == "specialiser") and self.special_menu_available:
            #self.cm.post(("mode_change","TOWER_SELL"))
            self.menu = self.special_menu
            self.need_update = True
        elif event [0] == "mode_change":
            if event [1] == "TOWER_CREATE":
                self.mouse_cursor.set_tc()
            elif event [1] == "TOWER_UPGRADE":
                self.mouse_cursor.set_tu()
            elif event [1] == "SELECT" :
                self.mouse_cursor.set_select()
            elif event [1] == "TOWER_SELL" :
                self.mouse_cursor.set_sell()
            self.need_update = True
        elif event [0] == "clic":
            ev = self.menu.clic(event)
            if ev:
                self.cm.post(ev)
            ev = self.main_menu.clic(event)
            if ev:
                #print "main menu sent",ev
                self.cm.post(ev)
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
                self.cm.post((bt.event,bt))
        elif event [0] == "badguy_count_update":
            b = event [1]
            self.update_bb()
        elif event [0] == "level_up":
            self.update_bb()
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
                
    #def stop(self):
        #self._stopevent.set()
    
    def destroy_stuff(self,stuff):
        stuff.kill()
                
    def create_gauge(self,init_value,final_value,stuff):
        sprite = stuff
        if not sprite:
            sprite = (GAME_WIDTH/2,GAME_HEIGHT/2)
        g = gauge(init_value,final_value,sprite,self.topsprites)
        self.need_update = True
        return g

    def debug(self,string):
        if self.debuging:
            print "DEBUG : " + string
        #self.bulle.update_text(string,(0,0))

    def create_bullet(self,tower,badguy):
    	bul = objects.bullet(self,tower,badguy,self.towersprites)
        bul.speed = badguy.speed * 2
        bul.power = tower.power
        bul.visual_coord = tower.visual_coord[:]
        self.need_update = True
        return bul
    
    def create_badguy(self):
        bg = objects.badguy(self,self.cm,self.badguysprites)
        return bg
    
    def create_tower(self,twclass):
        tw = twclass(self,self.cm,self.towersprites)
        self.update_bb()
        self.need_update = True
        return tw

    def update(self):
        self.towersprites.update()
        self.badguysprites.update()
        self.bmsprites.update()
        self.rmsprites.update()
        self.umsprites.update()
        self.mmsprites.update()
        self.smsprites.update()

    def draw(self):
        self.cm.handle_pygame_events()
        """ draw the game to the screen """
        now = pygame.time.get_ticks()
        if not self.need_update:
            return
        try:
                
            self.backsprites.clear  (self.window, self.background)
            self.towersprites.clear  (self.window, self.background)
            self.badguysprites.clear  (self.window, self.background)
            self.frontsprites.clear (self.window, self.background)
            self.bmsprites.clear (self.window, self.background)
            self.rmsprites.clear (self.window, self.background)
            self.umsprites.clear (self.window, self.background)
            self.mmsprites.clear (self.window, self.background)
            self.smsprites.clear (self.window, self.background)
            self.topsprites.clear (self.window, self.background)
            
            dirty = []
            
            for sprite in self.rmsprites.sprites() + self.bmsprites.sprites() + self.umsprites.sprites():
                dirty.append(pygame.Rect(sprite.rect))
    
            dirty += self.backsprites.draw (self.window)
            dirty += self.towersprites.draw (self.window)
            dirty += self.badguysprites.draw (self.window)
            dirty += self.frontsprites.draw (self.window)
            dirty += self.mmsprites.draw (self.window)
            if self.menu == self.build_menu:
                dirty += self.bmsprites.draw (self.window)
            elif self.menu == self.research_menu:
                dirty += self.rmsprites.draw(self.window)
            elif self.menu == self.upgrades_menu:
                dirty += self.umsprites.draw(self.window)
            elif self.menu == self.special_menu:
                dirty += self.smsprites.draw(self.window)
            dirty += self.topsprites.draw (self.window)
            pygame.display.update (dirty)
            self.need_update = False
        except:
            pass


class mydisplay(threading.Thread):
    def __init__(self,dm):
        threading.Thread.__init__(self)
        
        self.dm = dm
        self.clock = pygame.time.Clock()
        self._stopevent = threading.Event()
        
    def run(self):
        while not self._stopevent.isSet():
            self.dm.draw()
            self.clock.tick(TARGET_FPS)
            pygame.time.wait(0)
            
    def stop(self):
        self._stopevent.set()
