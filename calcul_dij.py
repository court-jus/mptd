import dijkstra
import pygame
import threading, time

class calcul_dij(threading.Thread):
    def __init__(self,mapdata,w,h,goal):
        threading.Thread.__init__(self)
        self._stopEvent = threading.Event()
        self.mapdata = mapdata
        self.w = w
        self.h = h
        self.goal = goal
        self.need_update = True
        self.times = []
        self.result = {}
       
    def run(self):
        while not self._stopEvent.isSet():
            pygame.time.wait(1)
            if self.need_update:
                self.rundij()
                
    def stop(self):
        self._stopEvent.set()
                
    def rundij(self):
        print "calcul"
        #self.draw_map()
        #self.result = None
        self.need_update = False
        now = pygame.time.get_ticks()
        self.result = dijkstra.Dijkstra(self.graph(),self.goal)[1]
        self.times.append((pygame.time.get_ticks() - now))
        print "fini"
        
    def map_to_coords(self,mapi):
	x = mapi % self.w
	y = mapi / self.w
	return (x,y)

    def coords_to_map(self,coord):
	x = coord[0]
	y = coord[1]
	return x + y * self.w

    def neighbourgs(self,coord):
	(x,y) = coord
	nb = []
	if x > 0:
            nb.append( (x-1 , y  ) )
	if y > 0:
            nb.append( (x   , y-1) )
	if x + 1 < self.w:
            nb.append( (x+1 , y  ) )
	if y + 1 < self.h:
            nb.append( (x   , y+1) )
	return nb

    def draw_map(self):
	for y in range(self.h):
            for x in range(self.w):
                s = str(self.mapdata[y * self.w + x])
                if len(s) < 2:
                    s = " " + s
                print s,
            print

    def graph(self):
	G = {}
	for i in range(len(self.mapdata)):
            c = self.map_to_coords(i)
            Gc = {}
            if self.mapdata[i] != 1:
                continue
            for n in self.neighbourgs(c):
                if self.mapdata[self.coords_to_map(n)] != 1:
                    continue
                else:
                    Gc [n] = 1
            G[c] = Gc
	return G