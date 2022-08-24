from creature import Creature


class Pet(Creature):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def create_item_icon(self):
        return self._create_icon(background=(120,205,255),border=(200,150,50))
