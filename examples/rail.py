import math
import random
from math import hypot
from random import randint
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

from ramka import *

Game.init('Рельсы')
Game.цветФона = 200, 200, 255


class PathPosition:
    def __init__(self, position=0, node=None):
        self.position = position
        self.node = 0 if node is None else node


class Path:
    def __init__(self, nodes=None, step=20):
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

        self.step = step

        self.points = []
        self.lengths = []
        self.accumulated_lengths = []
        self.total_length = 0

        self.angles = []
        self.deltas = []
        self.units = []
        self.step_nodes = []

        self.create_cache()

    def position_xy(self, position: PathPosition):
        pp = self.points[position.node]
        lp = position.position - self.accumulated_lengths[position.node]
        return pp[0] + self.units[position.node][0] * lp, pp[1] + self.units[position.node][1] * lp

    def move_position(self, position: PathPosition, amount):

        if self.total_length == 0:
            return

        new_pos = position.position + amount
        if new_pos < 0:
            new_pos = self.total_length + new_pos
        else:
            while new_pos >= self.total_length:
                new_pos = new_pos - self.total_length

        if position.node >= len(self.points):
            position.node = len(self.points) - 1

        while self.accumulated_lengths[position.node] > new_pos and position.node > 0:
            position.node -= 1

        while position.node + 1 < len(self.accumulated_lengths) and \
                self.accumulated_lengths[position.node + 1] < new_pos:
            position.node += 1

        position.position = new_pos

    def create_cache(self):

        x = [i[0] for i in self.nodes]
        y = [i[1] for i in self.nodes]

        x.append(self.nodes[0][0])
        y.append(self.nodes[0][1])

        tck, u = interpolate.splprep([x, y], s=0, per=1, k=3)
        unew = np.arange(0, 1.0, 0.01)
        out = interpolate.splev(unew, tck)

        self.points = [(out[0][i], out[1][i]) for i in range(len(out[0]))]

        self.total_length = 0
        cnt = len(self.points) - 1
        pp = None
        self.lengths = []

        dir = Vector(10.0, 0.0)

        for p in self.points:
            if pp:
                d = (p[0] - pp[0], p[1] - pp[1])
                dl = hypot(d[0], d[1])
                self.lengths.append(dl)
                self.deltas.append(d)
                self.units.append((d[0] / dl, d[1] / dl))
                self.angles.append(-dir.angle_to(Vector(d)))
                self.accumulated_lengths.append(self.total_length)
                self.total_length += dl
            pp = p

        d = (self.points[0][0] - pp[0], self.points[0][1] - pp[1])
        dl = hypot(d[0], d[1])
        self.lengths.append(dl)
        self.deltas.append(d)
        self.units.append((d[0] / dl, d[1] / dl))
        self.angles.append(-dir.angle_to(Vector(d)))
        self.accumulated_lengths.append(self.total_length)
        self.total_length += dl

        # print(len(self.accumulated_lengths))
        # print(self.accumulated_lengths)
        # print(self.total_length)
        # print(self.angles)

        # plt.figure()
        # plt.plot(x, y, 'x', out[0], out[1])
        # plt.show()


class Rail(GameObject):

    def __init__(self, nodes):
        super(Rail, self).__init__()
        self.path = Path(nodes)
        self.pos = PathPosition()
        self.spd = 0
        self.max_spd = 1000

        self.spd_koef = 1 # self.path.total_length / 1000

        self.pic = Sprite("sprites/arrow.png")
        self.pic.transform.scale_xy = 0.5,0.5

    def on_enter_game(self):
        Game.add_object(self.pic)
        self.pic.change_order(1)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        self.spd += Input.get("Horizontal") * 200 * deltaTime
        if abs(self.spd) > self.max_spd:
            self.spd = math.copysign(self.max_spd, self.spd)

        self.path.move_position(self.pos, self.spd * self.spd_koef * deltaTime)

        self.pic.transform.pos = self.path.position_xy(self.pos)

        self.pic.transform.angle = self.path.angles[self.pos.node]

    def draw(self, dest):
        color = (100, 155, 100)
        wd = 4
        points = self.path.points
        pygame.draw.lines(dest, color, True, points, width=wd)

        # p = self.path.position_xy(self.pos)
        # pygame.draw.circle(dest, (255, 0, 0), p, 12)
        # pp = None
        # for p in points:
        #     if pp:
        #         pygame.draw.line(dest, color, p, pp, wd)
        #     pp = p


random.seed(1)

v = Vector(1.0, 0)
shift = Vector(Game.ширинаЭкрана / 2, Game.высотаЭкрана / 2)
n = 16

s = [(randint(150, 225) * v.rotate(i * 360 / n)) for i in range(n - 1)]

n=26
for j in range(n):
    s = [(randint(int(200-50*(0.05*j)), int(200+50*(0.05*j))) * v.rotate(i * 360 / n)) for i in range(n - 1)]
    a = [(i*(j*0.1+1 - 0.8) + shift).xy for i in s]
    r = Rail(a)
    Game.add_object(r)



Game.run()
