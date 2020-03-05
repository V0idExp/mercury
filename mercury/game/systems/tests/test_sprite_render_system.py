import os

import inject

from mercury.core.system import SystemRegistry
from mercury.core.world import World
from mercury.gfx.sprite_renderer.renderer import SpriteRenderer

from ..sprite_render_system import SpriteComponent, SpriteRenderSystem


def test_sprite_tracking(mocker):
    w = World()
    sysreg = SystemRegistry(w)
    sprite_sys = SpriteRenderSystem()
    sysreg.register_system(sprite_sys)
    renderer = inject.instance(SpriteRenderer)
    base_dir = os.path.join(os.getcwd(), 'mercury', 'res', 'loaders', 'tests')
    resource0 = os.path.join(base_dir, 'test_sprite_0.xml')
    resource1 = os.path.join(base_dir, 'test_sprite_1.xml')

    comp_added = mocker.spy(sprite_sys, 'on_entity_component_added')
    comp_deleted = mocker.spy(sprite_sys, 'on_entity_component_deleted')
    sprite_add = mocker.spy(renderer, 'add_sprite')
    sprite_remove = mocker.spy(renderer, 'remove_sprite')
    render = mocker.spy(renderer, 'render')

    assert len(renderer.sprites) == 0

    # entity with a sprite component with undefined resource
    e = w.add_entity(components=(
        SpriteComponent(),
    ))

    comp_added.assert_called_once()

    sysreg.tick_all()

    comp = e[SpriteComponent]
    assert comp.x == 0
    assert comp.y == 0
    assert comp.resource == ''

    # only the sprite component should have been added and removed, no related
    # sprites should have been created and removed, since no resource was
    # specified
    assert len(renderer.sprites) == 0
    w.del_entity(e)
    comp_deleted.assert_called_once()
    sprite_add.assert_not_called()
    sprite_remove.assert_not_called()

    # create an empty entity once again, but set the resource afterwards
    e = w.add_entity(components=(
        SpriteComponent(),
    ))
    comp = e[SpriteComponent]

    # set the path to the sprite and tick again, the sprite should be created
    comp.resource = resource0
    sysreg.tick_all()
    assert len(renderer.sprites) == 1
    sprite_add.assert_called_once()
    render.assert_called()

    # destroy the entity, the sprite should be destroyed as well
    w.del_entity(e)
    assert len(renderer.sprites) == 0
    sprite_remove.assert_called_once()

    sprite_add.reset_mock()
    sprite_remove.reset_mock()

    # create another entity with resource specified
    e = w.add_entity(components=(
        SpriteComponent(x=99, y=199, resource=resource0),
    ))
    sysreg.tick_all()

    sprite_add.assert_called_once()
    assert len(renderer.sprites) == 1

    comp = e[SpriteComponent]
    assert comp.x == 99
    assert comp.y == 199
    assert comp.resource == resource0

    cur_sprite_id = id(renderer.sprites[0])

    # change the resource, the sprite should be replaced with a new one
    comp.resource = resource1
    sysreg.tick_all()
    sprite_remove.assert_called_once()
    assert sprite_add.call_count == 2
    assert len(renderer.sprites) == 1

    new_sprite_id = id(renderer.sprites[0])
    assert new_sprite_id != cur_sprite_id
