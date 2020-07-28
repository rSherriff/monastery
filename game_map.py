from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from tcod.console import Console

from entity import Actor, Prop
from entity_holder import EntityHolder
from enum import auto, Enum
from room_holder import Rooms
from utility import Neighbourhood
import tcod

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(self, engine: Engine, width: int, height: int):
        self.engine = engine
        self.width, self.height = width, height
        self.entity_holder = EntityHolder()
        self.tiles = np.full((width, height), fill_value=tile_types.floor, order="F")
        self.cost = None
        self.room_holder = Rooms(self)

    def update(self):
        self.cost = np.array(self.tiles["walkable"], dtype=np.int8)

        """ Very expensive!
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.cost[x, y] += self.tiles[x, y]["cost"]
        """
        for entity in self.entity_holder.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and self.cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                if isinstance(entity, Actor):
                    self.cost[entity.x, entity.y] += 10
                if isinstance(entity, Prop):
                    self.cost[entity.x, entity.y] += 1000

        self.graph = tcod.path.SimpleGraph(cost=self.cost, cardinal=2, diagonal=3)

    def add_entity(self, entity: Entity):
        self.entity_holder.entities.add(entity)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    @property
    def entities(self):
        return self.entity_holder.entities

    @property
    def rooms(self):
        return self.room_holder.rooms

    @property
    def all_entities(self):
        all_entities = set()
        for entity in self.entities:
            all_entities.add(entity)

        for room in self.rooms:
            for entity in room.entities:
                all_entities.add(entity)

        return all_entities

    @property
    def entities_sorted_for_rendering(self):
        return sorted(self.all_entities, key=lambda x: x.render_order.value)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            return

        for room in self.rooms:
            if entity in room.entities:
                self.entities.remove(entity)
                return

    def get_neighbouring_tiles(self, position: Tuple[int, int], neighbourhood: Neighbourhood):
        if neighbourhood is Neighbourhood.VON_NEUMANN:
            neighbours = ([position[0] - 1, position[1]],
                          [position[0] + 1, position[1]],
                          [position[0], position[1] - 1],
                          [position[0], position[1] + 1]
                          )
        elif neighbourhood is Neighbourhood.MOORE:
            neighbours = ([position[0] - 1, position[1] - 1],
                          [position[0], position[1] - 1],
                          [position[0] + 1, position[1] - 1],
                          [position[0] - 1, position[1]],
                          [position[0] + 1, position[1]],
                          [position[0] - 1, position[1] + 1],
                          [position[0], position[1] + 1],
                          [position[0] + 1, position[1] + 1],
                          )

        return neighbours

    def can_place_prop_in_tile(self, x: int, y: int):
        if self.get_actor_at_location(x, y) is not None:
            return False
        if len(self.get_entities_at_location(x, y)) > 0:
            return False

        return True

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entity_holder.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

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

        for room in self.rooms:
            for entity in room.entities:
                if entity.x == x and entity.y == y:
                    entities.append(entity)

        return entities

    def get_tile_bg_colour(self, x: int, y: int) -> Tuple[int, int, int]:
        for entity in reversed(sorted(self.get_entities_at_location(x, y), key=lambda x: x.render_order.value)):
            if entity.colours_bg:
                return entity.bg_colour

        np_colour_array = self.tiles[x, y]["graphic"]["bg"]
        return [np_colour_array[0], np_colour_array[1], np_colour_array[2]]

    def get_blocking_entity_at_location(self, location_x: int, location_y: int,) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        for room in self.rooms:
            for entity in room.entities:
                if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
                ):
                    return entity

        return None

    def replace_tile(self, x: int, y: int, tile: np.ndarray):
        self.tiles[x, y] = tile

    def get_room(self, room_type: RoomType):
        return self.room_holder.get_room(room_type)
