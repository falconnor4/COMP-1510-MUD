import math

def distance(x1, y1, x2, y2):
    """Calculate the distance between two points"""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)
