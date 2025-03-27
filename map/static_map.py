import math

# Map terrain types (characters used for rendering)
TERRAIN_TYPES = {
    'WALL': '#',  # Basic wall
    'STONE': '▓',  # Stone wall
    'TREE': '♣',  # Trees/forest
    'MOUNTAIN': '▲',  # Mountains
    'WATER': '~',  # Water/river
    'GRASS': '.',  # Grass/field
    'PATH': '·',  # Path/road
    'SAND': ':',  # Sand/desert
    'DOOR': '+',  # Door
    'STAIRS': '≡',  # Stairs
    'EMPTY': ' ',  # Empty space
}

# Terminal colors for different terrains
TERRAIN_COLORS = {
    'WALL': 7,  # White
    'STONE': 8,  # Gray
    'TREE': 2,  # Green
    'MOUNTAIN': 7,  # White
    'WATER': 4,  # Blue
    'GRASS': 2,  # Green
    'PATH': 3,  # Yellow
    'SAND': 3,  # Yellow
    'DOOR': 5,  # Magenta
    'STAIRS': 6,  # Cyan
    'EMPTY': 0,  # Black
}

# Map legend - maps numerical values to terrain types
LEGEND = {
    0: 'EMPTY',
    1: 'WALL',
    2: 'TREE',
    3: 'WATER',
    4: 'PATH',
    5: 'MOUNTAIN',
    6: 'DOOR',
    7: 'STAIRS',
    8: 'STONE',
    9: 'SAND',
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
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
]

WORLD_MAP_2 = [
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 8, 0, 0, 0, 0, 8, 0, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
]

# Current active map reference - start with the main world map
ACTIVE_MAP = WORLD_MAP


# Generate color map based on terrain types
def generate_color_map(world_map=None):
    if world_map is None:
        world_map = ACTIVE_MAP

    color_map = []
    for row in world_map:
        color_row = []
        for cell in row:
            terrain_type = LEGEND[cell]
            color_row.append(str(TERRAIN_COLORS[terrain_type]))
        color_map.append(color_row)
    return color_map


# Initialize color map immediately - THIS IS THE FIX
ACTIVE_COLORS = generate_color_map(ACTIVE_MAP)


# Switch between different maps
def switch_map(map_id):
    """Switch the active map to a different map"""
    global ACTIVE_MAP, ACTIVE_COLORS

    if map_id == 1:
        ACTIVE_MAP = WORLD_MAP
    elif map_id == 2:
        ACTIVE_MAP = WORLD_MAP_2
    else:
        # Default to main map
        ACTIVE_MAP = WORLD_MAP

    # Update colors for the new map
    ACTIVE_COLORS = generate_color_map(ACTIVE_MAP)

    return ACTIVE_MAP, ACTIVE_COLORS


# Raycast for interaction
def interact_raycast(player_x, player_y, player_angle, world_map):
    """Cast a ray from the player and detect interactive objects"""
    # Maximum interaction distance
    max_distance = 2.0
    distance = 0

    # Start from player position
    while distance < max_distance:
        # Increment distance
        distance += 0.1

        # Calculate position along ray
        test_x = player_x + distance * math.cos(player_angle)
        test_y = player_y + distance * math.sin(player_angle)

        # Check if we're out of bounds
        if (int(test_x) < 0 or int(test_x) >= len(world_map[0]) or
                int(test_y) < 0 or int(test_y) >= len(world_map)):
            return None, None, None  # No object found

        # Get cell type at this position
        cell_type = world_map[int(test_y)][int(test_x)]

        # Check if we hit an interactive object
        if cell_type == 6:  # Door
            return 'door', int(test_x), int(test_y)
        elif cell_type == 7:  # Stairs
            return 'stairs', int(test_x), int(test_y)
        # Could add other interaction types here... probably not.

        # Check if hit a wall (non-interactive)
        elif cell_type != 0 and cell_type != 4 and cell_type != 9:
            return 'wall', int(test_x), int(test_y)  # Hit a non-interactive wall

    # No interactive object found within range
    return None, None, None


# Generate character representation of map (for ASCII display)
# TODO: Figure out how to scale the map.
def generate_char_map():
    char_map = []
    for row in ACTIVE_MAP:
        char_row = []
        for cell in row:
            terrain_type = LEGEND[cell]
            char_row.append(TERRAIN_TYPES[terrain_type])
        char_map.append(char_row)
    return char_map


# Check if position is walkable
def is_walkable(x, y):
    if 0 <= y < len(ACTIVE_MAP) and 0 <= x < len(ACTIVE_MAP[0]):
        cell_type = LEGEND[ACTIVE_MAP[y][x]]
        # Define which terrain types are walkable
        return cell_type in ['EMPTY', 'PATH', 'SAND', 'GRASS']
    return False


# Get a string representation of the map with player position
def get_map_str(player_x, player_y):
    map_str = ""
    char_map = generate_char_map()

    # Round player position to nearest grid cell
    px = int(player_x)
    py = int(player_y)

    for y, row in enumerate(char_map):
        for x, cell in enumerate(row):
            if x == px and y == py:
                map_str += '@'  # Player marker
            else:
                map_str += cell
        map_str += '\n'

    return map_str

WORLD_COLORS = generate_color_map()


# Get terrain type at a specific location
def get_terrain_at(x, y):
    if 0 <= y < len(ACTIVE_MAP) and 0 <= x < len(ACTIVE_MAP[0]):
        cell_type = ACTIVE_MAP[int(y)][int(x)]
        return LEGEND[cell_type]
    return 'WALL'  # Default to wall for out of bounds (eliminates crashing on edge cases)
