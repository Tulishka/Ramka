import math
from random import randint

from ramka import *

Game.init('Snake')
Game.цветФона = 200, 200, 255

snake_body_spacing = 28

snake_body_length = 20


class Head(Sprite):
    def __init__(self):
        super().__init__("./sprites/sneak_head.png")
        self.transform.scale_xy = 1, 1

    def update(self, deltaTime: float):
        super().update(deltaTime)

        dir = Vector(Input.get("Horizontal"), Input.get("Vertical"))
        v = 600 * deltaTime * dir
        np = self.transform.pos + v
        if dir.length_squared() > 0:
            self.transform.look_at_ip(self.transform.pos + dir, False)
        self.transform.pos = np


class Body(Sprite):
    def __init__(self, parent: Sprite):
        super().__init__("./sprites/sneak_body.png")
        self.parent = parent
        self.transform.xy = parent.transform.xy - Vector(snake_body_spacing, 0)
        self.transform.scale_xy = 1, 1

    def update(self, deltaTime: float):
        super().update(deltaTime)

        step = self.transform.pos - self.parent.transform.pos
        step.scale_to_length(snake_body_spacing*prev.transform.scale_x)
        self.transform.xy = self.parent.transform.pos + step
        self.transform.look_at_ip(self.parent, False)


head = Head()
head.transform.xy = 100, 100
Game.add_object(head)

prev = head
for i in range(snake_body_length):
    body = Body(prev)
    Game.add_object(body)
    prev = body
    scl=1 - i*0.02
    if scl<0.1:
        scl=0.1
    prev.transform.scale_xy = scl, scl



Game.run()
