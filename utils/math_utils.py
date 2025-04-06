import math
from utils.collision import is_collision

def distance(x1, y1, x2, y2):
    """Calculate the distance between two points"""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)

def distance_between(entity1, entity2):
    """Calculate the distance between two entities using their coordinates."""
    return distance(entity1["x"], entity1["y"], entity2["x"], entity2["y"])

def has_line_of_sight(x1, y1, x2, y2, world_map):
    """Check if there's a clear line of sight between two points using Bresenham-like stepping."""
    dist = distance(x1, y1, x2, y2)
    if dist == 0:
        return True

    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist

    steps = max(1, int(dist * 5))
    step_size = dist / steps

    for i in range(1, steps):
        check_x = x1 + dx * i * step_size
        check_y = y1 + dy * i * step_size

        if is_collision(check_x, check_y, world_map):
            return False

    return True
