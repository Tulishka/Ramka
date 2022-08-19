from examples.Components.mini_map import MiniMapItem
from ramka import Sprite, GameObject


class ItemIcon(MiniMapItem):

    def get_color(self):
        return (0, 0, 240)

    def get_radius(self):
        return 1

class Fly_item(ItemIcon,Sprite):
    def __init__(self, item, target=None, callback=None, pick_type=None):
        super().__init__(item)
        self.item = item
        self.target = target
        self.callback = callback
        self.spd = 300
        self.pick_type = pick_type
        self.used = False

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.target:

            tt = self.target.transform.pos if isinstance(self.target, GameObject) else self.target

            d = tt - self.transform.pos
            l = d.length()
            if l > 0.01:
                d.scale_to_length(self.spd)
                d = d * deltaTime
                if d.length() > l:
                    d.scale_to_length(l)
                self.transform.pos += d
            elif self.callback:
                self.callback(self)
                self.callback = None
                self.target = None

    def pickable(self):
        return self.pick_type is not None