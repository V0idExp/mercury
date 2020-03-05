import os

from ..sprite_sheet_loader import SpriteSheetLoader


def test_load_spritesheet():
    loader = SpriteSheetLoader()

    expect_frame_geometry = {
        'plane0': (0, 0, 32, 27),
        'plane1': (0, 27, 32, 27),
        'plane2': (0, 55, 32, 27),
    }

    path = os.path.dirname(__file__)
    filename = os.path.join(path, 'test_sprite_sheet.xml')

    sheet = loader.load(filename)
    assert sheet.atlas.path == 'test_sprite_sheet.png'
    assert len(sheet.frames) == len(expect_frame_geometry)

    for name, (x, y, w, h) in expect_frame_geometry.items():
        assert name in sheet.frames
        frame = sheet.frames[name]
        assert frame.x == x
        assert frame.y == y
        assert frame.w == w
        assert frame.h == h
