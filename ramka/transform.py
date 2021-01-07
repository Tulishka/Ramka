from .shared import Vector


class Transform:
    ...


class Transform:

    def __init__(self, pos: Vector = None, rotate: float = 0.0, scale: Vector = None, offset: Vector = None, modifier_func = None):
        self.pos: Vector = pos if not pos is None else Vector()
        self.rotate = rotate
        self.scale: Vector = scale if not scale is None else Vector(1.0)
        self.offset: Vector = offset if not offset is None else Vector()
        self.modifier_func = modifier_func

    def copy(self):
        return Transform(Vector(self.pos), self.rotate, Vector(self.scale), Vector(self.offset), self.modifier_func)

    def get_modified(self):
        if self.modifier_func:
            return self.modifier_func(self)
        else:
            return self.copy()

    def use(self, transform: Transform):
        np = Vector(self.pos)
        if transform.scale.x != 1 or transform.scale.y != 1:
            np *= transform.scale.elementwise()
        if transform.rotate != 0:
            np = np - transform.offset
            np.rotate_ip(-transform.rotate)
        return Transform(transform.pos + transform.offset + np, self.rotate + transform.rotate,
                         self.scale.elementwise() * transform.scale, self.offset.elementwise() * transform.scale,self.modifier_func)
