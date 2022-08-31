from item import Item


class HandableItem(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.update_icon_args(angle=-45)

    def on_attach(self, dz):
        super().on_attach(dz)
        if dz.trigger_name == "LeftArm":
            self.transform.angle = 45
        elif dz.trigger_name == "RightArm":
            self.transform.angle = -45
        elif dz.trigger_name in ("Head", "Sleep", "Flat"):
            sz = self.get_size()
            if sz[1] > sz[0]:
                self.transform.angle = -90

        dz.update_attached_object_pos(self)

    def on_detach(self, dz):
        super().on_detach(dz)
        self.transform.angle = 0
