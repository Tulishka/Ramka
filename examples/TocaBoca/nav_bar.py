from random import random
from typing import Callable, Union, Dict

import pygame

from movable import Movable
from iconable import Iconable
from examples.Components.DragAndDrop import DragAndDropController
from base_item import BaseItem, DropZone
from camera_pos import CameraPos
from ramka import Sprite, Game, Camera, GameObject, Vector, Input, Animation, Cooldown, Transform
from ramka.effects import Effects
from ramka.gameobject_animators import ScaleAnimator, PosAnimator


class NavBtn(Sprite):
    def __init__(self, anim, chelik,
                 action: Union[Callable[[Sprite, int], None], Dict[int, Callable[[Sprite], None]]] = None,
                 update_func: Callable[[], pygame.Surface] = None, action_on_mb_up=False):
        super().__init__(anim)
        self.chelik = chelik
        self.action = action
        self.update_func = update_func
        self.eff = Effects(self)
        self.updated_anim = chelik.state.animation
        self.update_cd = Cooldown(0.5 + random())

        self.start_point = None

        self.on_mup_process: Callable[[int], None] = self.process_button if action_on_mb_up else None
        self.on_mdn_process: Callable[[int], None] = None if action_on_mb_up else self.process_button

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.update_cd.ready:
            self.update_cd.start()
            if self.chelik.state.animation != self.updated_anim and callable(self.update_func):
                self.set_sprite_animations({"default": Animation([self.update_func()], 5, True)})
                self.updated_anim = self.chelik.state.animation

    @Game.on_mouse_up
    def on_mouse_up(self, button):
        if DragAndDropController.controller and isinstance(self.chelik, BaseItem):

            obj = DragAndDropController.controller.get_just_dragged_object()
            if isinstance(obj, Movable):
                dzs = self.chelik.get_children(clas=DropZone, filter=lambda x: obj.can_attach_to(x))
                for dz in dzs:
                    obj.attach_to(dz)
                    DragAndDropController.controller.cancel_drag()
                    return

                obj.on_drag_end()
                DragAndDropController.controller.cancel_drag()
                obj.transform.pos=obj.transform.to_parent_local_coord(self.chelik)

        if self.on_mup_process and (Input.mouse_pos - self.start_point).length_squared() < 30:
            self.on_mup_process(button)

    @Game.on_mouse_down
    def on_mouse_down(self, button):
        self.eff.pulse(duration=0.2)
        self.start_point = Input.mouse_pos
        if self.on_mdn_process:
            self.on_mdn_process(button)
        return self

    def process_button(self, button):

        def tap(t):
            if hasattr(self.chelik, "eff"):
                self.chelik.eff.pulse(duration=0.5, koef=1.05)

        if callable(self.action):
            self.action(self.chelik, button)
        elif self.action and button in self.action:
            self.action[button](self.chelik)
        elif callable(self.chelik):
            self.chelik(button)
        elif not self.action:
            if 3 in button:
                if isinstance(Camera.main.target, CameraPos):
                    Camera.main.target.animate_to(self.chelik, tap)
            elif 1 in button and DragAndDropController.controller:
                if hasattr(self.chelik, "detach"):
                    self.chelik.detach()
                np = self.chelik.transform.to_parent_local_coord(
                    Input.mouse_pos + Vector(0, self.chelik.get_size().y / 4), False)
                self.chelik.transform.pos = np
                DragAndDropController.controller.drag_now(self.chelik)
                sc = self.chelik.transform.scale
                self.chelik.transform.scale = 0.1, 0.1
                ScaleAnimator(self.chelik, sc, 0.2)().kill()


class NavBar(GameObject):

    def __init__(self, name, pos=Vector(40, 40), row_direction=Vector(1, 0)):
        super().__init__()
        self.name = name
        self.row_direction = row_direction
        self.btns_gap = 5
        self.transform.pos = pos - row_direction.rotate(90) * 150
        PosAnimator(self, pos, 0.5)().kill()

        Game.add_object(self, Game.uiLayer)

    def add_btn(self, object: Iconable, prefix: str = "", action_on_mb_up=False, **kwargs):
        for i in self.get_children(filter=lambda x: x.chelik == object):
            return
        nb = NavBtn(object.get_icon(), object, update_func=object.get_icon, action_on_mb_up=action_on_mb_up, **kwargs)
        nb.parent_sort_me_by = str(prefix) + nb.parent_sort_me_by
        nb.transform.set_parent(self)
        Game.add_object(nb, self.layer)
        self.rearrange()

    def remove_btn(self, object: BaseItem):
        for i in self.get_children(filter=lambda x: x.chelik == object):
            i.transform.set_parent(None)
            Game.remove_object(i)
            self.rearrange()
            return

    def rearrange(self):
        self.layer.sort_object_children(self)
        pos = Vector(0)
        for i in self.get_children():
            i.transform.pos = pos
            pos += Vector(i.get_computed_size().x + self.btns_gap,
                          i.get_computed_size().y + self.btns_gap) * self.row_direction.elementwise()
