from math import copysign

from ramka import GameObject
from ramka.timeline import TimeLineProgressInfo, Timeline


class BaseAnimator:

    def __init__(self, game_object: GameObject, new_val, duration, interp_func=None):
        self.gameObject = game_object
        self.tl = Timeline(self.gameObject)
        self.new_val = new_val
        self.duration = duration

        def f(x):
            return self.start_val + self.spd * x

        self.interp_func = interp_func if interp_func else f

    def __call__(self, *args, **kwargs) -> Timeline:
        def finish(*a):
            self.apply_value(self.new_val)

        if self.tl.duration():
            finish()
            self.tl.reset()

        self.start_val = self.get_start_value()
        self.spd = self.new_val - self.start_val

        def do(ti: TimeLineProgressInfo):
            self.apply_value(self.interp_func(ti.entire_progress))

        self.tl.do(do, self.duration, continuous=True).do(finish)

        return self.tl

    def get_start_value(self):
        return 0

    def apply_value(self, value):
        pass

    def cancel(self):
        return self.tl.remove()


class PosAnimator(BaseAnimator):

    def get_start_value(self):
        return self.gameObject.transform.pos

    def apply_value(self, value):
        self.gameObject.transform.pos = value


class ScaleAnimator(BaseAnimator):

    def get_start_value(self):
        self.new_val[0] = copysign(self.new_val[0], self.gameObject.transform.scale[0])
        self.new_val[1] = copysign(self.new_val[1], self.gameObject.transform.scale[1])

        return self.gameObject.transform.scale

    def apply_value(self, value):
        self.gameObject.transform.scale = value


class AngleAnimator(BaseAnimator):

    def get_start_value(self):
        return self.gameObject.transform.angle

    def apply_value(self, value):
        print("apply val")
        self.gameObject.transform.angle = value
