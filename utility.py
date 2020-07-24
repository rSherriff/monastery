from typing import Iterable, Iterator, Optional, TYPE_CHECKING, Tuple

import tcod


def get_vonneumann_tiles(position: Tuple[int, int]):
    return ([position[0] - 1, position[1]],
            [position[0] + 1, position[1]],
            [position[0], position[1] - 1],
            [position[0], position[1] + 1],
            )


def line_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an line between these two points."""
    x1, y1 = start
    x2, y2 = end

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (x2, y2)).tolist():
        yield x, y


def horizontal_line_between(start_x: int, end_x: int, y: int) -> Iterator[Tuple[int, int]]:
    curr_x = min(start_x, end_x)
    end_x = max(start_x, end_x)
    while curr_x <= end_x:
        yield curr_x, y
        curr_x += 1


def vertical_line_between(start_y: int, end_y: int, x: int) -> Iterator[Tuple[int, int]]:
    curr_y = min(start_y, end_y)
    end_y = max(start_y, end_y)
    while curr_y <= end_y:
        yield x, curr_y
        curr_y += 1


def box_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    start_x = min(start[0], end[0])
    end_x = max(start[0], end[0])
    start_y = min(start[1], end[1])
    end_y = max(start[1], end[1])
    for x in range(start_x, end_x + 1):
        for y in range(start_y, end_y + 1):
            yield x, y


def box_width(tiles):
    start_y = tiles[0][1]
    curr_y = start_y
    index = 0
    while start_y is curr_y:
        start_y = tiles[index][1]
        index += 1

    return index


def box_height(tiles):
    return int(len(tiles) / box_width(tiles))
