from ramka import Sprite, Input, Game


class Background(Sprite):
    def __init__(self, image):
        super().__init__(image)

    def update(self, deltaTime: float):
        super(Background, self).update(deltaTime)
        Game.debug_str = str(Input.mouse_pos)