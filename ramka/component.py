from typing import Union

import pygame


class Component: ...


class Component:
    from .gameobject import GameObject

    def __init__(self, game_oject: GameObject, auto_add=True, tag=""):
        self.gameObject = game_oject
        self.component_tag=tag
        if auto_add:
            self.add(game_oject)

    def add(self, game_object: GameObject) -> Component:
        self.gameObject = game_object
        self.gameObject.add_component(self)
        return self

    def update(self, deltaTime: float):
        pass

    def draw(self, disp: pygame.Surface):
        pass

    def on_enter_game(self):
        pass

    def on_leave_game(self):
        pass

    def remove(self):
        self.gameObject.remove_component(self)
        # self.gameObject = None
