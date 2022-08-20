from typing import Union, Callable, Tuple, Type, List, Iterable
import numpy as np

import pygame

from ramka import GameObject, Vector, point_inside_poly, Input, Game, ObjectFilter


class Trigger(GameObject):

    def __init__(self, trigger_name, pos: Vector = None, radius=None, parent: GameObject = None, color=None, poly=None):
        super().__init__()

        self.trigger_name = trigger_name

        self.radius = radius if radius else 20

        if pos:
            self.transform.pos = pos

        if parent:
            self.transform.set_parent(parent)
            if radius is None:
                r = sum(parent.get_size()) / 4
                if r > 2:
                    self.radius = r

        self.__poly = poly
        self.__w_poly = []
        self.__dirty_signature = Vector(0)

        self.__trigger_listeners = []
        self.color = color
        self.entered = []

        self.__watch_for = []

    def set_squared_poly(self, size):
        w = size[0] / 2
        h = size[1] / 2
        new_poly = [Vector(-w, h), Vector(w, h), Vector(w, -h), Vector(-w, -h)]
        self.set_poly(new_poly)
        return self

    def set_n_poly(self, n, start_angle=0):
        v = Vector(self.radius, 0)
        a = 360 / n
        new_poly = [v.rotate(start_angle + i * a) for i in range(n)]
        self.set_poly(new_poly)
        return self

    def set_poly(self, poly):
        self.__poly = poly
        self.__w_poly = []
        self.__dirty_signature = Vector(0)

    def get_w_poly(self):

        if not self.__poly: return []

        tr = self.transform.get_world_transform()

        p = Vector(1001, 1001)
        p = tr.add_to_vector(p)

        if p != self.__dirty_signature:
            self.__dirty_signature = p
            self.__w_poly = []
            for p in self.__poly:
                self.__w_poly.append(tr.add_to_vector(p).xy)

            self.__w_poly = np.array(self.__w_poly)

        return self.__w_poly

    def w_radius(self):
        tr = self.w_transform()
        return self.radius * (abs(tr.scale.x) + abs(tr.scale.y)) * 0.5

    def is_collided(self, other: Union[GameObject, Vector], func: Callable = None) -> Union[bool, Tuple[int, int]]:

        r = self.w_radius()
        rr = r * r

        if isinstance(other, GameObject):
            pos = other.w_transform().pos
        else:
            pos = other

        dl = pos - self.w_transform().pos

        if dl.length_squared() > rr:
            return False
        else:
            if self.__poly:
                poly = self.get_w_poly()
                return point_inside_poly(pos.x, pos.y, poly)
            else:
                return True

    def add_listener(self, listener: GameObject):
        if listener not in self.__trigger_listeners:
            self.__trigger_listeners.append(listener)

    def remove_listener(self, listener: GameObject):
        if listener in self.__trigger_listeners:
            self.__trigger_listeners.remove(listener)

    def __get_listener(self):
        if self.__trigger_listeners:
            return self.__trigger_listeners
        return self.get_parent()

    def __notify_listeners(self, other, status, deltatime):
        if other not in self.entered:
            if status:
                p = self.__get_listener()
                if p:
                    self.send_message(p, "trigger.enter", other)
                self.entered.append(other)
        elif not status:
            p = self.__get_listener()
            if p:
                self.send_message(p, "trigger.exit", other)
            self.entered.remove(other)
        else:
            p = self.__get_listener()
            self.send_message(p, "trigger.update", (other, deltatime))

    def manual_watch(self, other: Union[
        Callable[[None], Union[GameObject, Vector, Iterable[GameObject]]], GameObject, Vector, Iterable[
            Union[Vector, GameObject]]], deltatime,
                     notify=True):

        if callable(other):
            objs = other()
        else:
            objs = other

        if isinstance(objs, pygame.math.Vector2) or not isinstance(objs, Iterable):
            objs = [objs]

        for obj in objs:
            c = self.is_collided(obj)
            if notify:
                self.__notify_listeners(other if isinstance(obj, pygame.math.Vector2) else obj, c, deltatime)

    def set_watch_for(self, objects: Union[Union[GameObject, Vector, Callable],List[Union[GameObject, Vector, Callable]]]):
        for e in self.entered:
            self.__notify_listeners(e, False, 0)
        self.entered = []
        if isinstance(objects, pygame.math.Vector2) or not isinstance(objects, Iterable):
            objects = [objects]
        self.__watch_for = objects
        return self

    def update(self, deltaTime: float):
        super().update(deltaTime)

        for w in self.__watch_for:
            self.manual_watch(w, deltaTime)

    def draw(self, dest: pygame.Surface):

        if self.color:
            poly = self.get_w_poly()
            if len(poly):
                pygame.draw.polygon(dest, self.color, poly, 1)
            else:
                pygame.draw.circle(dest, self.color, self.screen_pos(), self.w_radius(), 1)
