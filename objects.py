# -*- coding: utf-8 -*-
from livewires import games
import pygame.image
import pygame.sprite
from pygame.locals import RLEACCEL
import random
import os

class Selectable(object):
    """Every selectable object should subclass this"""

    def __init__(self):
        self.selected = False

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    def get_info(self):
        return str(self)

class shadow(games.Sprite):
    """Cursor shadow while in tower create mode"""
    def __init__(self, dm, cm):
        from pygame_dm import DATAPATH
        self.cm = cm
        cm.register(self)
        x = y = 0
        image = pygame.Surface((30, 30))
        self.image = pygame.image.load(DATAPATH + "tower_shadow.png").convert_alpha()
        super(shadow, self).__init__(dm, x, y, self.image)

    def notify(self, event):
        if event[0] == "mouse_move":
            self._erase()
            self.move_to(event[1][0]/10*10, event[1][1]/10*10)

    def kill(self):
        super(shadow, self).kill()
        self.cm.unregister(self)

class tower(games.Animation, Selectable):
    """ The tower class represents any tower in the game """
    cost = 0
        #life, speed, power, range, image,          upgrade_time, upgrade_price,    sell_income
    levels = [
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        [0, 0, 0, 0,    "tower.png", 0, 0, 0],
        ]
    type = "No type"
    def __init__(self, dm, cm, group = None):
        from pygame_dm import DATAPATH, TAR_NORMAL
        self.level = 0
        self.selected = False
        image_infos = self.levels[self.level][4]
        self.nrimage_list = [] # non repeating
        self.rimage_list = [] # repeating
        if isinstance(image_infos, dict):
            # animation
            self.nrimage_list = [os.path.join(DATAPATH, image_infos.get('folder'), imagename) for imagename in image_infos.get("nrfiles")]
            self.rimage_list = [os.path.join(DATAPATH, image_infos.get('folder'), imagename) for imagename in image_infos.get("rfiles")]
        else:
            self.nrimage_list = [os.path.join(DATAPATH, self.levels[self.level][4]),]
        self.image_name = self.nrimage_list[0]
        self.image = pygame.image.load(self.image_name).convert_alpha()
        self.rect = self.image.get_rect()
        self.image_save = self.image.copy()
        self.life   = self.levels[self.level][0]
        self.speed  = self.levels[self.level][1]
        self.power  = self.levels[self.level][2]
        self.range  = self.levels[self.level][3]
        self.dm        =    dm    # display manager
        self.cm        =    cm    # control manager
        self.last_launched_bullet = 0
        self.target    =    TAR_NORMAL # what target will the tower prefer
        self.coord    =    [0, 0]    # where the tower is
        self.visual_coord    =    [0, 0]    # where the tower is
        self.isobstacle = True              # badguys can't go through towers
        self.size   =   3
        self.current_construction = None # upgrade status
        self.end_upgrade = None # when will the upgrade be ready ?
        super(tower, self).__init__(dm, self.visual_coord[0], self.visual_coord[1], self.nrimage_list, self.rimage_list)
        self.draw()
        self.init = True

    def draw(self):
        self.replace_image(self.image)
        self.move_to(self.visual_coord)

    def set_map_coord(self, new_tower_coord):
        self.coord = new_tower_coord
        self.visual_coord = [self.coord [0]*10, self.coord[1]*10]
        self.rect.center = (self.visual_coord[0], self.visual_coord[1])
        self.draw()

    def update(self):
        if not hasattr(self, "init"):
            return
        if self.current_construction:
            self.continue_current_build()
        else:
            game = self.cm.game
            now = pygame.time.get_ticks()
            if now > self.last_launched_bullet + self.speed:
                for bg in game.badguys:
                    if not bg.starting:
                        distance = ((bg.coord[0] - self.coord[0])**2.0 + (bg.coord[1] - self.coord[1])**2.0)**(1.0/2.0)
                        if distance <= self.range:
                            self.dm.create_bullet(self, bg)
                            self.last_launched_bullet = now
                            break

    def get_visual_coord(self):
        return self.visual_coord[:]

    def _destroy(self):
        self.cm.game.remove_tower(self)
        if self.selected:
            self.cm.game.dm.update_bb(message = False)
        self.kill()
        
    def get_info(self):
        string = u"""Tour (%s) %s :
Vitesse : %s
Portée : %s
Puissance : %s""" % (self.type, self.level, self.speed, self.range, self.power)
        if len(self.levels) - 1 > self.level:
            string += u"""

Niveau suivant :
- coût : %s
- temps : %s
- vitesse : %s
- puissance : %s
- portée : %s""" % (self.levels[self.level][6], self.levels[self.level][5], self.levels[self.level + 1][1], self.levels[self.level + 1][2], self.levels[self.level + 1][3])
        return string
        
    def upgrade(self):
        if self.current_construction:
            return
        if self.levels [self.level][5] > 0 and self.cm.game.castle.money > self.levels [self.level][6]:
            self.cm.game.castle.modify_money(-self.levels [self.level][6])
            self.current_construction = "upgrade"
            self.end_upgrade = pygame.time.get_ticks() + self.levels [self.level][5] * 1000
            self.gauge = self.dm.create_gauge(pygame.time.get_ticks(), self.end_upgrade, self)
            
    def sell(self):
        income = self.levels[self.level][7]
        self.cm.game.castle.modify_money(income)
        self._destroy()

    def continue_current_build(self):
        from pygame_dm import DATAPATH
        self.gauge.update_gauge(pygame.time.get_ticks())
        if pygame.time.get_ticks() >= self.end_upgrade:
            self.gauge.kill()
            self.current_construction = None
            self.end_upgrade = None
            if self.level < len(self.levels) - 1:
                self.level += 1
                self.image_name  = self.levels[self.level][4]
                self.life   = self.levels[self.level][0]
                self.speed  = self.levels[self.level][1]
                self.power  = self.levels[self.level][2]
                self.range  = self.levels[self.level][3]
                self.image  = pygame.image.load(DATAPATH + self.image_name).convert_alpha()
                self.image_save = self.image.copy()
                self.draw()

class basic_tower(tower):
    
    cost = 5
    type = "Basic"
    
    levels = [
        [50,    40,     30 ,  10,    
            {"folder":"ctower",
            "nrfiles":["%03d.png" % i for i in range(1,10)],
            "rfiles":["%03d.png" % i for i in range(11,13)],
            },
            5,           20   ,  120  ],        # cout total : 250
        [50,    400,     6 ,  5,    "tower1.png",   4,            10  , 6   ],        # cout total : 10
        [50,    300,     10,  6,    "tower2.png",   8,            20  , 12   ],        # cout total : 20
        [50,    200,     15,  7,    "tower3.png",   15,           50  , 30   ],        # cout total : 40
        [50,    150,     22,  8,    "tower4.png",   30,           75  , 70   ],        # cout total : 90
        [50,    90,     30,  9,    "tower5.png",   60,            80  , 100   ],        # cout total : 165
        [50,    40,     60,  10,    "tower6.png",   0,             0  , 180   ],        # cout total : 245
        ]
        
    def __init__(self, dm, cm, group = None):
        super(basic_tower, self).__init__(dm, cm, group)
        self.init = True
       
        
        
class castle_tower(tower):
    
    cost = 999
    
    type = "Chateau"
    
    levels = [
        [50,    40,     30 ,  10,    
            {"folder":"ctower","files":["%03d.png" % i for i in range(1,13)]},
            5,           20   ,  120  ],        # cout total : 250
        [50,    35,     60 ,  12,    "ctower1.png",   10,           40   ,  220  ],        # cout total : 270
        [50,    30,     100,  15,    "ctower2.png",   15,           90   ,  280  ],        # cout total : 310
        [50,    25,     150,  20,    "ctower3.png",   20,          120   ,  350  ],        # cout total : 400
        [50,    20,     220,  22,    "ctower4.png",   25,          150   ,  450  ],        # cout total : 520
        [50,    10,     300,  25,    "ctower5.png",   30,          250   ,  550  ],        # cout total : 670
        [50,    15,     600,  35,    "ctower6.png",   0,             0   ,  800  ],        # cout total : 920
        ]
    
    def __init__(self, dm, cm, group=None):
        if cm.game.TEST:
            self.levels = [
                [50,    40,     30 ,  10,    
                    {"folder":"ctower","files":["%03d.png" % i for i in range(1,13)]},
                    5,           20   ,  120  ],        # cout total : 250
                [50,    35,     600,  12,    "ctower1.png",    1,            0   ,  220  ],        # cout total : 270
                [50,    30,    1000,  15,    "ctower2.png",    1,            0   ,  280  ],        # cout total : 310
                [50,    25,    1500,  20,    "ctower3.png",    1,            0   ,  350  ],        # cout total : 400
                [50,    20,    2200,  22,    "ctower4.png",    1,            0   ,  450  ],        # cout total : 520
                [50,    10,    3000,  25,    "ctower5.png",    1,            0   ,  550  ],        # cout total : 670
                [50,    15,    6000,  35,    "ctower6.png",    1,            0   ,  800  ],        # cout total : 920
                ]
        super(castle_tower, self).__init__(dm, cm, group)
        self.init = True
        
class brouzouf_tower(tower):
    
    cost = 999
    
    type = "Brouzouf"
        #life, speed, power, range, image,          upgrade_time, upgrade_price,    sell_income
    
    levels = [
        [50, 1000,  0,  0,  "btower0.png",       5,     50   ,  100],        # cout total : 250
        [50,  800,  0,  0,  "btower1.png",      10,    100   ,  125],        # cout total : 300
        [50,  600,  0,  0,  "btower2.png",      15,    200   ,  250],        # cout total : 400
        [50,  500,  0,  0,  "btower3.png",      20,    250   ,  480],        # cout total : 600
        [50,  400,  0,  0,  "btower4.png",      30,    350   ,  650],        # cout total : 850
        [50,  300,  0,  0,  "btower5.png",      50,    500   ,  900],        # cout total : 1200
        [50,  200,  0,  0,  "btower6.png",      80,    650   , 1200],        # cout total : 1700
        [50,  180,  0,  0,  "ctower.png",      115,    900   , 2000],        # cout total : 2350
        [50,  150,  0,  0,  "ctower1.png",     150,   1200   , 3000],        # cout total : 3250
        [50,  120,  0,  0,  "ctower2.png",     200,   1500   , 4000],        # cout total : 4450
        [50,  100,  0,  0,  "ctower3.png",     210,   2000   , 5000],        # cout total : 5950
        [50,   80,  0,  0,  "ctower4.png",     220,   2500   , 6500],        # cout total : 7950
        [50,   50,  0,  0,  "ctower5.png",     250,   3200   , 8000],        # cout total :10450 
        [50,   20,  0,  0,  "ctower6.png",       0,      0   , 10000],        # cout total :13650
        ]
        
    def __init__(self, dm, cm, group=None):
        if cm.game.TEST:
            self.levels = [
                [50, 1000,  0,  0,  "btower0.png",       1,      0   ,  100],        # cout total : 250
                [50,  800,  0,  0,  "btower1.png",       1,      0   ,  125],        # cout total : 300
                [50,  600,  0,  0,  "btower2.png",       1,      0   ,  250],        # cout total : 400
                [50,  500,  0,  0,  "btower3.png",       1,      0   ,  480],        # cout total : 600
                [50,  400,  0,  0,  "btower4.png",       1,      0   ,  650],        # cout total : 850
                [50,  300,  0,  0,  "btower5.png",       1,      0   ,  900],        # cout total : 1200
                [50,  200,  0,  0,  "btower6.png",       1,      0   , 1200],        # cout total : 1700
                [50,  180,  0,  0,  "ctower.png",        1,      0   , 2000],        # cout total : 2350
                [50,  150,  0,  0,  "ctower1.png",       1,      0   , 3000],        # cout total : 3250
                [50,  120,  0,  0,  "ctower2.png",       1,      0   , 4000],        # cout total : 4450
                [50,  100,  0,  0,  "ctower3.png",       1,      0   , 5000],        # cout total : 5950
                [50,   80,  0,  0,  "ctower4.png",       1,      0   , 6500],        # cout total : 7950
                [50,   50,  0,  0,  "ctower5.png",       1,      0   , 8000],        # cout total :10450 
                [50,   20,  0,  0,  "ctower6.png",       1,      0   , 10000],        # cout total :13650
                ]
        super(brouzouf_tower, self).__init__(dm, cm, group)
        self.init = True
        self.dernier_brouzouf_genre = 0
       
    def update(self):
        if not hasattr(self, "init"):
            return
        if self.current_construction:
            self.continue_current_build()
        game = self.cm.game
        now = pygame.time.get_ticks()
        if now > self.dernier_brouzouf_genre + self.levels[self.level][1]:
            self.dernier_brouzouf_genre = now
            game.castle.modify_money(2)
       
class badguy(games.Sprite, Selectable):
    """ The badguy class describe every badguy in the game """

    def __init__(self, dm, cm):
        self.transparent = (255, 0, 255)
        self.color = (50, 50, 50)
        self.dm        = dm        # display manager
        self.cm        = cm        # control manager
        self.life    = 0        # life
        self.full_life = self.life
        self.speed    = 0        # speed (nbre de pixel par seconde)
        self.special = None
        self.last_move = 0
        self.type    = 0    # type of badguy
        self.coord    = (0, 0)        # where the badguy is
        self.visual_coord = [0, 0]
        self.obj    =   [0, 0]        # coord this badguy wants to reach
        self.path = None            # the astar path
        self.next_step = None
        self.size   = 10            # withiin this range, the badguy is hit by bullets
        self.win        = False         # will be true when will reach the objective
        self.isobstacle = False         # badguys can go through themselves
        self.blocked = False
        self.starting = True
        self.kamikaze = False        # if kamikaze is True, the badguy will explode and _destroy every tower around him
        self.kamidistance = 90
        self.last_good_step = 0
        self.starting_coord = None
        self.birth = pygame.time.get_ticks()
        self.selected = False
        self.image = self._create_surface()
        self.rect = self.image.get_rect()
        self.image_save = self.image.copy()
        super(badguy, self).__init__(dm, self.visual_coord[0], self.visual_coord[1], self.image)
        self.draw()
        self.init = True

    def _create_surface(self):
        self.image = pygame.Surface((16,16))
        self.image.fill(self.transparent)
        self.image.set_colorkey(self.transparent, RLEACCEL)
        if self.selected:
            pygame.draw.circle(self.image, (255, 0, 0), (8, 8), 8, 0)
        else:
            pygame.draw.circle(self.image, (0, 0, 0), (8, 8), 8, 0)
        #color = pygame.color.multiply(self.color,  ( abs(self.life * 255) / (self.full_life + 1) ) )
        color = self.color
        pygame.draw.circle(self.image, color, (8, 8), 6, 0)
        if self.special == "kamikaze":
            pygame.draw.circle(self.image, (255, 0, 0), (8, 8), 3, 0)
        elif self.special == "para":
            pygame.draw.circle(self.image, (0, 0, 0), (8, 8), 3, 0)
        return self.image.convert()
        
    def draw(self):
        self.replace_image(self._create_surface())
        self.move_to(self.visual_coord)

    def explode(self):
        distance = self.kamidistance
        tower = None
        for t in self.cm.game.towers:
            if not isinstance(t, castle_tower) and not isinstance(t, brouzouf_tower):
                t_distance = ((self.visual_coord[0] - t.visual_coord[0])**2.0 + (self.visual_coord[1] - t.visual_coord[1])**2.0)**(1.0/2.0)
                if t_distance < distance:
                    tower = t
                    distance = t_distance
        if tower:
            tower._destroy()
            self.kamikaze = False
            self._destroy()
        else:
            rnd_tower = random.choice(self.cm.game.towers) 
            self.obj = [rnd_tower.coord[0], rnd_tower.coord[1]]
        
    def find_path(self):
        if not self.path:
            self.path = self.cm.game.astar(self.coord[0], self.coord[1])
            if not self.path:
                self.kamikaze = True
                self.explode()
                return
        if self.wincheck():
            return
        self.blocked = False
        self.starting = False
        self.next_step = self.path.pop(0)

    def update(self):
        if not hasattr(self, "init"):
            return
        self.draw()
        if self.kamikaze:
            self.explode()
            return
        if self.life <= 0:
            self.cm.post(["badguy_die", self])
            if self.special == "kamikaze":
                self.explode()
            else:
                self._destroy()
            return
        if self.blocked or not self.next_step:
            self.path = None
            self.find_path()
            return
        if self.wincheck():
            return
        self.follow_astar ()

    def wincheck(self):
        if self.coord[0] == self.obj[0] and self.coord[1] == self.obj[1]:
            self._win()
            return True
        return False

    def _win(self):
        self.win = True
        self.cm.game.castle.modify_life(-1)
        if not self.cm.game.single_player:
            self.cm.game.nm.send(":earn_money 1.5 *level:")
        self.dm.update_bb()
        self._destroy()

    def follow_astar(self):
        self.move_to_next_step()
        if self.visual_coord[0] / 10.0 == self.next_step%80 and self.visual_coord[1] / 10.0 == self.next_step/80:
            self.coord = (self.next_step%80, self.next_step/80)
            self.visual_coord = [self.coord[0]*10, self.coord[1]*10]
            self.last_good_step = self.next_step
            #self.next_step = self.path.pop(0)
            if self.wincheck():
                return
            self.find_path()

    def move_to_next_step(self):
        if self.blocked or self.starting:
            return
        if self.cm.game.mapdata[self.next_step] == -1:
            self.path = None
            self.find_path()
            return
        self.blocked = False
        x_dir = self.next_step%80*10 - self.visual_coord [0]
        y_dir = self.next_step/80*10 - self.visual_coord [1]
        speed = (pygame.time.get_ticks() - self.last_move) * self.speed
        self.last_move = pygame.time.get_ticks()
        if abs(x_dir) <= speed:
            x_move = x_dir
        else:
            x_move = speed * ( x_dir > 0) - speed * ( x_dir < 0)
        if abs(y_dir) <= speed:
            y_move = y_dir
        else:
            y_move = speed * ( y_dir > 0) - speed * ( y_dir < 0)
        self.visual_coord [0] += x_move
        self.visual_coord [1] += y_move
        self.rect.center = (self.visual_coord[0], self.visual_coord[1])
    
    def _destroy(self):
        if self in self.cm.game.badguys:
            self.cm.game.badguys.remove(self)
        self.kill()
        if self.selected:
            self.cm.game.dm.update_bb(message = False)

    def get_visual_coord(self):
        return [self.visual_coord[0] + 5, self.visual_coord[1] + 5]
        
    def get_info(self):
        string = "Mechant :\nVie : "+str(self.life)+"\nVitesse : "+str(self.speed)+"\nType : "+str(self.type)
        return string
    
#class badguy_sprite(pygame.sprite.Sprite):
    #def __init__ (self, stuff, group = None):
        #pygame.sprite.Sprite.__init__(self, group)
        #self.image = pygame.image.load(DATAPATH + "badguy.png").convert_alpha()
        #self.image_save = self.image.copy()
        #self.rect = self.image.get_rect()

class bullet(games.Sprite):
    """ The bullet class represents any bullet fired by a tower """
    def __init__(self, dm, tower, target, group = None):
        from pygame_dm import DATAPATH
        self.image = pygame.image.load(DATAPATH + "bullet.png").convert_alpha()
        self.image_save = self.image.copy()
        self.rect = self.image.get_rect()
        self.dm        =    dm    # display manager
        self.speed    =    0    # speed
        self.last_move = pygame.time.get_ticks()
        self.type    =    0
        self.power    =    0    # power (how much life does it remove from the badguys)
        self.visual_coord    = [0, 0]    # where the bullet is
        self.tower  =   tower   # what tower fired me ?
        self.target =   target  # what badguy will I shoot ?
        self.alive = True
        super(bullet, self).__init__(dm, self.visual_coord[0], self.visual_coord[1], self.image)
        self.draw()
        self.init = True

    def draw(self):
        self.replace_image(self.image)
        self.move_to(self.visual_coord)

    def update(self):
        if not hasattr(self, "init"):
            return
        if not self.alive:
            self._destroy()
        distance = ((self.target.visual_coord[0] - self.visual_coord[0])**2.0 + (self.target.visual_coord[1] - self.visual_coord[1])**2.0)**(1.0/2.0)
        if distance > self.target.size:
            self.move ()
        else:
            self.target.life -= self.power
            if self.target.selected:
                self.dm.update_bb(self.target.get_info())
            self._destroy()
    
    def move(self):
        x_dir = self.target.visual_coord [0] - self.visual_coord [0]
        y_dir = self.target.visual_coord [1] - self.visual_coord [1]
        speed = (pygame.time.get_ticks() - self.last_move) * self.speed
        self.last_move = pygame.time.get_ticks()
        if abs(x_dir) <= speed:
            x_move = x_dir
        else:
            x_move = speed * ( x_dir > 0) - speed * ( x_dir < 0)
        if abs(y_dir) <= speed:
            y_move = y_dir
        else:
            y_move = speed * ( y_dir > 0) - speed * ( y_dir < 0)
        self.visual_coord [0] += x_move
        self.visual_coord [1] += y_move
        self.draw()

    def _destroy(self):
        self.alive = False
        self.kill()

    def get_visual_coord(self):
        return self.visual_coord[:]

class gauge(games.Sprite):
    def __init__(self, screen, init_value, final_value, sprite_or_center):
        self.screen = screen
        if isinstance(sprite_or_center, games.Object):
            width = sprite_or_center._rect.width * 90/100
            center = sprite_or_center._rect.center
        else:
            width = 30
            center = sprite_or_center
        self.image = pygame.Surface((width, 4))
        self.image.fill((0, 0, 0))

        super(gauge, self).__init__(self.screen, center[0], center[1], self.image)
        
        self.move_to(center)
        self.ini_val = init_value
        self.fin_val = final_value
        self.update_gauge(init_value)
        
    def update_gauge(self, value):
        w = (value - self.ini_val) * self._rect.width / (self.fin_val - self.ini_val)
        rect = pygame.Rect((1, 1), (w, 2))
        self.image.fill((0, 0, 0))
        self.image.fill((255, 0, 0), rect)
        self.replace_image(self.image)
        
