import glob
from random import random, randint
from typing import Dict, Union, List

import pygame

from examples.Components.DragAndDrop import Draggable, DragAndDropController
from ramka import Sprite, Game, Animation, Cooldown, Camera, Component, Input, GameObject, Vector, ObjectFilter
from ramka.trigger import Trigger

Game.init('TocaBoca')
Game.цветФона = 250, 250, 250


# todo: по разным файлам разнести классы
# todo: предмет нельзя прикрепить к DropZone если 1) он шире чем докер 2) если место занято 3) если не подходящий класс
# todo: анимировать прикреплении объекта к DropZone, анимимровать конец перемещения (на новое место на экране)
# todo: перемещение камеры


class FallingDown(Component):
    def __init__(self, game_obj: Sprite):
        super().__init__(game_obj)
        self.floor_y = 587

        self.spd = 0
        self.g = 900
        self.enabled = True

    @Game.on_mouse_down(button=3,hover=True)
    def mouse_3_click(self):
        self.spd=-max(800 / self.gameObject.mass,400)

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if not self.enabled or isinstance(self.gameObject, Draggable) and self.gameObject.is_dragged():
            self.spd = 0
            return

        y = self.gameObject.screen_pos().y + self.gameObject.get_computed_size().y * 0.5
        if y < self.floor_y or self.spd < 0:
            self.spd += self.g * deltaTime
        elif self.spd > 0:
            if self.spd < 200:
                self.spd = 0
                # self.gameObject.transform.y = self.floor_y + 1 - self.gameObject.get_computed_size().y * 0.5

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


class BaseItem(Sprite):
    ...


class DropZone(Trigger):
    def __init__(self, parent: BaseItem, name, pos: Vector = None, radius=None):
        super().__init__(name, pos, radius, parent)

    def can_attach_object(self, object: GameObject):
        return True

    def attach_object(self, object: GameObject):
        object.transform.set_parent(self, True)
        self.layer.sort_object_children(self.get_parent())
        return True

    def detach_object(self, object: GameObject):
        object.transform.detach(True)
        return True


class FrontPart(Draggable, Sprite):
    def __init__(self, animations: Union[Animation, pygame.Surface, str, Dict[str, Animation]], parent: BaseItem):
        super().__init__(animations)
        self.transform.set_parent(parent)
        self.parent_sort_me_by = "__" + self.parent_sort_me_by

    @Game.on_mouse_down(hover=True)
    def mouse_down_proxy(self,btn):
        return self.get_parent()

    @Game.on_mouse_up(hover=True)
    def mouse_up_proxy(self,btn):
        return self.get_parent()

    def on_drag_start(self):
        p = self.get_parent()
        if isinstance(p, Draggable):
            p.on_drag_start()
            return self.get_parent()
        else:
            return False


class BaseItem(Sprite):
    dd_manager: DragAndDropController = None

    def __init__(self, anim: Union[str, Dict], pos, mass=None):
        if isinstance(anim, str):
            self.name = anim.split("|")[-1]
            animations = BaseItem.create_animation(anim)
        else:
            animations = anim
            self.name = "no name"

        super().__init__(animations)
        self.drop_zones = []
        self.state.id = 1
        self.transform.pos = pos
        self.mouse_start_point = None

        if not BaseItem.dd_manager:
            BaseItem.dd_manager = Game.get_object(clas=DragAndDropController)

        if mass:
            self.mass = mass
        else:
            self.update_mass()

        if "blink" in self.animations:
            Blink(self)

        self.front_object = None
        if isinstance(anim, str):
            front_anim = BaseItem.create_animation(anim, "_f")
            if front_anim:
                self.front_object = FrontPart(front_anim, self)

    def on_enter_game(self):
        if self.front_object:
            Game.add_object(self.front_object)

    @Game.on_child_add(clas=Draggable, recursively=True)
    def new_child(self, obj):
        pass

    @Game.on_child_remove(clas=Draggable, recursively=True)
    def del_child(self, obj):
        pass

    @staticmethod
    def create_animation(name, suffix=""):
        a = name.split("|")
        directory = a[-2]
        name = a[-1]
        obj = {}
        files = list(glob.glob(f".\\img\\{directory}\\{name}{suffix}_?.png"))
        files.sort()
        for f in files:
            if f[-5] == "m":
                obj["blink"] = Animation(f, 5, True)
            elif f[-5].isdigit():
                obj[f"state{f[-5]}"] = Animation(f, 5, True)
        return obj

    def drop_zone_add(self, name, pos: Vector = None, radius=35) -> BaseItem:

        Game.add_object(DropZone(self, name, pos, radius))

        return self

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
        if self.front_object:
            self.front_object.state.animation = self.state.animation

    def update_mass(self):
        sq = self.get_size()
        self.mass = sq.x * sq.y / (100 * 100)
        if self.mass < 1:
            self.mass = 1
        return self.mass


class Interier(BaseItem):
    def __init__(self, *a, **b):
        super(Interier, self).__init__(*a, **b)


class Movable(Draggable, BaseItem):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)
        self.__fallcomp = FallingDown(self)

        self.last_position = self.transform.pos
        self.last_vert_spd = 0

        self.__restore_parent = None

    def on_drag_start(self):
        self.detach()

    def is_attachable(self):
        return True

    def can_attach_to(self, dz: DropZone):
        return dz.can_attach_object(self)

    def is_attached(self):
        return isinstance(self.get_parent(), DropZone)

    def attach_to(self, dz: DropZone):
        if not self.is_attached():
            self.__restore_parent = self.get_parent()
            if dz.attach_object(self):
                self.transform.pos = 0, 0
                self.on_attach(dz)

    def detach(self):
        if self.is_attached():
            dz = self.get_parent()

            if isinstance(dz, DropZone):
                res = dz.detach_object(self)
            else:
                res = True
                self.transform.detach(True)

            if res:
                if self.__restore_parent:
                    self.transform.set_parent(self.__restore_parent, from_world=True)
                    self.__restore_parent = None
                self.on_detach(dz)

    def on_attach(self, dz):
        self.__fallcomp.enabled = False

    def on_detach(self, dz):
        self.__fallcomp.enabled = True

    def on_drag_end(self):
        if self.is_attachable():
            ll = list(Game.get_objects(clas=DropZone, filter=lambda x: self not in x.get_all_parents()))
            for dz in reversed(ll):
                if dz.is_collided(self) or dz.is_collided(Input.mouse_pos):
                    if self.can_attach_to(dz):
                        self.attach_to(dz)
                        return

        if self.last_vert_spd < 0:
            self.__fallcomp.spd = max(self.last_vert_spd / self.mass, -600)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self.is_dragged() and deltaTime > 0:
            self.last_vert_spd = (self.transform.pos.y - self.last_position.y) / deltaTime
        else:
            self.last_vert_spd = 0

        self.last_position = self.transform.pos


class Item(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)


class HandableItem(Item):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def on_attach(self, dz):
        super().on_attach(dz)
        if dz.trigger_name == "LeftArm":
            self.transform.angle = 45
        elif dz.trigger_name == "RightArm":
            self.transform.angle = -45
        elif dz.trigger_name in ("Head", "Sleep"):
            self.transform.angle = -90

    def on_detach(self, dz):
        super().on_detach(dz)
        self.transform.angle = 0


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


Game.add_object(DragAndDropController())

komnata2 = Background("img/komnata2.png")
komnata2.transform.scale = Game.ширинаЭкрана / komnata2.get_size().x, Game.ширинаЭкрана / komnata2.get_size().x
komnata2.transform.pos = Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2
Game.add_object(komnata2)

Game.add_object(Interier("mebel|bed2", (150, 545)).drop_zone_add("Sleep", Vector(0, -50), radius=90))
Game.add_object(Interier("mebel|window", (693, 278)))

Game.add_object(Pet("pets|oblachko", (700, 100)))

Game.add_object(Chelik("pers|pusya", (600, 100))
                .drop_zone_add("LeftArm", Vector(-56, 107))
                .drop_zone_add("RightArm", Vector(60, 107))
                .drop_zone_add("Head", Vector(0, -130), radius=50)
                )

Game.add_object(Item("predmet|rykzak", (600, 100)).drop_zone_add("Bag", Vector(0, 0)))
Game.add_object(HandableItem("predmet|telefon", (650, 100)))
Game.add_object(Item("predmet|kormushka", (700, 100)))

camera = Camera(lock_y=True)
Game.add_object(camera)
Game.run()
