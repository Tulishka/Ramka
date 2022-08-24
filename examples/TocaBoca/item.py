import math

import pygame

from movable import Movable
from ramka import Vector, Input


class Item(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)


    def draw(self, dest: pygame.Surface):
        super().draw(dest)

        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            icn=self.get_icon()
            pos = self.screen_pos() - (icn.get_size()[0]/2, icn.get_size()[1] + self.get_size()[1]/2 ) - self.image_offset + Vector(0,3*math.sin(self.time*8))
            dest.blit(icn, dest=pygame.Rect(pos, Vector(0)))

    def get_icon(self):
        return self._get_icon(background=(100, 100, 180), border=(70, 70, 100))
