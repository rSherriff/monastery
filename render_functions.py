from __future__ import annotations

from typing import TYPE_CHECKING

import colours
from tcod import Console, event

if TYPE_CHECKING:
    from engine import Engine
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y):
        return ""

    names = ", ".join(
        entity.name for entity in game_map.all_entities if entity.x == x and entity.y == y
    )

    return names


def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=45, width=20, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=colours.WHITE
    )


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.map_mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )
    console.print(x=x, y=y, string=names_at_mouse_location, fg=colours.WHITE)


def render_map_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.map_mouse_location
    console.print(x=x, y=y, string=f"X:{mouse_x} Y:{mouse_y}")


def render_rooms_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    room_str = str("")
    for room in engine.game_map.rooms:
        if room.is_point_in_room(engine.map_mouse_location):
            room_str = room.name

    console.print(x=x, y=y, string=room_str, fg=colours.WHITE)


def render_fps_counter(
    console: Console, x: int, y: int, fps: int
) -> None:
    console.print(x=x, y=y, string=f"FPS:{fps}", fg=colours.WHITE)

def render_message_box(console: Console, message: str) -> None:

    # TODO: Make this work with multiple line messages
    width = len(message) + 2
    height = 3

    log_console = Console(width, height)

    log_console.draw_frame(0, 0, width, height)
    log_console.print_box(0, 1, log_console.width, 1, message, alignment=2)
    log_console.blit(console, int(console.width / 2) - int(width / 2), int(console.height / 2) - int(height / 2))
