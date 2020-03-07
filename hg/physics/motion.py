from typing import cast

from hg.math import Vector2

from .body import Body


def apply_gravity(body: Body, gravity_accel: Vector2, time: float):
    if body.mass > 0:
        body.velocity += cast(Vector2, gravity_accel * time)


def apply_velocity(body: Body, time: float):
    body.position += cast(Vector2, body.velocity * time)
