from math import sin
from random import random, choice

from base_item_components import FloatingEffect
from base_item import DropZone, BaseItem
from creature import Creature
from item import Item
from interier import Interier
from ramka import Component, Vector, Sprite, Game, Cooldown
from ramka.gameobject_animators import ScaleAnimator
from ramka.object_generator import ObjectGenerator


class Puzirik(Sprite):
    def __init__(self, top_y, max_size):
        super().__init__("img/Particles/puz.png")
        r = random() * max_size * 0.5 + max_size * 0.5
        self.transform.scale = 0.1, 0.1
        ScaleAnimator(self, r, 2)().kill()
        self.top_y = top_y
        self.spd = 0
        self.g = -70
        self.faza = 3 * random()
        self.omega = random() * 4 + 1
        self.amplituda = (random() * 80 - 40) * max_size

    def update(self, deltaTime: float):
        super(Puzirik, self).update(deltaTime)
        self.spd += self.g * deltaTime
        self.transform.y += self.spd * deltaTime * self.transform.scale_x

        self.transform.x += self.amplituda * sin(self.omega * self.time + self.faza) * deltaTime

        if self.transform.y < self.top_y:
            Game.remove_object(self)


class AquariumBase:
    def init(self):

        tt = -self.get_size().y * 0.5 + 10

        self.puz_fish = None
        self.fish_cd = Cooldown(0.2)

        def get_puz(g):
            f = self.get_any_fish()
            if f:
                p = Puzirik(tt, max(min(f.get_size().x / 120, 1.2), 0.3)).pos(
                    f.transform.to_local_coord(self.transform, f.transform))
                p.transform.set_parent(self)
                p.parent_sort_me_by = "9" + p.parent_sort_me_by
                self.layer.sort_object_children(self)
                p.use_parent_mask = True
                return p

        self.puzgen = ObjectGenerator(get_puz, 5, [0, 0, 3, 0, 5, 0, lambda *a: random() * 4 + 2])

        self.puzgen.transform.set_parent(self)

    def get_any_fish(self):
        if self.puz_fish is None or self.fish_cd.ready:
            self.fish_cd.start()
            lst = list(self.get_children(clas=Creature, recursive=True))
            if lst:
                self.puz_fish = choice(lst)
            else:
                self.puz_fish = None
        return self.puz_fish

    def on_full_load(self):
        for c in self.get_children(True, clas=BaseItem, recursion_deep=1):
            self.on_object_attached(c.get_parent(), c)

    def on_object_attached(self, dz: DropZone, object: Sprite):
        self.timers.set_timeout(0.4, lambda *a: FloatingEffect(object))
        object.use_parent_mask = True

    def on_object_detached(self, dz: DropZone, object: Sprite):
        object.use_parent_mask = False
        if object == self.puz_fish:
            self.puz_fish = None
        for c in object.get_components(component_class=FloatingEffect):
            c.remove()


class Aquarium(AquariumBase, Interier):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.init()


class AquariumItem(AquariumBase, Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.init()
