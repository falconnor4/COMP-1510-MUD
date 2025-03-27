import random

from map.static_map import LEGEND

# Based on the following: https://roguebasin.com/index.php/Basic_BSP_Dungeon_generation

def generate_dungeon(width, height, min_room_size, max_splits):
    class Node: # Yes this has to be swapped from OOP to functional, I will do that later
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.left = None
            self.right = None
            self.room = None

        def get_room(self):
            if self.room:
                return self.room
            else:
                return None

    def split_node(node):
        if node.width > node.height:
            split_horizontally = False
        elif node.height > node.width:
            split_horizontally = True
        else:
             split_horizontally = random.random() < 0.5

        if split_horizontally:
            # Horizontal split
            max_y = node.height - min_room_size
            if max_y <= min_room_size:
                return False  # Cannot split

            split_y = random.randint(min_room_size, max_y)

            node.left = Node(node.x, node.y, node.width, split_y)
            node.right = Node(node.x, node.y + split_y, node.width, node.height - split_y)
        else:
            # Vertical split
            max_x = node.width - min_room_size
            if max_x <= min_room_size:
                return False  # Cannot split

            split_x = random.randint(min_room_size, max_x)

            node.left = Node(node.x, node.y, split_x, node.height)
            node.right = Node(node.x + split_x, node.y, node.width - split_x, node.height)

        return True

    def create_rooms(node, min_room_size):
        """Creates a room within a node, ensuring minimum size."""
        if node.left or node.right:
            # Not a leaf node
            return

        room_x = random.randint(node.x, node.x + max(0, node.width - min_room_size))
        room_y = random.randint(node.y, node.y + max(0, node.height - min_room_size))
        room_width = random.randint(min_room_size, node.x + node.width - room_x)
        room_height = random.randint(min_room_size, node.y + node.height - room_y)

        node.room = (room_x, room_y, room_width, room_height)

    def create_corridors(node, dungeon_map):
        """Connect leaf nodes with corridors."""
        if node is None or node.left is None or node.right is None:
            return

        # Recursively create corridors in sub-nodes
        create_corridors(node.left, dungeon_map)
        create_corridors(node.right, dungeon_map)

        # Connect the two child nodes
        room1 = node.left.get_room()
        room2 = node.right.get_room()

        if room1 and room2:
            connect_rooms(room1, room2, dungeon_map)

    def connect_rooms(room1, room2, dungeon_map):
        """Connect two rooms with either a straight or Z-shaped corridor."""
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2

        # Find center points of the rooms
        center1_x, center1_y = x1 + w1 // 2, y1 + h1 // 2
        center2_x, center2_y = x2 + w2 // 2, y2 + h2 // 2

        # Try straight corridor (horizontal then vertical)
        if x1 < x2 and x1 + w1 > x2 and y2 < y1 + h1 and y2 > y1:
            # Rooms are horizontally aligned
            for x in range(min(center1_x, center2_x), max(center1_x, center2_x) + 1):
                dungeon_map[center1_y][x] = 0  # EMPTY
            return

        if y1 < y2 and y1 + h1 > y2 and x2 < x1 + w1 and x2 > x1:
            # Rooms are vertically aligned
            for y in range(min(center1_y, center2_y), max(center1_y, center2_y) + 1):
                dungeon_map[y][center1_x] = 0  # EMPTY
            return

        # Z-shaped corridor
        # Connect horizontally, then vertically
        for x in range(min(center1_x, center2_x), max(center1_x, center2_x) + 1):
            dungeon_map[center1_y][x] = 0  # EMPTY

        for y in range(min(center1_y, center2_y), max(center1_y, center2_y) + 1):
            dungeon_map[y][center2_x] = 0  # EMPTY

    # 1. Initialize the dungeon with walls
    dungeon_map = [[1 for _ in range(width)] for _ in range(height)]  # 1 = WALL

    # 2. Create the root node
    root = Node(0, 0, width, height)

    # 3. Split the nodes recursively
    nodes = [root]
    splits = 0
    while splits < max_splits:
        new_nodes = []
        for node in nodes:
            if split_node(node):
                new_nodes.append(node.left)
                new_nodes.append(node.right)
        if not new_nodes:
            break  # No more splits possible
        nodes = new_nodes
        splits += 1

    # 4. Create rooms in leaf nodes
    for node in nodes:
        create_rooms(node, min_room_size)

    # 5. Create corridors
    create_corridors(root, dungeon_map)

    # 6. Carve out rooms in the dungeon map
    for node in nodes:
        if node.room:
            x, y, w, h = node.room
            for i in range(y, y + h):
                for j in range(x, x + w):
                    dungeon_map[i][j] = 0  # 0 = EMPTY

    return dungeon_map
