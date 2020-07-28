

from components.ai import MoveToPlayer
from components.ai import Brother
from components.animal import Animal
from components.schedule import BrotherSchedule, BaseSchedule

from entity import Actor
from entity import Prop
from entity import EntityID

import colours
import random

player = Actor(
    char="@",
    fg_colour=(255, 255, 255),
    name="Player",
    ai_cls=MoveToPlayer,
    schedule_cls=BaseSchedule,
    animal=Animal(hp=30,),
    weight=80,
)

brother = Actor(
    char="o",
    fg_colour=(63, 127, 63),
    name="Brother",
    ai_cls=Brother,
    schedule_cls=BrotherSchedule,
    animal=Animal(hp=10),
    weight=90,
)

wall = Prop(
    id=EntityID.WALL,
    char="═",
    fg_colour=colours.WALL_FG,
    bg_colour=colours.GREY,
    name="Wall",
    weight=500,
    colours_bg=True
)

stone_floor = Prop(
    id=EntityID.FLOOR,
    char=" ",
    fg_colour=colours.WHITE,
    bg_colour=colours.GREY,
    name="Stone Floor",
    weight=200,
    blocks_movement=False,
    colours_bg=True
)

cloister_grass = Prop(
    id=EntityID.FLOOR,
    char=" ",
    fg_colour=colours.DARK_GREEN,
    bg_colour=colours.GRASS_GREEN,
    name="Cloister Grass",
    weight=0,
    blocks_movement=True,
    colours_bg=False
)

pending_job = Prop(
    id=EntityID.PENDING_JOB,
    char=".",
    fg_colour=colours.WHITE,
    name="Pending Job",
    weight=0,
    blocks_movement=False,
)

door = Prop(
    id=EntityID.DOOR,
    char="∩",
    fg_colour=colours.WALL_FG,
    name="Door",
    weight=80,
    blocks_movement=False
)

stone_pillar = Prop(
    id=EntityID.DOOR,
    char="o",
    fg_colour=colours.WALL_FG,
    bg_colour=colours.GREY,
    name="Stone Pillar",
    weight=80,
    blocks_movement=False,
    colours_bg=True
)

field = Prop(
    id=EntityID.FIELD,
    char="~",
    fg_colour=colours.DRY_MUD_BROWN,
    bg_colour=colours.WET_MUD_BROWN,
    name="Farm Field",
    weight=0,
    blocks_movement=False,
    colours_bg=True
)

placeable_props = [door, stone_pillar]
