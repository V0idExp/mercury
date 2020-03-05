import inject
import os
from mercury.gfx.sprite_renderer.sprite import Image

from ..loader import Loader
from ..image_loader import ImageLoader
from ..sprite_sheet_loader import SpriteSheetLoader


class _ImageLoader(Loader):

    def load(self, path):
        return Image(path=os.path.basename(path), width=32, height=32)


def config(binder: inject.Binder):
    binder.bind_to_constructor(ImageLoader, _ImageLoader)
    binder.bind_to_constructor(SpriteSheetLoader, SpriteSheetLoader)
