from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import colours
import random
import jobs
import entity_factories
import utility
from game_map import Neighbourhood
from entity import EntityID
from rooms import Rooms, RoomType
from jobs import Job

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from actions import MapMouseDesiredAction


class Action:
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            print(f"{self.entity.name} is trying to move out of bounds!")
            return  # Destination is out of bounds.
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            print(f"{self.entity.name}'s destination blocked by tile!")
            return  # Destination is blocked by a tile.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            print(f"{self.entity.name} destination blocked by an entity!")
            return  # Destination is blocked by an entity.

        self.entity.move(self.dx, self.dy)

        # Tile is worn down as an actor moves on to it
        if self.engine.game_map.tiles[dest_x, dest_y]["wearable"]:
            self.engine.game_map.tiles[dest_x, dest_y]["wear"] = max(0, self.engine.game_map.tiles[dest_x, dest_y]["wear"] - self.entity.weight * (random.random() * 0.001))
            self.engine.game_map.tiles[dest_x, dest_y]["graphic"]["bg"] = colours.colour_lerp(colours.DRY_MUD_BROWN, self.engine.game_map.tiles[dest_x, dest_y]["original_bg"], self.engine.game_map.tiles[dest_x, dest_y]["wear"])


class WaitAction(Action):
    def perform(self) -> None:
        pass


class CreateJobAction(Action):
    def __init__(self, entity: Entity, job: Job) -> None:
        super().__init__(entity)
        self.job = job

    def perform(self) -> None:
        self.engine.message_log.add_message("Created Job", colours.WHITE)
        self.engine.jobs.queue.put(self.job)


class CreatePropAction(Action):
    def __init__(self, entity: Entity, prop: Prop, location: Tuple[int, int]) -> None:
        super().__init__(entity)

        self.location = location
        self.prop = prop

    def perform(self):
        self.prop.spawn(self.engine.game_map, self.location[0], self.location[1])


class CreateWallAction(Action):
    def __init__(self, entity: Entity, location: Tuple[int, int]) -> None:
        super().__init__(entity)

        self.location = location

    def perform(self):
        surrounding_entities = self.engine.game_map.get_surrounding_entities(self.location, Neighbourhood.MOORE)
        """
        Surrounding Entities:
        0 1 2
        3   4
        5 6 7
        """

        # Pick a tile for this new wall
        surrounding_walls = [False] * len(surrounding_entities)
        index = 0
        for entity_list in surrounding_entities:
            for entity in entity_list:
                if entity.is_type(EntityID.WALL):
                    surrounding_walls[index] = True
                    break
            index += 1

        wall = entity_factories.wall.spawn(self.engine.game_map, self.location[0], self.location[1])
        if surrounding_walls[1] and surrounding_walls[3] and surrounding_walls[4] and surrounding_walls[6]:
            wall.char = "╬"
        elif surrounding_walls[3] and surrounding_walls[1] and surrounding_walls[4]:
            wall.char = "╩"
        elif surrounding_walls[3] and surrounding_walls[6] and surrounding_walls[4]:
            wall.char = "╦"
        elif surrounding_walls[3] and surrounding_walls[1] and surrounding_walls[6]:
            wall.char = "╣"
        elif surrounding_walls[1] and surrounding_walls[4] and surrounding_walls[6]:
            wall.char = "╠"
        elif surrounding_walls[3] and surrounding_walls[1]:
            wall.char = "╝"
        elif surrounding_walls[1] and surrounding_walls[4]:
            wall.char = "╚"
        elif surrounding_walls[4] and surrounding_walls[6]:
            wall.char = "╔"
        elif surrounding_walls[3] and surrounding_walls[6]:
            wall.char = "╗"
        elif surrounding_walls[3] or surrounding_walls[4]:
            wall.char = "═"
        else:
            wall.char = "║"

        self.engine.game_map.tiles[self.location[0], self.location[1]]["walkable"] = False

        # Update the surrounding wall tiles
        for entity_list in surrounding_entities:
            for entity in entity_list:
                if entity.is_type(EntityID.WALL):
                    second_order_surrounding_entities = self.engine.game_map.get_surrounding_entities([entity.x, entity.y], Neighbourhood.MOORE)
                    surrounding_walls = [False] * len(second_order_surrounding_entities)
                    index = 0
                    for n in second_order_surrounding_entities:
                        for i in n:
                            if i.is_type(EntityID.WALL):
                                surrounding_walls[index] = True
                                break
                        index += 1
                    if surrounding_walls[1] and surrounding_walls[3] and surrounding_walls[4] and surrounding_walls[6]:
                        entity.char = "╬"
                    elif surrounding_walls[3] and surrounding_walls[1] and surrounding_walls[4]:
                        entity.char = "╩"
                    elif surrounding_walls[3] and surrounding_walls[6] and surrounding_walls[4]:
                        entity.char = "╦"
                    elif surrounding_walls[3] and surrounding_walls[1] and surrounding_walls[6]:
                        entity.char = "╣"
                    elif surrounding_walls[1] and surrounding_walls[4] and surrounding_walls[6]:
                        entity.char = "╠"
                    elif surrounding_walls[3] and surrounding_walls[1]:
                        entity.char = "╝"
                    elif surrounding_walls[1] and surrounding_walls[4]:
                        entity.char = "╚"
                    elif surrounding_walls[4] and surrounding_walls[6]:
                        entity.char = "╔"
                    elif surrounding_walls[3] and surrounding_walls[6]:
                        entity.char = "╗"
                    elif surrounding_walls[3] or surrounding_walls[4]:
                        entity.char = "═"
                    elif surrounding_walls[1] or surrounding_walls[6]:
                        entity.char = "║"


class CreateFloorAction(Action):
    def __init__(self, entity: Entity, location: Tuple[int, int]) -> None:
        super().__init__(entity)

        self.location = location

    def perform(self):
        floor = entity_factories.stone_floor.spawn(self.engine.game_map, self.location[0], self.location[1])


class ChangeMouseDesiredAction(Action):
    def __init__(self, entity: Entity, desired_action: MapMouseDesiredAction) -> None:
        super().__init__(entity)

        self.desired_action = desired_action

    def perform(self):
        self.engine.event_handler.mouse_action = self.desired_action


class CreateRoomAction(Action):
    def __init__(self, entity: Entity, room_type: RoomType, tiles: list) -> None:
        super().__init__(entity)
        self.room_type = room_type
        self.tiles = tiles

    def perform(self):
        self.engine.game_map.room_holder.add_room(self.room_type, self.tiles)


class GoToServiceAction(Action):
    def __init__(self, entity: Entity) -> None:
        super().__init__(entity)

    def perform(self):
        quire = self.entity.gamemap.room_holder.get_room(RoomType.QUIRE)
        if quire is not None:
            self.entity.schedule.jobs.append(Job([quire.get_random_point_in_room()], 1, None, None, None, "Service"))

 # Not actually tested!


class RemovePropAction(Action):
    def __init__(self, entity: Entity, location: Tuple[int, int]) -> None:
        super().__init__(entity)

        self.location = location

    def perform(self):
        self.engine.event_handler.mouse_action = self.desired_action
