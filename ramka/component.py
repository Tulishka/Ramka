


class Component:
    from .gameobject import GameObject
    def __init__(self, game_oject: GameObject):
        self.gameObject = game_oject
