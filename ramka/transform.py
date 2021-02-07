from typing import Union, List

from .game import Game
from .transform_modifiers import defaultTransformModifier
from .transformbase import TransformBase
from .shared import Vector


class Transform(TransformBase):
    pass


class Transform(TransformBase):
    def __init__(self, game_oject: Transform.GameObject, pos: Vector = None, rotate: float = 0.0,
                 scale: Vector = None, parent: Transform = None):

        super().__init__(game_oject, pos, rotate, scale)

        self.children: List[Transform] = []
        self.modifier = defaultTransformModifier
        self.__world_transform_cache: Union[None, TransformBase] = None

        self.parent: Union[None,Transform] = None
        if parent is not None:
            self.set_parent(parent)


    def on_change(self):
        if self.__world_transform_cache is not None:
            for ch in self.children:
                ch.on_change()
            self.__world_transform_cache = None

    def get_world_transform(self) -> TransformBase:
        dirty = self.__world_transform_cache is None
        if self.parent is None:
            if dirty:
                self.__world_transform_cache = self.modifier.apply(self)
        else:
            if dirty:
                if self.modifier.final_apply:
                    self.__world_transform_cache = self.modifier.apply_ip(self.add(self.parent.get_world_transform()))
                else:
                    self.__world_transform_cache = self.modifier.apply(self).add_ip(self.parent.get_world_transform())

        return self.__world_transform_cache.copy()

    def __nocache_get_world_transform(self) -> TransformBase:
        if self.parent is None:
            return self.modifier.apply(self)
        else:
            if self.modifier.final_apply:
                return self.modifier.apply_ip(self.add(self.parent.get_world_transform()))
            else:
                return self.modifier.apply(self).add_ip(self.parent.get_world_transform())

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

    @staticmethod
    def to_local_coord(parent: Transform, target: Union[Vector, TransformBase, Transform.GameObject] ,
                       local_target: bool = True ) ->Vector:
        if isinstance(target, Transform.GameObject):
            target = target.transform

        if isinstance(target, TransformBase):
            if target.gameObject.transform.parent == parent:
                local_target = True
                target = target._pos
            else:
                target = target.gameObject.transform.get_world_transform()._pos

        if not local_target and parent:
            transform = parent.get_world_transform()
            target=transform.sub_from_vector(target)
        else:
            target = Vector(target)

        return target

    def to_parent_local_coord(self, target: Union[Vector, TransformBase, Transform.GameObject],
                              local_target: bool = True) ->Vector:
        return self.to_local_coord(self.parent, target, local_target)
