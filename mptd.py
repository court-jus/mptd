# -*- coding: utf-8 -*-
import castle, calcul_dij
import pygame_dm, cm, nm
import pygame
import objects
#import globals
import random, os, sys, getopt, time
import AStar
import menu
import shelve
from pygame.locals import *
from livewires import games

ECART_MIN_ENTRE_BG = 150    # ms between two badguys
ECART_MIN_ENTRE_VAGUES = 30000    # ms between two forced waves
TEST = True

class mptd:
    """ this is the main class for mptd """

    def __init__(self, screen, settings): #serveur_hostname,serveur_port,single_player,fullscreen):
        #pygame.init()
        self.settings = settings # server_ip,server_port,fullscreen,solo
        #print self.settings
        self.mapw       =   80
        self.maph       =   60
        self.mapdata    =   [1 for i in range(self.mapw*self.maph)]      # only used for obstacles
        self.entries = [(0,0),(0,self.maph - 1),(self.mapw - 1,0),(self.mapw - 1,self.maph - 1)]
        self.castlex = 40
        self.castley = 30
        self.last_bg_sent = 0
        self.last_wave_sent = 0
        #for x in range(37,44):
            #for y in range(27,34):
                #self.mapdata[x + y * self.mapw] = 9
        now = pygame.time.get_ticks
        self.calcul = calcul_dij.calcul_dij(self.mapdata,self.mapw,self.maph,(self.castlex,self.castley))
        #p = self.calcul.calcul_unique((0,0),(40,30))
        #self.calcul.starting_path = self.make_road_from_path(p)
        self.single_player = settings["solo"]
        self.enemy_info = {}
        self.level = 1
        self.current_tower_creation_mode = objects.basic_tower
        self.cm        = cm.cm (self.settings["keys"],self.settings["touches_boutons"])            # create a new control manager
        self.cm.register_game (self)                # register self to cm        
        #self.dm        = pygame_dm.pygame_dm (self.cm, settings["fullscreen"], self.single_player)        # create a new display manager
        self.dm = screen
        self.castle = castle.castle(self.cm, self.single_player)
        if self.single_player:
            self.castle.update_boutons_text()
            print "TODO : update_bb"
            #self.dm.update_bb(message = "Bienvenue dans le mode solo")
        self.nm = None
        if self.settings["server_ip"] and not self.single_player:
            print "Connecting to serveur",self.settings["server_ip"],"on port",self.settings["server_port"]
            self.nm        = nm.nm (self.cm,self.settings["server_ip"],self.settings["server_port"])
            self.nm.start ()
            while not self.nm.connected:
                print "waiting for the connexion"
                time.sleep(1)
        self.last_cputick = 0

        self.waves = []
        self.colors = [ (255,128,128), (128,255,128), (128,128,255) ]

        self.towers    = []
        self.badguys    = []
        self.objects    = [self.towers , self.badguys]
        
                
                
        self.current_wave = {
            "number":   0,
            "life"  :   None,
            "speed" :   None,
            "special" : None,
            "coord" : (0,0),
            }
        self.calcul.daemon = True
        self.calcul.start()
        #print self.calcul.starting_path
        self.update_road = False
        self.cm.post(["mode_change","SELECT"])
        #self.road = self.find_road(self.mapdata[:])              # the "road" is the shortest path from (0,0) to the castle (this road must be kept open)
#        self.castle.build("badguy_factory",1000,0.1,castle.badguy_factory)
        
    def run(self):
        #self.dm.display.start()     # draw to screen in a thread
        self.mainloop()
        
    def make_text(self,stuff_type,stuff):
        l = False
        c = False
        if hasattr(self,"castle"):
            c = self.castle
            l = self.castle.has_building(castle.laboratory)
        if stuff_type == "research":
            text = str(castle.laboratory.technos_names[stuff]) + "\n"
            if l and stuff in l.science:
                text += "OK"
                return text
            text += str(castle.laboratory.technos[stuff][0]) + "\n"
            for need in castle.laboratory.technos[stuff][1]:
                if not l or need not in l.science:
                    text += castle.laboratory.technos_names[need] + " "
            for need in castle.laboratory.technos[stuff][2]:
                if not c or not c.has_building(need):
                    text += need.name + " "
        elif stuff_type == "building":
            text = str(castle.castle.known_buildings[stuff][5]) + "\n"
            if c and c.has_building(castle.castle.known_buildings[stuff][4]):
                text += "OK"
                return text
            text += str(castle.castle.known_buildings[stuff][0]) + "\n"
            for need in castle.castle.known_buildings[stuff][3]:
                if not l or need not in l.science:
                    text += castle.laboratory.technos_names[need] + " "
            for need in castle.castle.known_buildings[stuff][2]:
                if not c or not c.has_building(need):
                    text += need.name + " "
        return text

    def tick(self):
        #self.dm.update_bb()

        now = pygame.time.get_ticks()
        b = self.castle.has_building(castle.badguy_factory)
        self.dm.update()        # update sprites (badguys, towers...)
        self.castle.update()
        if self.current_wave["number"] > 0 and now > self.last_bg_sent + ECART_MIN_ENTRE_BG:
            self.last_bg_sent = now
            self.send_badguys(0,True)
        elif len(self.waves) > 0:
            self.current_wave = self.waves.pop(0)
            self.colors.append(self.colors.pop(0)) # rotation des couleurs
        if now > self.last_wave_sent + ECART_MIN_ENTRE_VAGUES and b and b.badguys_ready >= 20:
            self.cm.post(("send_badguys",None))
        if self.castle.lifes <= 0:
            self.cm.post(["quit_game",None])
        
    def make_road_from_path(self,ASPath):
        road = []
        for node in ASPath.getNodes():
            road.append(node.location.x + node.location.y * self.mapw)
        return road
        
    def notify(self,event):
        if event [0] == "badguy_die":
            #if self.single_player:
            self.level += 1
            self.cm.post(("level_up",self.level))
            self.castle.modify_money(max((self.level / 25),1))
            self.dm.update_bb()
            if not self.single_player:
                bg = event[1]
                income = int((pygame.time.get_ticks() - bg.birth) / (1000))
                self.nm.send(":earn_money " + str(income) + ":")
            try:
                self.badguys.remove (event [1])
            except:
                pass
        elif event [0] == "quit_game":
            self.running = False
            if self.nm:
                self.nm.stop()
            #if self.calcul:
                #self.calcul.stop()
            if self.dm and hasattr(self.dm.display,"stop"):
                self.dm.display.stop()
        elif event [0] == "clic":
            if event[1][0] == "TOWER_CREATE":
                if self.castle.money >= self.current_tower_creation_mode.cost:
                    self.create_tower(event[1][1])
            elif event[1][0] == "SELECT":
                self.select_stuff(event[1][1])
            elif event[1][0] == "TOWER_UPGRADE":
                tw = self.select_stuff(event[1][1])
                if isinstance(tw, objects.tower):
                    tw.upgrade()
            elif event[1][0] == "TOWER_SELL":
                tw = self.select_stuff(event[1][1])
                if isinstance(tw, objects.tower):
                    tw.sell()
        elif event [0] == "send_badguys":
            b = self.castle.has_building(castle.badguy_factory)
            if b:
                numb = b.badguys_ready
                if numb > 0:
                    l = self.castle.has_building(castle.laboratory) 
                    entry_num = 1
                    if l:
                        for sc in l.science:
                            if sc[:5] == "entry":
                                entry_num += 1
                    coord = self.entries [random.randrange(entry_num)]
                    if self.single_player:
                        wave = {
                            "number" : numb,
                            "life" : b.badguys_life,
                            "speed" : b.badguys_speed,
                            "special" : None,
                            "coord" : coord,
                            }
                        self.waves.append(wave)
                    else:
                        self.nm.send(":send_badguys " + str(numb) + " " + str(b.badguys_life) + " " + str(b.badguys_speed) + " None " + str(coord[0]) + " " + str(coord[1]) + ":")
                    b.badguys_ready = 0
                    self.cm.post(["badguy_count_update",b])
        elif event [0] == "launch wave":
            #print "preparing to launch wave"
            wave_type = event[1][0]
            bgnum = event[1][1]
            b = self.castle.has_building(castle.badguy_factory)
            l = self.castle.has_building(castle.laboratory) 
            entry_num = 1
            if l:
                for sc in l.science:
                    if sc[:5] == "entry":
                        entry_num += 1
            coord = self.entries [random.randrange(entry_num)]
            if self.single_player:
                wave = {
                    "number" : bgnum,
                    "life" : b.badguys_life,
                    "speed" : b.badguys_speed,
                    "special" : wave_type,
                    "coord" : coord,
                    }
                self.waves.append(wave)
            else:
                self.nm.send(":send_badguys " + str(bgnum) + " " + str(b.badguys_life) + " " + str(b.badguys_speed) + " " + wave_type + " " + str(coord[0]) + " " + str(coord[1]) + ":")
        elif event [0] == "network_recv":
            self.parse_and_execute_nw_order(event[1])
        elif event [0] == "castle_defense_built":
            self.current_tower_creation_mode = objects.castle_tower
            self.create_tower((400,300),False)
            self.current_tower_creation_mode = objects.basic_tower
        elif event [0] == "brouzouf_tower_building_built":
            self.current_tower_creation_mode = objects.brouzouf_tower
            self.create_tower((820,620),False)
            self.current_tower_creation_mode = objects.basic_tower
            
    def send_badguys(self,bg_numb,cont = False):
        self.current_wave["number"] -= 1
        self.create_badguy(self.current_wave["coord"],self.current_wave["life"],self.current_wave["speed"],self.current_wave["special"])
        
    def select_stuff(self,coord):
        dist = 50
        selected_stuff = None
        for stuff_cat in self.objects:
            for stuff in stuff_cat:
                distance = ((stuff.visual_coord[0] - coord[0])**2.0 + (stuff.visual_coord[1] - coord[1])**2.0)**(1.0/2.0)
                if distance < dist:
                    dist = distance
                    selected_stuff = stuff
        self.cm.post(("select_stuff",selected_stuff))
        return selected_stuff

    def parse_and_execute_nw_order(self,nwstr):
        #print "received nw order:",nwstr
        orders = nwstr.split(":")
        #print "splitted :",orders
        for nwor in orders:
            #print "PARSING",nwor
            order = nwor.split(" ")
            #print "nwor splitted : ",order
            #print "[" + order[0] + "]"
            if order [0] == "send_badguys":
                wave = {
                    "number" : int(order[1]),
                    "life"   : float(order[2]),
                    "speed"  : float(order[3]),
                    "special" : order[4],
                    "coord" : (int(order[5]),int(order[6])),
                    }
                self.waves.append(wave)
            elif order [0] == "earn_money":# 10 *level
                income = int(order [1])
                if len(order) > 2:
                    if order [2] == "*level":
                        income *= self.level
                self.castle.modify_money(income)
                self.dm.update_bb()
            elif order [0] == "mylife":
                self.enemy_info["life"] = int(order[1])
                self.dm.update_bb()

    def append_obstacle(self,obstacle):
        ox = obstacle.coord[0]
        oy = obstacle.coord[1]
        size = ((obstacle.size - 1)) - 1
        position = ox + oy * self.mapw
        self.mapdata[position] = -1
        for a in range(size + 1):
            self.mapdata[position + size + a * self.mapw] = -1
            self.mapdata[position - size + a * self.mapw] = -1
            self.mapdata[position + size - a * self.mapw] = -1
            self.mapdata[position - size - a * self.mapw] = -1
            self.mapdata[position - a - size * self.mapw] = -1
            self.mapdata[position + a - size * self.mapw] = -1
            self.mapdata[position - a + size * self.mapw] = -1
            self.mapdata[position + a + size * self.mapw] = -1
        #if self.update_road:
            #self.road = self.find_road(self.mapdata)
            #self.update_road = False
    
    def create_badguy(self,coord,life,speed,special = None):
        #print "creating a badguy at",coord,"with",life,"life and",speed,"speed"
        b = self.castle.has_building(castle.badguy_factory)
        bg = self.dm.create_badguy()
        bg.life = life
        bg.full_life = life
        bg.speed = speed
        bg.color = self.colors[0]
        if special:
            bg.special = special
        bg.coord = (coord [0], coord[1])
        if bg.special == "para":
            ok = False
            while not ok:
                bg.coord = (random.randrange(self.mapw - 10) + 5, random.randrange(self.maph - 10) + 5)
                if self.mapdata[bg.coord[0]%80 + bg.coord[1]/80 * self.mapw] == 1:
                    ok = True
        bg.visual_coord = [bg.coord [0]*10, bg.coord[1]*10]
        bg.obj = [self.castlex, self.castley]
        bg.blocked = True
        bg.path = None
        bg.next_step = None
        bg.starting = False
        self.dm.need_update = True        #bg = badguy.badguy (self.dm , self.cm)
        #bg.astar_calcul()
        self.badguys.append (bg)
            
    def create_tower(self,coord,check = True):
        new_tower_coord = [coord [0]/10, coord[1]/10]
        print "build a %s", new_tower_coord
        if self.can_create_tower(new_tower_coord) or not check:
            self.castle.modify_money(-self.current_tower_creation_mode.cost)
            tw = self.dm.create_tower(self.current_tower_creation_mode)
            tw.set_map_coord(new_tower_coord)
            tw.visual_coord = [tw.coord [0]*10, tw.coord[1]*10]
            self.towers.append (tw)
            self.calcul.need_update = True
            if check:
                self.append_obstacle(tw)
                
    def check_tower_cell(self,coord1d):
        """ is it possible de create a new tower into this cell
            this function uses the one dimension coordinate system and must
            be checked for every cell the tower will finally occupy """
        if len(self.mapdata) <= coord1d:
            return -2
        if self.mapdata[coord1d] != 1:
            return -2
        return 0

    def can_create_tower(self,coord):
        """ check if we can create a tower there """
        # is there another tower there ? or are the cells of the new tower on the "road" ?
        ox = coord[0]
        oy = coord[1]
        size = 1
        new_mapdata = self.mapdata[:]
        new_road = False
        for x in range(ox-size,ox+size+1):
            for y in range(oy-size,oy+size+1):
                p = x + y * self.mapw
                c = self.check_tower_cell(p)
                if c == -2:
                    return False
        return True
        
    def remove_tower(self,t):
        ox = t.coord[0]
        oy = t.coord[1]
        size = 1
        for x in range(ox-size,ox+size+1):
            for y in range(oy-size,oy+size+1):
                p = x + y * self.mapw
                self.mapdata[p] = 1
        self.towers.remove(t)
