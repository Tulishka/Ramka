from typing import Union, List

import pygame
from .math_utils import *
from .transformbase import TransformBase
from .collider import Collider
from .gameobject import GameObject
from .shared import Vector, Poly
from .game import Game

class BoxCollider(Collider):

    def __init__(self, game_oject: GameObject, size: Vector, offset: Vector = Vector(), rotate: float = 0):
        super().__init__(game_oject, offset, rotate)

        self.__size: Vector = size
        self.__poly: Poly = []
        self.__dirty_signature = Vector(0)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value: Vector):
        self.__size.update(value)
        self.__poly: Poly = []
        self.__dirty_signature = Vector(0)

    def get_nearest_point_loc(self, target: Union[GameObject, TransformBase, Vector],
                              local_target: bool = True) -> Vector:

        pos = self.gameObject.transform.pos
        vec = self.gameObject.transform.to_parent_local_coord(target) - pos
        vec.normalize_ip()

        return pos

    def get_nearest_point(self, target: Vector, local_target: bool = False) -> Vector:

        tt = self.transform.get_world_transform()
        pos = tt.pos

        # vec = self.transform.to_local_coord(None, target, False) - pos
        poly = self.get_poly()

        line=pos,target

        for i, p in enumerate(poly):
            if i == 0:
                p0 = poly[len(poly) - 1]
            else:
                p0 = poly[i - 1]

            cp=line_intersection_point(line,(p0,p))
            if cp is not None:
                return cp

        return pos

    def get_poly(self):

        tr = self.transform.get_world_transform()
        p = Vector(1001, 1001)
        p = tr.add_to_vector(p)
        dirty = p != self.__dirty_signature

        if dirty:
            self.__dirty_signature = p
            self.__poly = self.create_poly()
            for i, p in enumerate(self.__poly):
                self.__poly[i] = tr.add_to_vector(p)

        return self.__poly

    def create_poly(self) -> Poly:
        w = self.__size[0] / 2
        h = self.__size[1] / 2
        new_poly = [Vector(-w, h), Vector(w, h), Vector(w, -h), Vector(-w, -h)]
        return new_poly

    def draw(self, disp: pygame.Surface):
        poly = self.get_poly()
        pygame.draw.polygon(disp, self.color, poly, 1)

        for ot in Game.get_components(Collider):
            if ot != self:
                np = self.get_nearest_point(ot.transform.get_world_transform()._pos)
                pygame.draw.circle(disp, (255, 255, 0), np, 2, 0)


    def point_inside(self, local_point: Vector) -> bool:
        return False

