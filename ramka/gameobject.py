from typing import Dict, Union

import pygame




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

    def draw(self, dest: pygame.Surface, options: Dict):
        pass

    def set_layer(self, layer):
        if self.layer is not None:
            self.layer.remove_object(self)
        if layer:
            self.layer = layer
            layer.add_object(self)
