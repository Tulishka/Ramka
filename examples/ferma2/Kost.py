from examples.ferma2.Fly_item import Fly_item


class Kost(Fly_item):
    def __init__(self, target):
        def cb(p):
            self.ready = True

        super().__init__("ira_sprites/steavkost.png", target, callback=cb)
        self.spd = 900
        self.ready = False