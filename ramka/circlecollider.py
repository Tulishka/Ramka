from typing import Union

import pygame

from .game import Game
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
        sc = 1
        if parent is None:
            tt = tr.get_world_transform()
            sc = max(tt._scale)
            pos = tt.add_to_vector(self.get_rotated_offset())
        else:
            pos = tr.to_local_coord(parent, tr, local_target)

        vec = tr.to_local_coord(parent, target, local_target) - pos
        vec.normalize_ip()

        p = pos + self.radius * sc * vec

        return p

    def draw(self, disp: pygame.Surface):

        tr = self.gameObject.transform.get_world_transform()
        p = tr.add_to_vector(self.get_rotated_offset())
        pygame.draw.circle(disp, self.color, p, self.radius * max(tr._scale), 1)

        for ot in Game.get_components(Collider):
            if ot != self:
                np = self.get_nearest_point(ot.gameObject)
                pygame.draw.circle(disp, (255, 255, 0), np, 2, 0)

    def is_collided(self, other: Collider) -> Union[Vector, None]:

        pos = self.gameObject.transform.get_world_transform().pos
        my = self.get_nearest_point(other.gameObject)
        ot = other.get_nearest_point(self.gameObject) - pos
        if (my - pos).length_squared() > ot.length_squared():
            return my

        return None
