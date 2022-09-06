from math import copysign

from base_item_components import Blink, TurnToMoveDirection
from pet import Pet
from ramka import Cooldown, Vector


class Fish(Pet):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        for c in self.get_components(component_class=Blink):
            c.blink = Cooldown(1.5)

        TurnToMoveDirection(self)
