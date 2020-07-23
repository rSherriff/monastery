from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Tuple
from actions import Action, EscapeAction, MovementAction, CreateJobAction, CreatePropAction, CreateWallAction, CreateFloorAction, CreateRoomAction
from enum import auto, Enum
from jobs import Job
from highlight import Highlight
from rooms import get_room_types, get_room_name

import tcod.event
import colours
import utility
import entity_factories

if TYPE_CHECKING:
    from engine import Engine


class DragMode(Enum):
    NONE = auto(),
    STRAIGHT = auto(),
    HORIZONTAL = auto(),
    VERTICAL = auto(),
    BOX = auto(),


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.mouse_action = None
        self.is_mouse_down = False

        self.mouse_down_location = Tuple[int, int]
        self.mouse_up_location = Tuple[int, int]

        self.map_mouse_down_location = Tuple[int, int]
        self.map_mouse_up_location = Tuple[int, int]

        self.engine = engine

        self.mouse_action = MouseDesiredAction.NONE
        self.drag_mode = DragMode.NONE

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.get():
            context.convert_event(event)
            self.dispatch(event)
            pass

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        self.engine.mouse_location = event.tile.x, event.tile.y
        self.engine.ui.mousemove(self.engine.mouse_location[0], self.engine.mouse_location[1])
        if self.engine.is_mouse_in_map():
            self.engine.map_mouse_location = event.tile.x - self.engine.map_x_offset, event.tile.y - self.engine.map_y_offset

    def ev_quit(self, event: tcod.event.Quit) -> None:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class MouseDesiredAction(Enum):
    NONE = auto()
    BUILD_WALL = auto()
    BUILD_FLOOR = auto()
    PLACE_PROP = auto()
    PLACE_ROOM = auto()


class MainGameEventHandler(EventHandler):
    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.get():
            context.convert_event(event)
            actions = self.dispatch(event)

            if actions is None:
                continue

            for action in actions:
                action.perform()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[list(Action)]:
        actions = []

        key = event.sym

        player = self.engine.player

        if key == tcod.event.K_UP:
            actions.append(MovementAction(player, dx=0, dy=-1))
        elif key == tcod.event.K_DOWN:
            actions.append(MovementAction(player, dx=0, dy=1))
        elif key == tcod.event.K_LEFT:
            actions.append(MovementAction(player, dx=-1, dy=0))
        elif key == tcod.event.K_RIGHT:
            actions.append(MovementAction(player, dx=1, dy=0))
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)

        elif key == tcod.event.K_ESCAPE:
            actions.append(EscapeAction(player))

        # No valid key was pressed
        return actions

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[list(Action)]:
        actions = []

        player = self.engine.player

        self.is_mouse_down = True
        self.mouse_down_location = self.engine.mouse_location
        self.map_mouse_down_location = self.engine.map_mouse_location
        self.drag_mode = DragMode.NONE
        self.set_highlight_squares()

        if self.mouse_action is MouseDesiredAction.PLACE_PROP:
            self.engine.event_handler = PropPlacer(self.engine, self.map_mouse_down_location)

        self.engine.ui.mousedown(self.engine.mouse_location[0], self.engine.mouse_location[1])

    def ev_mousebuttonup(self, event: tcod.event.MouseButtonDown) -> Optional[list(Action)]:
        actions = []

        player = self.engine.player

        self.is_mouse_down = False
        self.mouse_up_location = self.engine.mouse_location
        self.map_mouse_up_location = self.engine.map_mouse_location

        self.engine.ui.highlight.clear()

        # Map Actions
        if self.engine.is_mouse_in_map():

            for x, y in self.highlight_tiles:
                x, y = self.screen_space_to_map_space(x, y)

                if self.engine.game_map.can_place_prop_in_tile(x, y):

                    if self.mouse_action is MouseDesiredAction.BUILD_WALL:
                        locations = utility.get_vonneumann_tiles([x, y])
                        completion_action = CreateWallAction(self.engine.player, [x, y])
                        job = Job(locations, 1, completion_action, None, None, "Build Wall")

                        actions.append(CreateJobAction(player, job))

                    if self.mouse_action is MouseDesiredAction.BUILD_FLOOR:
                        completion_action = CreateFloorAction(self.engine.player, [x, y])
                        job = Job([[x, y]], 1, completion_action, None, None, "Build Floor")

                        actions.append(CreateJobAction(player, job))

                if self.mouse_action is MouseDesiredAction.PLACE_ROOM:
                    map_highlight_tiles = list(map(lambda x: self.screen_space_to_map_space(x[0], x[1]), self.highlight_tiles))
                    self.engine.event_handler = RoomPlacer(self.engine, map_highlight_tiles)

            self.mouse_action = MouseDesiredAction.NONE

        return actions

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        self.engine.mouse_location = event.tile.x, event.tile.y
        self.engine.ui.mousemove(self.engine.mouse_location[0], self.engine.mouse_location[1])

        if self.engine.is_mouse_in_map():
            self.engine.map_mouse_location = event.tile.x - self.engine.map_x_offset, event.tile.y - self.engine.map_y_offset

            if self.is_mouse_down:

                if self.is_drag_action:
                    self.set_highlight_squares()

            if not self.is_mouse_down and self.mouse_action is not MouseDesiredAction.NONE:
                self.engine.ui.highlight.clear()
                self.highlight_tiles = list()
                self.highlight_tiles.append(self.engine.mouse_location)

            if self.mouse_action is not MouseDesiredAction.NONE:
                for tile in self.highlight_tiles:
                    map_location = self.screen_space_to_map_space(tile[0], tile[1])

                    if self.engine.game_map.can_place_prop_in_tile(map_location[0], map_location[1]):
                        self.engine.ui.highlight.add_tile(tile, colours.GREEN)
                    else:
                        self.engine.ui.highlight.add_tile(tile, colours.RED)

    def screen_space_to_map_space(self, x: int, y: int):
        return (x - self.engine.map_x_offset, y - self.engine.map_y_offset)

    def set_highlight_squares(self):
        self.engine.ui.highlight.clear()
        self.highlight_tiles = list()

        if self.engine.mouse_location[0] is self.mouse_down_location[0] and self.engine.mouse_location[1] is self.mouse_down_location[1]:
            self.drag_mode = DragMode.NONE
            self.highlight_tiles.append(self.mouse_down_location)

        elif self.is_horizontal_or_vertical_drag():

            dx = abs(self.engine.mouse_location[0] - self.mouse_down_location[0])
            dy = abs(self.engine.mouse_location[1] - self.mouse_down_location[1])

            if dy and dx < 5:
                if dy < dx:
                    self.drag_mode = DragMode.HORIZONTAL
                else:
                    self.drag_mode = DragMode.VERTICAL
            elif dy < 5:
                self.drag_mode = DragMode.HORIZONTAL
            elif dx < 5:
                self.drag_mode = DragMode.VERTICAL

            if self.drag_mode is DragMode.VERTICAL:
                for x, y in utility.vertical_line_between(self.mouse_down_location[1], self.engine.mouse_location[1], self.mouse_down_location[0]):
                    self.highlight_tiles.append((x, y))
            elif self.drag_mode is DragMode.HORIZONTAL:
                for x, y in utility.horizontal_line_between(self.mouse_down_location[0], self.engine.mouse_location[0], self.mouse_down_location[1]):
                    self.highlight_tiles.append((x, y))

        elif self.is_straight_drag():
            self.drag_mode = DragMode.STRAIGHT
            for x, y in utility.line_between(self.mouse_down_location, self.engine.mouse_location):
                self.highlight_tiles.append((x, y))

        elif self.is_box_drag():
            self.drag_mode = DragMode.BOX
            for x, y in utility.box_between(self.mouse_down_location, self.engine.mouse_location):
                self.highlight_tiles.append((x, y))

    def is_drag_action(self):
        return self.mouse_action is MouseDesiredAction.BUILD_WALL

    def is_horizontal_or_vertical_drag(self):
        return self.mouse_action is MouseDesiredAction.BUILD_WALL

    def is_straight_drag(self):
        return False

    def is_box_drag(self):
        return self.mouse_action is MouseDesiredAction.BUILD_FLOOR or self.mouse_action is MouseDesiredAction.PLACE_ROOM


class GameOverEventHandler(EventHandler):
    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.get():
            actions = self.dispatch(event)

            if actions is None:
                continue

            for action in actions:
                action.perform()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        actions = []

        key = event.sym

        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)

        # No valid key was pressed
        return actions


CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,


}


class PropPlacer(EventHandler):
    def __init__(self, engine: Engine, position: Tuple[int, int]):
        super().__init__(engine)
        self.selection = 0
        self.position = position
        self.shutting_down = False

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.get():
            context.convert_event(event)
            actions = self.dispatch(event)

            if actions is None:
                continue

            for action in actions:
                action.perform()

            if self.shutting_down:
                self.engine.event_handler = MainGameEventHandler(self.engine)

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        temp_console = tcod.Console(16, 15)

        # Draw a frame with a custom banner title.
        temp_console.draw_frame(0, 0, temp_console.width, temp_console.height)
        temp_console.print_box(
            0, 0, temp_console.width, 1, "┤Place Prop├", alignment=tcod.CENTER
        )
        y = 2
        count = 0
        for prop in entity_factories.placeable_props:
            temp_console.print(x=2, y=y, string=prop.name, fg=colours.RED if count is self.selection else colours.WHITE)
            y += 1
            count += 1

        temp_console.blit(console, console.width // 2 - temp_console.width // 2, console.height // 2 - temp_console.height // 2)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        actions = []
        player = self.engine.player

        if event.sym in CURSOR_Y_KEYS:
            self.selection = max(0, min(self.selection + CURSOR_Y_KEYS[event.sym], len(entity_factories.placeable_props) - 1))
        elif event.sym == tcod.event.K_RETURN:
            completion_action = CreatePropAction(self.engine.player, entity_factories.placeable_props[self.selection], self.position)
            job = Job([self.position], 1, completion_action, None, None, "Create Prop")
            actions.append(CreateJobAction(player, job))
            self.shutting_down = True
        else:
            self.shutting_down = True

        return actions


class RoomPlacer(EventHandler):
    def __init__(self, engine: Engine, room_tiles):
        super().__init__(engine)
        self.selection = 0
        self.room_tiles = room_tiles
        self.shutting_down = False

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.get():
            context.convert_event(event)
            actions = self.dispatch(event)

            if actions is None:
                continue

            for action in actions:
                action.perform()

            if self.shutting_down:
                self.engine.event_handler = MainGameEventHandler(self.engine)

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        temp_console = tcod.Console(16, 15)

        # Draw a frame with a custom banner title.
        temp_console.draw_frame(0, 0, temp_console.width, temp_console.height)
        temp_console.print_box(
            0, 0, temp_console.width, 1, "┤Place Room├", alignment=tcod.CENTER
        )
        y = 2
        count = 0
        for room in get_room_types():
            temp_console.print(x=2, y=y, string=get_room_name(room), fg=colours.RED if count is self.selection else colours.WHITE)
            y += 1
            count += 1

        temp_console.blit(console, int(console.width / 2) - int(temp_console.width / 2), int(console.height / 2) - int(temp_console.height / 2))

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        actions = []
        player = self.engine.player

        if event.sym in CURSOR_Y_KEYS:
            self.selection = max(0, min(self.selection + CURSOR_Y_KEYS[event.sym], len(get_room_types()) - 1))
        elif event.sym == tcod.event.K_RETURN:
            action = CreateRoomAction(self.engine.player, get_room_types()[self.selection], self.room_tiles)
            actions.append(action)
            self.shutting_down = True
        else:
            self.shutting_down = True

        return actions


class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            self.engine.event_handler = MainGameEventHandler(self.engine)
