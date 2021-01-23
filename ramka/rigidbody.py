from typing import List

from .gameobject import GameObject
from .component import Component
from .game import Game
from .shared import Vector
import pymunk


class Rigidbody(Component):
    def __init__(self, gameObject: GameObject, mass=1.0, velocity: Vector = None):
        super(Rigidbody, self).__init__(gameObject)
        self.body = pymunk.Body()
        self.shapes: List[pymunk.Shape] = []
        self.constraints: List[pymunk.Constraint] = []

    def update(self, deltaTime: float):
        self.gameObject.transform.xy = self.body.position

    def on_enter_game(self):
        Game.ph_space.add(self.body, *self.shapes, *self.constraints)

    def on_leave_game(self):
        Game.ph_space.remove(self.body, *self.shapes, *self.constraints)
