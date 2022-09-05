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

        self.requested_layer_name = ""

        self.state = State(self)
        self.time = 0

        self.enabled: bool = True
        self._visible: bool = True
        self._parent_visible = None

        self.props = {}
        self.opacity = 1.0

        self.timers = Timers()

        self.event_listeners = []
        self._messages_handlers = []

        self.__add_event_listers(self)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        for c in self.get_children(recursive=True):
            c._parent_visible = None

    def is_visible(self):
        if self._visible and self.transform.parent:
            if self._parent_visible is None:
                self._parent_visible = self.transform.parent.gameObject.is_visible()

            return self._parent_visible
        return self._visible

    @property
    def parent_sort_me_by(self):
        return self._parent_sort_me_by

    @parent_sort_me_by.setter
    def parent_sort_me_by(self, value):
        self._parent_sort_me_by = value
        # if self.transform.parent:
        #     self.layer.sort_object_children(self.transform.parent.gameObject)

    def get_children(self, recursive=False, clas=None, filter: Callable[[GameObject], bool] = None) -> Iterable[
        GameObject]:
        for c in self.transform.children:
            if (clas is None or isinstance(c.gameObject, clas)) and (not callable(filter) or filter(c.gameObject)):
                yield c.gameObject
            if recursive:
                for v in c.gameObject.get_children(recursive=recursive, clas=clas, filter=filter):
                    yield v

    def get_parent(self, clas=None, filter: Callable[[GameObject], bool] = None) -> GameObject:
        p = self.transform.parent
        if not p:
            return None
        p = p.gameObject

        if clas or filter:
            if not ((clas is None or isinstance(p, clas)) and (not callable(filter) or filter(p))):
                p = p.get_parent(clas, filter)

        return p

    def get_all_parents(self, clas=None, filter: Callable[[GameObject], bool] = None) -> List[GameObject]:
        res = []
        p = self.transform.parent

        while p:
            if (clas is None or isinstance(p, clas)) and (not callable(filter) or filter(p)):
                res.append(p.gameObject)
            p = p.parent

        return res

    def on_message(self, sender: GameObject, name, param):
        for mh in self._messages_handlers:
            if (not mh.name or mh.name == name) and (not mh.sender or isinstance(sender, mh.sender)):
                mh(sender, name, param)

    def send_message(self, receiver: Union[GameObject, Iterable[GameObject]], name, param,
                     asyn_callback: Callable = None):
        if isinstance(receiver, GameObject):
            receiver = [receiver]
        for object in receiver:
            if not asyn_callback:
                return object.on_message(self, name, param)
            else:
                def dd(*ar):
                    a = object.on_message(self, name, param)
                    if callable(asyn_callback):
                        asyn_callback(a)

                object.timers.set_timeout(0, dd)

    def w_transform(self):
        return self.transform.get_world_transform()

    def screen_pos(self):
        return self.transform.get_world_transform().pos

    def pos(self, *argv):
        if len(argv):
            if isinstance(argv[0], Iterable):
                self.transform.pos = argv[0]
            else:
                if len(argv) > 1:
                    self.transform.pos = argv[0], argv[1]
                else:
                    self.transform.pos = argv[0], argv[0]
            return self
        else:
            return self.transform.pos

    def __add_event_listers(self, source):
        for m in source.__dir__():
            try:
                m1 = source.__getattribute__(m)
                if callable(m1):
                    de = getattr(m1, 'event_descriptor', 0)
                    if de == 3:
                        self._messages_handlers.append(m1)
                    elif de:
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
        for dz in self.get_children():
            from ramka import Game
            Game.add_object(dz)

        self.layer.sort_object_children(self)

        for c in self.components:
            c.on_enter_game()

    def on_leave_game(self):
        for c in self.components:
            c.on_leave_game()

        if self.transform.parent:
            self.transform.detach()

    def get_rect(self):
        return Rect(self.transform.pos.x - 1, self.transform.pos.y - 1, 2, 2)

    def move_rect(self, offset: Vector):
        pass

    def touch_test(self, point: Vector, func: Callable = None):
        return self.get_rect().colliderect(pygame.Rect(point.x, point.y, 1, 1)) is not None

    def is_collided(self, other: GameObject, func: Callable = None) -> Union[bool, Tuple[int, int]]:
        return other.is_visible() and self.get_rect().colliderect(other.get_rect())

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
