from typing import Union, List

import pygame

from .transformbase import TransformBase
from .collider import Collider
from .gameobject import GameObject
from .shared import Vector, Poly


class BoxCollider(Collider):

    def __init__(self, game_oject: GameObject, size: Vector, offset: Vector = Vector(),rotate : float =0):
        super().__init__(game_oject,offset,rotate)

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

    def get_nearest_point(self, target: Union[GameObject, TransformBase, Vector],
                          local_target: bool = True, parent: Union[TransformBase, None] = None) -> Vector:

        tr = self.gameObject.transform
        if parent is None:
            pos = tr.get_world_transform().pos
        else:
            pos = tr.to_local_coord(parent, self.gameObject.transform, local_target)

        vec = tr.to_local_coord(parent, target, local_target) - pos
        vec.normalize_ip()

        return pos

    def get_poly(self):

        tr = self.gameObject.transform.get_world_transform()
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
        ofs=self.get_rotated_offset()
        new_poly = [Vector(-w, h)+ofs, Vector(w, h)+ofs, Vector(w, -h)+ofs, Vector(-w, -h)+ofs]
        return new_poly

    def draw(self, disp: pygame.Surface):
        poly = self.get_poly()
        pygame.draw.polygon(disp, self.color, poly, 1)

