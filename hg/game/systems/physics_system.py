import inject

from hg.core.system import System
from hg.core.world import World
from hg.game.components.body_component import BodyComponent
from hg.game.components.position_component import PositionComponent
from hg.game.settings import Settings
from hg.math import Vector2
from hg.physics.motion import apply_gravity, apply_velocity


class PhysicsSystem(System):

    def tick(self, world: World):
        cfg = inject.instance(Settings)
        gravity_accel = Vector2(0, cfg.gravity_force)
        for e in world.query_entities(lambda e: e.has_components(BodyComponent, PositionComponent)):
            # first, set the body position from position component
            body = e[BodyComponent].get_body()
            pos = e[PositionComponent]
            body.position.x = pos.x
            body.position.y = pos.y

            # apply forces to bodies
            apply_gravity(body, gravity_accel, cfg.physics_time_step)
            apply_velocity(body, cfg.physics_time_step)

            # update the position component from the body
            e[PositionComponent].x = body.position.x
            e[PositionComponent].y = body.position.y
