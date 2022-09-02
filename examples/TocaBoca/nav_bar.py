from random import random
from typing import Callable, Union, Dict, Tuple, Iterable

import pygame

from movable import Movable
from iconable import Iconable
from examples.Components.DragAndDrop import DragAndDropController
from base_item import BaseItem, DropZone
from camera_pos import CameraPos
from ramka import Sprite, Game, Camera, GameObject, Vector, Input, Animation, Cooldown, Transform, interp_func_spring, \
    interp_func_cubic, interp_func_squared
from ramka.effects import Effects
from ramka.gameobject_animators import ScaleAnimator, PosAnimator
from ramka.timeline import Timeline


class NavBtn(Sprite):
    def __init__(self, anim, object,
                 action: Union[Callable[[Sprite, int], None], Dict[int, Callable[[Sprite], None]]] = None,
                 update_func: Callable[[], pygame.Surface] = None, action_on_mb_up=False,
                 visible_func: Callable[[], bool] = None):
        super().__init__(anim)
        self.object = object
        self.action = action
        self.update_func = update_func
        self.eff = Effects(self)
        self.updated_anim = object.state.animation
        self.update_cd = Cooldown(0.3)

        self.visible_func = visible_func

        self.start_point = None

        self.on_mup_process: Callable[[int], None] = self.process_button if action_on_mb_up else None
        self.on_mdn_process: Callable[[int], None] = None if action_on_mb_up else self.process_button

        self.hovering = False
        self.scale_animator: Timeline = None

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.update_cd.ready:
            self.update_cd.start()
            if self.object.state.animation != self.updated_anim and callable(self.update_func):
                self.set_sprite_animations({"default": Animation([self.update_func()], 5, True)})
                self.updated_anim = self.object.state.animation

            if self.visible_func:
                w = self.visible_func()
                if w != self.visible:
                    self.visible = w
                    p = self.get_parent(clas=NavBar)
                    if p:
                        p.rearrange()

        if self.visible:
            hovering = self.touch_test(Input.mouse_pos)
        else:
            hovering = False

        if hovering != self.hovering:
            self.hovering = hovering
            if self.scale_animator:
                self.scale_animator.remove()

            self.scale_animator = ScaleAnimator(self, Vector(1.0 + (0.2 if hovering else 0)), 0.2,
                                                interp_func=interp_func_squared)().kill()

    @Game.on_mouse_up
    def on_mouse_up(self, button):
        if DragAndDropController.controller and isinstance(self.object, BaseItem):

            obj = DragAndDropController.controller.get_just_dragged_object()
            if isinstance(obj, Movable):
                dzs = self.object.get_children(clas=DropZone, filter=lambda x: obj.can_attach_to(x))
                for dz in dzs:
                    obj.attach_to(dz)
                    DragAndDropController.controller.cancel_drag()
                    return

                obj.on_drag_end()
                DragAndDropController.controller.cancel_drag()
                obj.transform.pos = obj.transform.to_parent_local_coord(self.object)

        if not self.start_point:
            self.start_point = Input.mouse_pos

        if self.on_mup_process and (Input.mouse_pos - self.start_point).length_squared() < 30:
            self.on_mup_process(button)

        self.start_point = None

    @Game.on_mouse_down
    def on_mouse_down(self, button):

        self.start_point = Input.mouse_pos
        if self.on_mdn_process:
            self.on_mdn_process(button)
        return self

    def process_button(self, button):
        self.eff.pulse(duration=0.2)

        def tap(t):
            if hasattr(self.object, "eff"):
                self.object.eff.pulse(duration=0.5, koef=1.05)

        if callable(self.action):
            self.action(self, button)
        elif self.action and button in self.action:
            self.action[button](self)
        elif callable(self.object):
            self.object(button)
        elif not self.action:
            if 3 in button:
                if isinstance(Camera.main.target, CameraPos):
                    Camera.main.target.animate_to(self.object, tap)
            elif 1 in button and DragAndDropController.controller:
                if hasattr(self.object, "detach"):
                    self.object.detach()
                np = self.object.transform.to_parent_local_coord(
                    Input.mouse_pos + Vector(0, self.object.get_size().y / 4), False)
                self.object.transform.pos = np
                DragAndDropController.controller.drag_now(self.object)
                sc = self.object.transform.scale
                self.object.transform.scale = 0.1, 0.1
                ScaleAnimator(self.object, sc, 0.2)().kill()


class NavBar(GameObject):

    def __init__(self, name, pos=Vector(40, 40), row_direction=Vector(1, 0), parent=None,
                 max_size=Game.высотаЭкрана * 0.9, gap=5):
        super().__init__()
        self.name = name
        self.row_direction = row_direction
        self.btns_gap = gap
        self.max_size = max_size
        self.transform.pos = pos
        self.short_cuts = []

        if parent:
            self.transform.set_parent(parent)

        Game.add_object(self, Game.uiLayer)

    def add_btn(self, object: Iconable, prefix: str = "", action_on_mb_up=False, sub_obj: GameObject = None,
                hot_key: Union[int, Tuple[int, int]] = None, **kwargs):
        for i in self.get_children(filter=lambda x: x.object == object):
            return
        nb = NavBtn(object.get_icon(), object, update_func=object.get_icon, action_on_mb_up=action_on_mb_up, **kwargs)
        nb.parent_sort_me_by = str(prefix) + nb.parent_sort_me_by
        nb.transform.set_parent(self)
        Game.add_object(nb, self.layer)

        if hot_key:
            if not isinstance(hot_key, Iterable):
                hot_key = (hot_key, 1)
            self.short_cuts.append((nb, hot_key))

        if sub_obj:
            sub_obj.transform.set_parent(nb, False)
            sub_obj.transform.pos = 0.4 * Vector(nb.get_size())
            Game.add_object(sub_obj, self.layer)

        self.rearrange()
        return nb

    def remove_btn(self, object: BaseItem):
        for i in self.get_children(filter=lambda x: x.object == object):
            i.transform.detach()
            Game.remove_object(i)
            for sc in self.short_cuts:
                if sc[0] == i:
                    self.short_cuts.remove(sc)
                    break
            self.rearrange()
            return

    @Game.on_key_down
    def on_key_down(self, keys):
        for sc in self.short_cuts:
            if sc[1][0] in keys and sc[0].enabled and sc[0].is_visible():
                sc[0].process_button([sc[1][1]])

    def update_btns_positions(self):
        pos = Vector(0)
        row = 1
        second_dir = self.row_direction.rotate(90)
        pp = second_dir * Game.высотаЭкрана / 2
        if pp.x > Game.ширинаЭкрана or pp.x < 0 or pp.y > Game.высотаЭкрана or pp.y < 0:
            second_dir = -1 * second_dir

        for i in self.get_children():
            if i.visible:
                i.transform.pos = pos
                pos += Vector(i.get_size().x + self.btns_gap,
                              i.get_size().y + self.btns_gap) * self.row_direction.elementwise()

                gr = (Vector(self.max_size) * self.row_direction.elementwise()).length()
                if gr < (pos * self.row_direction.elementwise()).length():
                    pos = Vector(i.get_size().x + self.btns_gap,
                                 i.get_size().y + self.btns_gap) * row * second_dir.elementwise()
                    row += 1

    def rearrange(self):
        self.layer.sort_object_children(self)
        self.update_btns_positions()
