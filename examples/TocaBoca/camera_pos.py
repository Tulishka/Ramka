from math import copysign
from typing import Callable

import pygame

from examples.Components.DragAndDrop import Draggable, DragAndDropController
from ramka import GameObject, Game, Input, Vector


class CameraPos(Draggable, GameObject):
    def __init__(self, min_x=0, max_x=0, auto_limits=True):
        super().__init__()
        self.transform.pos = Game.screen_size * 0.5
        self.spd = 300
        self.parent_sort_me_by = "..."
        self.last_position = self.transform.pos
        self.last_spd = Vector(0)
        self.auto_limits=auto_limits
        self.min_x = min_x
        self.max_x = max_x

    def is_inverted_drag(self):
        return True

    def use_world_drag(self):
        return True

    def move_me_top(self):
        return False

    def drag_set_new_position(self, pos: Vector):
        self.transform.pos = pos

        if self.transform.pos.x > self.max_x:
            self.transform.x = self.max_x
            self.last_spd.x *= -0.1

        if self.transform.pos.x < self.min_x:
            self.transform.x = self.min_x
            self.last_spd.x *= -0.1

    def touch_test(self, point: Vector, func: Callable = None):
        return True

    def update(self, deltaTime: float):
        super(CameraPos, self).update(deltaTime)

        if self.is_dragged() and deltaTime > 0:
            self.last_spd = (self.transform.pos - self.last_position) / deltaTime * 0.5
            self.last_spd[0] = copysign(min(abs(self.last_spd[0]),500),self.last_spd[0])
            self.last_spd[1] = copysign(min(abs(self.last_spd[1]),500),self.last_spd[1])
            self.last_position = self.transform.pos
        else:
            self.last_spd *= 0.94

            if self.last_spd.length_squared() > 1:
                self.drag_set_new_position(self.transform.pos + self.last_spd * deltaTime)

            obj = DragAndDropController.controller.get_dragged_object()
            if obj:
                if obj.screen_pos().x < Game.ширинаЭкрана * 0.05:
                    self.last_spd.x = - min(500,max(4*abs(self.transform.pos.x - self.min_x),100))
                elif obj.screen_pos().x > Game.ширинаЭкрана - Game.ширинаЭкрана * 0.05 :
                    self.last_spd.x = min(500,max(4*abs(self.transform.pos.x - self.max_x), 100))
