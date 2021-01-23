from typing import Union

import pygame



class Component: ...


class Component:
    from .gameobject import GameObject

    def __init__(self, game_oject: GameObject):
        self.gameObject = game_oject

    def update(self, deltaTime: float):
        pass

    def draw(self, disp: pygame.Surface):
        pass

    def on_enter_game(self):
        pass

    def on_leave_game(self):
        pass
