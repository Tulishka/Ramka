from movable import Movable


class Creature(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
