import random
from random import randint

from ramka import *
from ramka.path import Path, PathPosition

Game.init('Рельсы')
Game.цветФона = 200, 200, 255


class Rail(GameObject):

    def __init__(self, nodes):
        super(Rail, self).__init__()
        self.path = Path(nodes, curve=True, loop=0, step=20)
        self.pos = PathPosition()
        self.spd = 0
        self.max_spd = 1000

        self.spd_koef = 1  # self.path.total_length / 1000

        self.pic = Sprite("sprites/arrow.png")
        self.pic.transform.scale_xy = 0.5, 0.5

        self.near_pos = 0, 0

    def on_enter_game(self):
        Game.add_object(self.pic)
        self.pic.change_order(1)

    def edge_pass(self, edge):
        if not self.path.loop_navigation:
            self.spd *= -1

    def update(self, deltaTime: float):
        super().update(deltaTime)

        # dx = Input.get("Horizontal")

        self.near_pos = self.path.closest_position(pygame.mouse.get_pos(), 5)
        dl = self.near_pos.position - self.pos.position
        dx = math.copysign(1, dl)

        # if dx != 0:
        #     self.spd += dx * 200 * deltaTime
        #     if abs(self.spd) > self.max_spd:
        #         self.spd = math.copysign(self.max_spd, self.spd)
        # else:
        #     self.spd += -math.copysign(min(400.0, abs(self.spd)), self.spd) * deltaTime

        # self.path.move_position_ip(self.pos, self.spd * self.spd_koef * deltaTime, edge_pass=self.edge_pass)

        self.spd = min(self.max_spd, abs(dl))
        self.spd = math.copysign(self.spd, dl)

        self.path.move_position_ip(self.pos, self.spd * deltaTime, edge_pass=self.edge_pass)

        # Game.debug_str=str(self.pos.node)+": "+str(self.pos.position)

        self.pic.transform.pos = self.path.position_xy(self.pos)

        self.pic.transform.angle = self.path.angles[self.pos.node]

    def draw(self, dest):
        color = (100, 155, 100)
        wd = 4
        pygame.draw.lines(dest, color, self.path.loop, self.path.points, width=wd)

        for p in self.path.step_nodes:
            b = Vector(p)

        pygame.draw.line(dest, (100, 255, 0), self.path.position_xy(self.near_pos), pygame.mouse.get_pos(), 3)


random.seed(1)

v = Vector(1.0, 0)
shift = Vector(Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2)
n = 16

s = [(randint(150, 225) * v.rotate(i * 360 / n)) for i in range(n - 1)]

s = [(randint(int(200 - 50), int(200 + 50)) * v.rotate(i * 360 / n)) for i in range(n - 1)]
a = [(i + shift).xy for i in s]

# a = [(100, 100), (200, 100), (200, 200), (100, 200)]

r = Rail(a)
Game.add_object(r)

Game.run()
