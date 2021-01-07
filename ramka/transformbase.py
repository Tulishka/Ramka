from .component import Component
from .shared import Vector


class TransformBase(Component):
    pass


class TransformBase(Component):

    def __init__(self, game_oject: Component.GameObject, pos: Vector = None, rotate: float = 0.0, scale: Vector = None,
                 offset: Vector = None):
        super().__init__(game_oject)

        self.pos: Vector = pos if pos is not None else Vector()
        self.rotate = rotate
        self.scale: Vector = scale if scale is not None else Vector(1.0)
        self.offset: Vector = offset if offset is not None else Vector()

    def copy(self) -> TransformBase:
        return TransformBase(self.gameObject, Vector(self.pos), self.rotate, Vector(self.scale), Vector(self.offset))

    def assign_positions(self, other: TransformBase):
        self.pos = Vector(other.pos)
        self.rotate = other.rotate
        self.scale = Vector(other.scale)
        self.offset = Vector(other.offset)
        return self

    def add_ip(self, transform: TransformBase) -> TransformBase:

        if transform.scale.x != 1 or transform.scale.y != 1 or self.scale.x != 1 or self.scale.y != 1:
            self.pos *= transform.scale.elementwise()
            self.scale = self.scale.elementwise() * transform.scale
            self.offset = self.offset.elementwise() * self.scale

        if transform.rotate != 0:
            self.pos = self.pos - transform.offset
            self.pos.rotate_ip(-transform.rotate)

        self.pos += transform.pos + transform.offset
        self.rotate += transform.rotate

        return self

    def __add_old(self, transform: TransformBase) -> TransformBase:
        np = Vector(self.pos)
        if transform.scale.x != 1 or transform.scale.y != 1:
            np *= transform.scale.elementwise()
        if transform.rotate != 0:
            np = np - transform.offset
            np.rotate_ip(-transform.rotate)
        return TransformBase(self.gameObject, transform.pos + transform.offset + np, self.rotate + transform.rotate,
                             self.scale.elementwise() * transform.scale, self.offset.elementwise() * transform.scale)

    def sub_ip(self, transform: TransformBase) -> TransformBase:

        self.pos -= transform.pos + transform.offset

        if transform.scale.x != 1 or transform.scale.y != 1 or self.scale.x != 1 or self.scale.y != 1:
            self.pos /= transform.scale.elementwise()
            self.offset = self.offset.elementwise() / self.scale
            self.scale = self.scale.elementwise() / transform.scale

        if transform.rotate != 0:
            self.pos -= transform.offset
            self.pos.rotate_ip(transform.rotate)

        self.rotate -= transform.rotate

        return self

    def add(self, transform: TransformBase) -> TransformBase:
        return self.copy().add_ip(transform)

    def sub(self, transform: TransformBase) -> TransformBase:
        return self.copy().sub_ip(transform)

