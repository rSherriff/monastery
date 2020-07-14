from typing import Iterator, Tuple

import colours
import numpy as np  # type: ignore
from game_map import GameMap
from voronoi import Voronoi
import tcod.noise
import random
import tile_types


def generate_landscape(map_width, map_height) -> GameMap:
    landscape = GameMap(map_width, map_height)

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
