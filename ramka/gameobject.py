from typing import Dict, Union

import pygame
from .shared import Vector

class GameObject:
    from .component import Component

    def __init__(self):
        from .game import Game
        from .transform import Transform
        from .layers import Layer
        from .state import State

        self.transform: Transform = Transform(self)
        self.components: Dict[str, GameObject.Component] = {}

        self.state = State(self)
        self.time = 0

        self.game: Game = None
        self.parent: GameObject.Component.GameObject = None
        self.enabled: bool = True
        self.visible: bool = True

        self.layer: Union[Layer, None] = None



    def update(self, deltaTime: float):
        self.time += deltaTime

    def add_component(self, name: str, component: Component):
        self.components[name] = component

    def draw(self, dest: pygame.Surface):
        pass

    def draw_components(self, dest: pygame.Surface):
        for c in self.components.values():
            c.draw(dest)

    def set_layer(self, layer):
        if self.layer is not None:
            self.layer.remove_object(self)
        if layer:
            self.layer = layer
            layer.add_object(self)

    def get_components(self, component_class=None):
        for c in self.components.values():
            if component_class is None or isinstance(c, component_class):
                yield c
