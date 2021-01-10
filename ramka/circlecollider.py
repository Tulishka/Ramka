from typing import Union

import pygame

from .collider import Collider
from .gameobject import GameObject
from .shared import Vector
from .transformbase import TransformBase


class CircleCollider(Collider):

    def __init__(self, game_oject: GameObject, radius: float, offset: Vector = Vector(), rotate: float = 0):
        super().__init__(game_oject, offset, rotate)

        self.radius = radius

    def get_nearest_point_loc(self, target: Union[GameObject, TransformBase, Vector],
                              local_target: bool = True) -> Vector:

        pos = self.gameObject.transform.pos
        vec = self.gameObject.transform.to_parent_local_coord(target) - pos
        vec.normalize_ip()

        return pos + self.radius * vec

    def get_nearest_point(self, target: Union[GameObject, TransformBase, Vector],
                          local_target: bool = True, parent: Union[TransformBase, None] = None) -> Vector:
        tr = self.gameObject.transform
        if parent is None:
            pos = tr.get_world_transform()._pos
        else:
            pos = tr.to_local_coord(parent, tr, local_target)

        vec = tr.to_local_coord(parent, target, local_target) - pos
        vec.normalize_ip()

        return pos + self.radius * vec

    def draw(self, disp: pygame.Surface):

        tr = self.gameObject.transform.get_world_transform()
        p = tr.add_to_vector(self.get_rotated_offset())
        pygame.draw.circle(disp, (0, 255, 0), p, self.radius * max(tr._scale), 1)
