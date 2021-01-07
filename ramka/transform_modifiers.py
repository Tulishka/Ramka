from .transformbase import TransformBase
import math
from .shared import Vector
from .animation import FlipStyle


class TransformModifier:

    def __init__(self, final_apply=True):
        self.final_apply = final_apply

    def apply_ip(self, transform: TransformBase) -> TransformBase:
        return transform

    def apply(self, transform: TransformBase) -> TransformBase:
        return self.apply_ip(transform.copy())


class RotationNone(TransformModifier):
    def apply_ip(self, transform: TransformBase) -> TransformBase:
        transform.rotate = 0
        transform.scale.xy = abs(transform.scale.x), abs(transform.scale.y)
        return transform


class RotationFree(TransformModifier):
    def __init__(self, discrete: int = 0):
        super().__init__()
        self.discrete = discrete

    def apply_ip(self, transform: TransformBase) -> TransformBase:
        transform.rotate = transform.rotate if self.discrete == 0 else ((round(
            transform.rotate) + (self.discrete >> 1)) // self.discrete) * self.discrete
        return transform


class RotationFlip(TransformModifier):
    def __init__(self, flip_style: FlipStyle):
        super().__init__()
        self.flip_style = flip_style

    def apply_ip(self, transform: TransformBase) -> TransformBase:
        v = Vector(1.0, 0.0)
        v.rotate_ip(transform.rotate)
        if self.flip_style[0] and v.x < 0:
            transform.scale.x = -transform.scale.x
        if self.flip_style[1] and v.y < 0:
            transform.scale.y = -transform.scale.y

        transform.rotate = 0
        return transform


class RotationTarget(TransformModifier):
    def __init__(self, pos: Vector, shift=0.0):
        super().__init__()
        self.pos = pos
        self.shift = shift

    def apply_ip(self, transform: TransformBase) -> TransformBase:
        angle = -Vector(1.0, 0.0).angle_to(self.pos - transform.pos)
        transform.rotate = angle + self.shift
        return transform


class RotationCopy(TransformModifier):
    def __init__(self, target: TransformBase):
        super().__init__()
        self.target = target

    def apply_ip(self, transform: TransformBase) -> TransformBase:
        transform.rotate = self.target.rotate
        transform.scale = Vector(math.copysign(transform.scale.x, self.target.scale.x),
                                 math.copysign(transform.scale.y, self.target.scale.y))
        return transform


defaultTransformModifier = RotationFree(1)
