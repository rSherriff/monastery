from __future__ import annotations

from typing import TYPE_CHECKING

import colours
from tcod import Console, event
from actions import ChangeMouseDesiredAction
from input_handlers import MouseDesiredAction
from highlight import Highlight

if TYPE_CHECKING:
    from engine import Engine
    from game_map import GameMap
    from actions import Action


class UI:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.elements = list()
        self.highlight = Highlight()

        build_wall_button = Button(50, 80, 15, 5, "Build Wall", ChangeMouseDesiredAction(self.engine.player, MouseDesiredAction.BUILD_WALL))
        self.elements.append(build_wall_button)

        build_floor_button = Button(65, 80, 15, 5, "Build Floor", ChangeMouseDesiredAction(self.engine.player, MouseDesiredAction.BUILD_FLOOR))
        self.elements.append(build_floor_button)

        place_prop_button = Button(80, 80, 15, 5, "Place Prop", ChangeMouseDesiredAction(self.engine.player, MouseDesiredAction.PLACE_PROP))
        self.elements.append(place_prop_button)

        place_room_button = Button(95, 80, 15, 5, "Place Room", ChangeMouseDesiredAction(self.engine.player, MouseDesiredAction.PLACE_ROOM))
        self.elements.append(place_room_button)

    def render(self, console: Console):
        for element in self.elements:
            element.render(console)

        if self.highlight is not None:
            self.highlight.render(console)
            pass

    def mousedown(self, x: int, y: int):
        for element in self.elements:
            if element.is_mouseover(x, y):
                if isinstance(element, Button):
                    element.click_action.perform()

    def mousemove(self, x: int, y: int):
        for element in self.elements:
            if element.is_mouseover(x, y):
                element.mouseover = True
            else:
                element.mouseover = False


class UIElement:
    def __init__(self):
        self.mouseover = False
        pass

    def render():
        raise NotImplementedError()

    def is_mouseover(x: int, y: int) -> bool:
        raise NotImplementedError()


class Button(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, click_action: Action):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.click_action = click_action

        self.normal_bg = colours.BLACK
        self.highlight_bg = colours.WHITE

        self.normal_fg = colours.WHITE
        self.highlight_fg = colours.BLACK

    def render(self, console: Console):
        temp_console = Console(self.width, self.height)

        temp_console.draw_frame(0, 0, self.width, self.height)
        temp_console.print_box(0, 2, temp_console.width, 1, self.text, alignment=2, bg=self.highlight_bg if self.mouseover else self.normal_bg, fg=self.highlight_fg if self.mouseover else self.normal_fg)
        temp_console.blit(console, self.x, self.y)

    def is_mouseover(self, x: int, y: int):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
