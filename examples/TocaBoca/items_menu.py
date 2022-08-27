import math
from random import random, choice
from typing import Callable, Union, Tuple, Iterable

import pygame

from creature import Creature
from base_item import BaseItem
from lighting import Lighting
from examples.Components.DragAndDrop import DragAndDropController
from nav_bar import NavBar
from ramka import Sprite, GameObject, Vector, Game, interp_func_cubic, interp_func_spring, Circle
from ramka.gameobject_animators import ScaleAnimator, AngleAnimator


class ItemMenu(GameObject):

    def __init__(self, prefabs: Iterable, on_item_down: Callable):
        super().__init__()

        self.back = pygame.Surface(Game.размерЭкрана, pygame.SRCALPHA)
        self.back.fill((0, 0, 0, 200))

        self.prefabs = list(prefabs)

        self.navbar: NavBar = None

        self.on_item_down = on_item_down

    @Game.on_mouse_down(button=1)
    def mdown(self):
        Game.remove_object(self)

    @Game.on_mouse_up(button=1)
    def mup(self):
        pass

    def on_enter_game(self):
        super().on_enter_game()
        self.navbar = NavBar("item_select", gap=10, row_direction=Vector(1, 0),
                             pos=(max(50, Game.ширинаЭкрана * 0.10), 150),
                             max_size=Game.ширинаЭкрана * 0.80, parent=self)
        DragAndDropController.controller.cancel_drag()
        DragAndDropController.controller.enabled = False

        def fac(prefab):
            def de(navbat, btn):
                if not navbat.present:
                    if self.on_item_down:
                        self.on_item_down(prefab)
                    Game.remove_object(self)

            return de

        f = [interp_func_cubic, interp_func_spring]

        for i, p in enumerate(self.prefabs):
            p["object"].update_icon_args(size=80)
            pid = p["object"].type_uid

            if isinstance(p["object"], Creature):
                present = Game.get_object(clas=BaseItem, filter=lambda x: x.type_uid == pid)
                sub = Circle(radius=4, color=(0, 255, 0) if not present else (200, 0, 0))
            else:
                sub = None
                present = False

            nb = self.navbar.add_btn(p["object"], action=fac(p), sub_obj=sub)
            nb.present = present
            nb.transform.scale = 0.05, 0.05
            t = 0.05 + 0.25 * random()
            if random() > 0.7:
                t += random() * 0.2
            ScaleAnimator(nb, Vector(1.0), t)().kill()
            if random() > 0.6:
                nb.transform.angle = 10 + random() * 200
                AngleAnimator(nb, 0, 0.3 + 0.25 * random(), delay=t + (1 - random()) * t * 0.5,
                              interp_func=choice(f))().kill()

    def on_leave_game(self):
        super().on_leave_game()
        DragAndDropController.controller.enabled = True

    def touch_test(self, point: Vector, func: Callable = None):
        return True

    def is_collided(self, other: GameObject, func: Callable = None) -> bool:
        return True

    def draw(self, dest: pygame.Surface):
        super().draw(dest)
        if Lighting.applied_light:
            dest.blit(self.back, (0, 0))
