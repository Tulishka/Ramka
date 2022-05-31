import pygame

from ramka import Sprite, Game, Input
from ramka.path import Path, PathPosition

Game.init('Рельсы')
Game.цветФона = 200, 200, 255


class Bot(Sprite):
    def __init__(self):
        super().__init__("../examples/ira_sprites/pet?.png")
        self.skorost = 200
        put = [(264, 468), (226, 224), (441, 171), (741, 638)]
        self.path = Path(put)
        self.pos = PathPosition()
        self.pos1 = PathPosition()
        self.pos2 = PathPosition()
        self.p1 = Sprite("../examples/ira_sprites/wheel.png")
        self.p2 = Sprite("../examples/ira_sprites/pylka.png")
        self.spd1 = 200
        self.spd2 = 400

    def on_enter_game(self):
        Game.add_object(self.p1)
        Game.add_object(self.p2)
        self.p1.change_order(1)
        self.p2.change_order(1)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        l = self.path.min_delta_between(self.pos1, self.pos2, self.pos)
        Game.debug_str=str(l)

        self.p1.transform.pos = self.path.position_xy(self.pos1)
        self.p2.transform.pos = self.path.position_xy(self.pos2)
        self.path.move_position_ip(self.pos, self.skorost * deltaTime)
        self.transform.pos = self.path.position_xy(self.pos)

        dx = Input.get("Horizontal")
        self.path.move_position_ip(self.pos1, dx * 300 * deltaTime)
        dy = Input.get("Vertical")
        self.path.move_position_ip(self.pos2, - dy * 300 * deltaTime)


    def draw(self, dest):
        color = (100, 155, 100)
        wd = 4
        pygame.draw.lines(dest, color, self.path.loop, self.path.points, width=wd)
        super().draw(dest)


bot = Bot()
Game.add_object(bot)
Game.run()
