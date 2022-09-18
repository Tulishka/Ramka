from random import randint, random

import pygame

from painting import Painting
from base_item import DropZone
from flask_item import FlaskWithLiquid
from examples.Components.DragAndDrop import DragAndDropController
from interier import Interier
from ramka import Vector, Game, Input, Sprite
import os
import time


class PaintDesk(Interier):
    size = (420, 548)
    size2 = Vector(size) * 0.5 - Vector(1, 1)

    paints_dir = "paintings"

    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.surface = pygame.Surface(PaintDesk.size)
        self.clear()
        self.spread = 10
        self.default_color = (0, 0, 0)
        self.brush_sizes = [5, 10, 20]
        self.color = self.default_color
        self.last_draw_point = None
        self.empty = True

    def clear(self):
        self.surface.fill((255, 255, 255))
        self.empty = True

    @Game.on_mouse_up(button=1, hover=False)
    def end_paint(self):
        self.last_draw_point = None
        self.empty = False

    def save_painting(self):
        if self.empty:
            return

        tm = time.strftime("%Y%m%d_%H%M%S")
        suf = ""
        os.makedirs(".\\img\\" + PaintDesk.paints_dir, exist_ok=True)
        fname = ""
        for s in range(99):
            suf = "c" + str(s)
            fname = ".\\img\\" + PaintDesk.paints_dir + "\\" + tm + suf + ".png"
            if not os.path.exists(fname):
                break

        mm = pygame.transform.smoothscale(self.surface, (PaintDesk.size[0] // 2, PaintDesk.size[1] // 2))
        pygame.draw.rect(mm, (128, 128, 128), pygame.Rect((0, 0), mm.get_size()), 1)
        pygame.image.save(mm, fname)

        tm = tm + suf
        Game.add_object(Painting(PaintDesk.paints_dir + "|" + tm, self.transform.pos))

    @Game.on_key_down
    def on_keys(self, keys):
        k = {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_DELETE, pygame.K_INSERT, pygame.K_SPACE}.intersection(keys)
        if k and self.touch_test(Input.mouse_pos):
            if pygame.K_DELETE in k:
                self.clear()
            elif pygame.K_INSERT in k:
                self.save_painting()
            elif pygame.K_SPACE in k:
                obj = DragAndDropController.controller.get_dragged_object()
                if isinstance(obj, Sprite):
                    if obj.sprite.image:
                        p = self.transform.to_local_coord(self.transform, obj.screen_pos(),
                                                          False) + obj.get_rotated_offset(
                            obj.transform) + PaintDesk.size2
                        self.surface.blit(obj.sprite.image,
                                          p - Vector(obj.sprite.rect.width // 2, obj.sprite.rect.height // 2))
                        ps = obj.transform.pos - obj.screen_pos()
                        obj.draw_childs(self.surface, ps + p)
            else:
                k = list(k)[0] - pygame.K_1
                self.spread = self.brush_sizes[k]

    def on_object_attached(self, dz: DropZone, object: Sprite):
        if hasattr(object, "color"):
            self.color = object.color

    def on_object_detached(self, dz: DropZone, object: Sprite):
        if hasattr(object, "color"):
            self.color = self.default_color

    @Game.on_mouse_down(button=1)
    def click_once(self):
        if pygame.key.get_mods() & pygame.KMOD_LALT and not DragAndDropController.controller.get_dragged_object():
            pass


    @Game.on_mouse_down(button=1, continuos=True)
    def paint(self):
        if pygame.key.get_mods() & pygame.KMOD_LALT or pygame.key.get_mods() & pygame.KMOD_LSHIFT or DragAndDropController.controller.get_dragged_object():
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
        if self.touch_test(Input.mouse_pos) and not DragAndDropController.controller.get_dragged_object():
            pygame.draw.circle(dest, self.color, Input.mouse_pos, self.spread, 2)
            pygame.draw.circle(dest, (0, 0, 0), Input.mouse_pos, self.spread + 1, 1)
