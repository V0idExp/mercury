import inject
from unittest.mock import Mock
from ..renderer import SpriteRenderer


def config(binder: inject.Binder):
    binder.bind_to_constructor(SpriteRenderer, lambda: SpriteRenderer(sdl_renderer=Mock()))
