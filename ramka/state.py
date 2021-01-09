from .component import Component


class State(Component):
    def __init__(self, game_oject: Component.GameObject):
        super().__init__(game_oject)
        self.animation = "default"






