import glob

import pygame

from examples.Components.DragAndDrop import Draggable, DragAndDropController
from game_classes import GameClasses
from base_item_components import Blink
from iconable import Iconable
from savable import Savable
from typing import Dict, Union
from ramka import GameObject, Sprite, Game, Animation, Vector, Input
from ramka.gameobject_animators import PosAnimator
from ramka.trigger import Trigger


class BaseItem(Sprite):
    ...


class DropZone(Draggable,Savable, Trigger):
    def __init__(self, parent: BaseItem, name, pos: Vector = None, radius=None, max_items=1, accept_class=[]):
        super().__init__(name, pos, radius, parent,color=(255,0,0))
        self.max_items = max_items
        self.accept_class = accept_class

    @staticmethod
    def get_creation_params(dict):
        return [], {
            "parent": dict["parent"],
            "name": dict["trigger_name"],
        }

    def can_attach_object(self, object: GameObject):
        return self.max_items > len(
            self.transform.children) and (not self.accept_class or type(
            object) in self.accept_class) and self.get_parent().can_accept_dropzone_object(self, object)

    def attach_object(self, object: GameObject):
        object.transform.set_parent(self, True)
        self.layer.sort_object_children(self.get_parent())
        pos = Vector(0, 0)
        if object.transform.pos.length() > Game.ширинаЭкрана:
            object.transform.pos = pos
        else:
            PosAnimator(object, pos, 0.2)().kill()
        self.get_parent().on_object_attached(self, object)
        return True

    def detach_object(self, object: GameObject):
        object.transform.detach(True)
        self.get_parent().on_object_detached(self, object)
        return True

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        self.max_items = opts['max_items']
        self.accept_class = [GameClasses.get_class(t) for t in opts['accept_class']]
        self.radius = opts['radius']

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "max_items": self.max_items,
            "accept_class": [t.__name__ for t in self.accept_class],
            "radius": self.radius,
            "trigger_name": self.trigger_name,
        })
        return res

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.visible = pygame.key.get_mods() & pygame.KMOD_LSHIFT



class FrontPart(Draggable, Sprite):
    def __init__(self, animations: Union[Animation, pygame.Surface, str, Dict[str, Animation]], parent: BaseItem):
        super().__init__(animations)
        self.transform.set_parent(parent)
        self.parent_sort_me_by = "__" + self.parent_sort_me_by

    @Game.on_mouse_down(hover=True)
    def mouse_down_proxy(self, btn):
        return self.get_parent()

    @Game.on_mouse_up(hover=True)
    def mouse_up_proxy(self, btn):
        return self.get_parent()

    def on_drag_start(self):
        p = self.get_parent()
        if isinstance(p, Draggable):
            bs=p.on_drag_start()
            return bs if isinstance(bs,GameObject) else self.get_parent() if bs!=False else False
        else:
            return False


class BaseItem(Savable, Iconable, Sprite):
    dd_manager: DragAndDropController = None

    def __init__(self, anim: str, pos, mass=None):

        if isinstance(anim, str):
            self.name = anim.split("|")[-1]
            animations = BaseItem.create_animation(anim)
        else:
            print(anim, pos)
            raise Exception("Анимация BaseItem может быть создана только из строки! Неверный тип anim! ")

        self.anim_path = anim

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

        if "blink1" in self.animations:
            Blink(self)

        self.front_object = None
        if isinstance(anim, str):
            front_anim = BaseItem.create_animation(anim, "_f")
            if front_anim:
                self.front_object = FrontPart(front_anim, self)

    def get_init_dict(self):
        res = super().get_init_dict()
        res.update({
            "anim_path": self.anim_path,
            "state.id": self.state.id,
            "mass": self.mass,
        })
        return res

    def init_from_dict(self, opts):
        super().init_from_dict(opts)
        self.state.id = opts["state.id"]
        self.mass = opts["mass"]

    @staticmethod
    def get_creation_params(dict):
        return [], {
            "anim": dict["anim_path"],
            "pos": Vector(dict["transform"]["x"], dict["transform"]["y"]),
        }

    def can_accept_dropzone_object(self, dropzone: DropZone, obj: Sprite):
        return obj.get_size().x < self.get_size().x

    def on_enter_game(self):
        if self.front_object:
            Game.add_object(self.front_object)

    def on_object_attached(self, dz: DropZone, object: Sprite):
        pass

    def on_object_detached(self, dz: DropZone, object: Sprite):
        pass

    @staticmethod
    def create_animation(name, suffix=""):
        a = name.split("|")
        directory = a[-2]
        name = a[-1]
        obj = {}
        files = list(glob.glob(f".\\img\\{directory}\\{name}{suffix}??.png"))
        files.sort()
        for f in files:
            if f[-5] == "m":
                if f[-6].isdigit():
                    i = f[-6]
                else:
                    i = '1'
                obj["blink" + i] = Animation(f, 5, True)
            elif f[-5].isdigit():
                obj[f"state{f[-5]}"] = Animation(f, 5, True)
        return obj

    def drop_zone_add(self, name, pos: Vector = None, radius=35, max_items=1, accept_class=[]) -> BaseItem:

        Game.add_object(DropZone(self, name, pos, radius, max_items, accept_class))

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
