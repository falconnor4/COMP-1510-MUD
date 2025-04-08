TERRAIN_TYPES = {
    "WALL": "#",
    "STONE": "▓",
    "TREE": "♣",
    "MOUNTAIN": "▲",
    "WATER": "~",
    "GRASS": ".",
    "PATH": "·",
    "SAND": ":",
    "DOOR": "+",
    "STAIRS": "≡",
    "EMPTY": " ",
    "BOSS_DOOR": "B",
}

TERRAIN_COLORS = {
    "WALL": 7,
    "STONE": 8,
    "TREE": 2,
    "MOUNTAIN": 7,
    "WATER": 4,
    "GRASS": 2,
    "PATH": 3,
    "SAND": 3,
    "DOOR": 5,
    "STAIRS": 6,
    "EMPTY": 0,
    "BOSS_DOOR": 1,
}

TERRAIN_CHARS = {
    0: " ",
    1: "#",
    2: "♣",
    3: "~",
    4: "·",
    5: "▲",
    6: "+",
    7: "≡",
    8: "▓",
    9: ":",
    10: "B",
}

LEGEND = {
    0: "EMPTY",
    1: "WALL",
    2: "TREE",
    3: "WATER",
    4: "PATH",
    5: "MOUNTAIN",
    6: "DOOR",
    7: "STAIRS",
    8: "STONE",
    9: "SAND",
    10: "BOSS_DOOR",
}

WORLD_MAP = [
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 2, 2, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 2, 2, 2, 0, 8],
    [8, 0, 2, 2, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 2, 2, 2, 0, 8],
    [8, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 4, 0, 0, 1, 6, 1, 0, 0, 4, 0, 0, 5, 5, 0, 8],
    [8, 0, 0, 0, 0, 4, 0, 0, 1, 0, 1, 0, 0, 4, 0, 0, 5, 5, 0, 8],
    [8, 2, 2, 0, 0, 4, 0, 0, 1, 0, 1, 0, 0, 4, 0, 0, 5, 5, 0, 8],
    [8, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 4, 4, 4, 4, 0, 4, 4, 4, 4, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 8],
    [8, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 8],
    [8, 0, 0, 3, 3, 3, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
]

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

ARCHETYPES = {
    "CAVE": {
        "walls": 1,
        "special_walls": 8,
        "decor": [3],
        "floor": 0,
        "path": 4,
        "min_room": 5,
        "corridor_width": 1,
        "split_bias": 0.7,
        "room_count": (6, 10),
        "color_shift": 2,
    },
    "FOREST": {
        "walls": 2,
        "special_walls": 5,
        "decor": [3, 9],
        "floor": 0,
        "path": 4,
        "min_room": 7,
        "corridor_width": 2,
        "split_bias": 0.3,
        "room_count": (2, 5),
        "color_shift": 3,
    },
    "TECH": {
        "walls": 1,
        "special_walls": 8,
        "decor": [3],
        "floor": 0,
        "path": 4,
        "min_room": 6,
        "corridor_width": 1,
        "split_bias": 0.5,
        "room_count": (8, 12),
        "color_shift": 4,
    },
    "BOSS_ARENA": {
        "walls": 8,
        "special_walls": 1,
        "decor": [3],
        "floor": 0,
        "path": 4,
        "min_room": 8,
        "corridor_width": 2,
        "split_bias": 0.5,
        "room_count": (2, 3),
        "color_shift": 5,
    },
}

ACTIVE_MAP = WORLD_MAP.copy()
CURRENT_MAP_TYPE = 0
CURRENT_COLOR_SHIFT = 0

from .static_map import generate_color_map

ACTIVE_COLORS = generate_color_map(ACTIVE_MAP)

import sys
sys.modules['map.static_map'].ACTIVE_COLORS = ACTIVE_COLORS
