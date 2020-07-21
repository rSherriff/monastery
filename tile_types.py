from typing import Tuple

import numpy as np  # type: ignore
import colours
import random

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("wearable", np.bool),  # True if this tile can be worn down
        ("wear", np.float),  # True if this tile doesn't block FOV.
        ("graphic", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("original_bg", "3B"),
        ("cost", np.int)
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    graphic: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    wearable: bool
) -> np.ndarray:
    """Helper function for defining individual tile types """
    wear = 1
    cost = 0
    return np.array((walkable, transparent, wearable, wear, graphic, graphic[2], cost), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
#SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    wearable=True,
    graphic=(ord(" "), (255, 255, 255), colours.GRASS_GREEN),
)

stone_floor = new_tile(
    walkable=True,
    transparent=True,
    wearable=False,
    graphic=(ord(" "), (255, 255, 255), colours.GREY),
)

wall = new_tile(
    walkable=True,
    transparent=False,
    wearable=True,
    graphic=(ord(" "), colours.WALL_FG, colours.WALL_BG),
)
