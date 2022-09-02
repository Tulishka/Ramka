from base_item import DropZone
from key import Key
from shkaf import Shkaf


class Locker(Shkaf):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_state_change(self, old=None):
        super().on_state_change(old)
        for c in self.get_children(clas=DropZone):
            c.visible = self.state.id == 2 if c.trigger_name != "Head" else self.state.id == 1

    def state_next(self):
        for c in self.get_children(clas=DropZone, filter=lambda z:z.trigger_name == "Head" and list(z.get_children(clas=Key))):
            super().state_next()
            break

