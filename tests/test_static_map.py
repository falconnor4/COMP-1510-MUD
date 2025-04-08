import unittest
from unittest.mock import patch, MagicMock
import math
from map.static_map import (
    LEGEND,
    TERRAIN_CHARS,
    WORLD_MAP,
    ACTIVE_MAP,
    CURRENT_MAP_TYPE,
    CURRENT_COLOR_SHIFT,
    generate_color_map,
    find_tile_position,
    find_door_position,
    is_valid_boss_door_location,
    find_nearby_empty_space,
    is_spawn_valid,
    find_valid_spawn,
    interact_raycast,
    generate_char_map,
    is_walkable,
    get_map_str,
    get_terrain_at,
)


class TestStaticMap(unittest.TestCase):
    def setUp(self):
        self.test_map = [
            [1, 1, 1, 1, 1],
            [1, 0, 4, 6, 1],
            [1, 4, 0, 0, 1],
            [1, 7, 9, 0, 1],
            [1, 1, 1, 1, 1],
        ]

    def test_generate_color_map(self):
        color_map = generate_color_map(self.test_map, 0)
        self.assertEqual(len(self.test_map), len(color_map))
        self.assertEqual(len(self.test_map[0]), len(color_map[0]))

        wall_terrain_id = 1
        wall_color = str(LEGEND[wall_terrain_id])
        self.assertEqual(str(7), color_map[0][0])

        color_map_shifted = generate_color_map(self.test_map, 1)
        self.assertEqual(str(3), color_map_shifted[0][0])

    def test_find_tile_position(self):
        door_x, door_y = find_tile_position(self.test_map, 6)
        self.assertEqual(3, door_x)
        self.assertEqual(1, door_y)

        stairs_x, stairs_y = find_tile_position(self.test_map, 7)
        self.assertEqual(1, stairs_x)
        self.assertEqual(3, stairs_y)

        nonexistent_x, nonexistent_y = find_tile_position(self.test_map, 99)
        self.assertIsNone(nonexistent_x)
        self.assertIsNone(nonexistent_y)

    def test_find_door_position(self):
        door_x, door_y = find_door_position(self.test_map)
        self.assertEqual(3, door_x)
        self.assertEqual(1, door_y)

        map_without_door = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
        no_door_x, no_door_y = find_door_position(map_without_door)
        self.assertIsNone(no_door_x)
        self.assertIsNone(no_door_y)

    def test_is_valid_boss_door_location(self):
        self.assertTrue(is_valid_boss_door_location(self.test_map, 2, 2))

        self.assertFalse(is_valid_boss_door_location(self.test_map, 0, 0))
        self.assertFalse(is_valid_boss_door_location(self.test_map, 2, 1))
        self.assertFalse(is_valid_boss_door_location(self.test_map, -1, 2))
        self.assertFalse(is_valid_boss_door_location(self.test_map, 2, 5))
        self.assertFalse(is_valid_boss_door_location(self.test_map, 1, 4))

    def test_is_spawn_valid(self):
        self.assertTrue(is_spawn_valid(1.5, 1.5, self.test_map))
        self.assertTrue(is_spawn_valid(2.5, 1.5, self.test_map))
        self.assertTrue(is_spawn_valid(2.5, 3.5, self.test_map))

        self.assertFalse(is_spawn_valid(0.5, 0.5, self.test_map))
        self.assertFalse(is_spawn_valid(1.5, 3.5, self.test_map))

        self.assertFalse(is_spawn_valid(-1.0, 2.0, self.test_map))
        self.assertFalse(is_spawn_valid(10.0, 2.0, self.test_map))

    @patch("map.static_map.is_spawn_valid")
    def test_find_valid_spawn(self, mock_is_spawn_valid):
        test_map = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ]

        mock_is_spawn_valid.side_effect = lambda x, y, m: x == 2 and y == 2
        spawn_x, spawn_y = find_valid_spawn(test_map)
        self.assertEqual(2, spawn_x)
        self.assertEqual(2, spawn_y)

        mock_is_spawn_valid.side_effect = lambda x, y, m: x == 1 and y == 3
        spawn_x, spawn_y = find_valid_spawn(test_map)
        self.assertEqual(1, spawn_x)
        self.assertEqual(3, spawn_y)

        mock_is_spawn_valid.return_value = False
        test_map_copy = [row[:] for row in test_map]
        spawn_x, spawn_y = find_valid_spawn(test_map_copy)
        self.assertEqual(1, spawn_x)
        self.assertEqual(3, spawn_y)
        self.assertEqual(0, test_map_copy[2][2])

    def test_interact_raycast(self):
        result = interact_raycast(
            2.0, 1.5, 0.0, self.test_map
        )
        self.assertEqual("door", result[0])
        self.assertEqual(3, result[1])
        self.assertEqual(1, result[2])

        result = interact_raycast(
            2.0, 2.5, math.pi / 2, self.test_map
        )
        self.assertEqual("wall", result[0])
        self.assertEqual(2, result[1])
        self.assertEqual(4, result[2])

        result = interact_raycast(
            1.0, 1.5, math.pi, self.test_map
        )
        self.assertEqual("wall", result[0])
        self.assertEqual(0, result[1])
        self.assertEqual(1, result[2])

    @patch("map.static_map.ACTIVE_MAP")
    def test_is_walkable(self, mock_active_map):
        mock_active_map.__getitem__.side_effect = lambda y: self.test_map[y]

        self.assertFalse(is_walkable(0, 0))
        self.assertFalse(is_walkable(3, 1))
        self.assertFalse(is_walkable(1, 3))

        self.assertFalse(is_walkable(-1, 0))
        self.assertFalse(is_walkable(0, -1))
        self.assertFalse(is_walkable(100, 0))
        self.assertFalse(is_walkable(0, 100))

    @patch("map.static_map.ACTIVE_MAP")
    @patch("map.static_map.generate_char_map")
    def test_get_map_str(self, mock_generate_char_map, mock_active_map):
        char_map = [["#", "#", "#"], ["#", " ", "#"], ["#", "#", "#"]]
        mock_generate_char_map.return_value = char_map

        map_str = get_map_str(1.5, 1.5)
        expected = "###\n#@#\n###"
        self.assertEqual(expected, map_str)

        map_str = get_map_str(0.5, 0.5)
        expected = "@##\n# #\n###"
        self.assertEqual(expected, map_str)

    @patch("map.static_map.ACTIVE_MAP")
    def test_get_terrain_at(self, mock_active_map):
        mock_active_map.__getitem__.side_effect = lambda y: self.test_map[y]
        mock_active_map.__len__.return_value = len(self.test_map)

        self.assertEqual("WALL", get_terrain_at(0.5, 0.5))
        self.assertEqual("EMPTY", get_terrain_at(1.5, 1.5))
        self.assertEqual("PATH", get_terrain_at(2.5, 1.5))
        self.assertEqual("DOOR", get_terrain_at(3.5, 1.5))
        self.assertEqual("STAIRS", get_terrain_at(1.5, 3.5))

        self.assertEqual("WALL", get_terrain_at(-1.0, 0.0))
        self.assertEqual("WALL", get_terrain_at(0.0, -1.0))
        self.assertEqual("WALL", get_terrain_at(100.0, 0.0))
        self.assertEqual("WALL", get_terrain_at(0.0, 100.0))


if __name__ == "__main__":
    unittest.main()
