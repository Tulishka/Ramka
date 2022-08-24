from item import Item


class Pet(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)