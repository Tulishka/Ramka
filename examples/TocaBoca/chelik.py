import pygame

from creature import Creature
from base_item import DropZone
from ramka import Sprite, Vector


class Chelik(Creature):
    def __init__(self, name, *a, **b):
        super().__init__(name, *a, **b)
        self.im_sleep = False

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return super().can_accept_dropzone_object(dropzone, obj) and (
                not self.im_sleep or dropzone.trigger_name == "Head")

    def on_attach(self, dz):
        super().on_attach(dz)
        if dz.trigger_name == "Sleep":
            self.im_sleep = True

    def on_detach(self, dz):
        super().on_detach(dz)
        self.im_sleep = False

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.im_sleep:
            self.state.animation = "blink" + str(self.state.id)

    def get_icon(self):
        return self._get_icon(offset=(0, 0.1), border_radius=60,background=(0, 220, 220), border=(150, 150, 0))

