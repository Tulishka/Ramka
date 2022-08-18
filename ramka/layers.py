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

    def change_order(self, object: GameObject, delta=None, order=None):

        idx = self.gameObjects.index(object)

        if delta is not None:
            nidx = idx + delta
        else:
            nidx = order

        if nidx < 0:
            nidx = 0

        self.gameObjects.remove(object)
        if nidx > idx and nidx > 0:
            nidx -= 1

        if nidx >= len(self.gameObjects):
            self.gameObjects.append(object)
        else:
            self.gameObjects.insert(nidx, object)

    def change_order_first(self, object: GameObject):
        self.change_order(object, order=0)

    def change_order_last(self, object: GameObject):
        self.change_order(object, order=len(self.gameObjects) - 1)
