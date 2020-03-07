from hg.math import Vector2
from copy import copy
from typing import Optional


class Body:

    position: Vector2 = Vector2(0.0, 0.0)
    velocity: Vector2 = Vector2(0.0, 0.0)
    mass: float

    def __init__(self, position: Optional[Vector2] = None, velocity: Optional[Vector2] = None, mass: float = 1.0):
        self.position = position or copy(Body.position)
        self.velocity = velocity or copy(Body.velocity)
        self.mass = mass
