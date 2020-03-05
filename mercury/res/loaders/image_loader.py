import os

import sdl2

from mercury.gfx.sprite_renderer.sprite import Image

from .loader import Loader


class ImageLoader(Loader):

    def __init__(self, sdl_renderer: sdl2.SDL_Renderer):
        self.__renderer = sdl_renderer

    def load(self, path):
        surface = sdl2.ext.load_image(path)
        texture = sdl2.SDL_CreateTextureFromSurface(self.__renderer, surface)
        return Image(os.path.basename(path), surface.w, surface.h, texture)
