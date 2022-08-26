from typing import Callable, Union, Tuple, Iterable

import pygame

from examples.Components.DragAndDrop import DragAndDropController
from nav_bar import NavBar
from ramka import Sprite, GameObject, Vector, Game


class ItemMenu(GameObject):

    def __init__(self, prefabs: Iterable, on_item_down: Callable):
        super().__init__()

        self.back = pygame.Surface(Game.screen_size, pygame.SRCALPHA)
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
        self.navbar = NavBar("item_select", row_direction=Vector(1, 0), pos=(50, 150), parent=self)
        DragAndDropController.controller.cancel_drag()
        DragAndDropController.controller.enabled = False

        def fac(prefab):
            def de(obj, btn):
                if self.on_item_down:
                    self.on_item_down(prefab)
                Game.remove_object(self)

            return de

        for p in self.prefabs:
            self.navbar.add_btn(p["object"], action=fac(p))

    def on_leave_game(self):
        super().on_leave_game()
        DragAndDropController.controller.enabled = True

    def touch_test(self, point: Vector, func: Callable = None):
        return True

    def is_collided(self, other: GameObject, func: Callable = None) -> bool:
        return True

    def draw(self, dest: pygame.Surface):
        super().draw(dest)

        dest.blit(self.back, (0, 0))
