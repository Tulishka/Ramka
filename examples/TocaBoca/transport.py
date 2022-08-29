from math import copysign

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
                delta = self.screen_pos() - self.last_pos
            else:
                delta = Vector(0)

            self.path_len += delta.length()
            self.path_len *= 0.95

            if Camera.main and Camera.main.target and abs(Camera.main.target.last_spd.x) >= max(delta.x/deltaTime,705):
                delta = Camera.main.target.last_spd

            if delta.x > 3:
                self.direction = -1
            elif delta.x < -3:
                self.direction = 1

        self.last_pos = self.screen_pos()
        self.transform.scale_x = copysign(self.transform.scale_x, self.direction)

    def get_scroll_speed(self) -> float:
        return 700 + 3 * self.path_len

    def get_scroll_activation_edge_range(self) -> float:
        return Game.ширинаЭкрана * (0.05 + min(0.30 * self.path_len / 90,0.40))
