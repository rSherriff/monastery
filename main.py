#!/usr/bin/env python3
import tcod
import copy
import entity_factories
import time
import colours

from engine import Engine
from game_map import GameMap
from render_functions import render_names_at_mouse_location, render_map_mouse_location, render_rooms_at_mouse_location, render_fps_counter
import colours


def main() -> None:
    screen_aspect = (90, 60)
    map_aspect = (80, 50)
    scaler = 1.5
    screen_width = int(screen_aspect[0] * scaler)
    screen_height = int(screen_aspect[1] * scaler)

    map_width = int(map_aspect[0] * scaler)
    map_height = int(map_aspect[1] * scaler)

    tileset = tcod.tileset.load_tilesheet(
        "font.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player, map_width, map_height)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="In a Monastery Garden",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        engine.message_log.add_message("Starting...", colours.WHITE)

        cycle = 0
        time_sum = 0
        fps = 0
        while True:
            tic = time.perf_counter()

            root_console.clear()
            engine.event_handler.on_render(console=root_console)

            # Debug render functions
            render_fps_counter(console=root_console, x=50, y=3, fps=fps)
            render_map_mouse_location(console=root_console, x=5, y=50, engine=engine)
            render_names_at_mouse_location(console=root_console, x=5, y=5, engine=engine)
            render_rooms_at_mouse_location(console=root_console, x=5, y=6, engine=engine)

            context.present(root_console)

            engine.event_handler.handle_events(context)

            engine.update()

            toc = time.perf_counter()

            cycle += 1

            time_sum += toc - tic
            if cycle % 30 is 0:
                fps = int(1 / (time_sum / 30))
                time_sum = 0

            tick_length = 0.1
            time.sleep(tick_length - (tic - toc))


if __name__ == "__main__":
    main()
