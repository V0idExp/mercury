from typing import Any, Tuple, Set, Callable, List, Dict, Iterable
from .world import Entity, World


EntityType = Tuple[type, ...]


class System:

    def tick(self):
        pass

    def on_entity_added(self, entity: Entity):
        pass

    def on_entity_deleted(self, entity: Entity):
        pass

    def on_entity_component_added(self, entity: Entity, attr: str, comp: Any):
        pass

    def on_entity_component_deleted(self, entity: Entity, attr: str, comp: Any):
        pass


def _make_type_set(entity_type: Iterable[type]) -> Set[int]:
    return set(id(t) for t in entity_type)


class SystemRegistry:

    def __init__(self, world: World):
        self.__world = world
        self.__systems: List[System] = []
        self.__system_types: Dict[System, List[EntityType]] = {}

        world.on_entity_add += self.__on_entity_add
        world.on_entity_del += self.__on_entity_del
        world.on_entity_component_add += self.__on_entity_comp_add
        world.on_entity_component_del += self.__on_entity_comp_del

    def register_system(self, system: System, entity_type: EntityType):
        self.__systems.append(system)
        self.__system_types.setdefault(system, []).append(entity_type)

    def unregister_system(self, system: System):
        self.__systems.remove(system)
        self.__system_types.pop(system)

    def _visit_systems(self, entity: Entity, accept: Callable):
        entity_type_set = _make_type_set(type(comp) for comp in entity.components.values())
        if entity_type_set:
            for system in self.__systems:
                for entity_type in self.__system_types[system]:
                    system_type_set = _make_type_set(entity_type)
                    if system_type_set.issubset(entity_type_set):
                        accept(system)

    def __on_entity_add(self, entity):
        for system in self.__systems:
            system.on_entity_added(entity)

    def __on_entity_del(self, entity):
        for system in self.__systems:
            system.on_entity_deleted(entity)

    def __on_entity_comp_add(self, entity, attr, comp):
        self._visit_systems(entity, lambda system: system.on_entity_component_added(entity, attr, comp))

    def __on_entity_comp_del(self, entity, attr, comp):
        self._visit_systems(entity, lambda system: system.on_entity_component_deleted(entity, attr, comp))
