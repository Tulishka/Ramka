from math import sin

from examples.TocaBoca.base_item import DropZone
from interier import Interier
from ramka import Component, Vector, Sprite, Game


class FloatingEffect(Component):
    amplitude = 7
    freq = 3

    def on_add(self):
        self.pos = self.gameObject.transform.pos
        self.start_time=Game.time

    def update(self, deltaTime: float):
        super(FloatingEffect, self).update(deltaTime)

        self.gameObject.transform.pos = self.pos + Vector(0, FloatingEffect.amplitude * sin(
            FloatingEffect.freq * self.start_time+self.gameObject.time))


class Aquarium(Interier):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def on_object_attached(self, dz: DropZone, object: Sprite):
        FloatingEffect(object)
        object.use_parent_mask = True

    def on_object_detached(self, dz: DropZone, object: Sprite):
        object.use_parent_mask = False
        for c in object.get_components(component_class=FloatingEffect):
            c.remove()
