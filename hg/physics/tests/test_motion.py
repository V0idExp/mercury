from hg.math import Vector2

from ..body import Body
from ..motion import apply_gravity, apply_velocity


def test_body_fall_by_gravity():
    body = Body()

    apply_gravity(body, Vector2(0, -5), 1.0)
    apply_velocity(body, 1.0)

    assert body.position.x == 0
    assert body.position.y == -5


def test_massless_body_doesnt_fall():
    body = Body(mass=0.0)

    apply_gravity(body, Vector2(0, -5), 1.0)
    apply_velocity(body, 1.0)

    assert body.position.x == 0
    assert body.position.y == 0
