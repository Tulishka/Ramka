import math
from random import random
from typing import Dict

from ramka import pygame, Vector, FlipStyle, slice_image, Game, Sprite, Animation, Input, Cooldown, GameObject


class IK(GameObject):
    def __init__(self):
        super().__init__()
        self.def_length = 100
        self.bones = [Vector(self.def_length, 0).rotate(i * 5) for i in range(4)]
        self.origin = Vector(Game.ширинаЭкрана // 4, Game.высотаЭкрана // 2)
        self.wspd = 5
        self.transform.scale = 1, 1

        self.points = self.calculate_points()

    def calculate_points(self, to=0):
        pts = []
        scale = self.transform.scale_x
        p = 1.0 * self.origin
        for n, i in enumerate(self.bones):
            pts.append(p)
            if n > to > 0:
                break
            p = p + scale * i
        pts.append(p)
        return pts

    def update(self, deltaTime: float):
        super().update(deltaTime)

        dest = Vector(pygame.mouse.get_pos())

        self.solve(dest)

    def draw(self, dest: pygame.Surface):

        pts = self.calculate_points()
        pygame.draw.lines(dest, (255, 255, 255), False, pts, 2)

        for p in pts:
            pygame.draw.circle(dest, (255, 0, 0), p, 5)

    def solve(self, dest):

        pts = self.calculate_points()

        dst = (dest-pts[len(self.bones)]).length()



        n = len(self.bones)
        while n > 1:
            n -= 1
            b=self.bones[n]
            d = dest - pts[n]
            a = b.angle_to(d)

            b.rotate_ip(a)


Game.init("IK test")

Game.add_object(IK())
Game.run()
