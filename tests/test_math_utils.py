from unittest import TestCase
from utils.math_utils import distance, distance_between, has_line_of_sight


class TestMathUtils(TestCase):
    def test_distance_between(self):
        entity1 = {"x": 0, "y": 0}
        entity2 = {"x": 3, "y": 4}
        self.assertEqual(5.0, distance_between(entity1, entity2))

        entity3 = {"x": 10, "y": 20}
        entity4 = {"x": 10, "y": 20}
        self.assertEqual(0.0, distance_between(entity3, entity4))

        entity5 = {"x": -1, "y": -1}
        entity6 = {"x": 1, "y": 1}
        self.assertAlmostEqual(2.8284, distance_between(entity5, entity6), places=4)

        entity7 = {"x": -1, "y": 2}
        entity8 = {"x": 2, "y": -2}
        self.assertEqual(5.0, distance_between(entity7, entity8))

    def test_has_line_of_sight_clear_path(self):
        clear_map = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        self.assertTrue(has_line_of_sight(1, 1, 4, 1, clear_map))

        self.assertTrue(has_line_of_sight(1, 1, 1, 4, clear_map))

        self.assertTrue(has_line_of_sight(1, 1, 4, 4, clear_map))

        self.assertTrue(has_line_of_sight(2, 2, 2, 2, clear_map))

    def test_has_line_of_sight_with_obstacles(self):
        obstacle_map = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        self.assertFalse(has_line_of_sight(1, 1, 4, 4, obstacle_map))

        self.assertTrue(has_line_of_sight(0, 0, 1, 1, obstacle_map))

        self.assertTrue(has_line_of_sight(3, 0, 3, 4, obstacle_map))

        complex_map = [
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        self.assertFalse(has_line_of_sight(0, 0, 4, 0, complex_map))

        self.assertTrue(has_line_of_sight(0, 2, 4, 2, complex_map))
