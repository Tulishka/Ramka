from typing import Dict, Union, List, Iterable, Callable, Tuple

import pygame
from .shared import Vector, Rect
from .animation import FlipStyle
from .timers import Timers


class GameObject: ...



class GameObject:
    from .component import Component

    def __init__(self):
        from .transform import Transform
        from .layers import Layer
        from .state import State

        self.transform: Transform = Transform(self)
        self.components: List[GameObject.Component] = []

        self.state = State(self)
        self.time = 0

        self.enabled: bool = True
        self.visible: bool = True

        self.layer: Union[Layer, None] = None

        self.props = {}
        self.opacity = 1.0

        self.timers = Timers()

        self.event_listeners = []
        self.init_event_listeners()

    def init_event_listeners(self):
        self.event_listeners = []

        for m in self.__dir__():
            m1 = self.__getattribute__(m)
            if callable(m1) and getattr(m1, 'event_descriptor', 0):
                self.event_listeners.append(m1)

    def update(self, deltaTime: float):
        self.time += deltaTime
        self.timers.update(deltaTime)

    def add_component(self, component: Component):
        self.components.append(component)

    def draw(self, dest: pygame.Surface):
        pass

    def draw_components(self, dest: pygame.Surface):
        for c in self.components:
            c.draw(dest)

    def update_components(self, deltaTime: float):
        for c in self.components:
            c.update(deltaTime)

    def change_order(self, delta):
        self.layer.change_order(self, delta)

    def set_layer(self, layer):
        if self.layer is not None:
            self.layer.remove_object(self)
        if layer:
            self.layer = layer
            layer.add_object(self)

    def get_components(self, component_class=None):
        for c in self.components:
            if component_class is None or isinstance(c, component_class):
                yield c

    def on_enter_game(self):
        for c in self.components:
            c.on_enter_game()

    def on_leave_game(self):
        for c in self.components:
            c.on_leave_game()

    def get_rect(self):
        return Rect(self.transform.pos.x - 1, self.transform.pos.y - 1, 2, 2)

    def move_rect(self, offset: Vector):
        pass

    def touch_test(self, point: Vector, func: Callable = None):
        return self.get_rect().colliderect(pygame.Rect(point.x, point.y, 1, 1)) is not None

    def is_collided(self, other: GameObject, func: Callable = None) -> Union[bool, Tuple[int, int]]:
        return other.visible and self.get_rect().colliderect(other.get_rect())

    def get_flip(self) -> FlipStyle:
        return (False, False)

    def get_collided(self, other: Union[GameObject, Iterable[GameObject]], func: Callable = None,
                     test_offset: Union[Vector, None] = None) -> List[Tuple[GameObject, Tuple[int, int]]]:

        if test_offset is not None:
            self.move_rect(test_offset)

        if isinstance(other, GameObject):
            z = self.is_collided(other, func)
            if z:
                return [(other, z)]
            else:
                return []

        a = []
        for i in other:
            z = self.is_collided(i, func)
            if z:
                a.append((i, z))

        if test_offset is not None:
            self.move_rect(-test_offset)

        return a

    def __getitem__(self, item):
        return self.props.get(item, None)

    def __setitem__(self, key, value):
        self.props[key] = value
