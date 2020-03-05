import sys
from unittest.mock import Mock

import inject


class SDL2(Mock):

    @classmethod
    def SDL_GetTicks(cls):
        return 0


sys.modules['sdl2'] = SDL2()


def config(binder):
    from .gfx.sprite_renderer.tests.config import config as sprite_renderer_config
    from .res.loaders.tests.config import config as loaders_config
    binder.install(loaders_config)
    binder.install(sprite_renderer_config)


def pytest_runtestloop(session):
    inject.configure(config)
