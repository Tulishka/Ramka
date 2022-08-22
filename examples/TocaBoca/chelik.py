from examples.TocaBoca.item import Item


class Chelik(Item):
    def __init__(self, name, *a, **b):
        super().__init__(name, *a, **b)
        self.im_sleep = False

    def on_attach(self, dz):
        super().on_attach(dz)
        if dz.trigger_name == "Sleep":
            self.im_sleep = True

    def on_detach(self, dz):
        super().on_detach(dz)
        self.im_sleep = False

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.im_sleep:
            self.state.animation = "blink"