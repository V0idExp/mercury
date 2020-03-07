from unittest.mock import ANY

import pytest

from .. import renderer
from ..sprite import Frame, Sprite, SpriteSheet


@pytest.fixture
def spritesheet(mocker):
    frames = {
        'plane0': Frame(0, 0, 32, 32),
        'plane1': Frame(32, 0, 32, 32),
        'plane2': Frame(64, 0, 32, 32),
        'fire0': Frame(0, 32, 16, 16),
        'fire1': Frame(16, 32, 16, 16),
        'fire2': Frame(32, 32, 16, 16),
    }

    return SpriteSheet(mocker.Mock(), frames)


@pytest.fixture
def blit_mock(mocker):
    return mocker.patch.object(renderer, 'blit', mocker.Mock())


@pytest.fixture
def time_mock(mocker):

    class TimeMock:
        def __init__(self):
            self.time = 0

        def __call__(self):
            return self.time

    mock = TimeMock()
    mocker.patch.object(renderer, 'get_time', mock)

    return mock


def test_empty_sprite(mocker, spritesheet, blit_mock, time_mock):
    rndr = renderer.SpriteRenderer(mocker.Mock())
    sprite = Sprite(
        x=0,
        y=0,
        sheet=spritesheet,
        frames=(),
        fps=60.0,
        loop=True)

    rndr.add_sprite(sprite)
    play = mocker.spy(sprite, 'play')

    for second in range(10):
        time_mock.time = second * 1000
        rndr.render()

    blit_mock.assert_not_called()
    play.assert_called()
    assert play.call_count == 10


@pytest.mark.inject()
def test_sprite_play_once(mocker, spritesheet, blit_mock, time_mock):
    rndr = renderer.SpriteRenderer(mocker.Mock())
    sprite = Sprite(
        x=-10,
        y=-20,
        sheet=spritesheet,
        frames=('plane0', 'plane1', 'plane2'),
        fps=1.0,
        loop=False)

    rndr.add_sprite(sprite)

    # T+0: 'plane0'
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (0, 0, 32, 32),
        (-10, -20, 32, 32)
    )

    # T+1s: 'plane1'
    time_mock.time = 1000
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (32, 0, 32, 32),
        (-10, -20, 32, 32)
    )

    # T+2s: 'plane2'
    time_mock.time = 2000
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (64, 0, 32, 32),
        (-10, -20, 32, 32)
    )

    # T+3s: animation finished, sprite not rendered
    time_mock.time = 3000
    blit_mock.reset_mock()
    rndr.render()
    blit_mock.assert_not_called()


@pytest.mark.inject()
def test_sprite_play_loop(mocker, spritesheet, blit_mock, time_mock):
    rndr = renderer.SpriteRenderer(mocker.Mock())
    sprite = Sprite(
        x=10,
        y=20,
        sheet=spritesheet,
        frames=('fire0', 'fire1', 'fire2'),
        fps=2.0,
        loop=True
    )
    rndr.add_sprite(sprite)

    # T+0: 'fire0'
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (0, 32, 16, 16),
        (10, 20, 16, 16)
    )

    # T+0.5s: 'fire1':
    time_mock.time = 500
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (16, 32, 16, 16),
        (10, 20, 16, 16)
    )

    # T+1s: 'fire2':
    time_mock.time = 1000
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (32, 32, 16, 16),
        (10, 20, 16, 16)
    )

    # T+1.5s: 'fire0', loop from the beginning
    time_mock.time = 1500
    rndr.render()
    blit_mock.assert_called_with(
        ANY,
        spritesheet.atlas,
        (0, 32, 16, 16),
        (10, 20, 16, 16)
    )
