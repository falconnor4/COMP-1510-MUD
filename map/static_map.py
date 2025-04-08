import math


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

ACTIVE_MAP = WORLD_MAP

CURRENT_MAP_TYPE = 0

CURRENT_COLOR_SHIFT = 0


DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def generate_color_map(world_map=None, color_shift=0):
    """
    Generate a 2D list of color codes corresponding to the terrain types in the world map.

    Applies color shifts based on the provided `color_shift` value to represent different themes.

    :param world_map: list[list[int]], the map grid to generate colors for. Defaults to ACTIVE_MAP.
    :param color_shift: int, the identifier for the color theme shift to apply.
    :precondition: world_map must be a valid map grid using integers defined in LEGEND.
    :precondition: color_shift should correspond to a key in `color_shift_effects`.
    :postcondition: Returns a map of the same dimensions containing color codes as strings.
    :return: list[list[str]], the generated color map.
    """
    if world_map is None:
        world_map = ACTIVE_MAP

    color_shift_effects = {
        0: {},
        1: {"WALL": 3, "STONE": 3, "PATH": 3},
        2: {"WALL": 4, "WATER": 6, "EMPTY": 4, "PATH": 4},
        3: {"EMPTY": 2, "PATH": 2, "WALL": 2},
        4: {"WALL": 6, "STONE": 6, "EMPTY": 8, "PATH": 6, "WATER": 4},
        5: {"WALL": 7, "STONE": 7, "EMPTY": 7, "PATH": 7, "WATER": 6},
    }

    shift_map = color_shift_effects.get(color_shift, {})

    color_map = []
    for row in world_map:
        color_row = []
        for cell in row:
            terrain_type = LEGEND[cell]

            if terrain_type in shift_map:
                color_row.append(str(shift_map[terrain_type]))
            else:
                color_row.append(str(TERRAIN_COLORS[terrain_type]))
        color_map.append(color_row)
    return color_map


ACTIVE_COLORS = generate_color_map(ACTIVE_MAP)


def generate_new_dungeon(width=40, height=20):
    """
    Generate a new dungeon level, update global map state, and return spawn coordinates.

    Imports `generate_dungeon_level` dynamically to handle potential circular dependencies.

    :param width: int, the desired width of the new dungeon.
    :param height: int, the desired height of the new dungeon.
    :precondition: `map.dungeon_generator` module must be available and functional.
    :postcondition: Updates global ACTIVE_MAP, CURRENT_COLOR_SHIFT, ACTIVE_COLORS.
    :postcondition: Ensures the returned spawn point is valid.
    :return: tuple[float, float], the (x, y) coordinates for player spawn (center of tile).
    """
    from map.dungeon_generator import generate_dungeon_level, ARCHETYPES

    dungeon_map, spawn_x, spawn_y, archetype_key = generate_dungeon_level(width, height)
    global ACTIVE_MAP, CURRENT_COLOR_SHIFT, ACTIVE_COLORS
    ACTIVE_MAP = dungeon_map
    CURRENT_COLOR_SHIFT = ARCHETYPES[archetype_key]["color_shift"]
    ACTIVE_COLORS = generate_color_map(ACTIVE_MAP, CURRENT_COLOR_SHIFT)

    if not is_spawn_valid(spawn_x, spawn_y, ACTIVE_MAP):
        spawn_x, spawn_y = find_valid_spawn(ACTIVE_MAP)

    return spawn_x + 0.5, spawn_y + 0.5


def switch_map(map_id, player_level=1):
    """
    Switch the active map between the static overworld and generated dungeons, or generate a new level.

    Handles logic for entering/leaving dungeons and boss arenas, updating global map state.

    :param map_id: int | str, identifier for the target map (1 for overworld, 2+ or 'boss_arena' for dungeons).
    :param player_level: int, the current player level, used to determine boss door placement.
    :precondition: Global map state variables (ACTIVE_MAP, etc.) must be initialized.
    :precondition: `map.dungeon_generator` must be available if generating new levels.
    :postcondition: Updates global ACTIVE_MAP, ACTIVE_COLORS, CURRENT_MAP_TYPE, CURRENT_COLOR_SHIFT.
    :postcondition: Places a boss door (tile 10) in new dungeons if player_level >= 3.
    :return: tuple[list[list[int]], list[list[str]], tuple[float, float], bool], the new map, new colors, player spawn coordinates, and a flag indicating if a new dungeon was entered.
    """
    global ACTIVE_MAP, ACTIVE_COLORS, CURRENT_MAP_TYPE, CURRENT_COLOR_SHIFT
    is_new_dungeon = False

    if map_id == "boss_arena":
        from map.dungeon_generator import generate_boss_arena

        boss_map, _, _, entrance_x, entrance_y = generate_boss_arena()
        ACTIVE_MAP = boss_map

        CURRENT_COLOR_SHIFT = 5
        ACTIVE_COLORS = generate_color_map(ACTIVE_MAP, CURRENT_COLOR_SHIFT)

        player_spawn = (entrance_x + 0.5, entrance_y + 0.5)
        CURRENT_MAP_TYPE = 999
        is_new_dungeon = True
        return ACTIVE_MAP, ACTIVE_COLORS, player_spawn, is_new_dungeon

    if map_id != 1 and CURRENT_MAP_TYPE == 0:
        # Generate first dungeon level
        player_spawn = generate_new_dungeon()
        CURRENT_MAP_TYPE = 1
        is_new_dungeon = True

    elif CURRENT_MAP_TYPE > 0:
        # Generate next dungeon level
        player_spawn = generate_new_dungeon()
        CURRENT_MAP_TYPE += 1
        is_new_dungeon = True

    elif map_id == 1 and CURRENT_MAP_TYPE > 0:
        ACTIVE_MAP = WORLD_MAP
        CURRENT_COLOR_SHIFT = 0
        ACTIVE_COLORS = generate_color_map(ACTIVE_MAP)
        player_spawn = (10.5, 8.5)
        CURRENT_MAP_TYPE = 0

    else:
        ACTIVE_MAP = WORLD_MAP
        CURRENT_COLOR_SHIFT = 0
        ACTIVE_COLORS = generate_color_map(ACTIVE_MAP)
        player_spawn = (10.5, 8.5)
        CURRENT_MAP_TYPE = 0

    if is_new_dungeon and player_level >= 3:

        door_x, door_y = find_tile_position(ACTIVE_MAP, 6)
        if door_x is not None:

            placed = False
            for dx, dy in DIRECTIONS:
                new_x, new_y = door_x + dx, door_y + dy
                if is_valid_boss_door_location(ACTIVE_MAP, new_x, new_y):
                    ACTIVE_MAP[new_y][new_x] = 10
                    placed = True
                    break

            if not placed:
                boss_door_pos = find_nearby_empty_space(ACTIVE_MAP, door_x, door_y)
                if boss_door_pos:
                    ACTIVE_MAP[boss_door_pos[1]][boss_door_pos[0]] = 10

    return ACTIVE_MAP, ACTIVE_COLORS, player_spawn, is_new_dungeon


def find_tile_position(world_map, tile_value):
    """
    Find the first occurrence of a specific tile value in the map.

    :param world_map: list[list[int]], the map grid to search within.
    :param tile_value: int, the integer value of the tile to find.
    :precondition: world_map must be a valid 2D list.
    :postcondition: Returns the coordinates if found, otherwise (None, None).
    :return: tuple[int | None, int | None], the (x, y) coordinates of the tile, or (None, None) if not found.
    >>> test_map = [[1, 0], [8, 6]]
    >>> find_tile_position(test_map, 6)
    (1, 1)
    >>> find_tile_position(test_map, 99)
    (None, None)
    """
    for y, row in enumerate(world_map):
        for x, cell in enumerate(row):
            if cell == tile_value:
                return x, y
    return None, None


def find_door_position(world_map):
    """
    Find the position of the main door (tile value 6) in the map.

    Convenience function wrapping `find_tile_position`.

    :param world_map: list[list[int]], the map grid to search within.
    :precondition: world_map must be a valid 2D list.
    :postcondition: Returns the coordinates if found, otherwise (None, None).
    :return: tuple[int | None, int | None], the (x, y) coordinates of the door, or (None, None) if not found.
    >>> test_map = [[1, 0], [8, 6]]
    >>> find_door_position(test_map)
    (1, 1)
    """
    return find_tile_position(world_map, 6)


def is_valid_boss_door_location(world_map, x, y):
    """
    Check if a position is valid for placing a boss door (must be empty floor).

    :param world_map: list[list[int]], the map grid.
    :param x: int, the x-coordinate to check.
    :param y: int, the y-coordinate to check.
    :precondition: world_map must be a valid 2D list. x, y should be within bounds (excluding border).
    :postcondition: Determines if the location is suitable for a boss door.
    :return: bool, True if the location is valid (empty floor), False otherwise.
    >>> test_map = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    >>> is_valid_boss_door_location(test_map, 1, 1)
    True
    >>> is_valid_boss_door_location(test_map, 0, 0) # Border wall
    False
    >>> is_valid_boss_door_location(test_map, 2, 1) # Wall
    False
    """
    # Check bounds first
    if not (0 < x < len(world_map[0]) - 1 and 0 < y < len(world_map) - 1):
        return False
    # Check if the tile is empty floor (tile ID 0)
    return world_map[y][x] == 0


def find_nearby_empty_space(world_map, start_x, start_y, max_distance=5):
    """
    Find the nearest empty floor space (tile 0) using BFS, up to a maximum distance.

    :param world_map: list[list[int]], the map grid.
    :param start_x: int, the starting x-coordinate for the search.
    :param start_y: int, the starting y-coordinate for the search.
    :param max_distance: int, the maximum search distance (radius) from the start point.
    :precondition: world_map must be a valid 2D list. start_x, start_y should be within bounds.
    :postcondition: Returns coordinates of the nearest empty space if found within max_distance.
    :return: tuple[int, int] | None, the (x, y) coordinates of the empty space, or None if not found.
    >>> test_map = [[1, 1, 1, 1], [1, 6, 1, 1], [1, 0, 1, 1], [1, 1, 1, 1]]
    >>> find_nearby_empty_space(test_map, 1, 1)
    (1, 2)
    """
    queue = [(start_x, start_y, 0)]
    visited = {(start_x, start_y)}

    while queue:
        x, y, dist = queue.pop(0)
        if dist > max_distance:
            continue

        if world_map[y][x] == 0:
            return x, y

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if (
                (nx, ny) not in visited
                and 0 < nx < len(world_map[0]) - 1
                and 0 < ny < len(world_map) - 1
            ):
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))

    return None


def is_spawn_valid(x, y, current_map):
    """
    Check if a potential spawn position (float coordinates) corresponds to a walkable tile.

    Walkable tiles are defined as EMPTY (0), PATH (4), or SAND (9).

    :param x: float, the x-coordinate to check.
    :param y: float, the y-coordinate to check.
    :param current_map: list[list[int]], the map grid.
    :precondition: current_map must be a valid 2D list.
    :postcondition: Determines if the tile at the integer coordinates of (x, y) is walkable.
    :return: bool, True if the location is walkable, False otherwise.
    >>> test_map = [[1, 0, 4], [8, 9, 1]]
    >>> is_spawn_valid(1.5, 0.5, test_map) # Tile (1, 0) is 0 (EMPTY)
    True
    >>> is_spawn_valid(2.1, 0.9, test_map) # Tile (2, 0) is 4 (PATH)
    True
    >>> is_spawn_valid(1.2, 1.3, test_map) # Tile (1, 1) is 9 (SAND)
    True
    >>> is_spawn_valid(0.5, 1.5, test_map) # Tile (0, 1) is 8 (STONE)
    False
    >>> is_spawn_valid(10.0, 10.0, test_map) # Out of bounds
    False
    """
    grid_x, grid_y = int(x), int(y)

    # Check bounds
    if not (0 <= grid_y < len(current_map) and 0 <= grid_x < len(current_map[0])):
        return False

    # Check if the tile type is walkable
    walkable_types = [0, 4, 9]  # EMPTY, PATH, SAND
    return current_map[grid_y][grid_x] in walkable_types


def find_valid_spawn(current_map):
    """
    Find a guaranteed valid spawn location if the initial one fails.

    Searches the map for any walkable tile, defaulting to carving out the center if none are found.

    :param current_map: list[list[int]], the map grid.
    :precondition: current_map must be a valid 2D list.
    :postcondition: Returns coordinates of a valid spawn location. May modify current_map if no valid spot exists initially.
    :return: tuple[int, int], the (x, y) integer coordinates of a valid spawn tile.
    """
    height = len(current_map)
    width = len(current_map[0]) if height > 0 else 0

    center_x, center_y = width // 2, height // 2
    if is_spawn_valid(center_x, center_y, current_map):
        return center_x, center_y

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if is_spawn_valid(x, y, current_map):
                return x, y

    center_x, center_y = width // 2, height // 2
    current_map[center_y][center_x] = 0
    return center_x, center_y


def interact_raycast(player_x, player_y, player_angle, world_map):
    """
    Cast a short ray forward from the player to detect interactable objects.

    Checks for doors, boss doors, stairs, or walls within a short distance.

    :param player_x: float, the player's current x-coordinate.
    :param player_y: float, the player's current y-coordinate.
    :param player_angle: float, the player's current viewing angle in radians.
    :param world_map: list[list[int]], the map grid.
    :precondition: Player coordinates and angle must be valid. world_map must be a valid map.
    :postcondition: Identifies the type and location of the first interactable or blocking object hit by the ray.
    :return: tuple[str | None, int | None, int | None], the type of object hit ('door', 'boss_door', 'stairs', 'wall', or None), and its (x, y) integer coordinates, or (None, None, None) if nothing is hit within range.
    """
    max_distance = 2.0
    distance = 0

    while distance < max_distance:

        distance += 0.1

        test_x = player_x + distance * math.cos(player_angle)
        test_y = player_y + distance * math.sin(player_angle)

        if (
            int(test_x) < 0
            or int(test_x) >= len(world_map[0])
            or int(test_y) < 0
            or int(test_y) >= len(world_map)
        ):
            return None, None, None

        cell_type = world_map[int(test_y)][int(test_x)]

        if cell_type == 6:
            return "door", int(test_x), int(test_y)
        elif cell_type == 10:
            return "boss_door", int(test_x), int(test_y)
        elif cell_type == 7:
            return "stairs", int(test_x), int(test_y)

        elif cell_type != 0 and cell_type != 4 and cell_type != 9:
            return "wall", int(test_x), int(test_y)

    return None, None, None


# TODO: Figure out how to scale the map.
def generate_char_map():
    """
    Generate a 2D list of characters representing the current ACTIVE_MAP terrain.

    :precondition: Global ACTIVE_MAP must be initialized and valid. LEGEND and TERRAIN_TYPES must be defined.
    :postcondition: Returns a map of the same dimensions containing character representations.
    :return: list[list[str]], the character map.
    """
    char_map = []
    for row in ACTIVE_MAP:
        char_row = [
            TERRAIN_CHARS.get(cell, "?") for cell in row
        ]  # Use TERRAIN_CHARS, default to '?'
        char_map.append(char_row)
    return char_map


def is_walkable(x, y):
    """
    Check if integer map coordinates (x, y) correspond to a walkable tile type in ACTIVE_MAP.

    Deprecated in favor of `is_spawn_valid` which handles float coordinates and uses the correct walkable set.
    Kept for potential compatibility if used elsewhere, but should be updated.

    :param x: int, the x-coordinate to check.
    :param y: int, the y-coordinate to check.
    :precondition: Global ACTIVE_MAP must be initialized. x, y should be integers.
    :postcondition: Determines if the tile type at (x, y) is considered walkable.
    :return: bool, True if walkable, False otherwise.
    """
    # Check bounds first
    if not (0 <= y < len(ACTIVE_MAP) and 0 <= x < len(ACTIVE_MAP[0])):
        return False

    cell_value = ACTIVE_MAP[y][x]
    terrain_type = LEGEND.get(cell_value, "WALL")
    return terrain_type in ["EMPTY", "PATH", "SAND"]


def get_map_str(player_x, player_y):
    """
    Generate a string representation of the current map with the player marked as '@'.

    :param player_x: float, the player's current x-coordinate.
    :param player_y: float, the player's current y-coordinate.
    :precondition: Global ACTIVE_MAP must be initialized. Player coordinates must be valid.
    :postcondition: Returns a multi-line string representing the map.
    :return: str, the map string.
    """
    map_str = ""
    char_map = generate_char_map()
    px, py = int(player_x), int(player_y)

    for y, row in enumerate(char_map):
        row_str = ""
        for x, cell in enumerate(row):
            if x == px and y == py:
                row_str += "@"
            else:
                row_str += cell
        map_str += row_str + "\n"  # Add newline after each row
    return map_str.strip()  # Remove trailing newline


WORLD_COLORS = generate_color_map()


def get_terrain_at(x, y):
    """
    Get the terrain type name (e.g., 'WALL', 'EMPTY') at the given float coordinates.

    :param x: float, the x-coordinate.
    :param y: float, the y-coordinate.
    :precondition: Global ACTIVE_MAP must be initialized. LEGEND must be defined.
    :postcondition: Returns the string name of the terrain type.
    :return: str, the terrain type name, defaulting to 'WALL' if out of bounds or unknown.
    """
    map_x, map_y = int(x), int(y)
    if 0 <= map_y < len(ACTIVE_MAP) and 0 <= map_x < len(ACTIVE_MAP[0]):
        cell_type = ACTIVE_MAP[map_y][map_x]
        return LEGEND.get(cell_type, "WALL")  # Use LEGEND, default to WALL
    return "WALL"  # Out of bounds defaults to WALL
