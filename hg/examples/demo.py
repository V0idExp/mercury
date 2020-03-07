import os
from functools import partial

import inject
import sdl2
import sdl2.ext

from hg.core.system import SystemRegistry
from hg.core.world import World
from hg.game.components.body_component import BodyComponent
from hg.game.components.position_component import PositionComponent
from hg.game.components.sprite_component import SpriteComponent
from hg.game.settings import Settings
from hg.game.systems.physics_system import PhysicsSystem
from hg.game.systems.sprite_render_system import SpriteRenderSystem
from hg.gfx.sprite_renderer.renderer import SpriteRenderer
from hg.res.loaders.image_loader import ImageLoader
from hg.res.loaders.sprite_loader import SpriteLoader
from hg.res.loaders.sprite_sheet_loader import SpriteSheetLoader

ROOT_DIR = os.path.abspath(os.path.dirname(__package__))


def config(renderer: sdl2.SDL_Renderer, binder: inject.Binder):
    binder.bind(ImageLoader, ImageLoader(renderer))
    binder.bind(SpriteSheetLoader, SpriteSheetLoader())
    binder.bind(SpriteLoader, SpriteLoader())
    binder.bind(SpriteRenderer, SpriteRenderer(renderer))
    binder.bind(Settings, Settings())


def setup_systems(w: World) -> SystemRegistry:
    reg = SystemRegistry(w)

    # sprite render system
    reg.register_system(SpriteRenderSystem())

    # physics system
    reg.register_system(PhysicsSystem())

    return reg


def populate_world(w: World):
    w.add_entity('plane', components=(
        PositionComponent(50, 90),
        SpriteComponent(
            resource=os.path.join(ROOT_DIR, 'hg', 'res', 'loaders', 'tests', 'test_sprite_0.xml')
        ),
        BodyComponent(),
    ))


if __name__ == '__main__':
    title = os.path.basename(__file__)
    window = sdl2.ext.Window(title, size=(800, 600))
    window.show()

    renderer = sdl2.ext.Renderer(window)
    renderer.color = sdl2.ext.rgba_to_color(0x000000)

    inject.configure(partial(config, renderer.sdlrenderer))

    sprite_renderer = inject.instance(SpriteRenderer)

    w = World()
    systems = setup_systems(w)
    populate_world(w)

    tick = 0
    tick_time = inject.instance(Settings).physics_time_step * 1000
    last_frame_time = sdl2.SDL_GetTicks()
    time_acc = 0
    run = True
    while run:
        renderer.clear()

        now = sdl2.SDL_GetTicks()
        time_acc += now - last_frame_time
        last_frame_time = now

        while time_acc >= tick_time:
            time_acc -= tick_time

            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    run = False
                    break

            systems.tick_all()

            tick += 1

        sprite_renderer.render()
        renderer.present()
        window.refresh()

    sdl2.ext.quit()
