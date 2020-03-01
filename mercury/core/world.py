from copy import copy
from itertools import count
from typing import (Any, Callable, Dict, Generator, Mapping, Sequence, Union,
                    cast)

from .event import Event


class ComponentError(Exception):
    pass


class Entity:

    def __init__(self, world, uid: int, name: str = ''):
        self.__world = world
        self.__id = uid
        self.__name = name
        self.__components: Dict[type, Any] = {}

    @property
    def uid(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    def add_component(self, comp: type) -> Any:
        comp_type = type(comp)
        if comp_type in self.__components:
            raise ComponentError(f'{self} already has a component of type "{comp_type.__name__}"')

        self.__components[comp_type] = comp
        self.__world.on_entity_component_add(self, comp)
        return comp

    def del_component(self, comp_type: type) -> Any:
        if comp_type not in self.__components:
            raise ComponentError(f'{self} does not have a component of type "{comp_type.__name__}"')

        comp = self.__components[comp_type]
        self.__world.on_entity_component_del(self, comp)
        self.__components.pop(comp_type)
        return comp

    @property
    def components(self) -> Mapping[type, Any]:
        return copy(self.__components)

    def __repr__(self) -> str:
        return f'Entity(world={id(self.__world)}, uid={self.__id}, name={self.__name})'

    def __getitem__(self, comp_type: type) -> Any:
        if comp_type not in self.__components:
            raise ComponentError(f'{self} does not have a component of type "{comp_type.__name__}"')
        return self.__components[comp_type]


class World:

    def __init__(self):
        self.on_entity_add = Event('on_entity_add')
        self.on_entity_del = Event('on_entity_del')
        self.on_entity_component_add = Event('on_entity_component_add')
        self.on_entity_component_del = Event('on_entity_component_del')

        self.__entities = {}
        self.__id_gen = count(1000)

    def add_entity(self, name: str = '', components: Sequence[type] = None) -> Entity:
        entity = Entity(self, uid=next(self.__id_gen), name=name)
        self.__entities[entity.uid] = entity
        self.on_entity_add(entity)

        for comp in components or ():
            entity.add_component(comp)

        return entity

    def del_entity(self, entity: Union[Entity, int]):
        if isinstance(entity, int):
            entity = self.__entities.pop(entity)
        else:
            self.__entities.pop(entity.uid)

        entity = cast(Entity, entity)

        for comp_type in entity.components:
            entity.del_component(comp_type)

        self.on_entity_del(entity)

    def del_entities(self):
        for uid in list(self.__entities):
            self.del_entity(uid)

    def query_entities(self, filter: Callable[[Entity], bool]) -> Generator[Entity, None, None]:
        for entity in self.__entities.values():
            if filter(entity):
                yield entity
