from item import Item


class HandableItem(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def on_attach(self, dz):
        super().on_attach(dz)
        if dz.trigger_name == "LeftArm":
            self.transform.angle = 45
        elif dz.trigger_name == "RightArm":
            self.transform.angle = -45
        elif dz.trigger_name in ("Head", "Sleep","Flat"):
            self.transform.angle = -90

    def on_detach(self, dz):
        super().on_detach(dz)
        self.transform.angle = 0