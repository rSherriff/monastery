from typing import Iterator, Tuple, TYPE_CHECKING

import colours
import numpy as np  # type: ignore
from game_map import GameMap
from voronoi import Voronoi
import tcod.noise
import random
import tile_types
import utility
from entity import Actor
from actions import CreateWallAction, CreateFloorAction, CreatePropAction, CreateJobAction
from jobs import JobEffort
from rooms import RoomType

if TYPE_CHECKING:
    from engine import Engine

# TEMP
import entity_factories


def generate_landscape(engine, map_width, map_height) -> GameMap:
    landscape = GameMap(engine, map_width, map_height)
    map_center = (int(map_width / 2), int(map_height / 2))

    # Generate and draw a voronoi diagram, then grab the points from a few of its sections to fill later
    vorgen = Voronoi(40, np.array([-1, map_width + 1, -1, map_height + 1]))
    draw_voronoi(vorgen, landscape, colours.WHITE)
    voronoi_fill_points = get_voronoi_fill_points(random.randrange(3, 6), vorgen, landscape)

    clear_landscape(landscape, colours.GRASS_GREEN, colours.DARK_GREEN)

    noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.NOISE_PERLIN,
        implementation=tcod.noise.TURBULENCE,
        hurst=0.5,
        lacunarity=5.0,
        octaves=2,
        seed=None,
    )

    # Add a base layer of smooth, gradually changing noise to form base layer
    add_smooth_noise_to_landscape(landscape, noise, 0.05, colours.GRASS_GREEN, colours.DARK_GREEN)

    # Shade the voronoi sections we grabbed before now we have our base layer down
    fill_regions(landscape, voronoi_fill_points, colours.DRY_MUD_BROWN, colours.WET_MUD_BROWN, colours.DARK_GREEN, colours.DRY_MUD_BROWN_B)

    # Add more granular noise on top to break things up
    add_noise_to_landscape(landscape, noise, 0.9, colours.GRASS_GREEN, colours.DARK_GREEN)

    # Temp building placement
    """
    place_rectangle_building(landscape, (20, 20), 5, 5)
    place_rectangle_building(landscape, (40, 40), 8, 8)
    place_rectangle_building(landscape, (40, 20), 5, 5)
    """
    place_church(landscape, engine, (40, 35))

    refectory = ('''\
        quuuuuw
        x.....x
        x.....x
        x.....x
        euu.uur
        ''')
    place_building(landscape, refectory, engine, (50, 25))

    dormitory = ('''\
        quu.uuw
        x.....xx
        x......x
        x......x
        x.....xx
        euuuuur
        ''')
    place_building(landscape, dormitory, engine, (47, 44))

    # Save this version of the map so effects can happen to it over the course of the game
    save_original_colours(landscape)

    cloister_size = 14
    place_cloister(landscape, (map_center[0] - (cloister_size // 2), map_center[1] - (cloister_size // 2)), cloister_size)

    # Temp to test entity factories
    engine.player.place(map_center[0], map_center[1], landscape)

    return landscape


def clear_landscape(landscape, bg_colour, fg_colour):
    for x in range(0, landscape.width):
        for y in range(0, landscape.height):
            landscape.tiles[x, y]["graphic"]["bg"] = bg_colour
            landscape.tiles[x, y]["graphic"]["ch"] = 9617
            landscape.tiles[x, y]["graphic"]["fg"] = colours.colour_lerp(bg_colour, fg_colour, random.random())


def draw_voronoi(vorgen, landscape, colour):
    for region in vorgen.vor.filtered_regions:
        vertices = vorgen.vor.vertices[region, :]
        for i in range(0, len(vertices)):
            nextVertex = i + 1
            if(i == len(vertices) - 1):
                nextVertex = 0
            for x, y in line_between((int(vertices[i][0]), int(vertices[i][1])), (int(vertices[nextVertex][0]), int(vertices[nextVertex][1]))):
                if x >= 0 and y >= 0 and x < landscape.width and y < landscape.height:
                    landscape.tiles[x, y]["graphic"]["bg"] = colour


def get_voronoi_fill_points(num_regions, vorgen, landscape):
    dirt_patch_points = list()
    for i in range(0, num_regions):
        point = vorgen.vor.filtered_points[i]
        dirt_patch_points += [get_fill_points(landscape, point)]

    return dirt_patch_points


def fill_regions(landscape, region_points, start_colour, end_colour, blend_colour, accent_colour):
    # Start colour, end colour - The range of colours you want this tile to become
    # Blend colour - the colour this section blends into, tiles on the edge of the section will completely fade into it
    # accent colour - an extra dash for tiles that are completly surrounded by similar coloured tiles
    for i in region_points:
        for point in i:
            landscape.tiles[point[0], point[1]]["graphic"]["bg"] = start_colour

    for i in region_points:
        for point in i:
            x, y = point[0], point[1]
            score = 0
            if (x - 1, y) in i:
                score += 1
            if (x + 1, y) in i:
                score += 1
            if (x, y - 1) in i:
                score += 1
            if (x, y + 1) in i:
                score += 1
            if (x - 1, y + 1) in i:
                score += 1
            if (x + 1, y + 1) in i:
                score += 1
            if (x + 1, y - 1) in i:
                score += 1
            if (x + 1, y + 1) in i:
                score += 1

            if random.random() < 0.5:
                landscape.tiles[x, y]["graphic"]["ch"] = 9617
                landscape.tiles[x, y]["graphic"]["fg"] = colours.colour_lerp(start_colour, end_colour, min(0.4, random.random()))

            landscape.tiles[x, y]["graphic"]["bg"] = colours.colour_lerp(blend_colour, start_colour, score / 8)

            if score is 8:
                landscape.tiles[x, y]["graphic"]["bg"] = colours.colour_lerp(landscape.tiles[x, y]["graphic"]["bg"], accent_colour, random.random())


def add_smooth_noise_to_landscape(landscape, noise, scale, start_colour, end_colour):
    # Create an open multi-dimensional mesh-grid.
    ogrid = [np.arange(landscape.width, dtype=np.float32),
             np.arange(landscape.height, dtype=np.float32)]

    ogrid[0] *= scale
    ogrid[1] *= scale

    # Return the sampled noise from this grid of points.
    samples = noise.sample_ogrid(ogrid)

    for x in range(0, landscape.width):
        for y in range(0, landscape.height):
            landscape.tiles[x, y]["graphic"]["bg"] = colours.colour_lerp(landscape.tiles[x, y]["graphic"]["bg"], end_colour, samples[x, y] / 1.2)


def add_noise_to_landscape(landscape, noise, threshold, start_colour, end_colour):
    # Create an open multi-dimensional mesh-grid.
    ogrid = [np.arange(landscape.width, dtype=np.float32),
             np.arange(landscape.height, dtype=np.float32)]

    # Return the sampled noise from this grid of points.
    samples = noise.sample_ogrid(ogrid)

    for x in range(0, landscape.width):
        for y in range(0, landscape.height):
            if samples[x, y] > threshold:
                old_range = (1 - threshold)
                new_value = ((samples[x, y] - threshold) / old_range)
                colour = colours.colour_lerp(start_colour, end_colour, max(0.5, random.random()))
                landscape.tiles[x, y]["graphic"]["ch"] = 9617
                landscape.tiles[x, y]["graphic"]["bg"] = colour
                landscape.tiles[x, y]["graphic"]["fg"] = colours.colour_lerp(colour, colours.DARK_GREEN, max(0.8, random.random()))


def line_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (x2, y2)).tolist():
        yield x, y


def get_fill_points(landscape, start_coords: Tuple[int, int]):
    orig_value = (landscape.tiles[start_coords[0], start_coords[1]]["graphic"]["bg"]).copy()

    stack = set(((start_coords[0], start_coords[1]),))
    points = list()
    while stack:
        x, y = stack.pop()
        res = all(i == j for i, j in zip(landscape.tiles[x, y]["graphic"]["bg"], orig_value))
        if res:
            landscape.tiles[x, y]["graphic"]["bg"] = (255 - orig_value[0], 255 - orig_value[1], 255 - orig_value[2])
            points.append((x, y))
            if x > 0:
                stack.add((x - 1, y))
            if x < (landscape.width - 1):
                stack.add((x + 1, y))
            if y > 0:
                stack.add((x, y - 1))
            if y < (landscape.height - 1):
                stack.add((x, y + 1))

    return points


def save_original_colours(landscape):
    for x in range(0, landscape.width):
        for y in range(0, landscape.height):
            landscape.tiles[x, y]["original_bg"] = landscape.tiles[x, y]["graphic"]["bg"]


""" Temp building generators """


def place_rectangle_building(landscape, center: Tuple[int, int], width: int, height: int, place_door: bool, wear_surrounds: bool) -> None:
    # Place floor
    for x in range(center[0] - int(width / 2), center[0] + int(width / 2) + 1):
        for y in range(center[1] - int(height / 2), center[1] + int(height / 2) + 1):
            landscape.tiles[x, y]["graphic"]["bg"] = colours.GREY
            landscape.tiles[x, y]["graphic"]["ch"] = ord(' ')
            landscape.tiles[x, y]["wearable"] = False

    for x in range(center[0] - int(width / 2), center[0] + int(width / 2) + 1):
        point = (x, center[1] - int(height / 2))
        if wear_surrounds:
            landscape.tiles[point[0], point[1] - 1]["graphic"]["bg"] = colours.colour_lerp(colours.GRASS_GREEN, colours.DRY_MUD_BROWN, max(random.random(), 0.4))
            landscape.tiles[point[0], point[1] - 1]["cost"] = 10
        landscape.tiles[point[0], point[1]]["graphic"]["fg"] = colours.DARK_GREY
        landscape.tiles[point[0], point[1]]["graphic"]["ch"] = 9552
        landscape.tiles[point[0], point[1]]["walkable"] = False

        point = (x, center[1] + int(height / 2))
        if wear_surrounds:
            landscape.tiles[point[0], point[1] + 1]["graphic"]["bg"] = colours.colour_lerp(colours.GRASS_GREEN, colours.DRY_MUD_BROWN, max(random.random(), 0.4))
            landscape.tiles[point[0], point[1] + 1]["cost"] = 10
        landscape.tiles[point[0], point[1]]["graphic"]["fg"] = colours.DARK_GREY
        landscape.tiles[point[0], point[1]]["graphic"]["ch"] = 9552
        landscape.tiles[point[0], point[1]]["walkable"] = False

    for y in range(center[1] - int(height / 2), center[1] + int(height / 2) + 1):
        if wear_surrounds:
            landscape.tiles[center[0] - int(width / 2) - 1, y]["graphic"]["bg"] = colours.colour_lerp(colours.GRASS_GREEN, colours.DRY_MUD_BROWN, max(random.random(), 0.4))
            landscape.tiles[center[0] - int(width / 2) - 1, y]["cost"] = 10
        landscape.tiles[center[0] - int(width / 2), y]["graphic"]["fg"] = colours.DARK_GREY
        landscape.tiles[center[0] - int(width / 2), y]["graphic"]["ch"] = 9553
        landscape.tiles[center[0] - int(width / 2), y]["walkable"] = False

        if wear_surrounds:
            landscape.tiles[center[0] + int(width / 2) + 1, y]["graphic"]["bg"] = colours.colour_lerp(colours.GRASS_GREEN, colours.DRY_MUD_BROWN, max(random.random(), 0.4))
            landscape.tiles[center[0] + int(width / 2) + 1, y]["cost"] = 10
        landscape.tiles[center[0] + int(width / 2), y]["graphic"]["fg"] = colours.DARK_GREY
        landscape.tiles[center[0] + int(width / 2), y]["graphic"]["ch"] = 9553
        landscape.tiles[center[0] + int(width / 2), y]["walkable"] = False

    # Place corners

    landscape.tiles[center[0] - int(width / 2), center[1] - int(height / 2)]["graphic"]["ch"] = 9556
    landscape.tiles[center[0] - int(width / 2), center[1] + int(height / 2)]["graphic"]["ch"] = 9562
    landscape.tiles[center[0] + int(width / 2), center[1] - int(height / 2)]["graphic"]["ch"] = 9559
    landscape.tiles[center[0] + int(width / 2), center[1] + int(height / 2)]["graphic"]["ch"] = 9565

    # Place Door
    if place_door:
        if random.random() < 0.5:
            if random.random() < 0.5:
                door_position = (random.randint(center[0] - int(width / 2) + 1, center[0] + int(width / 2) - 1), center[1] + int(height / 2))
            else:
                door_position = (random.randint(center[0] - int(width / 2) + 1, center[0] + int(width / 2) - 1), center[1] - int(height / 2))
        else:
            if random.random() < 0.5:
                door_position = (center[0] - int(width / 2), random.randint(center[1] - int(height / 2) + 1, center[1] + int(height / 2) - 1))
            else:
                door_position = (center[0] + int(width / 2), random.randint(center[1] - int(height / 2) + 1, center[1] + int(height / 2) - 1))

        landscape.tiles[door_position]["graphic"]["fg"] = colours.DARK_GREY
        landscape.tiles[door_position]["graphic"]["ch"] = ord(' ')
        landscape.tiles[door_position]["walkable"] = True


def place_church(landscape, engine, position: Tuple[int, int]):
    # Place floor
    width = 13
    height = 5
    # place_rectangle_building(landscape, position, width, height, place_door=False, wear_surrounds=False)

    width = 7
    height = 18
    # place_rectangle_building(landscape, (position[0], position[1] + int(height / 5)), width, height, place_door=False, wear_surrounds=False)

    width = 11
    height = 3
    # draw_rectangle(landscape, position, width, height, colour=colours.GREY, character=ord(' '))

    """
    church = ('''\
        quuuuuw
        x.....x
        x.o.o.x
        x.....x
     quur.....euuw
     x...........x
     x...........x  xuux
     x...........x  x..x
     euuw.....qu.r  x..x
        x.o.o.x..uuuu.uuw
        x.....x.........x
        x.o.o.x.o o o o.x
        x.......       .x
        x.o.o.x.o     o.x
        x.....x.       .x
        x.o.o.x.o     o.x
        x.....x.       .x
        x.o.o.x.o o o o.x
        x.....x.........x
        eu.u.uruuuuuuuuur
        ''')
    """
    tiny_church = ('''\
         quw
        qroew
        xh.hx
        xh...
        xhhhx
        euuur
        ''')

    smaller_church = ('''\
         quuuw
        qr...ew
        x.....x
        xh...hx
        xh...hx
      qur.....euw
      x.........x
      x.........x
      x.........x
      euw.o.o.qur
        xhh.hhx
        xho.ohx
        xhh.hhx
        xho.ohx
        xhh.hhx
        x.o.o.x
        x.....x
        euu.uur
        ''')

    small_church = ('''\
         quuuuw
        qr....ew
        x......x
        x.o..o.x
        x......x
     quur.o..o.euuw
     x............x
     x............x
     x............x
     x............x
     euuw.o..o.quur
        x......x
        x.o..o.x
        x......x
        x.o..o.x
        x......x
        x.o..o.x
        x......x
        x.o..o.x
        x......x
        eu.uu.ur
        ''')

    big_church = ('''\
         quuuuuuuw
        qr.......ew
        x.........x
        x.........x
        x..o...o..x
        x..|...|..x
        x..|...|..x
        x..|...|..x
        x..|...|..x
        x..o...o..x
  quuuuur.........euuuuuw
  x.....................x
  x.o.o.o..o...o..o.o.o.x
  x.....................x
  x.....................x
  x.....................x
  x.o.o.o..o...o..o.o.o.x
  x.....................x
  euuuuuw..o...o..quuuuuruuuuuuuw
        x.........x.............x
        x..o...o..x.............x
        x.........x..         ..xuuuuuuuuuw
        x..o...o..x..         ..x.........x
        x.........x..         ..x.o.o.o.o.x
        x..o...o..x..         ..x.........x
        x.........x..         ..x.........x
        x..o...o..x..         ..x.o.o.o.o.x
        x.........x..         ..x.........x
        x..o...o..x..         ..xuuuuuuuuur
        x.........x..         ..x
        x..o...o..x.............x
        x.........x.............x
        x..o...o..xuuuuuuuuuuuuur
        x.........x
        x..o...o..x
        x.........x
        eu..uuu..ur
        ''')

    x, y = position[0], position[1]
    wall_jobs = list()
    floor_jobs = list()
    prop_jobs = list()
    for character in tiny_church:
        if character is not ' ' and character is not "\n" and character is not "\r":

            job = None
            if character is 'x' or character is 'u' or character is 'e' or character is 'r' or character is 'q' or character is 'w':
                locations = utility.get_vonneumann_tiles([x, y])
                completion_action = CreateWallAction(landscape.engine.player, [x, y])
                job = JobEffort(locations, 1, completion_action, None, None, "Build Wall")
                wall_jobs.append(job)
            elif character is 'o':
                completion_action = CreatePropAction(landscape.engine.player, entity_factories.stone_pillar, [x, y])
                job = JobEffort([[x, y]], 1, completion_action, None, None, "Create Prop")
                prop_jobs.append(job)
            else:
                completion_action = CreateFloorAction(landscape.engine.player, [x, y])
                job = JobEffort([[x, y]], 1, completion_action, None, None, "Build Floor")
                floor_jobs.append(job)

            # landscape.tiles[x, y]["graphic"]["ch"] = ord(' ')

        if character is "\n" or character is "\r":
            x = position[0]
            y += 1
        else:
            x += 1

    for j in wall_jobs:
        if j is not None:
            engine.jobs.queue.put(j)

    for j in prop_jobs:
        if j is not None:
            engine.jobs.queue.put(j)

    for j in floor_jobs:
        if j is not None:
            engine.jobs.queue.put(j)


def place_building(landscape, building, engine, position: Tuple[int, int]):
    x, y = position[0], position[1]
    wall_jobs = list()
    floor_jobs = list()
    prop_jobs = list()
    for character in building:
        if character is not ' ' and character is not "\n" and character is not "\r":

            job = None
            if character is 'x' or character is 'u' or character is 'e' or character is 'r' or character is 'q' or character is 'w':
                locations = utility.get_vonneumann_tiles([x, y])
                completion_action = CreateWallAction(landscape.engine.player, [x, y])
                job = JobEffort(locations, 1, completion_action, None, None, "Build Wall")
                wall_jobs.append(job)
            elif character is 'o':
                completion_action = CreatePropAction(landscape.engine.player, entity_factories.stone_pillar, [x, y])
                job = JobEffort([[x, y]], 1, completion_action, None, None, "Create Prop")
                prop_jobs.append(job)
            else:
                completion_action = CreateFloorAction(landscape.engine.player, [x, y])
                job = JobEffort([[x, y]], 1, completion_action, None, None, "Build Floor")
                floor_jobs.append(job)

            # landscape.tiles[x, y]["graphic"]["ch"] = ord(' ')

        if character is "\n" or character is "\r":
            x = position[0]
            y += 1
        else:
            x += 1

    for j in wall_jobs:
        if j is not None:
            engine.jobs.queue.put(j)

    for j in prop_jobs:
        if j is not None:
            engine.jobs.queue.put(j)

    for j in floor_jobs:
        if j is not None:
            engine.jobs.queue.put(j)


"""Temp function, this file should be just for landscape stuff"""


def place_random_entities(landscape, minimum_entities: int, maximum_entities: int,) -> None:
    n_entities = random.randint(minimum_entities, maximum_entities)

    for i in range(n_entities):
        x = random.randint(1, landscape.width - 1)
        y = random.randint(1, landscape.height - 1)

        if not any(entity.x == x and entity.y == y for entity in landscape.entities):
            brother = entity_factories.brother.spawn(landscape, x, y)
            brother.ai.route = [(20, 20), (40, 40), (20, 40)]


def place_entities_in_random_location(landscape, entity: Actor, n_entities: int,) -> None:
    for i in range(n_entities):
        x = random.randint(1, landscape.width - 1)
        y = random.randint(1, landscape.height - 1)

        if not any(entity.x == x and entity.y == y for entity in landscape.entities):
            brother = entity.spawn(landscape, x, y)
            brother.ai.route = [(20, 20), (40, 40), (40, 20)]


def get_surrounding_tiles(position: Tuple[int, int]):
    return ([position[0] - 1, position[1] - 1],
            [position[0] - 1, position[1] + 1],
            [position[0] + 1, position[1] - 1],
            [position[0] + 1, position[1] + 1],
            [position[0] - 1, position[1]],
            [position[0] + 1, position[1]],
            [position[0], position[1] - 1],
            [position[0], position[1] + 1],
            )


def draw_rectangle(landscape, center, width, height, colour: Tuple[int, int, int], character):
    for x in range(center[0] - int(width / 2), center[0] + int(width / 2) + 1):
        for y in range(center[1] - int(height / 2), center[1] + int(height / 2) + 1):
            landscape.tiles[x, y]["graphic"]["bg"] = colour
            landscape.tiles[x, y]["graphic"]["ch"] = character
            landscape.tiles[x, y]["wearable"] = False


def place_cloister(landscape, start: Tuple[int, int], size):
    room_tiles = []
    for x in range(0, size):
        for y in range(0, size):
            if (x >= 2 and x < size - 2) and (y >= 2 and y < size - 2):
                entity_factories.cloister_grass.spawn(landscape, start[0] + x, start[1] + y)
            else:
                room_tiles.append((start[0] + x, start[1] + y))

    landscape.room_holder.add_room(RoomType.CLOISTER, room_tiles)
