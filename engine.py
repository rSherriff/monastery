from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.console import Console

from actions import EscapeAction, MovementAction
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_bar, render_names_at_mouse_location, render_map_mouse_location, render_rooms_at_mouse_location
from jobs import Jobs
from calendar import Calendar
from monastery import Monastery
from ui import UI

from mapgen import generate_landscape

from entity import Actor
import time

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor, map_width, map_height):
        # Setting up all the systems that will run during the game. These systems depend on each other so order is very important!
        self.player = player
        self.map_height = map_height
        self.map_width = map_width
        self.jobs = Jobs(self)
        self.game_map = generate_landscape(self, map_width, map_height)
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.map_x_offset = 5
        self.map_y_offset = 3
        self.map_mouse_location = (0, 0)
        self.mouse_location = (0, 0)
        self.calendar = Calendar(self)
        self.monastery = Monastery(self)
        self.ui = UI(self)

    def render(self, console: Console) -> None:
        console.tiles_rgb[self.map_x_offset: self.map_width + self.map_x_offset, self.map_y_offset: self.map_height + self.map_y_offset] = self.game_map.tiles["graphic"]

        entity_console = Console(console.width, console.height)
        for entity in self.game_map.entities_sorted_for_rendering:
            x = entity.x + self.map_x_offset
            y = entity.y + self.map_y_offset

            entity_console.print(x=x, y=y, string=entity.char, fg=entity.fg_colour, bg=self.game_map.get_tile_bg_colour(entity.x, entity.y))
            entity_console.blit(console, src_x=x, dest_x=x, src_y=y, dest_y=y, width=1, height=1)

        self.message_log.render(console=console, x=0, y=self.map_height + self.map_y_offset + 2, width=40, height=10)
        self.calendar.render(console)
        self.ui.render(console)

        render_map_mouse_location(console=console, x=20, y=self.map_height + self.map_y_offset + 1, engine=self)
        render_names_at_mouse_location(console=console, x=20, y=self.map_height + self.map_y_offset, engine=self)
        render_rooms_at_mouse_location(console=console, x=30, y=self.map_height + self.map_y_offset, engine=self)

    def update(self):
        # self.calendar.update()
        self.game_map.update()
        for entity in self.game_map.entities - {self.player}:
            if isinstance(entity, Actor) and entity.ai:
                entity.ai.perform()

            entity.update()

    def is_mouse_in_map(self) -> bool:
        return self.map_x_offset <= self.mouse_location[0] < self.map_x_offset + self.game_map.width and self.map_y_offset <= self.mouse_location[1] < self.map_y_offset + self.game_map.height
