from math import copysign

import pygame

from CameraPosModificator import CameraPosModInterface
from creature import Creature
from base_item import DropZone
from examples.Components.DragAndDrop import DragAndDropController
from movable import Movable
from ramka import Input, Sprite, Game, Camera, Vector


class Transport(CameraPosModInterface, Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.direction = 1
        self.last_pos = None
        self.path_len = 0

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return super().can_accept_dropzone_object(dropzone, obj) and isinstance(obj, Creature)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.is_dragged():

            if self.last_pos:
                delta = self.transform.pos - self.last_pos
            else:
                delta = Vector(0)

            if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                self.path_len *= 0.96
                self.path_len += abs(delta.y)+0.0001
            else:

                if delta.x > 3:
                    self.direction = -1
                elif delta.x < -3:
                    self.direction = 1

                self.path_len = 0

        self.last_pos = self.transform.pos
        self.transform.scale_x = copysign(self.transform.scale_x, self.direction)

    def update_camera_speed(self, cur_spd: Vector) -> Vector:
        if self.path_len:
            return Vector(-self.direction * (300 + 3 * self.path_len), 0)
        else:
            return None
