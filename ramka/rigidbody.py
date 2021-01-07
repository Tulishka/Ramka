from .gameobject import GameObject
from .component import Component
from .shared import Vector




class Rigidbody(Component):
    def __init__(self, gameObject: GameObject, mass=1.0, velocity: Vector = None):
        super(Rigidbody, self).__init__(gameObject)
        self.mass = mass
        self.velocity = velocity if not velocity is None else Vector(0,0)
