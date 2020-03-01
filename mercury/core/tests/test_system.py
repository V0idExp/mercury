from ..system import SystemRegistry
from ..system import System
from ..world import World


class FooComp:
    pass


class BarComp:
    pass


class TrackingSystem(System):

    def __init__(self, comp_types):
        self.entities = {}
        self.comp_types = comp_types

    def on_entity_component_added(self, entity, attr, comp):
        if type(comp) in self.comp_types:
            self.entities.setdefault(entity.uid, 0)
            self.entities[entity.uid] += 1

    def on_entity_component_deleted(self, entity, attr, comp):
        if type(comp) in self.comp_types:
            self.entities[entity.uid] -= 1

    def on_entity_deleted(self, entity):
        if entity.uid in self.entities:
            self.entities.pop(entity.uid)


def test_system_notif_by_world_changes(mocker):
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

    w = World()
    sysreg = SystemRegistry(w)

    ###
    # register some systems for various component combinations (entity types)
    ###
    sysreg.register_system(foo_sys, (FooComp,))
    sysreg.register_system(bar_sys, (BarComp,))
    sysreg.register_system(foobar_sys, (FooComp, BarComp,))

    ###
    # add some entities and test the systems state
    ###
    foo_ent = w.add_entity(components={'foo': FooComp()})
    bar_ent = w.add_entity(components={'bar': BarComp()})
    foobar_ent = w.add_entity(components={'foo': FooComp(), 'bar': BarComp()})

    assert len(foo_sys.entities) == 2
    assert foo_sys.entities[foo_ent.uid] == 1
    assert foo_sys.entities[foobar_ent.uid] == 1

    assert len(bar_sys.entities) == 2
    assert bar_sys.entities[bar_ent.uid] == 1
    assert bar_sys.entities[foobar_ent.uid] == 1

    assert len(foobar_sys.entities) == 1
    assert foobar_sys.entities[foobar_ent.uid] == 1

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
