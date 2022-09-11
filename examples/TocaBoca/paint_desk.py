from random import randint, random

import pygame

from base_item import DropZone
from flask_item import FlaskWithLiquid
from examples.Components.DragAndDrop import DragAndDropController
from interier import Interier
from ramka import Vector, Game, Input, Sprite


class PaintDesk(Interier):
    size = (420, 548)
    size2 = Vector(size) * 0.5 - Vector(1, 1)

    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.surface = pygame.Surface(PaintDesk.size)
        self.clear()
        self.spread = 10
        self.default_color = (0, 0, 0)
        self.color = self.default_color
        self.last_draw_point = None

    def clear(self):
        self.surface.fill((255, 255, 255))

    @Game.on_mouse_up(button=1, hover=False)
    def end_paint(self):
        self.last_draw_point = None

    def on_object_attached(self, dz: DropZone, object: Sprite):
        if hasattr(object, "color"):
            self.color = object.color

    def on_object_detached(self, dz: DropZone, object: Sprite):
        if hasattr(object, "color"):
            self.color = self.default_color

    @Game.on_mouse_down(button=1, continuos=True)
    def paint(self):
        if pygame.key.get_mods() & pygame.KMOD_LSHIFT or DragAndDropController.controller.get_dragged_object():
            return False

        # dt = Game.deltaTime()
        p = self.transform.to_local_coord(self.transform, Input.mouse_pos, False) + PaintDesk.size2

        if self.last_draw_point:
            pygame.draw.line(self.surface, self.color, self.last_draw_point, p, int(self.spread * 2.2))
        pygame.draw.circle(self.surface, self.color, p, self.spread)

        # v = Vector(self.spread * (1 + random() * 2), 0)
        # for i in range(int(1000 * dt)):
        #     v.rotate_ip(randint(0, 270))
        # self.surface.set_at((int(p[0] + v.x), int(p[1] + v.y)), (255, 10, 200))

        self.last_draw_point = p

        Game.break_event_loop = True
        return self

    def draw(self, dest: pygame.Surface):
        super().draw(dest)
        p = self.screen_pos() - PaintDesk.size2
        dest.blit(self.surface, p)
        if self.touch_test(Input.mouse_pos):
            pygame.draw.circle(dest, self.color, Input.mouse_pos, self.spread, 1)
