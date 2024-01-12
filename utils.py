import struct
from functools import lru_cache
from pathlib import Path

import pygame


@lru_cache()
def load_shaders(vertex: str, fragment=None, ignore_extensions=False):
    if not fragment:
        fragment = vertex
    if not ignore_extensions:
        if not vertex.endswith('.vert'):
            vertex += '.vert'
        if not fragment.endswith('.frag'):
            fragment += '.frag'
    path = Path(__file__).parent / 'shaders'
    with open(path / vertex, 'r') as f:
        vertex_shader = f.read()
    with open(path / fragment, 'r') as f:
        fragment_shader = f.read()
    return {'vertex_shader': vertex_shader, 'fragment_shader': fragment_shader}


def float32(n):
    return struct.unpack('f', struct.pack('f', n))[0]


def float_bytes(n):
    return struct.pack('f', n)


def scale_rect(r1, r2):
    w1, h1 = r1
    w2, h2 = r2

    # Calculate the aspect ratios
    aspect_ratio_r1 = w1 / h1
    aspect_ratio_r2 = w2 / h2

    # Check if r2 can fit inside r1 horizontally or vertically
    if aspect_ratio_r1 >= aspect_ratio_r2:
        # Scale based on height
        new_h = h1
        new_w = int(h1 * aspect_ratio_r2)
    else:
        # Scale based on width
        new_w = w1
        new_h = int(w1 / aspect_ratio_r2)

    return new_w, new_h


def rotate_and_scale_rect_points(rect, scale=1, angle=0):
    rect = pygame.Rect(*rect)
    pos = [*rect.center]
    rect.center = (0, 0)
    points = [
        pygame.Vector2(*i).rotate(angle) * scale + pos for i in
        (rect.topleft, rect.topright, rect.bottomright, rect.bottomleft)
    ]
    for i, j in [(0, 3), (1, 2)]:
        points[i], points[j] = points[j], points[i]
    return points


def rect_to_normalized_vertices(rect, t_size, cartesian=False):
    x, y, width, height = rect
    t_width, t_height = t_size

    if cartesian:
        # normalized Cartesian coordinates
        normalized_x = 2 * (x / t_width) - 1
        normalized_y = 1 - 2 * (y / t_height)
        normalized_width = 2 * (width / t_width)
        normalized_height = -2 * (height / t_height)
    else:
        # normalized coordinates
        normalized_x = x / t_width
        normalized_y = y / t_height
        normalized_width = width / t_width
        normalized_height = height / t_height

    vertices = [
        [normalized_x, normalized_y],  # Top-left
        [normalized_x + normalized_width, normalized_y],  # Top-right
        [normalized_x + normalized_width, normalized_y + normalized_height],  # Bottom-right
        [normalized_x, normalized_y + normalized_height]  # Bottom-left
    ][::-1 if not cartesian else 1]

    return vertices


def point_to_coordinates(point, t_size, cartesian=False):
    x, y = point
    t_width, t_height = t_size

    if cartesian:
        # normalized Cartesian coordinates
        normalized_x = 2 * (x / t_width) - 1
        normalized_y = 1 - 2 * (y / t_height)
    else:
        #   normalized coordinates
        normalized_x = x / t_width
        normalized_y = y / t_height

    return normalized_x, normalized_y
