# from __future__ import division

import math
from typing import Tuple, Union, List

# from .shared import Vector
import pygame

Vector = pygame.Vector2


def line_intersection_point(line1: Tuple[Vector, Vector], line2: Tuple[Vector, Vector]) -> Union[None, Vector]:
    def def_line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0] * p2[1] - p2[0] * p1[1])
        return A, B, -C

    if line1[0].x == line1[1].x:
        line1[1].x += 0.001
    if line1[0].y == line1[1].y:
        line1[1].y += 0.001
    if line2[0].x == line2[1].x:
        line2[1].x += 0.001
    if line2[0].y == line2[1].y:
        line2[1].y += 0.001

    l1 = def_line(*line1)
    l2 = def_line(*line2)

    d = l1[0] * l2[1] - l1[1] * l2[0]
    dx = l1[2] * l2[1] - l1[1] * l2[2]
    dy = l1[0] * l2[2] - l1[2] * l2[0]
    if d != 0:
        x = dx / d
        y = dy / d
        if min(line1[0].x, line1[1].x) <= x <= max(line1[0].x, line1[1].x) \
                and min(line1[0].y, line1[1].y) <= y <= max(line1[0].y, line1[1].y) \
                and min(line2[0].x, line2[1].x) <= x <= max(line2[0].x, line2[1].x) \
                and min(line2[0].y, line2[1].y) <= y <= max(line2[0].y, line2[1].y):
            return Vector(x, y)
        else:
            return None
    else:
        return None


def distance_point_to_line(point: Vector, line: Tuple[Vector, Vector], line_length=0):
    line1, line2 = line
    h = abs((line1[1] - line2[1]) * point[0] + (line2[0] - line1[0]) * point[1] + (
            line1[0] * line2[1] - line2[0] * line1[1]))

    if line_length == 0:
        line_length = math.hypot((line2[0] - line1[0]), (line2[1] - line1[1]))

    if line_length == 0:
        h = 999999999
    else:
        h = h / line_length

    return h


def point_inside_poly(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def _point_inside_poly(points,polygon):
    import matplotlib.path as mpltPath
    path = mpltPath.Path(polygon)
    inside2 = path.contains_points(points)


def interp_mid_spd(to_val: Union[Vector, List, Tuple],
                   from_val: Union[Vector, List, Tuple] = (0, 0)):
    d = [0, 0]
    d[0] = to_val[0] - from_val[0]
    d[1] = to_val[1] - from_val[1]
    g = 12 * d[1] / (d[0] ** 3)
    v0 = g * d[0] / 2

    def interp(x):
        x = x - from_val[0]
        if x <= 0:
            return from_val[1]
        elif x >= to_val[0]:
            return to_val[1]

        return from_val[1] + v0 * (x ** 2) / 2 - g * (x ** 3) / 6

    return interp


def interp_pulse(to_val: Union[Vector, List, Tuple],
                 from_val: Union[Vector, List, Tuple] = (0, 0), type=1):
    d = [0, 0]
    d[0] = to_val[0] - from_val[0]
    d[1] = to_val[1] - from_val[1]
    type = 2 if type == 1 else 1

    if not d[0]:
        return lambda x: from_val[1]

    def interp(x):
        x = (x - from_val[0]) / d[0]
        if x <= 0:
            x = 0
        elif x > 1:
            x = 1

        return from_val[1] + d[1] * math.exp(-0.8 * (type * math.e * x - math.e) ** 2)

    return interp
