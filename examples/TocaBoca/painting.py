from item import Item


class Painting(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
