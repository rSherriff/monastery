from __future__ import annotations

import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING

from render_order import RenderOrder
from enum import auto, Enum

import colours
import random

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.animal import Animal
    from components.schedule import BaseSchedule
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class EntityID(Enum):
    NONE = -1
    WALL = auto()
    FLOOR = auto()
    PENDING_JOB = auto()
    DOOR = auto()
    FIELD = auto()


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    # TODO: Change blocks movemnt to a cost, things that totally block change the tile beneath them
    gamemap: GameMap

    def __init__(
        self,
        id: int = -1,
        gamemap: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        name: str = "<unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
        weight: int = 0
    ):
        self.id = id
        self.x = x
        self.y = y
        self.char = char
        self.bg_colour = bg_colour
        self.fg_colour = fg_colour
        self.colours_bg = colours_bg
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self.weight = weight
        if gamemap:
            # If gamemap isn't provided now then it will be set later.
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone)

        return clone

    def spawn_in_room(self: T, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y

        return clone

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entitiy at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "gamemap"):  # Possibly uninitialized.
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def update(self):
        pass

    def is_type(self, id: entity_factories.EntityID):
        return self.id is id


class Actor(Entity):
    def __init__(
        self,
        *,
        id: int = -1,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        name: str = "<unnamed>",
        ai_cls: Type[BaseAI],
        schedule_cls: Type[BaseSchedule],
        animal: Animal,
        weight: int = 0,
    ):
        super().__init__(
            id=id,
            x=x,
            y=y,
            char=char,
            name=name,
            bg_colour=bg_colour,
            fg_colour=fg_colour,
            colours_bg=colours_bg,
            blocks_movement=False,
            render_order=RenderOrder.ACTOR,
            weight=weight
        )

        self.ai: Optional[BaseAI] = ai_cls(self)
        self.schedule: Optional[BaseSchedule] = schedule_cls(self)

        self.animal = animal
        self.animal.entity = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    def update(self):
        if self.schedule:
            self.schedule.update()

        if self.ai:
            self.ai.perform()

    def get_effort(self):
        # TODO: Return effort based on the job and the actors abilities
        return 1


class Prop(Entity):
    def __init__(
        self,
        id: int = -1,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        bg_colour: Tuple[int, int, int] = (255, 255, 255),
        fg_colour: Tuple[int, int, int] = (255, 255, 255),
        colours_bg: bool = False,
        weight: int = 0,
        name: str = "<unnamed>",
        blocks_movement: bool = False,
    ):
        super().__init__(
            id=id,
            x=x,
            y=y,
            char=char,
            bg_colour=bg_colour,
            fg_colour=fg_colour,
            colours_bg=colours_bg,
            name=name,
            blocks_movement=blocks_movement,
            render_order=RenderOrder.PROP,
            weight=weight
        )

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        clone = super().spawn(gamemap, x, y)

        if self.colours_bg:
            clone.bg_colour = colours.colour_lerp(clone.bg_colour, (max(0, clone.bg_colour[0] - 30), max(0, clone.bg_colour[1] - 30), max(0, clone.bg_colour[2] - 30)), max(0.4, random.random()))

        return clone

    def spawn_in_room(self: T, x: int, y: int) -> T:
        clone = super().spawn_in_room(x, y)

        if self.colours_bg:
            clone.bg_colour = colours.colour_lerp(clone.bg_colour, (max(0, clone.bg_colour[0] - 30), max(0, clone.bg_colour[1] - 30), max(0, clone.bg_colour[2] - 30)), max(0.4, random.random()))

        return clone
