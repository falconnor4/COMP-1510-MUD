from unittest import TestCase
from unittest.mock import patch
from map.dungeon_generator import (
    generate_dungeon,
    is_valid_spawn,
    is_open_area,
    has_nearby_walls,
)


class TestDungeonGenerator(TestCase):
    @patch("map.dungeon_generator.random.choice")
    @patch("map.dungeon_generator.random.randint")
    def test_generate_dungeon(self, mock_randint, mock_choice):
        mock_randint.return_value = 5
        mock_choice.return_value = "CAVE"
        width, height = 20, 15
        dungeon_map, archetype_key = generate_dungeon(width, height, "CAVE")
        self.assertEqual(len(dungeon_map), height)
        self.assertEqual(len(dungeon_map[0]), width)
        self.assertEqual(archetype_key, "CAVE")

        mock_choice.return_value = "RUINS"
        dungeon_map, archetype_key = generate_dungeon(width, height)
        self.assertEqual(archetype_key, "RUINS")

    def test_is_valid_spawn(self):
        dungeon_map = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
        self.assertTrue(is_valid_spawn(dungeon_map, 1, 1))
        self.assertFalse(is_valid_spawn(dungeon_map, 0, 0))
        self.assertFalse(is_valid_spawn(dungeon_map, 5, 5))

    def test_is_open_area(self):
        dungeon_map = [[1 for _ in range(5)] for _ in range(5)]
        for idx in range(1, 4):
            dungeon_map[2][idx] = 0
        self.assertFalse(is_open_area(dungeon_map, 2, 2, 1))
        for row_idx in range(1, 4):
            for col_idx in range(1, 4):
                dungeon_map[row_idx][col_idx] = 0
        self.assertTrue(is_open_area(dungeon_map, 2, 2, 1))

    def test_has_nearby_walls(self):
        dungeon_map = [[0 for _ in range(5)] for _ in range(5)]
        for idx in range(5):
            dungeon_map[0][idx] = dungeon_map[4][idx] = 1
        for idx in range(5):
            dungeon_map[idx][0] = dungeon_map[idx][4] = 1
        self.assertTrue(has_nearby_walls(dungeon_map, 1, 1))
        self.assertFalse(has_nearby_walls(dungeon_map, 2, 2))
