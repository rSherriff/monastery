from typing import Tuple

GRASS_GREEN = (17, 41, 6)
DARK_GREEN = (40, 50, 6)
DRY_MUD_BROWN = (75, 57, 35)
DRY_MUD_BROWN_B = (75, 65, 35)
WET_MUD_BROWN = (39, 27, 10)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (96, 96, 96)

WALL_BG = DARK_GREY
WALL_FG = DARK_GREEN


def colour_lerp(colour1: Tuple[int, int, int], colour2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (int(colour1[0] + t * (colour2[0] - colour1[0])), int(colour1[1] + t * (colour2[1] - colour1[1])), int(colour1[2] + t * (colour2[2] - colour1[2])))


def lighten_darken_colour(col: Tuple[int, int, int], amt) -> Tuple[int, int, int]:
    r = col[0] + amt
    b = (col[1] & 0x00FF) + amt
    g = (col[2] & 0x0000FF) + amt
    return (r, g, b)
