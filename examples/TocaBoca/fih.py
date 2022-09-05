from base_item_components import Blink
from pet import Pet
from ramka import Cooldown


class Fih(Pet):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        for c in self.get_components(component_class=Blink):
            c.blink = Cooldown(1.5)
