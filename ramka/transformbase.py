from math import copysign
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
        pos = self._pos.xy
        scale = self._scale.xy
        angle = self._angle
        self._pos = Vector(other._pos)
        self._angle = other._angle
        self._scale = Vector(other._scale)
        if angle != self.angle or pos != self._pos or scale != self._scale:
            self.on_change()
        return self

    @property
    def pos(self):
        return Vector(self._pos)

    @pos.setter
    def pos(self, value):
        xy = self._pos.xy
        self._pos.xy = value
        if xy != self._pos:
            self.on_change()

    @property
    def scale(self):
        return Vector(self._scale)

    @scale.setter
    def scale(self, value):
        xy = self._scale.xy
        self._scale.xy = value
        if xy != self._scale:
            self.on_change()

    @property
    def x(self):
        return self._pos.x

    @x.setter
    def x(self, value):
        v = self._pos.x
        self._pos.x = value
        if value != v:
            self.on_change()

    @property
    def y(self):
        return self._pos.y

    @y.setter
    def y(self, value):
        v = self._pos.y
        self._pos.y = value
        if v != value:
            self.on_change()

    @property
    def xy(self):
        return Vector(self._pos.xy)

    @xy.setter
    def xy(self, value):
        xy = self._pos.xy
        self._pos.xy = value
        if xy != value:
            self.on_change()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        v = self._angle
        self._angle = value
        if v != value:
            self.on_change()

    @property
    def scale_x(self):
        return self._scale.x

    @scale_x.setter
    def scale_x(self, value):
        v = self._scale.x
        self._scale.x = value
        if v != value:
            self.on_change()

    @property
    def scale_y(self):
        return self._scale.y

    @scale_y.setter
    def scale_y(self, value):
        v = self._scale.y
        self._scale.y = value
        if v != value:
            self.on_change()

    @property
    def scale_xy(self):
        return Vector(self._scale.xy)

    @scale_xy.setter
    def scale_xy(self, value):
        xy = self._scale.xy
        self._scale.xy = value
        if xy != value:
            self.on_change()

    def look_at_ip(self, target: Union[Vector, TransformBase, Component.GameObject],
                   use_local: bool = True, max_delta=None) -> TransformBase:
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
            angle = -Vector(1.0, 0.0).angle_to(target - self._pos)
        else:
            pr = self.gameObject.transform.parent.get_world_transform()
            angle = -Vector(1.0, 0.0).angle_to(target - self.add(pr)._pos) - pr._angle

        if max_delta:
            an = self._angle % 360
            if an > 180:
                an = an - 360

            angle = angle - an
            if abs(angle) > max_delta:
                angle = copysign(max_delta, angle)

            angle = self._angle + angle

        self._angle = angle
        self.on_change()

        return self

    def look_at(self, target: Union[Vector, TransformBase, Component.GameObject],
                use_local: bool = True, max_delta=None) -> TransformBase:
        p = self.copy()
        return p.look_at_ip(target, use_local, max_delta)

    def add_to_vector(self, vector: Vector):
        vector = Vector(vector)
        vector *= self._scale.elementwise()
        vector.rotate_ip(-self._angle)
        vector += self._pos
        return vector

    def sub_from_vector(self, vector: Vector):
        vector = Vector(vector)
        vector -= self._pos
        vector.rotate_ip(self._angle)
        if self._scale.x != 0 and self._scale.y != 0:
            vector /= self._scale.elementwise()
        return vector

    def add_ip(self, transform: TransformBase) -> TransformBase:

        if transform._scale.x != 1 or transform._scale.y != 1 or self._scale.x != 1 or self._scale.y != 1:
            self._pos *= transform._scale.elementwise()
            self._scale = self._scale.elementwise() * transform._scale

        if transform._angle != 0:
            self._pos.rotate_ip(-transform._angle)

        self._pos += transform._pos

        if transform._scale.y * transform._scale.x < 0:
            self._angle = -self._angle

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

        if transform._scale.y * transform._scale.x < 0:
            self._angle = -self._angle

        self._angle -= transform._angle
        self.on_change()

        return self

    def add(self, transform: TransformBase) -> TransformBase:
        return self.copy().add_ip(transform)

    def sub(self, transform: TransformBase) -> TransformBase:
        return self.copy().sub_ip(transform)

    def move_forward_ip(self, distance: float):
        if distance:
            v = distance * Vector(1.0, 0)
            v.rotate_ip(-self._angle)
            self._pos += v
            self.on_change()

    def move_forward(self, distance: float):
        v = distance * Vector(1.0, 0)
        v.rotate_ip(-self._angle)
        v += self._pos
        return v

    def move_toward_ip(self, target: Union[Vector, TransformBase, Component.GameObject], distance: float,
                       look_to_target: bool = False,
                       use_local: bool = True, step_info=None) -> TransformBase:
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
            diff = self._pos - target
            angle = -Vector(1.0, 0.0).angle_to(diff)
        else:
            pr = self.gameObject.transform.parent.get_world_transform()
            diff = self.add(pr)._pos - target
            angle = -Vector(1.0, 0.0).angle_to(diff) - pr._angle

        v = Vector(0)
        if distance:
            ds = diff.length_squared()
            if ds:
                if ds <= distance * distance:
                    v = diff
                else:
                    v = distance * Vector(1.0, 0)
                    v.rotate_ip(-angle)

                self._pos -= v

                if round(v.x) or round(v.y):
                    if look_to_target:
                        self._angle = angle
                    self.on_change()

        if step_info is not None:
            step_info["start_distance"] = distance
            step_info["delta"] = v

        return self

    def move_toward(self, target: Union[Vector, TransformBase, Component.GameObject], distance: float,
                    look_to_target: bool = False,
                    use_local: bool = True, step_info=None) -> TransformBase:
        return self.copy().move_toward_ip(target, distance, use_local, step_info=step_info)
