from __future__ import annotations

from typing import TYPE_CHECKING

import colours
from tcod import Console

if TYPE_CHECKING:
    from engine import Engine
    from game_map import GameMap
    from actions import Action


class Highlight():
    """ Class representing an area of the screen selected by the players.
    Contains the highlighted tiles and renders them to the screen."""

    def __init__(self):
        self.tiles = list()

    def add_tile(self, point: Tuple[int, int], colour: Tuple[int, int, int]):
        """ Add a tile to the highlighted area. """
        self.tiles.append((point, colour))

    def render(self, console: Console):
        """Renders the highlighted slection to the screen. """
        temp_console = Console(width=console.width, height=console.height, order="F")

        for tile in self.tiles:
            temp_console.tiles_rgb[tile[0][0], tile[0][1]] = (ord(" "), (255, 255, 255), tile[1])
            temp_console.blit(console, src_x=tile[0][0], src_y=tile[0][1], dest_x=tile[0][0], dest_y=tile[0][1], width=1, height=1)

    def clear(self):
        """ Clears the highlighted tiles.
        Happens everytime mouse one is down and the mouse moves. """
        self.tiles = list()
