

from components.ai import MoveToPlayer
from components.ai import Brother
from components.animal import Animal

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
    animal=Animal(hp=30,),
    weight=80,
)

brother = Actor(
    char="o",
    fg_colour=(63, 127, 63),
    name="Brother",
    ai_cls=Brother,
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

pending_job = Prop(
    id=EntityID.PENDING_JOB,
    char=".",
    fg_colour=colours.WALL_FG,
    name="Pending Job",
    weight=0,
    blocks_movement=False
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

placeable_props = [door, stone_pillar]
