from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from entity import Actor, Prop

if TYPE_CHECKING:
    from entity import Entity


class EntityHolder():
    def __init__(self):
        self.entities = set()

    def get_blocking_entity_at_location(self, location_x: int, location_y: int,) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_surrounding_entities(self, position: Tuple[int, int], neighbourhood: Neighbourhood):
        entities = list()
        neighbours = self.get_neighbouring_tiles(position, neighbourhood)

        for neighbour in neighbours:
            entities.append(self.get_entities_at_location(neighbour[0], neighbour[1]))

        return entities

    def get_entities_at_location(self, x: int, y: int) -> list(Entity):
        entities = list()
        for entity in self.entities:
            if entity.x == x and entity.y == y:
                entities.append(entity)

        return entities

    def remove_entity(self, entity: Entity):
        entities.remove(entity)
