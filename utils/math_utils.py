import math
from utils.collision import is_collision


def distance(x1, y1, x2, y2):
    """
    Calculate the Euclidean distance between two points (x1, y1) and (x2, y2).

    :param x1: float, x-coordinate of the first point.
    :param y1: float, y-coordinate of the first point.
    :param x2: float, x-coordinate of the second point.
    :param y2: float, y-coordinate of the second point.
    :precondition: x1, y1, x2, y2 must be numbers.
    :postcondition: Calculates the correct Euclidean distance.
    :return: float, the distance between the two points.
    >>> distance(0, 0, 3, 4)
    5.0
    >>> distance(1, 1, 1, 1)
    0.0
    >>> distance(-1, -1, 1, 1)
    2.8284271247461903
    """
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def distance_between(entity1, entity2):
    """
    Calculate the distance between two entities based on their 'x' and 'y' coordinates.

    Entities are expected to be dictionaries with 'x' and 'y' keys.

    :param entity1: dict, the first entity dictionary containing 'x' and 'y'.
    :param entity2: dict, the second entity dictionary containing 'x' and 'y'.
    :precondition: entity1 and entity2 must be dictionaries with numeric 'x' and 'y' keys.
    :postcondition: Calculates the correct distance between the entity centers.
    :return: float, the distance between the two entities.
    >>> e1 = {'x': 0, 'y': 0}
    >>> e2 = {'x': 3, 'y': 4}
    >>> distance_between(e1, e2)
    5.0
    >>> e3 = {'x': -1, 'y': 2}
    >>> e4 = {'x': 2, 'y': -2}
    >>> distance_between(e3, e4)
    5.0
    """
    return distance(entity1["x"], entity1["y"], entity2["x"], entity2["y"])


def has_line_of_sight(x1, y1, x2, y2, world_map):
    """
    Check if there is an unobstructed straight line between two points on the map.

    Uses a stepping algorithm to check for collisions along the line segment.

    :param x1: float, x-coordinate of the starting point.
    :param y1: float, y-coordinate of the starting point.
    :param x2: float, x-coordinate of the ending point.
    :param y2: float, y-coordinate of the ending point.
    :param world_map: list[list[int]], the map grid used for collision checks.
    :precondition: x1, y1, x2, y2 must be valid coordinates.
    :precondition: world_map must be a valid map structure where `is_collision` can operate.
    :postcondition: Determines if the line segment is clear of obstacles.
    :return: bool, True if line of sight is clear, False otherwise.
    """
    dist = distance(x1, y1, x2, y2)
    if dist == 0:
        return True  # Points are the same

    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist

    # Determine number of steps based on distance (e.g., 5 steps per unit)
    steps = max(1, int(dist * 5))
    step_size = dist / steps  # Calculate actual size of each step along the line

    # Check intermediate points along the line segment
    for i in range(1, steps):  # Start from 1 to avoid checking the start point itself
        check_x = x1 + dx * i * step_size
        check_y = y1 + dy * i * step_size

        if is_collision(check_x, check_y, world_map):
            return False  # Obstacle found

    return True  # No obstacles found
