from typing import Union, Iterable, Tuple

import pygame


from .transformbase import TransformBase
from .component import Component
from .shared import Vector


class Collider(Component): ...


class Collider(Component):

    def __init__(self, game_oject: Component.GameObject, offset: Vector = None, rotate: float = 0):
        from .transform import Transform
        super().__init__(game_oject)
        self.transform = Transform(game_oject,offset,rotate,Vector(1.0),game_oject.transform)
        self.color = (0, 255, 0)

    def get_nearest_point_loc(self, target: Vector, local_target: bool = False) -> Vector:
        return self.transform.pos

    def get_nearest_point(self, target: Vector, local_target: bool = False) -> Vector:
        return self.transform.get_world_transform().pos

    def get_collided(self, colliders: Iterable[Collider]) -> Union[Tuple[Vector, Collider], None]:
        for c in colliders:
            if c != self:
                col = self.is_collided(c)
                if col is not None:
                    return col, c
        return None

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

    def point_inside(self, local_point: Vector) -> bool:
        return False
