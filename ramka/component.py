from typing import Union

import pygame


class Component: ...


class Component:
    from .gameobject import GameObject

    def __init__(self, game_object: GameObject, auto_add=True, tag=""):
        self.gameObject = game_object
        self.component_tag=tag
        if auto_add:
            self.add(game_object)

    def add(self, game_object: GameObject) -> Component:
        self.gameObject = game_object
        self.gameObject.add_component(self)
        self.on_add()
        return self

    def update(self, deltaTime: float):
        pass

    def draw(self, disp: pygame.Surface):
        pass

    def on_enter_game(self):
        pass

    def on_leave_game(self):
        pass

    def on_add(self):
        pass

    def on_remove(self):
        pass

    def remove(self):
        if self in self.gameObject.components:
            self.on_remove()
            self.gameObject.remove_component(self)
