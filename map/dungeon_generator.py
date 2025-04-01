import random, collections, heapq, math
from map.static_map import LEGEND, generate_color_map


ARCHETYPES = {
    'CAVE': {
        'walls': 1,         
        'special_walls': 8, 
        'decor': [3, 9],    
        'floor': 0,         
        'path': 4,          
        'min_room': 4,      
        'corridor_width': 1,
        'split_bias': 0.4,  
        'room_count': (3, 7),
        'color_shift': 0    
    },
    'RUINS': {
        'walls': 8,         
        'special_walls': 1, 
        'decor': [2, 9],    
        'floor': 0,         
        'path': 4,          
        'min_room': 6,      
        'corridor_width': 2,
        'split_bias': 0.5,  
        'room_count': (4, 8),
        'color_shift': 1    
    },
    'CRYPT': {
        'walls': 8,         
        'special_walls': 5, 
        'decor': [3],       
        'floor': 0,         
        'path': 4,          
        'min_room': 5,      
        'corridor_width': 1,
        'split_bias': 0.7,  
        'room_count': (6, 10),
        'color_shift': 2    
    },
    'FOREST': {
        'walls': 2,         
        'special_walls': 5, 
        'decor': [3, 9],    
        'floor': 0,         
        'path': 4,          
        'min_room': 7,      
        'corridor_width': 2,
        'split_bias': 0.3,  
        'room_count': (2, 5),
        'color_shift': 3    
    },
    'TECH': {
        'walls': 1,         
        'special_walls': 8, 
        'decor': [3],       
        'floor': 0,         
        'path': 4,          
        'min_room': 6,      
        'corridor_width': 1,
        'split_bias': 0.5,  
        'room_count': (8, 12),
        'color_shift': 4    
    },
    'BOSS_ARENA': {
        'walls': 8,         
        'special_walls': 1, 
        'decor': [3],       
        'floor': 0,         
        'path': 4,          
        'min_room': 8,      
        'corridor_width': 2, 
        'split_bias': 0.5,  
        'room_count': (2, 3), 
        'color_shift': 5    
    }
}

def generate_dungeon(width, height, archetype_key=None):
    """Compact dungeon generator with archetypes"""
    
    if not archetype_key or archetype_key not in ARCHETYPES:
        archetype_key = random.choice(list(ARCHETYPES.keys()))
    
    archetype = ARCHETYPES[archetype_key]
    min_room_size = archetype['min_room']
    max_splits = random.randint(*archetype['room_count'])
    
    
    class Node: 
        def __init__(self, x, y, w, h): self.x, self.y, self.w, self.h, self.left, self.right, self.room = x, y, w, h, None, None, None
        def add_room(self): self.room = (self.x + random.randint(1, 3), self.y + random.randint(1, 3), 
                             max(min_room_size, random.randint(self.w // 3, self.w - 3)), 
                             max(min_room_size, random.randint(self.h // 3, self.h - 3)))
    
    
    dungeon = [[archetype['walls'] for _ in range(width)] for _ in range(height)]
    
    
    def split(node, depth):
        if depth == 0 or node.w < min_room_size*2 or node.h < min_room_size*2: 
            node.add_room()
            return [node]
        
        
        split_h = random.random() > archetype['split_bias'] if node.w == node.h else node.w > node.h
        
        if split_h:  
            split_pos = random.randint(min_room_size, node.w - min_room_size)
            node.left = Node(node.x, node.y, split_pos, node.h)
            node.right = Node(node.x + split_pos, node.y, node.w - split_pos, node.h)
        else:  
            split_pos = random.randint(min_room_size, node.h - min_room_size)
            node.left = Node(node.x, node.y, node.w, split_pos)
            node.right = Node(node.x, node.y + split_pos, node.w, node.h - split_pos)
            
        return split(node.left, depth-1) + split(node.right, depth-1)
    
    
    leaves = split(Node(0, 0, width, height), max_splits)
    
    
    for node in leaves:
        if not node.room: continue
        x, y, w, h = node.room
        for i in range(y, min(y + h, height - 1)):
            for j in range(x, min(x + w, width - 1)):
                dungeon[i][j] = archetype['floor']
    
    
    def connect_rooms():
        
        centers = [(node.room[0] + node.room[2]//2, node.room[1] + node.room[3]//2) for node in leaves if node.room]
        
        
        if len(centers) <= 1: return
        
        
        edges = []
        for i, (x1, y1) in enumerate(centers):
            for j, (x2, y2) in enumerate(centers):
                if i != j:
                    dist = abs(x2 - x1) + abs(y2 - y1)  
                    edges.append((dist, (x1, y1), (x2, y2)))
        
        
        edges.sort()
        
        
        connected = {i: i for i in range(len(centers))}
        def find(x): return x if connected[x] == x else find(connected[x])
        
        
        for _, (x1, y1), (x2, y2) in edges:
            set1 = find(centers.index((x1, y1)))
            set2 = find(centers.index((x2, y2)))
            if set1 != set2:
                
                connected[set2] = set1
                
                
                corridor_w = archetype['corridor_width']
                
                
                if random.random() < 0.5:  
                    
                    mid_x, mid_y = x2, y1
                else:  
                    
                    mid_x, mid_y = x1, y2
                
                
                for x in range(min(x1, mid_x), max(x1, mid_x) + 1):
                    for offset in range(-corridor_w//2 + 1, corridor_w//2 + 1):
                        ny = y1 + offset
                        if 0 < ny < height-1 and 0 < x < width-1:
                            dungeon[ny][x] = archetype['path'] if random.random() < 0.7 else archetype['floor']
                
                
                for y in range(min(y1, mid_y), max(y1, mid_y) + 1):
                    for offset in range(-corridor_w//2 + 1, corridor_w//2 + 1):
                        nx = mid_x + offset
                        if 0 < y < height-1 and 0 < nx < width-1:
                            dungeon[y][nx] = archetype['path'] if random.random() < 0.7 else archetype['floor']
                
                
                for y in range(mid_y-1, mid_y+2):
                    for x in range(mid_x-1, mid_x+2):
                        if 0 < y < height-1 and 0 < x < width-1:
                            dungeon[y][x] = archetype['floor']
                
                
                if mid_x != x2 or mid_y != y2:
                    for x in range(min(mid_x, x2), max(mid_x, x2) + 1):
                        for offset in range(-corridor_w//2 + 1, corridor_w//2 + 1):
                            ny = mid_y + offset
                            if 0 < ny < height-1 and 0 < x < width-1:
                                dungeon[ny][x] = archetype['path'] if random.random() < 0.7 else archetype['floor']
                    
                    for y in range(min(mid_y, y2), max(mid_y, y2) + 1):
                        for offset in range(-corridor_w//2 + 1, corridor_w//2 + 1):
                            nx = x2 + offset
                            if 0 < y < height-1 and 0 < nx < width-1:
                                dungeon[y][nx] = archetype['path'] if random.random() < 0.7 else archetype['floor']
    
    connect_rooms()
    
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            
            if dungeon[y][x] == archetype['walls'] and random.random() < 0.15:
                dungeon[y][x] = archetype['special_walls']
            
            elif dungeon[y][x] == archetype['floor'] and random.random() < 0.05:
                dungeon[y][x] = random.choice(archetype['decor'])
    
    
    for x in range(width): 
        dungeon[0][x] = dungeon[height-1][x] = 8
    for y in range(height): 
        dungeon[y][0] = dungeon[y][width-1] = 8
    
    return dungeon, archetype_key

def generate_dungeon_level(width=40, height=20, min_room_size=5, max_splits=4, player_level=1):
    """Generate dungeon with spawn and door - maintains compatibility with existing code"""
    
    dungeon_map, archetype = generate_dungeon(width, height)
    
    
    ensure_connectivity(dungeon_map)
    
    
    spawn_x, spawn_y = find_safe_spawn_location(dungeon_map, width, height)
    
    
    door_point = find_farthest_point(dungeon_map, spawn_x, spawn_y)
    door_x, door_y = door_point
    
    
    if player_level >= 3:
        dungeon_map[door_y][door_x] = 10  
    else:
        dungeon_map[door_y][door_x] = 6   
    
    
    add_features(dungeon_map, archetype)
    
    
    if not is_valid_spawn(dungeon_map, spawn_x, spawn_y):
        spawn_x, spawn_y = find_safe_spawn_location(dungeon_map, width, height)
    
    
    return dungeon_map, spawn_x, spawn_y, archetype

def find_safe_spawn_location(dungeon_map, width, height):
    """Find a guaranteed safe spawn location away from walls and doors"""
    
    spawn_corner = (1, 1, width // 4, height // 4)
    x_min, y_min, x_max, y_max = spawn_corner
    
    
    spawn_candidates = []
    for y in range(y_min + 1, y_max):
        for x in range(x_min + 1, x_max):
            
            if is_valid_spawn(dungeon_map, x, y):
                
                if is_open_area(dungeon_map, x, y):
                    spawn_candidates.append((x, y))
    
    
    if not spawn_candidates:
        for y in range(1, height-1):
            for x in range(1, width-1):
                if is_valid_spawn(dungeon_map, x, y) and is_open_area(dungeon_map, x, y):
                    spawn_candidates.append((x, y))
    
    
    if not spawn_candidates:
        spawn_x, spawn_y = width // 4, height // 4
        create_safe_spawn_area(dungeon_map, spawn_x, spawn_y)
        return spawn_x, spawn_y
    
    
    return random.choice(spawn_candidates)

def is_valid_spawn(dungeon_map, x, y):
    """Check if a position is valid for spawning (must be empty floor)"""
    return 0 <= x < len(dungeon_map[0]) and 0 <= y < len(dungeon_map) and dungeon_map[y][x] == 0

def is_open_area(dungeon_map, x, y, radius=1):
    """Check if there's enough open space around spawn point"""
    h, w = len(dungeon_map), len(dungeon_map[0])
    walkable = [0, 4, 9]  
    
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            nx, ny = x + dx, y + dy
            if not (0 < nx < w-1 and 0 < ny < h-1 and dungeon_map[ny][nx] in walkable):
                return False
    return True

def create_safe_spawn_area(dungeon_map, x, y, size=2):
    """Create a guaranteed safe spawn area at the given position"""
    h, w = len(dungeon_map), len(dungeon_map[0])
    
    
    x = max(2, min(x, w-3))
    y = max(2, min(y, h-3))
    
    
    for dy in range(-size, size+1):
        for dx in range(-size, size+1):
            nx, ny = x + dx, y + dy
            if 0 < ny < h-1 and 0 < nx < w-1:
                dungeon_map[ny][nx] = 0  


def ensure_connectivity(dmap):
    """Make sure all walkable spaces are connected"""
    h, w = len(dmap), len(dmap[0])
    regions = []
    visited = set()
    
    
    for y in range(1, h-1):
        for x in range(1, w-1):
            if dmap[y][x] in [0, 4, 9] and (x, y) not in visited:
                region = []
                queue = collections.deque([(x, y)])
                visited.add((x, y))
                
                while queue:
                    cx, cy = queue.popleft()
                    region.append((cx, cy))
                    
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = cx+dx, cy+dy
                        if (0 < nx < w-1 and 0 < ny < h-1 and 
                            dmap[ny][nx] in [0, 4, 9] and (nx, ny) not in visited):
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                
                if region: regions.append(region)
    
    
    if len(regions) <= 1: return
    regions.sort(key=len, reverse=True)
    
    for i in range(1, len(regions)):
        
        best_dist, best_pair = float('inf'), None
        for p1 in random.sample(regions[0], min(30, len(regions[0]))):
            for p2 in random.sample(regions[i], min(30, len(regions[i]))):
                dist = abs(p2[0]-p1[0]) + abs(p2[1]-p1[1])
                if dist < best_dist: best_dist, best_pair = dist, (p1, p2)
        
        
        if best_pair:
            x1, y1 = best_pair[0]
            x2, y2 = best_pair[1]
            
            
            mid_x = (x1 + x2) // 2
            dmap[y1][mid_x] = dmap[y2][mid_x] = 0
            for y in range(min(y1, y2), max(y1, y2)+1): dmap[y][mid_x] = 0
            for x in range(min(x1, mid_x), max(x1, mid_x)+1): dmap[y1][x] = 0
            for x in range(min(mid_x, x2), max(mid_x, x2)+1): dmap[y2][x] = 0

def find_farthest_point(dmap, sx, sy):
    """Find point farthest from start using A*"""
    h, w = len(dmap), len(dmap[0])
    
    
    target_area = {
        'x_min': w * 3 // 4, 'y_min': h * 3 // 4,
        'x_max': w - 2, 'y_max': h - 2
    }
    
    
    is_forest_map = False
    tree_count = 0
    for y in range(1, h-1):
        for x in range(1, w-1):
            if dmap[y][x] == 2:  
                tree_count += 1
                if tree_count > 10:  
                    is_forest_map = True
                    break
        if is_forest_map:
            break
    
    open_set, closed_set = [], set()
    g_scores = {(sx, sy): 0}
    heapq.heappush(open_set, (0, sx, sy))
    
    best_point, max_dist = (sx, sy), 0
    min_distance_required = 10  
    
    while open_set:
        _, cx, cy = heapq.heappop(open_set)
        if (cx, cy) in closed_set: continue
        closed_set.add((cx, cy))
        
        
        curr_dist = g_scores[(cx, cy)]
        in_target = (target_area['x_min'] <= cx <= target_area['x_max'] and
                    target_area['y_min'] <= cy <= target_area['y_max'])
        
        
        direct_dist = math.sqrt((cx-sx)**2 + (cy-sy)**2)
        
        
        if is_forest_map:
            if direct_dist > min_distance_required and is_good_door_spot(dmap, cx, cy):
                if direct_dist > max_dist:
                    max_dist, best_point = direct_dist, (cx, cy)
                    if in_target:  
                        min_distance_required = direct_dist  
        else:
            
            if curr_dist > max_dist and is_good_door_spot(dmap, cx, cy):
                if in_target or not (target_area['x_min'] <= best_point[0] <= target_area['x_max'] and
                                   target_area['y_min'] <= best_point[1] <= target_area['y_max']):
                    max_dist, best_point = curr_dist, (cx, cy)
        
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = cx+dx, cy+dy
            if (nx, ny) in closed_set or not (0 < nx < w-1 and 0 < ny < h-1):
                continue
            
            
            walkable = [0, 4, 9]
            if is_forest_map:
                walkable.append(2)  
                
            if dmap[ny][nx] not in walkable:
                continue
            
            tent_g = g_scores[(cx, cy)] + 1
            if (nx, ny) not in g_scores or tent_g > g_scores[(nx, ny)]:
                g_scores[(nx, ny)] = tent_g
                heapq.heappush(open_set, (-tent_g, nx, ny))
    
    
    if is_forest_map and math.sqrt((best_point[0]-sx)**2 + (best_point[1]-sy)**2) < min_distance_required:
        
        for attempt in range(100):  
            test_x = random.randint(w//2, w-3)
            test_y = random.randint(h//2, h-3)
            if is_good_door_spot(dmap, test_x, test_y):
                direct_dist = math.sqrt((test_x-sx)**2 + (test_y-sy)**2)
                if direct_dist > min_distance_required:
                    best_point = (test_x, test_y)
                    break
    
    
    if not is_good_door_spot(dmap, best_point[0], best_point[1]):
        best_point = find_door_spot(dmap, best_point[0], best_point[1])
    
    return best_point

def is_good_door_spot(dmap, x, y):
    """Check if position is suitable for a door"""
    if not (0 < x < len(dmap[0])-1 and 0 < y < len(dmap)-1):
        return False
        
    if dmap[y][x] not in [0, 4, 9]: return False
    
    
    wall_count = sum(1 for dy in range(-1, 2) for dx in range(-1, 2)
                    if 0 < y+dy < len(dmap)-1 and 0 < x+dx < len(dmap[0])-1 and 
                    dmap[y+dy][x+dx] in [1, 2, 5, 8])  
    
    empty_count = sum(1 for dy in range(-1, 2) for dx in range(-1, 2)
                     if 0 < y+dy < len(dmap)-1 and 0 < x+dx < len(dmap[0])-1 and 
                     dmap[y+dy][x+dx] in [0, 4, 9])
    
    return wall_count >= 1 and wall_count <= 5 and empty_count >= 3

def find_door_spot(dmap, x, y):
    """Find suitable door location near given point"""
    queue = collections.deque([(x, y)])
    visited = {(x, y)}
    
    while queue:
        cx, cy = queue.popleft()
        if is_good_door_spot(dmap, cx, cy): return cx, cy
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = cx+dx, cy+dy
            if ((nx, ny) not in visited and 0 < nx < len(dmap[0])-1 and 
                0 < ny < len(dmap)-1 and dmap[ny][nx] in [0, 4, 9]):
                queue.append((nx, ny))
                visited.add((nx, ny))
    
    return x, y  

def add_features(dmap, archetype_key):
    """Add decorative features based on archetype"""
    archetype = ARCHETYPES[archetype_key]
    h, w = len(dmap), len(dmap[0])
    
    
    for y in range(2, h-2):
        for x in range(2, w-2):
            if dmap[y][x] == 0:  
                
                if random.random() < 0.03 and 3 in archetype['decor']:
                    dmap[y][x] = 3
                
                elif random.random() < 0.02 and 2 in archetype['decor']:
                    dmap[y][x] = 2
                
                elif random.random() < 0.03 and 9 in archetype['decor']:
                    dmap[y][x] = 9
                
                elif has_nearby_walls(dmap, x, y) and random.random() < 0.6:
                    dmap[y][x] = 4

def has_nearby_walls(dmap, x, y):
    """Check if position has walls nearby"""
    wall_count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dmap[y+dy][x+dx] in [1, 8]: wall_count += 1
    return wall_count >= 3

def generate_boss_arena(width=30, height=22):
    """Generate a specialized arena for boss fights"""
    
    dungeon_map, _ = generate_dungeon(width, height, "BOSS_ARENA")
    
    
    center_x, center_y = width // 2, height // 2
    arena_radius = min(width, height) // 3
    
    
    for y in range(center_y - arena_radius, center_y + arena_radius):
        for x in range(center_x - arena_radius, center_x + arena_radius):
            if 0 < y < height-1 and 0 < x < width-1:
                dungeon_map[y][x] = 0  
    
    
    for corner_y in [center_y - arena_radius + 2, center_y + arena_radius - 2]:
        for corner_x in [center_x - arena_radius + 2, center_x + arena_radius - 2]:
            if 0 < corner_y < height-1 and 0 < corner_x < width-1:
                structure_size = random.randint(2, 3)
                
                for sy in range(corner_y - structure_size, corner_y + structure_size):
                    for sx in range(corner_x - structure_size, corner_x + structure_size):
                        if (0 < sy < height-1 and 0 < sx < width-1 and 
                            random.random() < 0.6 and
                            abs(sy - corner_y) + abs(sx - corner_x) <= structure_size):
                            dungeon_map[sy][sx] = 8  
    
    
    entrance_x = width // 2
    entrance_y = height - 2
    
    
    safe_radius = 3  
    for y in range(entrance_y - safe_radius, entrance_y + 1):  
        for x in range(entrance_x - safe_radius, entrance_x + safe_radius + 1):
            if 0 < y < height-1 and 0 < x < width-1:
                dungeon_map[y][x] = 0  
    
    
    for x in range(width):
        dungeon_map[0][x] = dungeon_map[height-1][x] = 8
    for y in range(height):
        dungeon_map[y][0] = dungeon_map[y][width-1] = 8
    
    
    dungeon_map[entrance_y][entrance_x] = 0
    
    return dungeon_map, center_x, center_y, entrance_x, entrance_y
