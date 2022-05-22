import math
from math import hypot
import numpy as np
# import matplotlib.pyplot as plt
from scipy import interpolate

from ramka import Vector


class PathPosition:
    def __init__(self, position=0, node=None):
        self.position = position
        self.node = 0 if node is None else node

    def copy(self):
        return PathPosition(self.position, self.node)


class Path:
    def __init__(self, nodes=None, step=0, loop=1, curve=True, loop_navigation=None):
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

        self.loop = loop
        self.curve = curve

        self.loop_navigation = loop_navigation if not loop_navigation is None else loop

        self.create_cache()

    def min_delta_between(self, position: PathPosition, to_position: PathPosition):
        d = to_position.position - position.position
        if self.loop:
            dr = d + self.total_length
            d1 = d if abs(d) < abs(dr) else dr
            dr = d1 - self.total_length
            d = d1 if abs(d1) < abs(dr) else dr

        return d

    def move_position_toward_ip(self, position: PathPosition, to_position: PathPosition, amount: float, edge_pass=None):
        d = self.min_delta_between(position, to_position)
        self.move_position_ip(position, math.copysign(min(abs(d), abs(amount)), d), edge_pass=edge_pass)

    def move_position_toward(self, position: PathPosition, to_position: PathPosition, amount: float, edge_pass=None):
        pos = position.copy()
        self.move_position_toward_ip(pos, to_position, amount, edge_pass=edge_pass)
        return pos

    def move_position_desc(self, position, point, step):
        ps = position.copy()
        p = self.position_xy(ps)
        dl = (point[0] - p[0]) ** 2 + (point[1] - p[1]) ** 2
        for m in range(200):
            np = self.move_position(ps, step)
            p = self.position_xy(np)
            nl = (point[0] - p[0]) ** 2 + (point[1] - p[1]) ** 2
            if nl > dl or np.position == ps.position:
                return ps, math.sqrt(dl)
            else:
                ps = np
                dl = nl

        print("1000 !!!!")
        return position.copy(), 0

    def closest_position(self, point, step=10):
        mi = 0
        ml = -1
        for i, p in enumerate(self.points):
            dl = (point[0] - p[0]) ** 2 + (point[1] - p[1]) ** 2
            if ml < 0 or ml > dl:
                ml = dl
                mi = i

        mi = mi if mi < len(self.points) - 1 else len(self.accumulated_lengths) - 1
        pos = PathPosition(self.accumulated_lengths[mi], mi)

        p1, l1 = self.move_position_desc(pos, point, step)
        p2, l2 = self.move_position_desc(pos, point, -step)

        return p2 if l1 > l2 else p1

    def position_xy(self, position: PathPosition):
        pp = self.points[position.node]
        lp = position.position - self.accumulated_lengths[position.node]
        return pp[0] + self.units[position.node][0] * lp, pp[1] + self.units[position.node][1] * lp

    def position_relative(self, position: PathPosition):
        if self.total_length == 0:
            return 1
        else:
            return position.position / self.total_length

    def move_position_ip(self, position: PathPosition, amount, edge_pass=None):

        if self.total_length == 0:
            return

        ep = ""
        new_pos = position.position + amount
        if new_pos < 0:
            if self.loop_navigation:
                new_pos = self.total_length + new_pos
            else:
                new_pos = 0

            ep = "start"
        else:
            ep = "end" if new_pos > self.total_length else ""
            if self.loop_navigation:
                while new_pos >= self.total_length:
                    new_pos = new_pos - self.total_length
            else:
                if ep != "":
                    new_pos = self.total_length

        if position.node >= len(self.points):
            position.node = len(self.points) - 1

        while self.accumulated_lengths[position.node] > new_pos and position.node > 0:
            position.node -= 1

        while position.node + 1 < len(self.accumulated_lengths) and \
                self.accumulated_lengths[position.node + 1] < new_pos:
            position.node += 1

        position.position = new_pos

        if ep != "" and edge_pass:
            edge_pass(ep)

    def move_position(self, position: PathPosition, amount, edge_pass=None):

        if self.total_length == 0:
            return

        pos = position.copy()

        self.move_position_ip(pos, amount, edge_pass=edge_pass)

        return pos

    def create_cache(self):

        if self.curve > 0:
            x = [i[0] for i in self.nodes]
            y = [i[1] for i in self.nodes]

            if self.loop:
                x.append(self.nodes[0][0])
                y.append(self.nodes[0][1])

            tck, u = interpolate.splprep([x, y], s=0, per=self.loop, k=3)
            unew = np.arange(0, 1.0, 0.01)
            out = interpolate.splev(unew, tck)

            self.points = [(out[0][i], out[1][i]) for i in range(len(out[0]))]
        else:
            self.points = self.nodes

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

        if self.loop:
            d = (self.points[0][0] - pp[0], self.points[0][1] - pp[1])
            dl = hypot(d[0], d[1])
            self.lengths.append(dl)
            self.deltas.append(d)
            self.units.append((d[0] / dl, d[1] / dl))
            self.angles.append(-dir.angle_to(Vector(d)))
            self.accumulated_lengths.append(self.total_length)
            self.total_length += dl

        if self.step:
            p = PathPosition()

            lp = -self.step
            while p.position - lp >= self.step:
                lp = p.position
                self.step_nodes.append(self.position_xy(p))
                self.move_position_ip(p, self.step)

        # print(len(self.accumulated_lengths))
        # print(self.accumulated_lengths)
        # print(self.total_length)
        # print(self.angles)

        # plt.figure()
        # plt.plot(x, y, 'x', out[0], out[1])
        # plt.show()
