from typing import List

from .gameobject import GameObject


class Layer:

    def __init__(self, name: str, order: float, visible=True):
        self.name = name
        self.order = order
        self.visible = visible

        self.gameObjects: List[GameObject] = []

    def add_object(self, game_object: GameObject):
        if game_object not in self.gameObjects:
            self.gameObjects.append(game_object)

    def remove_object(self, game_object: GameObject):
        if game_object in self.gameObjects:
            self.gameObjects.remove(game_object)


