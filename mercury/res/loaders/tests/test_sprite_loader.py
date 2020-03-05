import os

from ..sprite_loader import SpriteLoader


def test_load_sprite():
    loader = SpriteLoader()

    path = os.path.dirname(__file__)
    filename = os.path.join(path, 'test_sprite_0.xml')

    sprite = loader.load(filename)

    assert sprite.sheet.atlas.path == 'test_sprite_sheet.png'
    assert len(sprite.frames) == 3
    assert sprite.frames == ['plane0', 'plane1', 'plane2']
    assert sprite.fps == 10
    assert sprite.loop
