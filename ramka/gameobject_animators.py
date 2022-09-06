from math import copysign

from ramka import GameObject, Vector
from ramka.timeline import TimeLineProgressInfo, Timeline


class VectorValue:

    def validate_new_val(self, value):
        return value if isinstance(value, Vector) else Vector(value)


class BaseAnimator:

    def __init__(self, game_object: GameObject, new_val, duration, interp_func=None, delay=0, remove_previous=True):
        self.gameObject = game_object

        tag = type(self).__name__
        tl = None
        for c in self.gameObject.get_components(component_class=Timeline, component_tag=tag):
            if remove_previous:
                c.remove()
            else:
                tl = c
            break

        self.tl = tl if tl else Timeline(self.gameObject, tag=type(self).__name__)
        self.new_val = self.validate_new_val(new_val)
        self.duration = duration
        self.delay = delay

        def f(x):
            return x

        self.interp_func = interp_func if interp_func else f

    def validate_new_val(self, value):
        return value

    def __call__(self, *args, **kwargs) -> Timeline:

        def finish(*a):
            # self.apply_value(self.new_val)
            self.apply_value(self.start_val + self.spd * self.interp_func(1))

        # if self.tl.duration():
        #     finish()
        #     self.tl.reset()

        self.start_val = self.get_start_value()
        self.spd = self.new_val - self.start_val

        if self.delay:
            self.tl.wait(self.delay)

        def do(ti: TimeLineProgressInfo):
            self.apply_value(self.start_val + self.spd * self.interp_func(ti.section_progress))

        self.tl.do(do, self.duration, continuous=True).do(finish)

        return self.tl

    def get_start_value(self):
        return 0

    def apply_value(self, value):
        pass

    def cancel(self):
        return self.tl.remove()


class PosAnimator(VectorValue, BaseAnimator):

    def get_start_value(self):
        return self.gameObject.transform.pos

    def apply_value(self, value):
        self.gameObject.transform.pos = value


class ScaleAnimator(VectorValue, BaseAnimator):

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
        self.gameObject.transform.angle = value
