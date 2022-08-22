from examples.TocaBoca.movable import Movable


class Item(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)