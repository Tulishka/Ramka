from math import copysign

import pygame

from CameraPosModificator import CameraPosModInterface
from base_item_components import TurnToMoveDirection
from creature import Creature
from base_item import DropZone
from examples.Components.DragAndDrop import DragAndDropController
from movable import Movable
from ramka import Input, Sprite, Game, Camera, Vector


class Transport(CameraPosModInterface, Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.path_len = 0
        self.last_y = 0
        self.tc = TurnToMoveDirection(self, right_direction=-1)

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return super().can_accept_dropzone_object(dropzone, obj) and isinstance(obj, Creature)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.tc.enabled = not (pygame.key.get_mods() & pygame.KMOD_LSHIFT)

        if self.tc.enabled:
            self.path_len = 0
        else:

            if self.last_y:
                delta = self.transform.y - self.last_y
            else:
                delta = 0

            self.last_y = self.transform.y

            self.path_len *= 0.96
            self.path_len += abs(delta) + 0.0001

    def update_camera_speed(self, cur_spd: Vector) -> Vector:
        if self.path_len:
            return Vector(-self.tc.direction * (300 + 3 * self.path_len), 0)
        else:
            return None
