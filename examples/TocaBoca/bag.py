from base_item import DropZone
from item import Item
from ramka import Sprite


class Bag(Item):
    def __init__(self, name, *a, **b):
        super().__init__(name, *a, **b)

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return (super().can_accept_dropzone_object(dropzone, obj)) and self.state.id == 2

    def on_object_attached(self, dz,obj):
        super().on_object_attached(dz,obj)
        obj.use_parent_mask = True

    def on_object_detached(self, dz, obj):
        super().on_object_detached(dz,obj)
        obj.use_parent_mask = False

