# castle

import pygame.time

MAX_LIFE_MULT = 1.5

TEST = True
            
class building(object):
    
    name = "Building"
    bt_name = ""
    
    def __init__(self,castle,cm):
        self.castle = castle
        self.cm = cm
        self.cm.register(self)
        self.life = 0
        pass
    
    def notify(self,event):
        pass
    
    def update(self):
        pass
    
class badguy_factory(building):
    
    name = "Usine"
    bt_name = "bg_factory"
    upgrades = {
        "speed"       : [0.05 , 0.06 , 0.08 , 0.10 , 0.13 , 0.15 , 0.19 , 0.25 , 0.30 , 0.36 , 0.45 ],
        "life"        : [20   , 40   , 75   , 100  , 200  , 300  , 400  , 600  , 800  , 950  , 1200 ],
        "build_speed" : [10   , 8    , 5    , 2    , 1    , 0.9  , 0.8  , 0.6  , 0.5  , 0.4  , 0.2  ],
        }
    upgrades = {
        "speed"       : [0.05 , 0.06 , 0.08 , 0.10 , 0.13 , 0.15 , 0.19 , 0.25 , 0.30 , 0.36 , 0.45 ],
        "life"        : [50   , 40   , 75   , 100  , 200  , 300  , 400  , 600  , 800  , 950  , 1200 ],
        "build_speed" : [0.5 for a in range(10)],
        }
        
    upgrades_names = {
        "speed" : "Vitesse",
        "life" : "Vie",
        "build_speed" : "Product.",
        "sell_badguys": "Revendre",
        }
        
    waves = {
        #"nom" : [ price, time ]
        "para" :     [ 50,  2 ],
        "kamikaze" : [ 100, 5 ],
        }
        
    if TEST:
        waves = {
            "para" :     [ 0,  0.1 ],
            "kamikaze" : [ 0, 0.11 ],
            }
    
    def __init__(self,castle,cm):
        super(badguy_factory, self).__init__(castle,cm)
        self.castle = castle
        self.begin_build = None
        self.end_upgrade = None
        self.current_upgrade = None
        self.current_construction = None
        self.badguys_ready = 1
        self.special_waves_ready = []
        self.current_wave_preparing = None
        self.end_current_wave_preparing = None
        self.badguy_sell_price = 1
        self.life_level = 0
        self.speed_level = 0
        self.build_speed_level = 0
        self.badguys_life = self.upgrades["life"][self.life_level]
        self.badguys_speed = self.upgrades["speed"][self.speed_level]
        self.building_time = self.upgrades["build_speed"][self.build_speed_level] * 1000
        self.cm.game.dm.upgrades_menu_available = True
        self.upgrades_boutons = None
        self.update_boutons_text()
        
    def prepare_wave(self,wave_type,gauge_stuff):
        for wr in self.special_waves_ready:
            if wr[0] == wave_type:
                #print "a",wave_type,"wave is already ready, launching it"
                self.cm.post(("launch wave",wr))
                self.special_waves_ready.remove(wr)
                return
        if self.current_wave_preparing or self.current_upgrade:
            return
        br = self.badguys_ready
        if br < 1:
            return
        if not self.castle.money > (br * self.waves[wave_type][0]):
            return
        self.current_wave_preparing = [wave_type,br]
        self.castle.modify_money(-(br * self.waves[wave_type][0]))
        self.end_current_wave_preparing = pygame.time.get_ticks() + (br * 1000 * self.waves[wave_type][1])
        self.badguys_ready -= br
        self.cm.game.dm.update_bb()
        self.gauge = self.cm.game.dm.create_gauge(pygame.time.get_ticks(),self.end_current_wave_preparing,gauge_stuff)
        
    def continue_current_wave(self):
        if not self.current_wave_preparing:
            return
        self.gauge.update_gauge(pygame.time.get_ticks())
        self.cm.game.dm.need_update = True
        if pygame.time.get_ticks() > self.end_current_wave_preparing:
            #print "wave",self.current_wave_preparing,"ready !"
            #self.cm.post(("wave_ready",self.current_wave_preparing))
            self.special_waves_ready.append(self.current_wave_preparing)
            self.current_wave_preparing = None
            self.end_current_wave_preparing = None
            self.gauge.kill()
            
    def update_boutons_text(self):
        if not self.cm.game.dm.upgrades_menu:
            return
        if not self.upgrades_boutons:
            self.upgrades_boutons = {
                "speed" : self.cm.game.dm.upgrades_menu.boutons["upgrade_bgspeed"],
                "life"   : self.cm.game.dm.upgrades_menu.boutons["upgrade_bglife"],
                "build_speed" : self.cm.game.dm.upgrades_menu.boutons["upgrade_bgbdspeed"],
                #"sell_badguys" : self.cm.game.dm.upgrades_menu.boutons["sell_badguys"],
                }
        chaine = self.upgrades_names["speed"]
        if (self.speed_level + 2) <= len(self.upgrades["speed"]):
            chaine += " " + str(int(((self.speed_level + 1) * 10 ) ** 1.5))
        chaine += "\n" + str(self.speed_level) + " : " + str(self.badguys_speed)
        if (self.speed_level + 2) <= len(self.upgrades["speed"]):
            chaine += "\n" + str(self.speed_level + 1)  + " : " + str(self.upgrades["speed"][self.speed_level + 1])
        self.upgrades_boutons["speed"].update_text(chaine)
        
        chaine = self.upgrades_names["build_speed"]
        if (self.build_speed_level + 2) <= len(self.upgrades["build_speed"]):
            chaine += " " + str(int(((self.build_speed_level + 1) * 10 ) ** 1.5))
        chaine += "\n" + str(self.build_speed_level) + " : " + str(self.building_time / 1000) + "s"
        if (self.build_speed_level + 2) <= len(self.upgrades["build_speed"]):
            chaine += "\n" + str(self.build_speed_level + 1 ) + " : " + str(self.upgrades["build_speed"][self.build_speed_level + 1]) + "s"
        self.upgrades_boutons["build_speed"].update_text(chaine)
        
        chaine = self.upgrades_names["life"]
        chaine += " " + str(int(((self.life_level + 1) * 10 ) ** 1.5))
        chaine += "\n" + str(self.life_level) + " : " + str(self.badguys_life)
        if (self.life_level + 2) <= len(self.upgrades["life"]):
            chaine += "\n" + str(self.life_level + 1) + " : " + str(self.upgrades["life"][self.life_level + 1])
        else:
            chaine += "\n" + str(self.life_level + 1 ) + ": Mult"
        self.upgrades_boutons["life"].update_text(chaine)
        
        #chaine = self.upgrades_names["sell_badguys"] + "\n" + str(self.badguys_ready) + " mechant(s)\npour : " + str(self.badguys_ready * self.badguy_sell_price) + " br."
        #self.upgrades_boutons["sell_badguys"].update_text(chaine)
        
    def begin_upgrade(self, upg, gauge_stuff):
        if self.end_upgrade or self.current_upgrade or self.current_wave_preparing:
            return
        if upg == "speed" and (self.speed_level + 2) > len(self.upgrades["speed"]):
            return
        if upg == "build_speed" and (self.build_speed_level + 2) > len(self.upgrades["build_speed"]):
            return
        time = pygame.time.get_ticks() + 10
        if upg == "life":
            cost = int(((self.life_level + 1) * 10 ) ** 1.5)
            #cost = 0
            time += (self.life_level + 1) * 1000
        elif upg == "speed" :
            cost = int(((self.speed_level + 1) * 10 ) ** 1.5)
            #cost = 0
            time += (self.speed_level + 1) * 1000
        elif upg == "build_speed" :
            cost = int(((self.build_speed_level + 1) * 10 ) ** 1.5)
            #cost = 0
            time += (self.build_speed_level + 1) * 1000
        if self.castle.money < cost:
            return
        self.current_upgrade = upg
        self.end_upgrade = time
        self.castle.modify_money(-cost)
        self.gauge = self.cm.game.dm.create_gauge(pygame.time.get_ticks(),self.end_upgrade,gauge_stuff)
        
    def upgrade_bgspeed(self):
        self.speed_level += 1
        #print "new speed level",self.speed_level
        if len(self.upgrades["speed"]) > self.speed_level:
            self.badguys_speed = self.upgrades["speed"][self.speed_level]
        #print "new speed",self.badguys_speed
    
    def upgrade_bglife(self):
        self.life_level += 1
        #print "new life level",self.life_level
        if len(self.upgrades["life"]) > self.life_level:
            self.badguys_life = self.upgrades["life"][self.life_level]
        else:
            mult = 1.1 + 0.05 * (self.life_level - len(self.upgrades["life"]))
            if mult > MAX_LIFE_MULT: mult = MAX_LIFE_MULT
            #print "new mult ! ",mult
            self.badguys_life *= mult
            self.badguys_life = int (self.badguys_life)
        #print "new life",self.badguys_life
    
    def upgrade_bgbdspeed(self):
        self.build_speed_level += 1
        #print "new bgbdspeed level",self.build_speed_level
        if len(self.upgrades["build_speed"]) > self.build_speed_level:
            self.building_time = self.upgrades["build_speed"][self.build_speed_level] * 1000
        #print "new bgbdspeed",self.building_time

    def build(self):
        self.current_construction = "badguy"
        self.begin_build = pygame.time.get_ticks()
        #self.cm.game.dm.debug (begingin breeding of",self.current_construction,"at",self.begin_build
        
    def continue_current_build(self):
        if not self.begin_build:
            # always prepare a new badguy if none is currently beeing bred
            self.build()
        if pygame.time.get_ticks() >= self.begin_build + self.building_time:
            self.current_construction = None
            self.begin_build = None
            #self.cm.game.dm.debug (breeding of badguy ended"
            self.badguys_ready += 1
            self.cm.post(["badguy_count_update",self])
            
    def continue_current_upgrade(self):
        if not self.current_upgrade:
            return
        self.gauge.update_gauge(pygame.time.get_ticks())
        self.cm.game.dm.need_update = True
        if pygame.time.get_ticks() > self.end_upgrade:
            if self.current_upgrade == "life": self.upgrade_bglife()
            elif self.current_upgrade == "speed" : self.upgrade_bgspeed()
            elif self.current_upgrade == "build_speed" : self.upgrade_bgbdspeed()
            self.current_upgrade = None
            self.end_upgrade = None
            self.gauge.kill()
            self.update_boutons_text()
            
    def update(self):
        self.continue_current_build()
        self.continue_current_upgrade()
        self.continue_current_wave()
    
    def notify (self,event):
        if event [0] == "upgrade_bgspeed":
            self.begin_upgrade("speed",event[1])
        elif event [0] == "upgrade_bglife":
            self.begin_upgrade("life",event[1])
        elif event [0] == "upgrade_bgbdspeed":
            self.begin_upgrade("build_speed",event[1])
        elif event [0] == "badguy_count_update":
            self.update_boutons_text()
        elif event [0] == "special_wave_kamikaze":
            self.prepare_wave("kamikaze",event[1])
        elif event [0] == "special_wave_para":
            self.prepare_wave("para",event[1])
        #elif event [0] == "sell_badguys":
            #income = self.badguys_ready * self.badguy_sell_price
            #self.badguys_ready = 0
            #self.castle.modify_money(income)

class castle_defense(building):
    """ This building will add towers to the castle, and may be upgradable """
    bt_name = "build_castle_defense"
    name = "Donjon"
    
    def __init__(self,castle,cm):
        super(castle_defense, self).__init__(castle,cm)
        self.level = 0
        self.cm.post(["castle_defense_built",self])
        
class brouzouf_tower_building(building):
    
    bt_name = "build_brouzouf_tower"
    name = "Brouzouf Tw"
    
    def __init__(self,castle,cm):
        super(brouzouf_tower_building).__init__(castle,cm)
        self.level = 0
        self.cm.post(["brouzouf_tower_building_built",self])
        

class laboratory(building):
    
    # arbre des technos :
    # chaque entree :
    #  nom  : [   prix    ,   necessites (science)    ,   necessites (batiments), temps ]
    
    technos = {
        "defensive_castle": [250,    [], [], 30  ],
        "special"         : [400,    [], [castle_defense], 20],
        "entry2"          : [1000,   [], [], 30 ],
        "entry3"          : [2500,   ["entry2"], [], 60 ],
        "entry4"          : [6000,   ["entry3"], [], 120 ],
        }
    
    if TEST:
        technos = {
            "defensive_castle": [0,    [], [], 1  ],
            "special"         : [0,    [], [castle_defense], 1],
            "entry2"          : [0,   [], [], 1 ],
            "entry3"          : [0,   ["entry2"], [], 1 ],
            "entry4"          : [0,   ["entry3"], [], 1 ],
            }
        
    technos_names = {
        "defensive_castle" : "Catapulte",
        "special": "Special",
        "entry2"  : "Entree 2",
        "entry3"  : "Entree 3",
        "entry4"  : "Entree 4",
        }
        
    name = "Labo"
    bt_name = "labo"
        
    def __init__(self,castle,cm):
        super(laboratory, self).__init__(castle,cm)
        self.level = 0
        self.castle = castle
        self.begin_build = None
        self.current_construction = None
        self.science = []
        self.update_boutons_text()
        self.cm.game.dm.research_menu_available = True
        
    def update_boutons_text(self,recurse = True):
        self.cm.game.dm.research_menu.boutons["research_defensive_castle"].update_text(self.cm.game.make_text("research","defensive_castle"))
        self.cm.game.dm.research_menu.boutons["research_special"].update_text(self.cm.game.make_text("research","special"))
        self.cm.game.dm.research_menu.boutons["research_entry2"].update_text(self.cm.game.make_text("research","entry2"))
        self.cm.game.dm.research_menu.boutons["research_entry3"].update_text(self.cm.game.make_text("research","entry3"))
        self.cm.game.dm.research_menu.boutons["research_entry4"].update_text(self.cm.game.make_text("research","entry4"))
        if recurse:
            self.castle.update_boutons_text(False)

    def build(self,research, gauge_stuff):
        if self.begin_build:
            self.cm.game.dm.debug ("no, already searching " + self.current_construction)
            return
        if not research in self.technos:
            self.cm.game.dm.debug ("no " + research + " does not exist")
            return
        if self.castle.money < self.technos[research][0]:
            self.cm.game.dm.debug ("not enough money")
            return
        if research in self.science:
            self.cm.game.dm.debug ("no, you already have " + research)
            return
        for need_sc in self.technos[research][1]:
            if not need_sc in self.science:
                self.cm.game.dm.debug ("no, you need " + need_sc)
                return
        for need_build in self.technos[research][2]:
            if not self.castle.has_building(need_build):
                self.cm.game.dm.debug ("no, you need " + need_build.name)
                return
        self.current_construction= research
        self.castle.modify_money(-self.technos[research][0])
        self.building_time = self.technos[research][3] * 1000
        now = pygame.time.get_ticks()
        self.begin_build = now
        self.gauge = self.cm.game.dm.create_gauge(self.begin_build, self.begin_build + self.building_time,gauge_stuff)
        
    def upgrade_science(self,research, gauge_stuff):
        self.build(research, gauge_stuff)
        
    def continue_current_build(self):
        now = pygame.time.get_ticks()
        self.gauge.update_gauge(now)
        self.cm.game.dm.need_update = True
        if now >= self.begin_build + self.building_time:
            self.gauge.kill()
            research = self.current_construction
            self.current_construction = None
            self.begin_build = None
            self.science.append(research)
            if research == "special":
                self.cm.game.dm.special_menu_available = True
            self.update_boutons_text()
            self.cm.post(("research complete",research))
            
    def notify(self,event):
        if event[0] == "research_defensive_castle":
            self.upgrade_science("defensive_castle",event[1])
        elif event [0] == "research_special":
            self.upgrade_science("special",event[1])
        elif event [0] == "research_entry2":
            self.upgrade_science("entry2",event[1])
        elif event [0] == "research_entry3":
            self.upgrade_science("entry3",event[1])
        elif event [0] == "research_entry4":
            self.upgrade_science("entry4",event[1])
            
    def update(self):
        if self.begin_build:
            self.continue_current_build()
            
class castle:
    
    #   "name" : [ price, time, needs (build), needs (science), class ,"hr name"],
    
    known_buildings = {
        "badguy_factory" :  [100, 1, [], [], badguy_factory ,"Usine"],
        "laboratory"     :  [250, 20, [badguy_factory], [], laboratory ,"Labo"],
        "castle_defense" :  [500, 30, [], ["defensive_castle"], castle_defense ,"Donjon"],
        "brouzouf_tower" :  [250, 15, [badguy_factory,laboratory], [], brouzouf_tower_building ,"Brouzouf tw"],
        }
        
    if TEST:
        known_buildings = {
            "badguy_factory" :  [0, 1, [], [], badguy_factory ,"Usine"],
            "laboratory"     :  [0, 1, [badguy_factory], [], laboratory ,"Labo"],
            "castle_defense" :  [0, 1, [], ["defensive_castle"], castle_defense ,"Donjon"],
            "brouzouf_tower" :  [0, 1, [badguy_factory,laboratory], [], brouzouf_tower_building ,"Brouzouf tw"],
            }
            
    def __init__(self,cm, mode_solo = None):
        self.cm = cm
        #self.dm = self.cm.game.dm
        self.cm.register(self)
        self.lifes = 100
        self.money = 2500
        self.gauge = None
        
        self.buildings = []
        if mode_solo:
            self.buildings.append(badguy_factory(self, self.cm))
        self.update_boutons_text()
        
        self.current_construction = None # what is the current building being built ?
        self.begin_build = None # when did I begin the build ?
    
    def update_boutons_text(self,recurse = True):
        if not self.cm.game.dm.build_menu:
            return
        self.cm.game.dm.build_menu.boutons["labo"].update_text(self.cm.game.make_text("building","laboratory"))
        self.cm.game.dm.build_menu.boutons["bg_factory"].update_text(self.cm.game.make_text("building","badguy_factory"))
        self.cm.game.dm.build_menu.boutons["build_castle_defense"].update_text(self.cm.game.make_text("building","castle_defense"))
        self.cm.game.dm.build_menu.boutons["build_brouzouf_tower"].update_text(self.cm.game.make_text("building","brouzouf_tower"))
        l = self.has_building(laboratory)
        if l and recurse:
            l.update_boutons_text(False)
            
    def modify_life(self,modif):
        self.lifes += modif
        self.cm.game.dm.update_bb()
        if not self.cm.game.single_player:
            self.cm.game.nm.send(":mylife " + str (self.lifes) + ":")
            
    def modify_money(self,value):
        self.money += value
        self.cm.game.dm.update_bb()
        
    #def infobulle(self,building_name):
        #if building_name not in self.known_buildings:
            #if building_name not in laboratory.technos:
                #return ""
            ## TODO : a completer pour les recherches
            #return building_name 
            
        #string = self.known_buildings[building_name][4].name
        #for bld in self.buildings:
            #if isinstance(bld, self.known_buildings[building_name][4]):
                #string += "\nAlready built"
                #return string
        #string += "\nCost : " + str(self.known_buildings[building_name][0])
        #string += "\nTime : " + str(self.known_buildings[building_name][1])
        #req = ""
        #for need_bd in self.known_buildings[building_name][2]:
            #if not self.has_building(need_bd):
                #req += need_bd.name + " "
        #for need_sc in self.known_buildings[building_name][3]:
            #req += "Sc " + need_sc + " "
        #if req != "":
            #string += "\nRequires : " + req
        #return string
        
    def build(self,building_name, gauge_stuff = None): #,building_buildtime,building_class, gauge_stuff = None):
        if self.begin_build:
            self.cm.game.dm.debug ("already building")
            return
        if not building_name in self.known_buildings:
            self.cm.game.dm.debug ("i don't know what " + building_name + " is")
            return
        if self.money < self.known_buildings[building_name][0]:
            self.cm.game.dm.debug ("not enough money")
            return
        for bld in self.buildings:
            if isinstance(bld, self.known_buildings[building_name][4]):
                self.cm.game.dm.debug ("no, you already have " + str(building_name))
                return
        for need_bd in self.known_buildings[building_name][2]:
            if not self.has_building(need_bd):
                self.cm.game.dm.debug ("no, you don't have " + str(need_bd))
                return
        if len(self.known_buildings[building_name][3]) > 0 and not self.has_building(laboratory):
            self.cm.game.dm.debug ("no, you need " + str  (self.known_buildings[building_name][3]) + " and don't even have a labo")
            return
        lab = self.has_building(laboratory)
        for need_sc in self.known_buildings[building_name][3]:
            if not need_sc in lab.science:
                self.cm.game.dm.debug ("no, you need the science " + need_sc + " and don't have it")
                return
        building_price = self.known_buildings[building_name][0]
        building_buildtime = self.known_buildings[building_name][1] * 1000
        building_class = self.known_buildings[building_name][4]
        if not gauge_stuff:
            gauge_stuff = self
        self.modify_money(-building_price)
        self.current_construction = [building_name,building_price,building_buildtime,building_class]
        self.begin_build = pygame.time.get_ticks()
        now = pygame.time.get_ticks()
        self.gauge = self.cm.game.dm.create_gauge(self.begin_build, self.begin_build + self.current_construction[2],gauge_stuff)
        
    def continue_current_build(self):
        if self.gauge:
            self.gauge.update_gauge(pygame.time.get_ticks())
        self.cm.game.dm.need_update = True
        if pygame.time.get_ticks() >= self.begin_build + self.current_construction[2]:
            self.gauge.kill()
            b = self.current_construction[3](self,self.cm)
            self.cm.game.dm.build_menu.boutons[b.bt_name].update_text(b.name + "\nOK")
            self.buildings.append(b)
            self.begin_build = None
            self.current_construction = None
            self.update_boutons_text()
            self.cm.game.dm.update_bb()
        
    def update(self):
        for bd in self.buildings:
            bd.update()
        if self.begin_build:
            self.continue_current_build()

    
    def notify(self,event):
        if event [0] == "build_laboratory":
            self.cm.game.dm.debug ("build laboratory !")
            self.build("laboratory",event[1])
        elif event [0] == "build_badguy_factory":
            self.cm.game.dm.debug ("build_badguy_factory")
            self.build("badguy_factory",event[1])
        elif event [0] == "build_castle_defense":
            self.cm.game.dm.debug ("build_castle_defense")
            self.build("castle_defense",event[1])
        elif event [0] == "build_brouzouf_tower":
            self.cm.game.dm.debug ("build_castle_defense")
            self.build("brouzouf_tower",event[1])
    
    def get_badguys_ready(self):
        count = 0
        for b in self.buildings:
            if isinstance(b,badguy_factory):
                count += b.badguys_ready
        return count
            
    def has_building(self,building_class):
        for b in self.buildings:
            if isinstance(b,building_class):
                return b
        return False
