import inject
import pytest

from hg.core.system import SystemRegistry
from hg.core.world import World

from ...components.body_component import BodyComponent
from ...components.position_component import PositionComponent
from ...settings import Settings
from ..physics_system import PhysicsSystem


@pytest.fixture
def inject_config():
    return {
        Settings: lambda: Settings(gravity_force=1.0),
    }


@pytest.mark.inject()
def test_objects_falling():
    w = World()
    systems = SystemRegistry(w)
    systems.register_system(PhysicsSystem())
    cfg = inject.instance(Settings)

    e = w.add_entity(components=(
        PositionComponent(),
        BodyComponent(),
    ))

    num_ticks = int(1.0 / cfg.physics_time_step)
    for _ in range(num_ticks):
        systems.tick_all()

    assert e[BodyComponent].get_body().velocity.y == pytest.approx(1.0, 1)
    assert e[PositionComponent].x == 0
    assert e[PositionComponent].y == pytest.approx(1/2, 1)  # 1/2 * 1m/s^2 * 1.0s
