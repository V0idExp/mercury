import os
import sys
from unittest.mock import Mock

import pytest

from hg.gfx.sprite_renderer.sprite import Image
from hg.gfx.sprite_renderer.renderer import SpriteRenderer
from hg.res.loaders.image_loader import ImageLoader
from hg.res.loaders.loader import Loader
from hg.res.loaders.sprite_sheet_loader import SpriteSheetLoader


class SDL2(Mock):

    @classmethod
    def SDL_GetTicks(cls):
        return 0


sys.modules['sdl2'] = SDL2()


class _ImageLoader(Loader):

    def load(self, path):
        return Image(path=os.path.basename(path), width=32, height=32)


@pytest.fixture
def inject_config(mocker):
    return {
        ImageLoader: _ImageLoader,
        SpriteSheetLoader: SpriteSheetLoader,
        SpriteRenderer: lambda: SpriteRenderer(sdl_renderer=mocker.Mock()),
    }


@pytest.fixture
def inject(inject_config):
    import inject

    def bind(binder: inject.Binder):
        for cls, constructor in inject_config.items():
            binder.bind_to_constructor(cls, constructor)

    inject.clear_and_configure(bind)

    yield

    inject.clear()


def pytest_configure(config):
    config.addinivalue_line('markers', 'inject: configure the dependency injector for a given test')


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        if item.get_closest_marker('inject'):
            item.fixturenames.append('inject')
