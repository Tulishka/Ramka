from typing import Union, List

from .transformbase import TransformBase
from .shared import Vector


class Transform(TransformBase):
    pass


class Transform(TransformBase):
    def __init__(self, game_oject: Transform.GameObject, pos: Vector = None, rotate: float = 0.0,
                 scale: Vector = None, offset: Vector = None, modifier_func=None, parent: Transform = None):

        super().__init__(game_oject, pos, rotate, scale, offset, modifier_func)
        self.parent: Union[Transform, None] = parent
        self.children: List[Transform] = []

    def get_world_transform(self) -> TransformBase:
        if self.parent is None:
            return self.get_modified()
        else:
            return self.add(self.parent.get_world_transform()).get_modified()

    def __add_child(self, child: Transform):
        if child not in self.children:
            self.children.append(child)

    def __remove_child(self, child: Transform):
        if child in self.children:
            self.children.remove(child)

    def __iter__(self):
        for obj in self.children:
            yield obj
            try:
                yield next(iter(obj))
            except StopIteration:
                pass

    def detach(self, to_world: bool = False):
        if self.parent:
            if to_world:
                self.assign_positions(self.get_world_transform())

            self.parent = None

    def set_parent(self, parent: Union[Transform, Transform.GameObject, None], from_world: bool = False):
        if self.parent:
            self.detach(from_world)

        if isinstance(parent, Transform.GameObject):
            parent = parent.transform

        self.parent = parent
        if from_world and parent is not None:
            self.sub_ip(parent.get_world_transform())
