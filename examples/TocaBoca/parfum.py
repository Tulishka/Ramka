import math
from random import random, randint

from base_item_components import TurnToMoveDirection
from item import Item
from ramka import Game, Sprite, Vector, Camera
from ramka.gameobject_animators import ScaleAnimator
from ramka.object_generator import ObjectGenerator


def spd_interp(time):
    return math.exp(-time * 8)


def size_interp(time):
    if time < 0.33333333:
        return math.exp(-0.8 * ((math.e * (3 * time - 1)) ** 2))
    else:
        return 1 - math.exp(12 * (time - 1))


class Oblachko(Sprite):
    max_size = 2
    angle = 30

    def __init__(self, dir):
        super().__init__("img/Particles/puz.png")
        r = random() * Oblachko.max_size * 0.5 + Oblachko.max_size * 0.5
        self.transform.scale = 0.2, 0.2
        self.spd = Vector(dir, 0).rotate(randint(-Oblachko.angle, Oblachko.angle))
        self.life_time = 2 + random() * 2
        ScaleAnimator(self, r, self.life_time, interp_func=size_interp)().kill()

    def update(self, deltaTime: float):
        super().update(deltaTime)

        step = self.spd * deltaTime * spd_interp(self.time / self.life_time) * 500

        self.transform.pos += step

        if self.time > self.life_time:
            Game.remove_object(self)


class Parfum(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.pretty_points.update({"soplo": (0, 0)})
        TurnToMoveDirection(self, right_direction=-1)

    @Game.on_mouse_down(button=3)
    def pshik(self):
        p = ObjectGenerator(self.create_particle, 0.2, 14, loop_callback=lambda x: Game.remove_object(x))
        Game.add_object(p)

    def create_particle(self, c):
        o = Oblachko(1 if self.transform.scale_x < 0 else -1).pos(self.transform.add_to_vector(self.get_pretty_point("soplo")))
        return o
