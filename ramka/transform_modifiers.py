from .transformbase import TransformBase
import math
from .shared import Vector
from .animation import FlipStyle


class TransformModifier:

    def __init__(self, final_apply=True):
        self.final_apply = final_apply

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        return transform

    def apply(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        return self.apply_ip(transform.copy(), prev_transform)


class TransformLockX(TransformModifier):

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        transform.x=prev_transform.x
        return transform

class TransformLockY(TransformModifier):

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        transform.y=prev_transform.y
        return transform


class RotationNone(TransformModifier):
    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        transform._angle = 0
        transform._scale.xy = abs(transform._scale.x), abs(transform._scale.y)
        return transform


class RotationFree(TransformModifier):
    def __init__(self, discrete: int = 0):
        super().__init__()
        self.discrete = discrete

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        transform._angle = transform._angle if self.discrete == 0 else ((round(
            transform._angle) + (self.discrete >> 1)) // self.discrete) * self.discrete
        return transform


class RotationFlip(TransformModifier):
    def __init__(self, flip_style: FlipStyle):
        super().__init__()
        self.flip_style = flip_style

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        v = Vector(1.0, 0.0)
        v.rotate_ip(transform._angle)
        if self.flip_style[0] and v.x < 0:
            transform._scale.x = -transform._scale.x
        if self.flip_style[1] and v.y < 0:
            transform._scale.y = -transform._scale.y

        transform._angle = 0
        return transform


class RotationFlipLocal(RotationFlip):
    def __init__(self, flip_style: FlipStyle):
        super().__init__(FlipStyle)
        self.flip_style = flip_style
        self.final_apply = False


class RotationTarget(TransformModifier):
    def __init__(self, pos: Vector, shift=0.0):
        super().__init__()
        self.pos = pos
        self.shift = shift

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        angle = -Vector(1.0, 0.0).angle_to(self.pos - transform._pos)
        transform._angle = angle + self.shift
        return transform


class RotationCopy(TransformModifier):
    def __init__(self, target: TransformBase):
        super().__init__()
        self.target = target

    def apply_ip(self, transform: TransformBase, prev_transform: TransformBase) -> TransformBase:
        transform._angle = self.target._angle
        transform._scale = Vector(math.copysign(transform._scale.x, self.target._scale.x),
                                  math.copysign(transform._scale.y, self.target._scale.y))
        return transform


defaultTransformModifier = RotationFree(1)
