import glob
from random import random, randint
from typing import Dict, Union

from examples.Components.DragAndDrop import Draggable, DragAndDropController
from ramka import Sprite, Game, Animation, Cooldown, Camera, Component, Input, GameObject

Game.init('TocaBoca')
Game.цветФона = 250, 250, 250


class FallingDown(Component):
    def __init__(self, game_obj: Sprite):
        super().__init__(game_obj)
        self.floor_y = 587

        self.spd = 0
        self.g = 900

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if isinstance(self.gameObject, Draggable) and self.gameObject.is_dragged():
            return

        y = self.gameObject.screen_pos().y + self.gameObject.get_computed_size().y * 0.5
        if y < self.floor_y:
            self.spd += self.g * deltaTime
        elif self.spd > 0:
            if self.spd < 200:
                self.spd = 0
                self.gameObject.transform.y = self.floor_y + 1 - self.gameObject.get_computed_size().y * 0.5

            else:
                self.spd *= -0.3
        if self.spd:
            self.gameObject.transform.y = self.gameObject.transform.y + self.spd * deltaTime

        if y > Game.высотаЭкрана - 10:
            self.gameObject.transform.y = Game.высотаЭкрана - 11 - self.gameObject.get_computed_size().y * 0.5


class Blink(Component):
    def __init__(self, obj):
        super().__init__(obj)
        self.blink = Cooldown(0.1)
        self.blink_time = 0

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if not self.blink.ready:
            self.gameObject.state.animation = "blink"

        if self.gameObject.time > self.blink_time:
            self.blink.start()
            self.blink_time = self.gameObject.time + randint(1, 8)


class DropZone(GameObject):
    pass


class Docker(Sprite):
    def __init__(self, anim: Union[str, Dict], pos):
        if isinstance(anim, str):
            anim = Docker.create_animation(anim)

        super(Docker, self).__init__(anim)
        self.drop_zones = []
        self.state.id = 1
        self.transform.pos = pos
        self.mouse_start_point = None
        if "blink" in self.animations:
            Blink(self)

    @staticmethod
    def create_animation(name):
        a = name.split("|")
        directory = a[-2]
        name = a[-1]
        obj = {}
        files = list(glob.glob(f".\\img\\{directory}\\{name}_?.png"))
        files.sort()
        for f in files:
            if f[-5] == "m":
                obj["blink"] = Animation(f, 5, True)
            elif f[-5].isdigit():
                obj[f"state{f[-5]}"] = Animation(f, 5, True)
        return obj

    def drop_zone_add(self, zone):
        pass

    def state_next(self):
        n = f"state{self.state.id + 1}"
        if n in self.animations:
            self.state.id += 1
        else:
            self.state.id = 1

    def state_anim_name(self):
        return f"state{self.state.id}"

    @Game.on_mouse_up(button=1)
    def on_mouse_up(self):
        if self.mouse_start_point:
            self.state_next()

    @Game.on_mouse_down(button=1)
    def on_mouse_down(self):
        self.mouse_start_point = Input.mouse_pos

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.mouse_start_point:
            if (Input.mouse_pos - self.mouse_start_point).length_squared() > 30:
                self.mouse_start_point = None

        self.state.animation = self.state_anim_name()


class Interier(Docker):
    def __init__(self, *a, **b):
        super(Interier, self).__init__(*a, **b)


class Movable(Draggable, Docker):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        FallingDown(self)


class Item(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)


class Pet(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)


class Background(Sprite):
    def __init__(self, image):
        super().__init__(image)

    def update(self, deltaTime: float):
        super(Background, self).update(deltaTime)
        Game.debug_str = str(Input.mouse_pos)


class Chelik(Item):
    def __init__(self, name, *a, **b):
        super().__init__(name, *a, **b)
        self.name = name.split("|")[-1]

    def update(self, deltaTime: float):
        super().update(deltaTime)


komnata2 = Background("img/komnata2.png")
komnata2.transform.scale = Game.ширинаЭкрана / komnata2.get_size().x, Game.ширинаЭкрана / komnata2.get_size().x
komnata2.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2
Game.add_object(komnata2)

Game.add_object(Interier("mebel|bed2", (150, 545)))
Game.add_object(Interier("mebel|window", (693, 278)))

Game.add_object(Pet("pets|oblachko", (700, 100)))

Game.add_object(Chelik("pers|pusya", (600, 100)))

Game.add_object(Item("predmet|rykzak", (600, 100)))
Game.add_object(Item("predmet|telefon", (650, 100)))
Game.add_object(Item("predmet|kormushka", (700, 100)))

Game.add_object(DragAndDropController())

camera = Camera(lock_y=True)
Game.add_object(camera)
Game.run()
