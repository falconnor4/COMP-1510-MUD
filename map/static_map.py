import math


TERRAIN_TYPES = {
    'WALL': '#',  
    'STONE': '▓',  
    'TREE': '♣',  
    'MOUNTAIN': '▲',  
    'WATER': '~',  
    'GRASS': '.',  
    'PATH': '·',  
    'SAND': ':',  
    'DOOR': '+',  
    'STAIRS': '≡',  
    'EMPTY': ' ',  
    'BOSS_DOOR': 'B',  
}


TERRAIN_COLORS = {
    'WALL': 7,  
    'STONE': 8,  
    'TREE': 2,  
    'MOUNTAIN': 7,  
    'WATER': 4,  
    'GRASS': 2,  
    'PATH': 3,  
    'SAND': 3,  
    'DOOR': 5,  
    'STAIRS': 6,  
    'EMPTY': 0,  
    'BOSS_DOOR': 1,  
}


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
    10: 'BOSS_DOOR',  
}

# Add centralized terrain character mapping
TERRAIN_CHARS = {
    0: ' ',  # EMPTY
    1: '#',  # WALL
    2: '♣',  # TREE
    3: '~',  # WATER
    4: '·',  # PATH
    5: '▲',  # MOUNTAIN
    6: '+',  # DOOR
    7: '≡',  # STAIRS
    8: '▓',  # STONE
    9: ':',  # SAND
    10: 'B', # BOSS_DOOR
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

ACTIVE_MAP = WORLD_MAP

CURRENT_MAP_TYPE = 0

CURRENT_COLOR_SHIFT = 0



def generate_color_map(world_map=None, color_shift=0):
    """Generate color map with optional color shifting for different dungeon themes"""
    if world_map is None:
        world_map = ACTIVE_MAP

    
    color_shift_effects = {
        0: {},  
        1: {    
            'WALL': 3,
            'STONE': 3,
            'PATH': 3
        },
        2: {    
            'WALL': 4,
            'WATER': 6,
            'EMPTY': 4,
            'PATH': 4
        },
        3: {    
            'EMPTY': 2,
            'PATH': 2,
            'WALL': 2
        },
        4: {    
            'WALL': 6,
            'STONE': 6,
            'EMPTY': 8,
            'PATH': 6,
            'WATER': 4
        },
        5: {    
            'WALL': 7,
            'STONE': 7,
            'EMPTY': 7,
            'PATH': 7,
            'WATER': 6
        }
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



def switch_map(map_id, player_level=1):
    """
    Switch the active map to a different map or generate a new dungeon
    Returns: (new_map, new_colors, player_spawn, is_new_dungeon)
    """
    global ACTIVE_MAP, ACTIVE_COLORS, CURRENT_MAP_TYPE, CURRENT_COLOR_SHIFT
    is_new_dungeon = False
    
    
    if map_id == 'boss_arena':
        from map.dungeon_generator import generate_boss_arena
        boss_map, center_x, center_y, entrance_x, entrance_y = generate_boss_arena()
        ACTIVE_MAP = boss_map
        
        
        CURRENT_COLOR_SHIFT = 5  
        ACTIVE_COLORS = generate_color_map(ACTIVE_MAP, CURRENT_COLOR_SHIFT)
        
        
        player_spawn = (entrance_x + 0.5, entrance_y + 0.5)
        CURRENT_MAP_TYPE = 999  
        is_new_dungeon = True
        return ACTIVE_MAP, ACTIVE_COLORS, player_spawn, is_new_dungeon
    
    if map_id != 1 and CURRENT_MAP_TYPE == 0:
        
        from map.dungeon_generator import generate_dungeon_level
        dungeon_map, spawn_x, spawn_y, archetype = generate_dungeon_level(40, 20)
        ACTIVE_MAP = dungeon_map
        
        
        from map.dungeon_generator import ARCHETYPES
        CURRENT_COLOR_SHIFT = ARCHETYPES[archetype]['color_shift']
        
        
        ACTIVE_COLORS = generate_color_map(ACTIVE_MAP, CURRENT_COLOR_SHIFT)
        
        
        if not is_spawn_valid(spawn_x, spawn_y, ACTIVE_MAP):
            spawn_x, spawn_y = find_valid_spawn(ACTIVE_MAP)
        
        player_spawn = (spawn_x + 0.5, spawn_y + 0.5)  
        CURRENT_MAP_TYPE = 1  
        is_new_dungeon = True
        
    
    elif CURRENT_MAP_TYPE > 0:
        
        from map.dungeon_generator import generate_dungeon_level
        dungeon_map, spawn_x, spawn_y, archetype = generate_dungeon_level(40, 20)
        ACTIVE_MAP = dungeon_map
        
        
        from map.dungeon_generator import ARCHETYPES
        CURRENT_COLOR_SHIFT = ARCHETYPES[archetype]['color_shift']
        
        
        ACTIVE_COLORS = generate_color_map(ACTIVE_MAP, CURRENT_COLOR_SHIFT)
        
        
        if not is_spawn_valid(spawn_x, spawn_y, ACTIVE_MAP):
            spawn_x, spawn_y = find_valid_spawn(ACTIVE_MAP)
        
        player_spawn = (spawn_x + 0.5, spawn_y + 0.5)
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
        
        door_x, door_y = find_door_position(ACTIVE_MAP)
        if door_x is not None:
            
            placed = False
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = door_x + dx, door_y + dy
                if (is_valid_boss_door_location(ACTIVE_MAP, new_x, new_y)):
                    ACTIVE_MAP[new_y][new_x] = 10  
                    placed = True
                    break
            
            
            if not placed:
                boss_door_pos = find_nearby_empty_space(ACTIVE_MAP, door_x, door_y)
                if boss_door_pos:
                    ACTIVE_MAP[boss_door_pos[1]][boss_door_pos[0]] = 10
    
    return ACTIVE_MAP, ACTIVE_COLORS, player_spawn, is_new_dungeon

def find_door_position(world_map):
    """Find the position of the main door in the map"""
    for y in range(len(world_map)):
        for x in range(len(world_map[0])):
            if world_map[y][x] == 6:  
                return x, y
    return None, None

def is_valid_boss_door_location(world_map, x, y):
    """Check if a position is valid for placing a boss door"""
    if not (0 < x < len(world_map[0])-1 and 0 < y < len(world_map)-1):
        return False
    return world_map[y][x] == 0  

def find_nearby_empty_space(world_map, start_x, start_y, max_distance=5):
    """Find a nearby empty space for placing a boss door"""
    queue = [(start_x, start_y, 0)]  
    visited = {(start_x, start_y)}
    
    while queue:
        x, y, dist = queue.pop(0)
        if dist > max_distance:
            continue
            
        if world_map[y][x] == 0:  
            return x, y
            
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if ((nx, ny) not in visited and 
                0 < nx < len(world_map[0])-1 and 
                0 < ny < len(world_map)-1):
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))
                
    return None


def is_spawn_valid(x, y, current_map):
    """Check if the spawn position is valid (not a wall or door)"""
    
    grid_x, grid_y = int(x), int(y)
    
    
    if grid_y < 0 or grid_y >= len(current_map) or grid_x < 0 or grid_x >= len(current_map[0]):
        return False
    
    
    walkable_types = [0, 4, 9]  
    return current_map[grid_y][grid_x] in walkable_types


def find_valid_spawn(current_map):
    """Find a valid spawn position if the original one is not walkable"""
    height = len(current_map)
    width = len(current_map[0]) if height > 0 else 0
    
    
    center_x, center_y = width // 2, height // 2
    if is_spawn_valid(center_x, center_y, current_map):
        return center_x, center_y
    
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            if is_spawn_valid(x, y, current_map):
                return x, y
    
    
    center_x, center_y = width // 2, height // 2
    current_map[center_y][center_x] = 0  
    return center_x, center_y



def interact_raycast(player_x, player_y, player_angle, world_map):
    """Cast a ray from the player and detect interactive objects"""
    
    max_distance = 2.0
    distance = 0

    
    while distance < max_distance:
        
        distance += 0.1

        
        test_x = player_x + distance * math.cos(player_angle)
        test_y = player_y + distance * math.sin(player_angle)

        
        if (int(test_x) < 0 or int(test_x) >= len(world_map[0]) or
                int(test_y) < 0 or int(test_y) >= len(world_map)):
            return None, None, None  

        
        cell_type = world_map[int(test_y)][int(test_x)]

        
        if cell_type == 6:  
            return 'door', int(test_x), int(test_y)
        elif cell_type == 10:  
            return 'boss_door', int(test_x), int(test_y)
        elif cell_type == 7:  
            return 'stairs', int(test_x), int(test_y)
        

        
        elif cell_type != 0 and cell_type != 4 and cell_type != 9:
            return 'wall', int(test_x), int(test_y)  

    
    return None, None, None



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



def is_walkable(x, y):
    if 0 <= y < len(ACTIVE_MAP) and 0 <= x < len(ACTIVE_MAP[0]):
        cell_type = LEGEND[ACTIVE_MAP[y][x]]
        
        return cell_type in ['EMPTY', 'PATH', 'SAND', 'GRASS']
    return False



def get_map_str(player_x, player_y):
    map_str = ""
    char_map = generate_char_map()

    
    px = int(player_x)
    py = int(player_y)

    for y, row in enumerate(char_map):
        for x, cell in enumerate(row):
            if x == px and y == py:
                map_str += '@'  
            else:
                map_str += cell
        map_str += '\n'

    return map_str


WORLD_COLORS = generate_color_map()



def get_terrain_at(x, y):
    if 0 <= y < len(ACTIVE_MAP) and 0 <= x < len(ACTIVE_MAP[0]):
        cell_type = ACTIVE_MAP[int(y)][int(x)]
        return LEGEND[cell_type]
    return 'WALL'
