from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING, Tuple
from tcod.console import Console
from enum import auto, Enum
from entity import Actor
from entity_holder import EntityHolder

import tcod
import queue
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from action import Action
    from game_map import GameMap


class RoomType(Enum):
    NONE = auto()
    QUIRE = auto()
    CHAPTER_HOUSE = auto()
    REFECTORY = auto()
    CELLARIUM = auto()
    DORMITORY = auto()
    CLOISTER = auto()
    FARM = auto()

    @staticmethod
    def get_room_types():
        return [RoomType.QUIRE, RoomType.CHAPTER_HOUSE, RoomType.REFECTORY, RoomType.CELLARIUM, RoomType.DORMITORY, RoomType.FARM]


class Room():
    def __init__(self, landscape: GameMap, room_type: RoomType, tiles: list):
        self.landscape = landscape
        self.type = room_type
        self.tiles = tiles
        self.entity_holder = EntityHolder()

    def get_random_point_in_room(self) -> Tuple[int, int]:
        return self.tiles[random.randint(0, len(self.tiles) - 1)]

    def is_point_in_room(self, point: Tuple[int, int]) -> bool:
        return point in self.tiles

    @property
    def name(self) -> str:
        return Room.get_room_name(self.type)

    @property
    def entities(self):
        return self.entity_holder.entities

    def update(self):
        pass

    def spawn_entity(self, entity: Entity, x: int, y: int):
        self.entities.add(entity.spawn_in_room(x, y))

    @staticmethod
    def get_room_name(room_type: RoomType):
        if room_type is RoomType.NONE:
            return "None"
        if room_type is RoomType.QUIRE:
            return "Quire"
        if room_type is RoomType.CHAPTER_HOUSE:
            return "Chapter House"
        if room_type is RoomType.REFECTORY:
            return "Refectory"
        if room_type is RoomType.CELLARIUM:
            return "Cellarium"
        if room_type is RoomType.DORMITORY:
            return "Dormitory"
        if room_type is RoomType.CLOISTER:
            return "Cloister"
        if room_type is RoomType.FARM:
            return "Farm"
