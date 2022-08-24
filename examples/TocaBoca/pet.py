from creature import Creature


class Pet(Creature):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def get_icon(self):
        return self._get_icon(background=(120, 205, 255), border=(200, 150, 50))
