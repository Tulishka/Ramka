from math import copysign

from creature import Creature
from base_item import DropZone
from examples.Components.DragAndDrop import DragAndDropController
from movable import Movable
from ramka import Input, Sprite


class Transport(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.direction = 1
        self.last_pos = None

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return super().can_accept_dropzone_object(dropzone, obj) and isinstance(obj, Creature)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.is_dragged():
            if self.last_pos:
                delta = self.screen_pos().x - self.last_pos.x
                if delta > 5:
                    self.direction = -1
                elif delta < -5:
                    self.direction = 1

        self.last_pos = self.screen_pos()
        self.transform.scale_x = copysign(self.transform.scale_x, self.direction)
