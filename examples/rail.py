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

        self.pics = [Sprite("sprites/train.png") for i in range(3)]
        for i in self.pics:
            i.transform.scale_xy = 2, 2

        self.tr_dist=38*2

        self.near_pos = 0, 0

    def on_enter_game(self):
        for i in self.pics:
            Game.add_object(i)
            i.change_order(1)

    def edge_pass(self, edge):
        if not self.path.loop_navigation:
            self.spd *= -1

    def update(self, deltaTime: float):
        super().update(deltaTime)

        # dx = Input.get("Horizontal")
        # if dx != 0:
        #     self.spd += dx * 200 * deltaTime
        #     if abs(self.spd) > self.max_spd:
        #         self.spd = math.copysign(self.max_spd, self.spd)
        # else:
        #     self.spd += -math.copysign(min(400.0, abs(self.spd)), self.spd) * deltaTime
        # self.path.move_position_ip(self.pos, self.spd * self.spd_koef * deltaTime, edge_pass=self.edge_pass)

        self.near_pos = self.path.closest_position(pygame.mouse.get_pos(), 5)
        dl = self.path.move_position_toward_ip(self.pos, self.near_pos, 500 * deltaTime, edge_pass=self.edge_pass)

        ps=self.pos.copy()
        pr=None
        for i in self.pics:
            i.transform.pos = self.path.position_xy(ps)
            # i.transform.angle = self.path.angles[ps.node]
            if pr is None:
                i.transform.angle = self.path.angles[ps.node]
            else:
                i.transform.look_at_ip(pr)
            pr=i
            self.path.move_position_ip(ps,self.tr_dist)

    def draw(self, dest):
        color = (100, 155, 100)
        wd = 4
        pygame.draw.lines(dest, color, self.path.loop, self.path.points, width=wd)

        for p in self.path.step_nodes:
            b = Vector(p)
        pp = self.path.position_xy(self.near_pos)
        pygame.draw.circle(dest, (200, 0, 0), pp, 5, 2)
        pygame.draw.line(dest, (200, 0, 0), pp, pygame.mouse.get_pos(), 2)
        pygame.draw.line(dest, (100, 255, 0), self.path.position_xy(self.pos), pygame.mouse.get_pos(), 3)


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
