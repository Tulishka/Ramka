import math
from random import randint

import pygame.sprite

from examples.Components.DragAndDrop import Draggable
from ramka import Component, Sprite, Game, Cooldown, TransformLockX, defaultTransformModifier, TransformLockY, \
    Transform, Vector, GameObject


class FallingDown(Component):
    floor_y = 800
    max_floor_y = 900
    floor_find_object_class = Sprite

    def __init__(self, game_obj: Sprite):
        super().__init__(game_obj)

        self.spd = 0
        self.g = 900

    def find_floor(self, start_y=None):

        r = self.gameObject.get_rect()
        t, b, l, r, cx = r.y, r.bottom, r.left, r.right, r.centerx

        m = start_y if start_y else max(FallingDown.floor_y, b)

        def colid(obj):
            sp = obj.get_rect()
            return sp.bottom > m and (sp.x < cx < sp.right)

        objs = Game.get_objects(clas=FallingDown.floor_find_object_class,
                                filter=lambda x: colid(x),
                                revers=True)

        for o in objs:
            nm = o.get_rect().bottom
            if nm > m:
                m = nm

        self.floor_y = min(m, FallingDown.max_floor_y)

    @Game.on_mouse_down(button=3, hover=True)
    def mouse_3_click(self):
        self.spd = -max(800 / self.gameObject.mass, 400)

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if isinstance(self.gameObject, Draggable) and self.gameObject.is_dragged():
            self.spd = 0
            return

        p = self.gameObject.get_parent()
        if hasattr(p, "floor_y") and p.floor_y is not None:
            floor_y = p.floor_y
            y = self.gameObject.transform.y
            popup = True
        else:
            floor_y = self.floor_y
            y = self.gameObject.screen_pos().y
            popup = False

        height = self.gameObject.get_rect().height

        y = y + height * 0.5
        if y < floor_y or self.spd < 0:
            self.spd += self.g * deltaTime
        else:
            if 0 < self.spd < 200:
                self.spd = 0
            else:
                self.spd *= -0.3
            if popup:
                self.gameObject.transform.y = floor_y - height * 0.5

        if self.spd:
            self.gameObject.transform.y = self.gameObject.transform.y + self.spd * deltaTime

        if y > FallingDown.max_floor_y:
            self.gameObject.transform.y = FallingDown.max_floor_y - height * 0.5


class ParentJockey(Component):

    def __init__(self, game_obj: Sprite):
        self.host = None
        self.me_start_pos = None
        self.parent_last_pos = None
        super().__init__(game_obj)

        self.spd = 0
        self.g = 850
        self.enabled = True

        self.current_height = 0
        self.max_height = 25

    def on_add(self):
        self.host = self.gameObject.get_parent(clas=Sprite)
        if self.host is None:
            return
        self.me_start_pos = self.gameObject.transform.pos

    def on_remove(self):
        self.host = None
        self.me_start_pos = None

    def update(self, deltaTime: float):
        super().update(deltaTime)
        p = self.host
        if p is None or not self.enabled:
            return

        if self.parent_last_pos is not None:
            dl = p.transform.pos - self.parent_last_pos

            self.current_height += dl.y

        if self.current_height > 0:

            if self.current_height > self.max_height:
                self.current_height = self.max_height

            self.spd += self.g * deltaTime

            self.current_height -= self.spd * deltaTime
            if self.current_height < 0:
                self.current_height = 0

        elif self.current_height < 0:
            self.spd = 0
            self.current_height = 0

        self.gameObject.transform.y = self.me_start_pos.y - self.current_height
        self.parent_last_pos = p.transform.pos


class Blink(Component):
    def __init__(self, obj):
        super().__init__(obj)
        self.blink = Cooldown(0.1)
        self.blink_time = 0

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if not self.blink.ready:
            self.gameObject.state.animation = "blink" + str(self.gameObject.state.id)

        if self.gameObject.time > self.blink_time:
            self.blink.start()
            self.blink_time = self.gameObject.time + randint(1, 8)


class AutoKill(Component):

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.gameObject.time > 3:
            Game.remove_object(self.gameObject)


class FloatingEffect(Component):
    amplitude = 7
    freq = 3

    def on_add(self):
        self.pos = self.gameObject.transform.pos
        self.start_time = Game.time

    def update(self, deltaTime: float):
        super(FloatingEffect, self).update(deltaTime)

        self.gameObject.transform.pos = self.pos + Vector(0, FloatingEffect.amplitude * math.sin(
            FloatingEffect.freq * self.start_time + self.gameObject.time))


class TurnToMoveDirection(Component):
    def __init__(self, game_object: GameObject, right_direction=1, *a, **b):
        super().__init__(game_object,*a, **b)

        self.direction = 1
        self.last_pos = None

        self.right_direction=-1 if right_direction<0 else 1

    def update(self, deltaTime: float):
        super().update(deltaTime)

        tr = self.gameObject.transform
        if self.gameObject.is_dragged():

            if self.last_pos:
                delta = tr.pos - self.last_pos
            else:
                delta = Vector(0)

            if delta.x > 3:
                self.direction = self.right_direction
            elif delta.x < -3:
                self.direction = -self.right_direction

        self.last_pos = tr.pos
        tr.scale_x = math.copysign(tr.scale_x, self.direction)
