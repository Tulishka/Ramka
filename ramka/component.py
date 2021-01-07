

class Component:...

class Component:
    from .gameobject import GameObject

    def __init__(self, game_oject):
        self.gameObject:GameObject = game_oject
