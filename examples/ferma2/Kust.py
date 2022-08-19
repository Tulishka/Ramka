import random

from examples.ferma2.Fly_item import Fly_item
from ramka import Sprite, Animation, Game, Vector


class Kust(Sprite):
    def ani(self):
        return {
        "rost": Animation("ira_sprites/rost.png", 24, True),
        "rezult": Animation("ira_sprites/kust.png", 24, True)
    }

    def __init__(self):
        super().__init__(self.ani())

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.time > 10:
            self.state.animation = "rezult"

    def harvest(self):
        position = self.transform.pos
        Game.remove_object(self)

        def fly(item):
            item.pick_type = 1

        for i in range(random.randint(1, 3)):
            pt = position + Vector(30, 0).rotate(random.randint(0, 360))
            ph = Fly_item("ira_sprites/steavphen.png", pt, fly)
            ph.transform.angle = random.randint(-30, 30)
            ph.transform.pos = position
            Game.add_object(ph)