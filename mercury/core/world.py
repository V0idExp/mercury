from .event import Event
from itertools import count
from typing import Union, Any, cast, Mapping, Dict


class ComponentError(Exception):
    pass


class Entity:

    def __init__(self, world, uid: int, name: str = ''):
        self.__world = world
        self.__id = uid
        self.__name = name
        self.__components: Dict[str, Any] = {}

    @property
    def uid(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    def add_component(self, attr: str, comp: Any):
        if hasattr(self, attr):
            raise ComponentError(f'attribute "{attr}" already exists')

        self.__components[attr] = comp
        setattr(self, attr, comp)
        self.__world.on_entity_component_add(self, attr, comp)

    def del_component(self, attr: str) -> Any:
        if not hasattr(self, attr):
            raise ComponentError(f'attribute "{attr}" does not exist')
        elif attr in ('uid', 'name', 'components'):
            raise ComponentError(f'invalid attribute name "{attr}"')

        self.__world.on_entity_component_del(self, attr, getattr(self, attr))

        comp = self.__components.pop(attr)
        delattr(self, attr)
        return comp

    @property
    def components(self) -> Mapping[str, Any]:
        return dict(**self.__components)


class World:

    def __init__(self):
        self.on_entity_add = Event('on_entity_add')
        self.on_entity_del = Event('on_entity_del')
        self.on_entity_component_add = Event('on_entity_component_add')
        self.on_entity_component_del = Event('on_entity_component_del')

        self.__entities = {}
        self.__id_gen = count(1000)

    def add_entity(self, name: str = '', components: Mapping[str, Any] = None):
        entity = Entity(self, uid=next(self.__id_gen), name=name)
        self.__entities[entity.uid] = entity
        self.on_entity_add(entity)

        if components is not None:
            for attr, value in components.items():
                entity.add_component(attr, value)

        return entity

    def del_entity(self, entity: Union[Entity, int]):
        if isinstance(entity, int):
            entity = self.__entities.pop(entity)
        else:
            self.__entities.pop(entity.uid)

        entity = cast(Entity, entity)

        for attr in entity.components:
            entity.del_component(attr)

        self.on_entity_del(entity)

        return entity
