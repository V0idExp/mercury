import inject

from hg.core.system import System
from hg.core.world import Entity, World
from hg.gfx.sprite_renderer.renderer import SpriteRenderer
from hg.res.loaders.sprite_loader import SpriteLoader

from ..components.sprite_component import SpriteComponent
from ..components.position_component import PositionComponent


class SpriteRenderSystem(System):

    def __init__(self):
        self.__sprites = {}

    @inject.autoparams()
    def tick(self, world: World, renderer: SpriteRenderer):
        entities = world.query_entities(lambda e: e.has_components(SpriteComponent, PositionComponent))
        own_uids = set(self.__sprites)
        cur_uids = set(e.uid for e in entities)

        in_common = own_uids.intersection(cur_uids)
        to_destroy = own_uids.difference(cur_uids)
        to_create = cur_uids.difference(own_uids)

        # check current sprites for resource changes and mark them for
        # destruction or replacement
        for uid in in_common:
            e = world[uid]
            component = e[SpriteComponent]
            resource, sprite = self.__sprites[uid]

            if component.resource != resource:
                to_destroy.add(uid)
                if component.resource:
                    to_create.add(uid)

        # remove sprites from entities marked for destruction
        for uid in to_destroy:
            self.__destroy_sprite(uid)

        # create and initialize sprites for new ones with a valid resource
        for uid in to_create:
            e = world[uid]
            component = e[SpriteComponent]
            if component.resource:
                sprite = self.__create_sprite(uid, component.resource)

        # update sprite positions
        for uid in self.__sprites:
            e = world[uid]
            pos = e[PositionComponent]
            sprite.x = int(round(pos.x))
            sprite.y = int(round(pos.y))

    def on_entity_deleted(self, entity: Entity):
        if entity.uid in self.__sprites:
            self.__destroy_sprite(entity.uid)

    @inject.autoparams()
    def __create_sprite(self, uid: int, resource: str, loader: SpriteLoader, renderer: SpriteRenderer):
        sprite = loader.load(resource)
        renderer.add_sprite(sprite)
        self.__sprites[uid] = (resource, sprite)
        return sprite

    @inject.autoparams()
    def __destroy_sprite(self, uid: int, renderer: SpriteRenderer):
        renderer.remove_sprite(self.__sprites[uid][1])
        self.__sprites.pop(uid)
