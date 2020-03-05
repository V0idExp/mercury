from dataclasses import dataclass
from itertools import count
from unittest.mock import Mock

import pytest

from .. import world


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
    class Progress:
        value: float = 0

    @dataclass
    class Sprite:
        path: str = 'resources/no_sprite.png'

    comp_added = mocker.Mock()
    comp_deleted = mocker.Mock()

    w = world.World()
    w.on_entity_component_add += comp_added
    w.on_entity_component_del += comp_deleted

    ###
    # entity creation with components
    ###
    components = [Sprite, Progress]

    e = w.add_entity('player', (comp_cls() for comp_cls in components))
    comp_added.assert_called()

    for i, call_args in enumerate(comp_added.call_args_list):
        target_entity, comp_obj = call_args[0]
        assert target_entity.uid == e.uid
        assert isinstance(comp_obj, components[i])

    added_components = {type(call_args[0][1]) for call_args in comp_added.call_args_list}
    assert added_components == set(components)

    ###
    # entity testing
    ###
    assert Sprite in e
    assert Progress in e
    assert float not in e
    assert e[Sprite].path == 'resources/no_sprite.png'
    assert e[Progress].value == 0.0

    ###
    # component destruction
    ###
    w.del_entity(e.uid)
    comp_deleted.assert_called()
    assert comp_deleted.call_count == 2
    assert set(type(call_args[0][1]) for call_args in comp_deleted.call_args_list) == set(components)


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
    # Test component add
    ###
    e.add_component(5)
    e.add_component(False)
    e.add_component('hello')

    assert e[int] == 5
    assert not e[bool]
    assert e[str] == 'hello'
    assert {int, bool, str} == set(e.components.keys())

    comp_added.assert_called()
    assert comp_added.call_count == 3

    ###
    # Test adding of already present components
    ###
    with pytest.raises(world.ComponentError):
        e.add_component(3)

    with pytest.raises(world.ComponentError):
        e.add_component(True)

    ###
    # Test component removal
    ###
    e.del_component(int)
    comp_deleted.assert_called_once()

    with pytest.raises(world.ComponentError):
        e.del_component(float)

    ###
    # Test access of undefined components
    ###
    with pytest.raises(world.ComponentError):
        e[dict]
