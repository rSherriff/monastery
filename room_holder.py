from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING, Tuple
from rooms import RoomType, Room
from farm import Farm

import tcod
import queue
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from action import Action
    from game_map import GameMap


class Rooms():
    def __init__(self, engine: Engine):
        self.engine = engine
        self.rooms = list()
        pass

    def add_room(self, room_type: RoomType, landscape: GameMap, tiles: list):
        new_room = None
        if room_type is RoomType.FARM:
            new_room = Farm(landscape, tiles)
        else:
            new_room = Room(landscape, room_type, tiles)

        self.rooms.append(new_room)
        print(f"Created a new {new_room.name}")

    def get_room(self, room_type: RoomType):
        for room in self.rooms:
            if room.type is room_type:
                return room

        return None
