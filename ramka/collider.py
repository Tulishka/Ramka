from typing import Union, Iterable, Tuple

import pygame

from .transformbase import TransformBase
from .component import Component
from .shared import Vector


class Collider(Component): ...


class Collider(Component):

    def __init__(self, game_oject: Component.GameObject, offset: Vector = Vector(), rotate: float = 0):
        super().__init__(game_oject)
        self.offset = offset
        self.rotate = rotate
        self.color = (0, 255, 0)

    def get_nearest_point_loc(self, target: Union[Component.GameObject, TransformBase, Vector],
                              local_target: bool = True) -> Vector:
        return self.gameObject.transform.pos

    def get_nearest_point(self, target: Union[Component.GameObject, TransformBase, Vector], local_target: bool = True,
                          parent: Union[TransformBase, None] = None) -> Vector:
        return self.gameObject.transform.pos

    def get_rotated_offset(self):
        rotated_offset = self.offset if self.rotate == 0 else self.offset.rotate(-self.rotate)
        return -rotated_offset

    def get_collided(self, colliders: Iterable[Collider]) -> Union[Tuple[Vector, Collider], None]:
        for c in colliders:
            if c != self:
                col = self.is_collided(c)
                if col is not None:
                    return col, c
        return None

    def is_collided(self, other: Collider) -> Union[Vector, None]:
        return None
