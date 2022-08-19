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
            # self.sort_object_children(
            #     game_object.transform.parent.gameObject if game_object.transform.parent else game_object)

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

        self.gameObjects.insert(nidx, object)

        self.sort_object_children(object)

    def sort_object_children(self, object: GameObject):
        if object.transform.children:
            idx = self.gameObjects.index(object)
            object.transform.children.sort(key=lambda x: x.gameObject._parent_sort_me_by)
            for c in object.transform.children:
                if c.gameObject in self.gameObjects:
                    self.gameObjects.remove(c.gameObject)
                    self.gameObjects.insert(idx + 1, c.gameObject)
                    idx += 1
            for c in object.transform.children:
                self.sort_object_children(c.gameObject)

    def change_order_first(self, object: GameObject):
        self.change_order(object, order=0)

    def change_order_last(self, object: GameObject):
        if object in self.gameObjects:
            self.gameObjects.remove(object)
            self.gameObjects.append(object)
            self.sort_object_children(object)
