import math

import pygame

from movable import Movable
from ramka import Vector, Input


class Item(Movable):
    def __init__(self, *a, **b):
        super().__init__(*a, **b)

    def get_icon(self):
        return self._get_icon(background=(100, 100, 180), border=(70, 70, 100))
