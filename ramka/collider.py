from typing import Union

import pygame

from .transformbase import TransformBase
from .component import Component
from .shared import Vector


class Collider(Component):

    def __init__(self, game_oject: Component.GameObject, offset: Vector = Vector(),rotate : float =0):
        super().__init__(game_oject)
        self.offset = offset
        self.rotate = rotate

    def get_nearest_point_loc(self, target: Union[Component.GameObject, TransformBase, Vector],local_target: bool = True) -> Vector:
        return self.gameObject.transform.pos

    def get_nearest_point(self, target: Union[Component.GameObject, TransformBase, Vector],local_target: bool = True, parent: Union[TransformBase,None] = None) -> Vector:
        return self.gameObject.transform.pos

    def get_rotated_offset(self):
        rotated_offset = self.offset if self.rotate == 0 else self.offset.rotate(-self.rotate)
        return -rotated_offset
