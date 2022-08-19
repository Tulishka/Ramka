from typing import Dict, Union, List, Iterable, Callable, Tuple

import pygame
from .shared import Vector, Rect
from .animation import FlipStyle
from .timers import Timers


class GameObject: ...


class GameObject:
    from .component import Component
    _cur_obj_id = 1

    def __init__(self):
        from .transform import Transform
        from .layers import Layer
        from .state import State

        self._obj_id = GameObject._cur_obj_id
        GameObject._cur_obj_id += 1

        self.components: List[GameObject.Component] = []
        self.layer: Union[Layer, None] = None
        self._parent_sort_me_by = str(self._obj_id).rjust(6, "0")

        self.transform: Transform = Transform(self)

        self.state = State(self)
        self.time = 0

        self.enabled: bool = True
        self.visible: bool = True

        self.props = {}
        self.opacity = 1.0

        self.timers = Timers()

        self.event_listeners = []
        self.__add_event_listers(self)

    @property
    def parent_sort_me_by(self):
        return self._parent_sort_me_by

    @parent_sort_me_by.setter
    def parent_sort_me_by(self,value):
        self._parent_sort_me_by=value
        # if self.transform.parent:
        #     self.layer.sort_object_children(self.transform.parent.gameObject)


    def w_transform(self):
        return self.transform.get_world_transform()

    def screen_pos(self):
        return self.transform.get_world_transform().pos

    def __add_event_listers(self, source):
        for m in source.__dir__():
            try:
                m1 = source.__getattribute__(m)
                if callable(m1) and getattr(m1, 'event_descriptor', 0):
                    self.event_listeners.append(m1)
            except:
                pass

    def __remove_event_listers(self, source):
        for m in source.__dir__():
            try:
                m1 = source.__getattribute__(m)
                if callable(m1) and getattr(m1, 'event_descriptor', 0) and m1 in self.event_listeners:
                    self.event_listeners.remove(m1)
            except:
                pass

    def update(self, deltaTime: float):
        self.time += deltaTime
        self.timers.update(deltaTime)

    def add_component(self, component: Component):
        if not component in self.components:
            self.components.append(component)
            self.__add_event_listers(component)

    def remove_component(self, component: Component):
        if component in self.components:
            self.components.remove(component)
            self.__remove_event_listers(component)

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

    def get_components(self, component_class=None, component_tag=None):
        for c in self.components:
            if (component_class is None or isinstance(c, component_class)) and (
                    component_tag is None or component_tag == c.component_tag):
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
