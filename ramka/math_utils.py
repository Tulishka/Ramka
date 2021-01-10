# from __future__ import division

import math
from typing import Tuple, Union

# from .shared import Vector
import pygame

Vector = pygame.Vector2


def line_intersection_point(line1: Tuple[Vector, Vector], line2: Tuple[Vector, Vector]) -> Union[None, Vector]:
    def def_line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0] * p2[1] - p2[0] * p1[1])
        return A, B, -C

    l1 = def_line(*line1)
    l2 = def_line(*line2)

    d = l1[0] * l2[1] - l1[1] * l2[0]
    dx = l1[2] * l2[1] - l1[1] * l2[2]
    dy = l1[0] * l2[2] - l1[2] * l2[0]
    if d != 0:
        x = dx / d
        y = dy / d
        if (line1[0].x <= x <= line1[1].x or line1[0].x >= x >= line1[1].x) and (
                line2[0].x <= x <= line2[1].x or line2[0].x >= x >= line2[1].x):
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


print(line_intersection_point((Vector(0, 1), Vector(3, 1)), (Vector(2, 0), Vector(2, 3))))
print(line_intersection_point((Vector(0, 1), Vector(3, 1)), (Vector(2, 3), Vector(1, 0))))
