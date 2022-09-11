import pygame

from handable_item import HandableItem
from ramka import Sprite, Game, Vector, RotationNone


class FlaskWithLiquid(HandableItem):
    def __init__(self, anim, pos, color=(100, 100, 255), *a, **b):
        super().__init__(anim, pos, *a, **b)
        h = self.get_size().y
        self.filling = 0.6
        fh = int(h * self.filling)
        o = pygame.Surface((h, fh), flags=pygame.SRCALPHA)
        o.fill(color)
        self.color=color
        self.liquid = Sprite(o)
        self.liquid.use_parent_mask = True
        self.liquid.image_offset = Vector(0, -h * 0.5 + fh * 0.5)
        self.liquid.transform.modifier = RotationNone()

        self.liquid.transform.set_parent(self)
        Game.add_object(self.liquid)


    def on_enter_game(self):
        self.layer.sort_object_children(self)


class FlaskWithRedLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (255, 0, 0), *a, **b)


class FlaskWithPurpleLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (138, 43, 226), *a, **b)


class FlaskWithPinkLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (255, 105, 180), *a, **b)
