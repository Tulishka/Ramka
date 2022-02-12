import math
from random import random, randint
from typing import Dict

from ramka import pygame, Vector, FlipStyle, slice_image, Game, Sprite, Animation, Input


class Block(Sprite):
    def __init__(self):
        super().__init__("sprites/bee?.png")
        self.transform.xy = 150, 150
        self.dest=self.transform.pos
        self.spd=100

    def update(self, deltaTime: float):
        super().update(deltaTime)

        napr=self.dest-self.transform.pos
        dist=napr.length()
        if dist>0:
            napr.normalize_ip()
            puti=self.spd * deltaTime
            while puti>0:
                p1=min(dist,puti)
                puti -= p1
                if p1>0:
                    self.transform.pos=self.transform.pos+p1*napr
                else:
                    break
                if puti>0:
                    if not self.newDest():
                        break
        else:
            self.newDest()

    def newDest(self):
        self.dest=self.transform.pos+Vector(30,0).rotate(randint(0,360))
        return True


Game.init('Рамка')

bl=Block()


Game.add_object(bl)

# === RUN GAME
Game.run()
