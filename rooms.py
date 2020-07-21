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


class RoomType(Enum):
    NONE = auto()
    QUIRE = auto()
    CHAPTER_HOUSE = auto()
    REFECTORY = auto()
    CELLARIUM = auto()
    DORMITORY = auto()


def get_room_types():
    return [RoomType.QUIRE, RoomType.CHAPTER_HOUSE, RoomType.REFECTORY, RoomType.CELLARIUM, RoomType.DORMITORY]


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


class Room():
    def __init__(self, room_type: RoomType, point: Tuple[int, int], width: int, height: int):
        self.type = room_type
        self.point = point
        self.width = width
        self.height = height
        self.entity_holder = EntityHolder()

    def get_random_point_in_room(self) -> Tuple[int, int]:
        return [self.point[0] + random.randint(0, self.width), self.point[1] + random.randint(0, self.height)]

    def is_point_in_room(self, point: Tuple[int, int]) -> bool:
        return (self.point[0] <= point[0] <= (self.point[0] + self.width)) and (self.point[1] <= point[1] <= (self.point[1] + self.height))

    @property
    def name(self) -> str:
        return get_room_name(self.type)

    @property
    def entities(self):
        return self.entity_holder.entities


class Rooms():
    def __init__(self, engine: Engine):
        self.engine = engine
        self.rooms = list()
        pass

    def add_room(self, room_type: RoomType, point: Tuple[int, int], width: int, height: int):
        new_room = Room(room_type, point, width, height)
        self.rooms.append(new_room)
        print(f"Created a new {get_room_name(room_type)}")
