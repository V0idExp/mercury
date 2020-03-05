from typing import List, Optional, Tuple

import sdl2

from .sprite import Image, Sprite

Rect = Tuple[int, int, int, int]


def blit(rndr: sdl2.SDL_Renderer, image: Image, src_rect: Rect, dst_rect: Rect):
    src = sdl2.SDL_Rect(*src_rect)
    dst = sdl2.SDL_Rect(*dst_rect)
    sdl2.SDL_RenderCopy(rndr, image.data, src, dst)


def get_time() -> int:
    return sdl2.SDL_GetTicks()


class SpriteRenderer:

    def __init__(self, sdl_renderer: sdl2.SDL_Renderer):
        self.sprites: List[Sprite] = []
        self.__renderer = sdl_renderer
        self.__last_time: Optional[int] = None

    def add_sprite(self, sprite: Sprite):
        if sprite not in self.sprites:
            self.sprites.append(sprite)

    def remove_sprite(self, sprite: Sprite):
        if sprite in self.sprites:
            self.sprites.remove(sprite)

    def render(self):
        if self.__last_time is None:
            self.__last_time = get_time()

        now = get_time()
        time_delta = now - self.__last_time
        self.__last_time = now

        for sprite in self.sprites:
            sprite.play(time_delta)

            if sprite.current_frame is not None:
                frame = sprite.current_frame
                src_x = frame.x
                src_y = frame.y
                w = frame.w
                h = frame.h
                dst_x = sprite.x
                dst_y = sprite.y
                blit(
                    self.__renderer,
                    sprite.sheet.atlas,
                    (src_x, src_y, w, h),
                    (dst_x, dst_y, w, h)
                )
