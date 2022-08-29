import math
from math import copysign
from typing import Callable

from CameraPosModificator import CameraPosModInterface
from examples.Components.DragAndDrop import Draggable, DragAndDropController
from ramka import GameObject, Game, Input, Vector, Transform, Camera, interp_func_cubic
from ramka.gameobject_animators import PosAnimator
from ramka.timeline import Timeline


class CameraPos(Draggable, GameObject):
    def __init__(self, min_x=0, max_x=0, auto_limits=True):
        super().__init__()
        self.transform.pos = Game.screen_size * 0.5
        self.spd = 700
        self.parent_sort_me_by = "..."
        self.last_position = self.transform.pos
        self.last_spd = Vector(0)
        self.auto_limits = auto_limits
        self.min_x = min_x
        self.max_x = max_x

    def is_inverted_drag(self):
        return True

    def use_world_drag(self):
        return True

    def move_me_top(self):
        return False

    def use_limits(self, pos: Vector):

        if pos.x > self.max_x:
            pos.x = self.max_x
            self.last_spd.x *= -0.1

        if pos.x < self.min_x:
            pos.x = self.min_x
            self.last_spd.x *= -0.1

        return pos

    def drag_set_new_position(self, pos: Vector):
        self.transform.pos = self.use_limits(pos)

    def touch_test(self, point: Vector, func: Callable = None):
        return True

    def update(self, deltaTime: float):
        super(CameraPos, self).update(deltaTime)

        if self.is_dragged() and deltaTime > 0:
            self.last_spd = (self.transform.pos - self.last_position) / deltaTime * 0.5
            self.last_spd[0] = copysign(min(abs(self.last_spd[0]), 500), self.last_spd[0])
            self.last_spd[1] = copysign(min(abs(self.last_spd[1]), 500), self.last_spd[1])
            self.last_position = self.transform.pos
        else:
            self.last_spd *= 0.94

            if self.last_spd.length_squared() > 2:
                self.drag_set_new_position(self.transform.pos + self.last_spd * deltaTime)
            else:
                self.last_spd = Vector(0)

            obj = DragAndDropController.controller and DragAndDropController.controller.get_dragged_object()
            if obj:
                scp = obj.screen_pos()
                if isinstance(obj, CameraPosModInterface):
                    spd = obj.get_scroll_speed()
                    rng = obj.get_scroll_activation_edge_range()
                else:
                    spd = self.spd
                    rng = Game.высотаЭкрана * 0.05
                if Game.высотаЭкрана * 0.20 < scp.y < Game.высотаЭкрана * 0.80:
                    if scp.x < rng:
                        self.last_spd.x = - min(spd, max(4 * abs(self.transform.pos.x - self.min_x), 100))
                    elif scp.x > Game.ширинаЭкрана - rng:
                        self.last_spd.x = min(spd, max(4 * abs(self.transform.pos.x - self.max_x), 100))

    def animate_to(self, gameobject, on_finish) -> Timeline:

        pos = self.use_limits(Transform.to_local_coord(Camera.main.transform, gameobject.transform))

        tl = PosAnimator(Camera.main.target, pos, 0.5, interp_func=interp_func_cubic)()
        if on_finish:
            tl.do(on_finish, 0.5)
        tl.kill()

        return tl
