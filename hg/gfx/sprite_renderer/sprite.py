from typing import Sequence, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Frame:

    x: int
    y: int
    w: int
    h: int


@dataclass
class Image:

    path: str
    width: int
    height: int
    data: Optional[Any] = None


@dataclass
class SpriteSheet:

    atlas: Image
    frames: Dict[str, Frame]


class Sprite:

    def __init__(self, x: int, y: int, sheet: SpriteSheet, frames: Sequence, fps: float, loop: bool):
        self.x = x
        self.y = y
        self.sheet = sheet
        self.fps = fps
        self.frames = frames
        self.loop = loop

        self.__time_acc = 0.0
        self.__frame_seq = None
        self.__frame: Optional[Any] = None

        self.stop()

    @property
    def current_frame(self) -> Optional[Frame]:
        if self.__frame is not None:
            return self.sheet.frames[self.__frame]
        return None

    def play(self, time: float):
        if self.fps > 0 and time > 0:
            self.__time_acc += time
            frame_time = 1000.0 / self.fps
            while self.__time_acc >= frame_time:
                self.__time_acc -= frame_time
                self.__frame = self.__next_frame()

    def stop(self):
        self.__time_acc = 0.0
        self.__frame_seq = (f for f in self.frames) if self.frames else None
        self.__frame = self.__next_frame()

    def __next_frame(self) -> Optional[Frame]:
        if self.__frame_seq is not None:
            try:
                return next(self.__frame_seq)
            except StopIteration:
                if self.loop:
                    self.stop()
                    return self.__frame

        return None
