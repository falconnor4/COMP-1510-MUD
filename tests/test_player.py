from unittest import TestCase
import math
import curses
import time
from unittest.mock import patch

from player import (
    create_player,
    update_input,
    check_key_timeout,
    update_player,
    update_head_bob,
)


class TestPlayer(TestCase):
    def test_create_player_default_values(self):
        player = create_player()

        self.assertEqual(1.5, player["x"])
        self.assertEqual(1.5, player["y"])
        self.assertEqual(0.0, player["angle"])
        self.assertEqual(0.0, player["velocity_x"])
        self.assertEqual(0.0, player["velocity_y"])
        self.assertEqual(0.0, player["velocity_angle"])
        self.assertEqual(3.0, player["max_speed"])
        self.assertEqual(8.0, player["acceleration"])
        self.assertEqual(4.0, player["friction"])
        self.assertEqual(100, player["health"])
        self.assertEqual(100, player["max_health"])
        self.assertEqual(1, player["level"])
        self.assertEqual(0, player["exp"])
        self.assertEqual(100, player["exp_to_next"])

    def test_create_player_custom_values(self):
        player = create_player(x=5.0, y=10.0, angle=math.pi)

        self.assertEqual(5.0, player["x"])
        self.assertEqual(10.0, player["y"])
        self.assertEqual(math.pi, player["angle"])

        self.assertEqual(0.0, player["velocity_x"])
        self.assertEqual(3.0, player["base_speed"])
        self.assertEqual(0, player["stages_descended"])

    @patch("player.DEBUG_CONSOLE", {"active": False})
    def test_update_input_normal_key_press(self):
        player_state = {"active_keys": set(), "key_timestamps": {}, "map_mode": False}
        key = ord("w")

        result = update_input(player_state, key, pressed=True)

        self.assertIn(key, player_state["active_keys"])
        self.assertIn(key, player_state["key_timestamps"])
        self.assertFalse(result)

    @patch("player.DEBUG_CONSOLE", {"active": False})
    def test_update_input_quit_key(self):
        player_state = {"active_keys": set(), "key_timestamps": {}, "map_mode": False}
        key = ord("q")

        result = update_input(player_state, key, pressed=True)

        self.assertIn(key, player_state["active_keys"])
        self.assertTrue(result)

    @patch("player.DEBUG_CONSOLE", {"active": False})
    def test_update_input_map_toggle(self):
        player_state = {"active_keys": set(), "key_timestamps": {}, "map_mode": False}
        key = ord("m")

        update_input(player_state, key, pressed=True)

        self.assertTrue(player_state["map_mode"])

        update_input(player_state, key, pressed=True)

        self.assertFalse(player_state["map_mode"])

    @patch("player.DEBUG_CONSOLE", {"active": False})
    def test_update_input_key_release(self):
        player_state = {
            "active_keys": {ord("w")},
            "key_timestamps": {ord("w"): time.time()},
            "map_mode": False,
        }
        key = ord("w")

        update_input(player_state, key, pressed=False)

        self.assertNotIn(key, player_state["active_keys"])
        self.assertNotIn(key, player_state["key_timestamps"])

    @patch("player.toggle_console")
    @patch("player.DEBUG_CONSOLE", {"active": False})
    def test_update_input_toggle_console(self, mock_toggle_console):
        player_state = {"active_keys": set(), "key_timestamps": {}, "map_mode": False}
        key = ord(";")

        result = update_input(player_state, key, pressed=True)

        mock_toggle_console.assert_called_once()
        self.assertFalse(result)

    @patch("player.process_input")
    @patch("player.DEBUG_CONSOLE", {"active": True})
    def test_update_input_with_console_active(self, mock_process_input):
        player_state = {"active_keys": set(), "key_timestamps": {}, "map_mode": False}
        key = ord("w")

        result = update_input(player_state, key, pressed=True)

        mock_process_input.assert_called_once_with(key, player_state)
        self.assertFalse(result)

    def test_check_key_timeout_no_timeout(self):
        current_time = 100.0
        player_state = {
            "active_keys": {ord("w"), ord("a")},
            "key_timestamps": {
                ord("w"): current_time - 0.3,
                ord("a"): current_time - 0.2,
            },
        }

        check_key_timeout(player_state, current_time, timeout=0.5)

        self.assertEqual(2, len(player_state["active_keys"]))
        self.assertEqual(2, len(player_state["key_timestamps"]))

    def test_check_key_timeout_with_timeout(self):
        current_time = 100.0
        player_state = {
            "active_keys": {ord("w"), ord("a")},
            "key_timestamps": {
                ord("w"): current_time - 0.6,
                ord("a"): current_time - 0.2,
            },
        }

        check_key_timeout(player_state, current_time, timeout=0.5)

        self.assertEqual(1, len(player_state["active_keys"]))
        self.assertEqual(1, len(player_state["key_timestamps"]))
        self.assertNotIn(ord("w"), player_state["active_keys"])
        self.assertNotIn(ord("w"), player_state["key_timestamps"])
        self.assertIn(ord("a"), player_state["active_keys"])

    @patch("player.check_key_timeout")
    @patch("player.would_collide", return_value=False)
    def test_update_player_no_movement(self, mock_would_collide, mock_check_timeout):
        player_state = create_player()
        player_state["active_keys"] = set()
        world_map = [[0, 0], [0, 0]]

        shoot, interact = update_player(player_state, 0.016, world_map)

        self.assertEqual(1.5, player_state["x"])
        self.assertEqual(1.5, player_state["y"])
        self.assertEqual(0.0, player_state["angle"])
        self.assertFalse(player_state["is_moving"])
        self.assertFalse(shoot)
        self.assertFalse(interact)

    @patch("player.check_key_timeout")
    @patch("player.would_collide", return_value=False)
    def test_update_player_forward_movement(
        self, mock_would_collide, mock_check_timeout
    ):
        player_state = create_player()
        player_state["active_keys"] = {ord("w")}
        player_state["angle"] = 0.0
        world_map = [[0, 0], [0, 0]]

        update_player(player_state, 0.1, world_map)

        self.assertGreater(player_state["x"], 1.5)
        self.assertEqual(1.5, player_state["y"])
        self.assertTrue(player_state["is_moving"])

    @patch("player.check_key_timeout")
    @patch("player.would_collide", return_value=False)
    def test_update_player_rotation(self, mock_would_collide, mock_check_timeout):
        player_state = create_player()
        player_state["active_keys"] = {curses.KEY_RIGHT}
        world_map = [[0, 0], [0, 0]]

        update_player(player_state, 0.1, world_map)

        self.assertGreater(player_state["angle"], 0.0)

    @patch("player.check_key_timeout")
    @patch("player.would_collide", return_value=True)
    def test_update_player_collision(self, mock_would_collide, mock_check_timeout):
        player_state = create_player()
        player_state["active_keys"] = {ord("w")}
        player_state["velocity_x"] = 1.0
        player_state["velocity_y"] = 1.0
        world_map = [[0, 0], [0, 0]]

        update_player(player_state, 0.1, world_map)

        self.assertEqual(1.5, player_state["x"])
        self.assertEqual(1.5, player_state["y"])

        self.assertLess(abs(player_state["velocity_x"]), 1.0)
        self.assertLess(abs(player_state["velocity_y"]), 1.0)

    @patch("player.check_key_timeout")
    @patch("player.would_collide")
    def test_update_player_shoot_interact(self, mock_would_collide, mock_check_timeout):
        mock_would_collide.return_value = False
        player_state = create_player()
        player_state["active_keys"] = {ord(" "), ord("e")}
        world_map = [[0, 0], [0, 0]]

        shoot, interact = update_player(player_state, 0.016, world_map)

        self.assertTrue(shoot)
        self.assertTrue(interact)

        self.assertNotIn(ord(" "), player_state["active_keys"])
        self.assertNotIn(ord("e"), player_state["active_keys"])

    def test_update_head_bob_when_moving(self):
        player_state = {
            "is_moving": True,
            "bob_phase": 0.0,
            "bob_frequency": 7.0,
            "max_speed": 3.0,
            "bob_amplitude": 0.1,
            "bob_offset": 0.0,
        }

        initial_offset = player_state["bob_offset"]

        update_head_bob(player_state, 0.1, 2.0)

        self.assertNotEqual(0.0, player_state["bob_phase"])
        self.assertNotEqual(initial_offset, player_state["bob_offset"])

    def test_update_head_bob_when_stationary(self):
        player_state = {
            "is_moving": False,
            "bob_phase": 0.5,
            "bob_frequency": 7.0,
            "max_speed": 3.0,
            "bob_amplitude": 0.1,
            "bob_offset": 0.05,
        }

        update_head_bob(player_state, 0.1, 0.0)

        self.assertLess(abs(player_state["bob_offset"]), 0.05)

        for _ in range(10):
            update_head_bob(player_state, 0.1, 0.0)

        self.assertAlmostEqual(0.0, player_state["bob_offset"], places=4)
        self.assertEqual(0.0, player_state["bob_phase"])
