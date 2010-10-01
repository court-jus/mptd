# -*- coding: utf-8 -*-
from livewires import games
from mptd import mptd

class MptdScreen(games.Screen):
    def __init__(self, width, height, settings):
        games.Screen.__init__(self, width, height)
        games.pygame.display.set_caption('MPTD | By Ghislain Lévêque')
        self.model = mptd(self, settings)

    def tick(self):
        self.model.tick()
