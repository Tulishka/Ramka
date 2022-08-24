import glob
from typing import Union, Dict

import pygame
from examples.Components.DragAndDrop import DragAndDropController, Draggable
from Iconable import Iconable
from base_item_components import Blink
from ramka import GameObject
from ramka import Sprite, Game, Animation, Vector, Input
from ramka.gameobject_animators import PosAnimator
from ramka.trigger import Trigger


class BaseItem(Sprite):
    ...


class DropZone(Trigger):
    def __init__(self, parent: BaseItem, name, pos: Vector = None, radius=None, max_items=1, accept_class=[]):
        super().__init__(name, pos, radius, parent)
        self.max_items = max_items
        self.accept_class = accept_class

    def can_attach_object(self, object: GameObject):
        return self.max_items > len(
            self.transform.children) and (not self.accept_class or type(
            object) in self.accept_class) and self.get_parent().can_accept_dropzone_object(self, object)

    def attach_object(self, object: GameObject):
        object.transform.set_parent(self, True)
        self.layer.sort_object_children(self.get_parent())
        PosAnimator(object, Vector(0, 0), 0.2)().kill()
        self.get_parent().on_object_attached(self, object)
        return True

    def detach_object(self, object: GameObject):
        object.transform.detach(True)
        self.get_parent().on_object_detached(self, object)
        return True


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
            p.on_drag_start()
            return self.get_parent()
        else:
            return False


class BaseItem(Iconable,Sprite):
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

        if "blink1" in self.animations:
            Blink(self)

        self.front_object = None
        if isinstance(anim, str):
            front_anim = BaseItem.create_animation(anim, "_f")
            if front_anim:
                self.front_object = FrontPart(front_anim, self)

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

