import os

import inject
from lxml import etree

from hg.gfx.sprite_renderer.sprite import Sprite

from .loader import Loader
from .sprite_sheet_loader import SpriteSheetLoader


sprite_schema = None


class XMLSpriteLoadError(Exception):
    pass


class SpriteLoader(Loader):

    def load(self, path) -> Sprite:
        global sprite_schema
        if sprite_schema is None:
            schema_dir = os.path.dirname(__file__)
            schema_file = os.path.join(schema_dir, 'sprite_schema.xsd')
            with open(schema_file, 'rb') as fo:
                schema_data = etree.XML(fo.read())
            sprite_schema = etree.XMLSchema(schema_data)

        with open(path, 'rb') as fo:
            data = fo.read()

        sheet_loader = inject.instance(SpriteSheetLoader)
        res_dir = os.path.dirname(path)

        parser = etree.XMLParser(schema=sprite_schema)
        try:
            root = etree.fromstring(data, parser=parser)
        except etree.XMLSyntaxError as err:
            raise XMLSpriteLoadError(f'Invalid sprite XML file: {err}')

        sheet_file = root.attrib['sheet']
        sheet = sheet_loader.load(os.path.join(res_dir, sheet_file))

        frames = []
        for frame in root.getiterator('frame'):
            frames.append(frame.text)

        duration = float(root.attrib['duration'])
        if duration > 0:
            frame_time = duration / len(frames)
            fps = 1.0 / frame_time
        else:
            fps = 0.0

        loop = root.attrib['loop'] == 'true'

        return Sprite(0, 0, sheet, frames, fps, loop)
