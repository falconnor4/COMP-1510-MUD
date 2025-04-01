"""Utility functions for collision detection"""

def is_collision(x, y, world_map):
    """Check if a position collides with a wall"""
    grid_x, grid_y = int(x), int(y)

    if grid_y < 0 or grid_y >= len(world_map) or grid_x < 0 or grid_x >= len(world_map[0]):
        return True

    walkable_types = [0, 4, 9]  # EMPTY, PATH, SAND
    return world_map[grid_y][grid_x] not in walkable_types


def would_collide(x, y, new_x, new_y, world_map):
    """Advanced collision check with buffer zone"""
    if is_collision(new_x, new_y, world_map):
        return True

    steps = 3
    for i in range(1, steps):
        check_x = x + (new_x - x) * i / steps
        check_y = y + (new_y - y) * i / steps

        if is_collision(check_x, check_y, world_map):
            return True

    return False
