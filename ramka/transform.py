from typing import Union, List

from .transform_modifiers import defaultTransformModifier
from .transformbase import TransformBase
from .shared import Vector


class Transform(TransformBase):
    pass


class Transform(TransformBase):
    def __init__(self, game_oject: Transform.GameObject, pos: Vector = None, rotate: float = 0.0,
                 scale: Vector = None, offset: Vector = None, parent: Transform = None):

        super().__init__(game_oject, pos, rotate, scale, offset)
        self.parent: Union[Transform, None] = parent
        self.children: List[Transform] = []
        self.modifier = defaultTransformModifier

    def get_world_transform(self) -> TransformBase:
        if self.parent is None:
            return self.modifier.apply(self)
        else:
            if self.modifier.final_apply:
                return self.modifier.apply_ip(self.add(self.parent.get_world_transform()))
            else:
                return self.modifier.apply(self).add(self.parent.get_world_transform())

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
            self.parent.__remove_child(self)
            self.parent = None

    def set_parent(self, parent: Union[Transform, Transform.GameObject, None], from_world: bool = False):
        if self.parent:
            self.detach(from_world)

        if isinstance(parent, Transform.GameObject):
            parent = parent.transform

        self.parent = parent
        parent.__add_child(self)
        if from_world and parent is not None:
            self.sub_ip(parent.get_world_transform())
