from __future__ import annotations

from typing import TYPE_CHECKING

import colours
from tcod import Console

if TYPE_CHECKING:
    from engine import Engine
    from game_map import GameMap
    from actions import Action


class Highlight():
    def __init__(self):
        self.tiles = list()

    def add_tile(self, point: Tuple[int, int], colour: Tuple[int, int, int]):
        self.tiles.append((point, colour))

    def render(self, console: Console):
        temp_console = Console(width=console.width, height=console.height, order="F")

        for tile in self.tiles:
            temp_console.tiles_rgb[tile[0][0], tile[0][1]] = (ord(" "), (255, 255, 255), tile[1])
            temp_console.blit(console, src_x=tile[0][0], src_y=tile[0][1], dest_x=tile[0][0], dest_y=tile[0][1], width=1, height=1)

    def clear(self):
        self.tiles = list()
