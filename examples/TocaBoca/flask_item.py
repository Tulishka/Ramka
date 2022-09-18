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
        self.color = color
        self.liquid = Sprite(o)
        self.liquid.use_parent_mask = True
        self.liquid.image_offset = Vector(0, -h * 0.5 + fh * 0.5)
        self.liquid.transform.modifier = RotationNone()
        self.liquid.transform.set_parent(self)

    def get_init_dict(self):
        a = super().get_init_dict()
        a.update({
            "color": list(self.color)
        })
        return a

    @staticmethod
    def get_creation_params(dict, parent):
        p,pp = super(FlaskWithLiquid,FlaskWithLiquid).get_creation_params(dict, parent)
        pp["color"]=dict.get("color",(128,128,128))
        return p,pp

    def on_enter_game(self):
        Game.add_object(self.liquid)
        # self.layer.sort_object_children(self)


class FlaskWithRedLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (255, 0, 0))


class FlaskWithPurpleLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (138, 43, 226))


class FlaskWithPinkLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (255, 105, 180))


class FlaskWithWiteLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (255, 255, 255))


class FlaskWithGreenLiquid(FlaskWithLiquid):
    def __init__(self, anim, pos, *a, **b):
        super().__init__(anim, pos, (0, 255, 0))
