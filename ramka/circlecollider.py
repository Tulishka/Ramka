from typing import Union

import pygame

from .game import Game
from .collider import Collider
from .gameobject import GameObject
from .shared import Vector
from .transformbase import TransformBase


class CircleCollider(Collider):

    def __init__(self, game_oject: GameObject, radius: float, offset: Vector = None, rotate: float = 0):
        super().__init__(game_oject, offset, rotate)

        self.radius = radius

    def get_nearest_point_loc(self, target: Vector, local_target: bool = False) -> Vector:

        pos = self.transform.pos
        vec = self.transform.to_local_coord(target) - pos
        vec.normalize_ip()

        return pos + self.radius * vec

    def get_nearest_point(self, target: Vector, local_target: bool = False) -> Vector:

        tt = self.transform.get_world_transform()
        pos = tt.pos

        vec = self.transform.to_local_coord(None, target, False) - pos
        if vec.x!=0 or vec.y!=0:
            vec.normalize_ip()

        p = pos + self.radius * max(tt._scale) * vec

        return p

    def draw(self, disp: pygame.Surface):

        tr = self.transform.get_world_transform()
        pygame.draw.circle(disp, self.color, tr._pos, self.radius * max(tr._scale), 1)

        for ot in Game.get_components(Collider):
            if ot != self:
                np = self.get_nearest_point(ot.transform.get_world_transform()._pos)
                pygame.draw.circle(disp, (255, 255, 0), np, 2, 0)


    def point_inside(self, local_point: Vector) -> bool:
        return local_point.length_squared()<self.radius*self.radius

    def is_collided(self, other: Collider) -> Union[Vector, None]:

        tt = self.transform.get_world_transform()
        pos=tt.pos
        ott=other.transform.get_world_transform()
        my = self.get_nearest_point(ott.pos)
        ll=(my - pos).length_squared()
        ot = other.get_nearest_point(pos) - pos

        if ll > ot.length_squared():
            return my
        else:
            if other.point_inside(ott.sub_from_vector(pos)):
                return my

        return None
