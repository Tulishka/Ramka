import math

import pygame

from movable import Movable
from ramka import Vector, Input


class Item(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def def_icon_args(self):
        self.set_icon_args(background=(100, 100, 180), border=(70, 70, 100),scale_contain=True)
        return self

