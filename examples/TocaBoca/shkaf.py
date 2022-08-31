from base_item import DropZone
from interier import Interier
from ramka import Sprite, Vector


class Shkaf(Interier):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return (super().can_accept_dropzone_object(dropzone, obj)) and (
                    self.state.id == 2 or dropzone.trigger_name == "Head")

    def on_object_attached(self, dz, obj):
        super().on_object_attached(dz, obj)

    def on_object_detached(self, dz, obj):
        super().on_object_detached(dz, obj)

    def on_state_change(self, old=None):
        super().on_state_change(old)
        for c in self.get_children(clas=DropZone, filter=lambda d: d.trigger_name != "Head"):
            c.visible = self.state.id == 2
