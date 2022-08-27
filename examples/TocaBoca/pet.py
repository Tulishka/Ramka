from creature import Creature


class Pet(Creature):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def def_icon_args(self):
        self.set_icon_args(background=(120, 205, 255), border=(200, 150, 50))
        return self
