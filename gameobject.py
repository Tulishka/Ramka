from typing import Dict, Union

from .transform import Transform


class GameObject: ...


class GameObject:
    from .component import Component

    def __init__(self, transform: Transform):
        from .game import Game
        self.transform = transform
        self.time = 0
        self.components: Dict[str, GameObject.Component] = {}
        self.children: Dict[str, GameObject.Component.GameObject] = {}
        self.game: Game = None
        self.parent: GameObject.Component.GameObject = None
        self.enabled: bool = True
        self.visible: bool = True

    def update(self, deltaTime: float):
        self.time += deltaTime

    def add_component(self, name: str, component: Component):
        self.components[name] = component

    def get_world_transform(self) -> Transform:
        if self.parent is None:
            return self.transform.get_modified()
        else:
            return self.transform.use(self.parent.get_world_transform()).get_modified()

    def add_child(self, child_name: str, child_object: Component.GameObject):
        if child_name in self.children:
            self.remove_child(child_name)

        child_object.game = self.game
        child_object.parent = self
        self.children[child_name] = child_object

    def remove(self):
        if self.parent:
            self.parent.remove_child(self)
        elif self.game:
            self.game.remove_object(self)

    def remove_child(self, child: Union[str, GameObject]):
        if type(child) == str:
            if child in self.children:
                ob = self.children[child]
                ob.parent = None
                ob.game = None
                del self.children[child]
        else:
            idx = [n for n, x in self.children.items() if x == child]
            if len(idx):
                child.parent = None
                child.game = None
                del self.children[idx[0]]

    def __iter__(self):
        for name, obj in self.children.items():
            yield (name, obj)
            try:
                yield next(iter(obj))
            except StopIteration:
                pass
