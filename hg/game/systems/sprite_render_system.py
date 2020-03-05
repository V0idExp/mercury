from copy import copy

import inject

from hg.core.system import System
from hg.core.world import Entity, World
from hg.gfx.sprite_renderer.renderer import SpriteRenderer
from hg.res.loaders.sprite_loader import SpriteLoader

from ..components.sprite_component import SpriteComponent


class SpriteRenderSystem(System):

    def __init__(self):
        self.__sprites = {}
        self.__pending_entities = []

    def on_entity_component_added(self, entity, component):
        if isinstance(component, SpriteComponent):
            self.__pending_entities.append(entity.uid)

    def on_entity_component_deleted(self, entity, component):
        if isinstance(component, SpriteComponent):
            if entity.uid in self.__sprites:
                self.__destroy_sprite(entity)
            else:
                self.__pending_entities.remove(entity.uid)

    @inject.autoparams()
    def tick(self, world: World, renderer: SpriteRenderer):
        # process pending entities and create a sprite for those who have a
        # valid SpriteComponent
        for uid in copy(self.__pending_entities):
            entity = world[uid]
            component = entity[SpriteComponent]
            if component.resource:
                self.__create_sprite(entity, component)
                self.__pending_entities.pop(0)

        # update sprites
        for uid, (resource, sprite) in list(self.__sprites.items()):
            entity = world[uid]
            component = entity[SpriteComponent]

            # replace the sprite with a new one in case the resource has changed
            if component.resource != resource:
                self.__destroy_sprite(entity)
                if component.resource:
                    self.__create_sprite(entity, component)
            else:
                sprite.x = component.x
                sprite.y = component.y

        renderer.render()

    @inject.autoparams()
    def __create_sprite(self, entity: Entity, component: SpriteComponent, loader: SpriteLoader,
                        renderer: SpriteRenderer):
        sprite = loader.load(component.resource)
        renderer.add_sprite(sprite)
        self.__sprites[entity.uid] = (component.resource, sprite)
        return sprite

    @inject.autoparams()
    def __destroy_sprite(self, entity: Entity, renderer: SpriteRenderer):
        renderer.remove_sprite(self.__sprites[entity.uid][1])
        self.__sprites.pop(entity.uid)
