from dataclasses import dataclass
from functools import partial
from math import sqrt
from typing import Tuple

import pytest

from ..system import System, SystemRegistry
from ..world import World


@pytest.fixture
def w():
    world = World()
    yield world
    world.del_entities()


def test_system_notif_by_world_changes(w, mocker):
    ###
    # Some simple component definitions
    ###

    class FooComp:
        pass

    class BarComp:
        pass

    ###
    # A system which just tracks entities and components related to it
    ###
    class TrackingSystem(System):

        def __init__(self, comp_types):
            self.entities = {}
            self.comp_types = set(comp_types)

        def tick():
            pass

        def on_entity_component_added(self, entity, comp):
            if self.comp_types.issubset(set(entity.components)):
                self.entities[entity.uid] = True

        def on_entity_component_deleted(self, entity, comp):
            if type(comp) in self.comp_types and entity.uid in self.entities:
                self.entities.pop(entity.uid)

    ###
    # Create a world and register few systems for various component combinations
    ###
    foo_sys = TrackingSystem((FooComp,))
    bar_sys = TrackingSystem((BarComp,))
    foobar_sys = TrackingSystem((FooComp, BarComp,))

    systems = [foo_sys, bar_sys, foobar_sys]
    spies = {}
    for system in systems:
        spies[system] = {
            'on_entity_added': mocker.spy(system, 'on_entity_added'),
            'on_entity_deleted': mocker.spy(system, 'on_entity_deleted'),
        }

    sysreg = SystemRegistry(w)

    sysreg.register_system(foo_sys)
    sysreg.register_system(bar_sys)
    sysreg.register_system(foobar_sys)

    ###
    # Add some entities and test the systems state
    ###
    foo_ent = w.add_entity(components=(FooComp(),))
    bar_ent = w.add_entity(components=(BarComp(),))
    foobar_ent = w.add_entity(components=(FooComp(), BarComp(),))

    assert len(foo_sys.entities) == 2
    assert foo_sys.entities[foo_ent.uid]
    assert foo_sys.entities[foobar_ent.uid]

    assert len(bar_sys.entities) == 2
    assert bar_sys.entities[bar_ent.uid]
    assert bar_sys.entities[foobar_ent.uid]

    assert len(foobar_sys.entities) == 1
    assert foobar_sys.entities[foobar_ent.uid]

    w.del_entity(foo_ent)
    w.del_entity(bar_ent)
    w.del_entity(foobar_ent)

    assert len(foo_sys.entities) == 0
    assert len(bar_sys.entities) == 0
    assert len(foobar_sys.entities) == 0

    for system in systems:
        spies[system]['on_entity_added'].assert_called()
        assert spies[system]['on_entity_added'].call_count == 3

        spies[system]['on_entity_deleted'].assert_called()
        assert spies[system]['on_entity_deleted'].call_count == 3


def filter_by_type_subset(types: Tuple[type, ...], entity) -> bool:
    entity_type_set = set(entity.components)
    type_set = set(types)
    return type_set.issubset(entity_type_set)


def test_simple_game_ticking(w):
    ###
    # Some simple components
    ###
    @dataclass
    class HitPoints:
        """Component for tracking someone's hit points."""
        hp: int

    @dataclass
    class Position:
        """Component which holds someone's position."""
        x: float
        y: float

    @dataclass
    class Mass:
        """Component which gives an entity some physical mass."""
        mass: float

    @dataclass
    class DamageSource:
        damage: int
        radius: float

    ###
    # Some systems which implement some logic on top of the components
    ###
    class DamageAreaSystem(System):
        """
        Deals some damage to all entities near damage sources, which have
        position and hitpoints components attached to them.
        """
        def tick(self, world):
            targets = list(world.query_entities(partial(filter_by_type_subset, (Position, HitPoints))))
            for source in world.query_entities(partial(filter_by_type_subset, (DamageSource, Position))):
                for target in targets:
                    # compute the distance of the target to the damage source
                    t_pos = target[Position]
                    pos = source[Position]
                    dx = pos.x - t_pos.x
                    dy = pos.y - t_pos.y
                    dist = sqrt(dx * dx + dy * dy)

                    # if the target is within reach, damage it
                    if dist <= source[DamageSource].radius:
                        target[HitPoints].hp -= source[DamageSource].damage

    class GravitySystem(System):
        """
        Pulls down all entities which have a position and mass components.
        """
        def tick(self, world: World):
            for entity in world.query_entities(partial(filter_by_type_subset, (Position, Mass))):
                has_mass = entity[Mass].mass > 0
                if has_mass:
                    entity[Position].y -= 4.9  # 1/2 * 9.81 * 1

    class DeathSystem(System):
        """
        Destroys all entities which hitpoints are lesser or equal to 0.
        """
        def tick(self, world: World):
            dead = []
            for entity in world.query_entities(partial(filter_by_type_subset, (HitPoints,))):
                if entity[HitPoints].hp <= 0:
                    dead.append(entity.uid)

            for entity in dead:
                world.del_entity(entity)

    ###
    # Create a world, register the systems and populate it with entities
    ###
    sysreg = SystemRegistry(w)
    sysreg.register_system(DamageAreaSystem())
    sysreg.register_system(GravitySystem())
    sysreg.register_system(DeathSystem())

    # add a 5kg barbell, somewhere at 10m in the air
    barbell = w.add_entity(
        name='barbell',
        components=(
            Mass(5),
            Position(x=0.0, y=10.0),
        )
    )

    # add two fireballs on the floor, each dealing different amounts of damage
    # per second
    fire_dmg_1 = 5
    fire_dmg_2 = 3
    w.add_entity(
        name='fireball_1',
        components=(
            Position(x=0.0, y=0.0),
            DamageSource(damage=fire_dmg_1, radius=2)
        )
    )
    w.add_entity(
        name='fireball_2',
        components=(
            Position(x=3.0, y=0.0),
            DamageSource(damage=fire_dmg_2, radius=2)
        )
    )

    # add three mobs, one in the middle of both fireballs, another one affected
    # only by the second, and another one which jumped high, out of their reach,
    # but which has mass, so it is affected by gravity and will shortly fall
    # into the second fireball
    mob_hp = 10
    mob1 = w.add_entity(
        name='mob_1',
        components=(
            Position(x=1.5, y=0.0),
            HitPoints(hp=mob_hp),
        )
    )
    mob2 = w.add_entity(
        name='mob_2',
        components=(
            Position(x=3.5, y=0.0),
            HitPoints(hp=mob_hp),
        )
    )
    mob3 = w.add_entity(
        name='mob_3',
        components=(
            Position(x=3.0, y=6),
            HitPoints(hp=mob_hp),
            Mass(mass=1),
        )
    )

    ###
    # First tick! (1 tick = 1 sec)
    ###
    sysreg.tick_all()

    # the barbell should fall down by almost 5 meters (~4.9 to be more precise) during the tick
    assert barbell[Position].y == pytest.approx(5, 0.1)

    # the first mob should have taken damage from both the fireballs
    assert mob1[HitPoints].hp == mob_hp - (fire_dmg_1 + fire_dmg_2)
    # the second mob should have taken damage only from the second fireball
    assert mob2[HitPoints].hp == mob_hp - fire_dmg_2
    # the third mob should have taken no damage
    assert mob3[HitPoints].hp == mob_hp

    ###
    # Second tick!
    ###
    sysreg.tick_all()

    # the barbell has almost reached the floor
    assert barbell[Position].y < 0.5

    # the first mob has taken too much damage and is dead (removed from the
    # world and all components are destroyed)
    assert len(list(w.query_entities(lambda e: e.uid == mob1.uid))) == 0
    # the second mob has more damage, but is still alive
    assert mob2[HitPoints].hp == mob_hp - fire_dmg_2 * 2
    # the third mob has fallen into the second fireball during the previous
    # tick, and has also taken damage
    assert mob3[HitPoints].hp == mob_hp - fire_dmg_2
    assert mob3[Position].y < 2
