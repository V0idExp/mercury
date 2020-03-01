import pytest
from .. import world
from unittest.mock import Mock
from itertools import count
from dataclasses import dataclass


@pytest.fixture
def count_from_one(mocker: Mock):

    def _count_from_one(_):
        return count(1)

    # patch the itertools.count
    mocker.patch.object(world, 'count', _count_from_one)


@pytest.mark.usefixtures('count_from_one')
def test_entity_empty(mocker: Mock):
    w = world.World()

    entity_added = mocker.Mock()
    entity_deleted = mocker.Mock()
    w.on_entity_add += entity_added
    w.on_entity_del += entity_deleted

    entity = w.add_entity(name='dummy')
    entity_added.assert_called_once()
    assert entity.uid == 1
    assert entity.name == 'dummy'
    assert entity_added.call_args[0][0].uid == entity.uid

    w.del_entity(entity.uid)
    entity_deleted.assert_called_once()


@pytest.mark.usefixtures('count_from_one')
def test_entity_w_components(mocker):

    @dataclass
    class ProgressComponent:
        value: float = 0

    @dataclass
    class SpriteComponent:
        path: str = 'resources/no_sprite.png'

    comp_added = mocker.Mock()
    comp_deleted = mocker.Mock()

    w = world.World()
    w.on_entity_component_add += comp_added
    w.on_entity_component_del += comp_deleted

    ###
    # entity creation with components
    ###
    components = {
        'player': SpriteComponent(),
        'weapon': SpriteComponent(),
        'progress': ProgressComponent(),
    }

    e = w.add_entity(name='player', components=dict(components))
    comp_added.assert_called()

    for call_args in comp_added.call_args_list:
        target_entity, comp_attr, comp_obj = call_args[0]
        assert target_entity.uid == e.uid
        assert isinstance(comp_obj, type(components[comp_attr]))

    added_components = {call_args[0][1] for call_args in comp_added.call_args_list}
    assert added_components == set(components.keys())

    ###
    # entity testing
    ###
    assert e.player.path == 'resources/no_sprite.png'
    assert e.progress.value == 0.0

    ###
    # component destruction
    ###
    for comp_attr in components:
        e.del_component(comp_attr)
        comp_deleted.assert_called_once()
        assert comp_deleted.call_args[0][1] == comp_attr
        comp_deleted.reset_mock()


@pytest.mark.usefixtures('count_from_one')
def test_entity_dynamic_component_add_del(mocker):
    comp_added = mocker.Mock()
    comp_deleted = mocker.Mock()

    w = world.World()
    w.on_entity_component_add += comp_added
    w.on_entity_component_del += comp_deleted

    e = w.add_entity()

    comp_added.assert_not_called()

    ###
    # Test some valid components
    ###
    e.add_component('some_int', 123)
    e.add_component('some_bool', True)

    assert e.some_int == 123
    assert e.some_bool

    comp_added.assert_called()
    assert comp_added.call_count == 2

    ###
    # Test add of invalid components
    ###
    with pytest.raises(world.ComponentError):
        e.add_component('name', str)

    with pytest.raises(world.ComponentError):
        e.add_component('some_int', str)

    ###
    # Test component removal
    ###
    e.del_component('some_int')
    comp_deleted.assert_called_once()

    with pytest.raises(AttributeError):
        e.some_int

    with pytest.raises(world.ComponentError):
        e.del_component('some_nonexisting_comp')

    with pytest.raises(world.ComponentError):
        e.del_component('name')
