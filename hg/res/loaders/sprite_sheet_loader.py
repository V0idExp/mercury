import os

import inject
from lxml import etree

from hg.gfx.sprite_renderer.sprite import Frame, SpriteSheet

from .image_loader import ImageLoader
from .loader import Loader

spritesheet_schema = None


class XMLSpriteSheetLoadError(Exception):
    pass


class SpriteSheetLoader(Loader):

    def load(self, path: str) -> SpriteSheet:
        global spritesheet_schema
        if spritesheet_schema is None:
            schema_path = os.path.dirname(__file__)
            schema_file = os.path.join(schema_path, 'sprite_sheet_schema.xsd')
            with open(schema_file, 'rb') as fo:
                schema_data = etree.XML(fo.read())
            spritesheet_schema = etree.XMLSchema(schema_data)

        parser = etree.XMLParser(schema=spritesheet_schema)
        try:
            with open(path, 'rb') as fo:
                data = fo.read()
            texture_atlas = etree.fromstring(data, parser=parser)
        except etree.XMLSyntaxError as err:
            raise XMLSpriteSheetLoadError(f'Invalid spritesheet XML file: {err}')

        frames = {}

        for sub_texture in texture_atlas.getiterator('SubTexture'):
            frame_name = sub_texture.attrib['name']
            frame = Frame(
                x=int(sub_texture.attrib['x']),
                y=int(sub_texture.attrib['y']),
                w=int(sub_texture.attrib['width']),
                h=int(sub_texture.attrib['height']),
            )
            frames[frame_name] = frame

        base_dir = os.path.dirname(path)
        image_path = os.path.join(base_dir, texture_atlas.attrib['imagePath'])
        atlas = inject.instance(ImageLoader).load(image_path)

        return SpriteSheet(atlas, frames)
