from examples.TocaBoca.base_item import DropZone
from examples.TocaBoca.item import Item
from ramka import Sprite


class Bag(Item):
    def __init__(self, name, *a, **b):
        super().__init__(name, *a, **b)

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return super().can_accept_dropzone_object(dropzone, obj) and self.state.id == 2
