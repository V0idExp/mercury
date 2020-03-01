from abc import ABCMeta, abstractmethod
from typing import Any, List

from .world import Entity, World


class System(metaclass=ABCMeta):

    @abstractmethod
    def tick(self, world: World):
        raise NotImplementedError

    def on_entity_added(self, entity: Entity):
        pass

    def on_entity_deleted(self, entity: Entity):
        pass

    def on_entity_component_added(self, entity: Entity, comp: Any):
        pass

    def on_entity_component_deleted(self, entity: Entity, comp: Any):
        pass


class SystemRegistry:

    def __init__(self, world: World):
        self.__world = world
        self.__systems: List[System] = []

        world.on_entity_add += self.__on_entity_add
        world.on_entity_del += self.__on_entity_del
        world.on_entity_component_add += self.__on_entity_comp_add
        world.on_entity_component_del += self.__on_entity_comp_del

    def register_system(self, system: System):
        self.__systems.append(system)

    def unregister_system(self, system: System):
        self.__systems.remove(system)

    def tick_all(self):
        for system in self.__systems:
            system.tick(self.__world)

    def __on_entity_add(self, entity):
        for system in self.__systems:
            system.on_entity_added(entity)

    def __on_entity_del(self, entity):
        for system in self.__systems:
            system.on_entity_deleted(entity)

    def __on_entity_comp_add(self, entity, comp):
        for system in self.__systems:
            system.on_entity_component_added(entity, comp)

    def __on_entity_comp_del(self, entity, comp):
        for system in self.__systems:
            system.on_entity_component_deleted(entity, comp)
