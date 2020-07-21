from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from tcod.console import Console
from entity import Actor

import tcod
import queue
import entity_factories
import random

if TYPE_CHECKING:
    from entity import Entity
    from engine import Engine
    from game_map import GameMap

# TODO: Create a proc gen class for names and such


def generate_brother_name():
    name = str("Brother ")
    pot_names = ["Simon", "Paul", "Robert", "Richard", "John", "Matthew", "Peter"]
    name = name + pot_names[random.randrange(0, len(pot_names) - 1)]
    return name


class Monastery:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.money = 0
        self.food = 0

        n_brothers = 5
        for i in range(0, n_brothers):
            brother = entity_factories.brother.spawn(self.engine.game_map, i, i)
            brother.name = generate_brother_name()
            pass
