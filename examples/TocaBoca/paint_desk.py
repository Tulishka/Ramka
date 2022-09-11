from random import randint

import pygame

from interier import Interier
from ramka import Vector, Game, Input


class PaintDesk(Interier):

    size=(420,548)
    size2=Vector(size)*0.5

    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.surface = pygame.Surface(PaintDesk.size)
        self.clear()
        self.spread=10

    def clear(self):
        self.surface.fill((255,255,255))

    @Game.on_mouse_down(button=1,continuos=True)
    def paint(self):
        dt=Game.deltaTime()
        p=self.transform.to_local_coord(self.transform,Input.mouse_pos,False)+PaintDesk.size2

        for i in range(int(1000*dt)):
            self.surface.set_at((int(p[0])+randint(-self.spread,self.spread),int(p[1])+randint(-self.spread,self.spread)),(255,0,0))

        Game.break_event_loop=True
        return self

    def draw(self, dest: pygame.Surface):
        super().draw(dest)
        p=self.screen_pos()-PaintDesk.size2
        dest.blit(self.surface,p)
        if self.touch_test(Input.mouse_pos):
            pygame.draw.circle(dest,(0,255,255),Input.mouse_pos,self.spread,1)

