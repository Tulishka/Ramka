from typing import Union

from .component import Component
from .shared import Vector


class TransformBase(Component):
    pass


class TransformBase(Component):

    def __init__(self, game_oject: Component.GameObject, pos: Vector = None, rotate: float = 0.0, scale: Vector = None):
        super().__init__(game_oject)

        self._pos: Vector = pos if pos is not None else Vector()
        self._scale: Vector = scale if scale is not None else Vector(1.0)
        self._angle = rotate

    def on_change(self):
        pass

    def copy(self) -> TransformBase:
        return TransformBase(self.gameObject, Vector(self._pos), self._angle, Vector(self._scale))

    def assign_positions(self, other: TransformBase):
        pos=self._pos.xy
        scale = self._scale.xy
        angle= self._angle
        self._pos = Vector(other._pos)
        self._angle = other._angle
        self._scale = Vector(other._scale)
        if angle!=self.angle or pos!=self._pos or scale!=self._scale:
            self.on_change()
        return self

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        xy=self._pos.xy
        self._pos = value
        if xy!=self._pos:
            self.on_change()

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        xy=self._scale.xy
        self._scale = value
        if xy!=self._scale:
            self.on_change()

    @property
    def x(self):
        return self._pos.x

    @x.setter
    def x(self, value):
        v=self._pos.x
        self._pos.x = value
        if value!=v:
            self.on_change()

    @property
    def y(self):
        return self._pos.y

    @y.setter
    def y(self, value):
        v=self._pos.y
        self._pos.y = value
        if v!=value:
            self.on_change()

    @property
    def xy(self):
        return self._pos.xy

    @xy.setter
    def xy(self, value):
        xy=self._pos.xy
        self._pos.xy = value
        if xy!=value:
            self.on_change()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        v=self._angle
        self._angle = value
        if v!=value:
            self.on_change()

    @property
    def scale_x(self):
        return self._scale.x

    @scale_x.setter
    def scale_x(self, value):
        v=self._scale.x
        self._scale.x = value
        if v!=value:
            self.on_change()

    @property
    def scale_y(self):
        return self._scale.y

    @scale_y.setter
    def scale_y(self, value):
        v=self._scale.y
        self._scale.y = value
        if v != value:
            self.on_change()

    @property
    def scale_xy(self):
        return self._scale.xy

    @scale_xy.setter
    def scale_xy(self, value):
        xy=self._scale.xy
        self._scale.xy = value
        if xy!=value:
            self.on_change()

    def look_at_ip(self, target: Union[Vector, TransformBase, Component.GameObject],
                   use_local: bool = True) -> TransformBase:
        if isinstance(target, Component.GameObject):
            target = target.transform

        if isinstance(target, TransformBase):
            if target.gameObject.transform.parent == self.gameObject.transform.parent:
                use_local = True
                target = target._pos
            else:
                target = target.gameObject.transform.get_world_transform()._pos

        if not use_local and self.gameObject.transform.parent is None:
            use_local = True

        if use_local:
            angle = -Vector(1.0, 0.0).angle_to(self._pos - target)
        else:
            pr = self.gameObject.transform.parent.get_world_transform()
            angle = -Vector(1.0, 0.0).angle_to(self.add(pr)._pos - target) - pr._angle

        self._angle = angle
        self.on_change()

        return self

    def look_at(self, target: Union[Vector, TransformBase, Component.GameObject],
                use_local: bool = True) -> TransformBase:
        p = self.copy()
        return p.look_at_ip(target, use_local)

    def add_ip(self, transform: TransformBase) -> TransformBase:

        if transform._scale.x != 1 or transform._scale.y != 1 or self._scale.x != 1 or self._scale.y != 1:
            self._pos *= transform._scale.elementwise()
            self._scale = self._scale.elementwise() * transform._scale

        if transform._angle != 0:
            self._pos.rotate_ip(-transform._angle)

        self._pos += transform._pos
        self._angle += transform._angle
        self.on_change()

        return self

    def sub_ip(self, transform: TransformBase) -> TransformBase:

        self._pos -= transform._pos

        if transform._scale.x != 1 or transform._scale.y != 1 or self._scale.x != 1 or self._scale.y != 1:
            self._pos /= transform._scale.elementwise()
            self._scale = self._scale.elementwise() / transform._scale

        if transform._angle != 0:
            self._pos.rotate_ip(transform._angle)

        self._angle -= transform._angle
        self.on_change()

        return self

    def add(self, transform: TransformBase) -> TransformBase:
        return self.copy().add_ip(transform)

    def sub(self, transform: TransformBase) -> TransformBase:
        return self.copy().sub_ip(transform)
