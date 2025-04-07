import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
import curses

import debug


class TestDebugModule(TestCase):

    def setUp(self):
        """Reset DEBUG_CONSOLE state before each test."""
        debug.DEBUG_CONSOLE = {
            "active": False,
            "command": "",
            "history": [],
            "history_index": -1,
            "max_history": 5,
            "cursor_pos": 0,
            "last_result": None,
            "initialized": False,
        }
        debug.COMMANDS = {
            "next": {"help": "...", "callback": None},
            "help": {"help": "...", "callback": lambda cmd=None: debug.show_help(cmd)},
            "clear": {"help": "...", "callback": lambda: debug.clear_history()},
            "level": {
                "help": "...",
                "callback": None,
            },
            "boss": {
                "help": "...",
                "callback": None,
            },
            "test_cmd": {
                "help": "Test command",
                "callback": MagicMock(return_value="Test OK"),
            },
            "test_args": {
                "help": "Test args",
                "callback": MagicMock(return_value="Args OK"),
            },
            "test_error": {
                "help": "Test error",
                "callback": MagicMock(side_effect=TypeError("Bad args")),
            },
        }
        debug.initialize_commands(player_state={}, change_level_callback=MagicMock())

    def test_toggle_console_activate(self):
        """Test activating the console."""
        debug.DEBUG_CONSOLE["active"] = False
        debug.DEBUG_CONSOLE["command"] = "some text"
        debug.DEBUG_CONSOLE["cursor_pos"] = 4
        debug.toggle_console()
        self.assertTrue(debug.DEBUG_CONSOLE["active"])
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 0)

    def test_toggle_console_deactivate(self):
        """Test deactivating the console."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "some text"
        debug.DEBUG_CONSOLE["cursor_pos"] = 4
        debug.toggle_console()
        self.assertFalse(debug.DEBUG_CONSOLE["active"])
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "some text")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 4)

    def test_clear_history(self):
        """Test clearing the command history."""
        debug.DEBUG_CONSOLE["history"] = ["cmd1", "cmd2"]
        debug.DEBUG_CONSOLE["history_index"] = 1
        result = debug.clear_history()
        self.assertEqual(debug.DEBUG_CONSOLE["history"], [])
        self.assertEqual(debug.DEBUG_CONSOLE["history_index"], -1)
        self.assertEqual(result, "History cleared")

    def test_show_help_all(self):
        """Test showing help for all commands."""
        result = debug.show_help()
        self.assertIn("Available commands:", result)
        self.assertIn("help", result)
        self.assertIn("clear", result)
        self.assertIn("test_cmd", result)

    def test_show_help_specific(self):
        """Test showing help for a specific command."""
        result = debug.show_help("test_cmd")
        self.assertEqual(result, "test_cmd: Test command")

    def test_show_help_unknown(self):
        """Test showing help for an unknown command."""
        result = debug.show_help("unknown_cmd")
        self.assertEqual(result, "Unknown command: unknown_cmd")

    def test_set_player_level_invalid_string(self):
        """Test setting player level with invalid input."""
        player_state = {"level": 1}
        result = debug.set_player_level(player_state, "abc")
        self.assertEqual(result, "Invalid level. Please provide a number.")
        self.assertEqual(player_state["level"], 1)

    def test_set_player_level_get_current(self):
        """Test getting the current level."""
        player_state = {"level": 3}
        result = debug.set_player_level(player_state)
        self.assertEqual(result, "Current level: 3. Use 'level <number>' to change it.")

    def test_set_player_level_no_state(self):
        """Test setting level when player_state is None."""
        result = debug.set_player_level(None, "5")
        self.assertEqual(result, "Player state not available")

    def test_set_player_level_below_one(self):
        """Test setting level below 1."""
        player_state = {"level": 5}
        result = debug.set_player_level(player_state, "0")
        self.assertEqual(result, "Level must be at least 1")
        self.assertEqual(player_state["level"], 5)

    def test_teleport_to_boss_no_state(self):
        """Test teleporting to boss when player_state is None."""
        result = debug.teleport_to_boss(None)
        self.assertEqual(result, "Player state not available")

    def test_execute_command_valid_no_args(self):
        """Test executing a valid command without arguments."""
        debug.execute_command("test_cmd")
        debug.COMMANDS["test_cmd"]["callback"].assert_called_once_with()
        self.assertEqual(debug.DEBUG_CONSOLE["last_result"], "Test OK")
        self.assertIn("test_cmd", debug.DEBUG_CONSOLE["history"])
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 0)

    def test_execute_command_valid_with_args(self):
        """Test executing a valid command with arguments."""
        debug.execute_command("test_args arg1 arg2")
        debug.COMMANDS["test_args"]["callback"].assert_called_once_with("arg1", "arg2")
        self.assertEqual(debug.DEBUG_CONSOLE["last_result"], "Args OK")
        self.assertIn("test_args arg1 arg2", debug.DEBUG_CONSOLE["history"])

    def test_execute_command_unknown(self):
        """Test executing an unknown command."""
        debug.execute_command("unknown_command")
        self.assertEqual(
            debug.DEBUG_CONSOLE["last_result"], "Unknown command: unknown_command"
        )
        self.assertIn("unknown_command", debug.DEBUG_CONSOLE["history"])

    def test_execute_command_empty(self):
        """Test executing an empty command string."""
        debug.execute_command("   ")
        self.assertIsNone(debug.DEBUG_CONSOLE["last_result"])
        self.assertEqual(debug.DEBUG_CONSOLE["history"], [])

    def test_execute_command_history_management(self):
        """Test command history addition and trimming."""
        max_hist = debug.DEBUG_CONSOLE["max_history"]
        for i in range(max_hist + 2):
            cmd = f"cmd_{i}"
            debug.execute_command(cmd)

        self.assertEqual(len(debug.DEBUG_CONSOLE["history"]), max_hist)
        self.assertEqual(debug.DEBUG_CONSOLE["history"][0], f"cmd_{max_hist + 1}")
        self.assertEqual(debug.DEBUG_CONSOLE["history"][-1], f"cmd_2")

        debug.execute_command("cmd_new")
        debug.execute_command("cmd_new")
        self.assertEqual(debug.DEBUG_CONSOLE["history"].count("cmd_new"), 1)
        self.assertEqual(debug.DEBUG_CONSOLE["history"][0], "cmd_new")

    def test_execute_command_callback_error(self):
        """Test error handling when a command callback raises an exception."""
        debug.execute_command("test_error arg")
        debug.COMMANDS["test_error"]["callback"].assert_called_once_with("arg")
        self.assertIn(
            "Error: Incorrect arguments for 'test_error'",
            debug.DEBUG_CONSOLE["last_result"],
        )
        self.assertIn("Usage: Test error", debug.DEBUG_CONSOLE["last_result"])
        self.assertIn("Details: Bad args", debug.DEBUG_CONSOLE["last_result"])
        self.assertIn("test_error arg", debug.DEBUG_CONSOLE["history"])

    def test_process_input_inactive(self):
        """Test process_input does nothing when console is inactive."""
        debug.DEBUG_CONSOLE["active"] = False
        result = debug.process_input(ord("a"))
        self.assertFalse(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "")

    def test_process_input_character(self):
        """Test adding a character."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "tes"
        debug.DEBUG_CONSOLE["cursor_pos"] = 3
        result = debug.process_input(ord("t"))
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "test")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 4)

    def test_process_input_character_insert(self):
        """Test inserting a character."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "tst"
        debug.DEBUG_CONSOLE["cursor_pos"] = 1
        result = debug.process_input(ord("e"))
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "test")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 2)

    def test_process_input_backspace(self):
        """Test backspace key."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 4
        result = debug.process_input(curses.KEY_BACKSPACE)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "tes")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 3)

    def test_process_input_backspace_middle(self):
        """Test backspace key in the middle of the command."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 2
        result = debug.process_input(curses.KEY_BACKSPACE)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "tst")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 1)

    def test_process_input_backspace_start(self):
        """Test backspace key at the start."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 0
        result = debug.process_input(curses.KEY_BACKSPACE)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "test")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 0)

    def test_process_input_left_arrow(self):
        """Test left arrow key."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 3
        result = debug.process_input(curses.KEY_LEFT)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 2)

    def test_process_input_left_arrow_at_start(self):
        """Test left arrow key at the start."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 0
        result = debug.process_input(curses.KEY_LEFT)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 0)

    def test_process_input_right_arrow(self):
        """Test right arrow key."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 1
        result = debug.process_input(curses.KEY_RIGHT)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 2)

    def test_process_input_right_arrow_at_end(self):
        """Test right arrow key at the end."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "test"
        debug.DEBUG_CONSOLE["cursor_pos"] = 4
        result = debug.process_input(curses.KEY_RIGHT)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 4)

    def test_process_input_up_arrow_history(self):
        """Test up arrow key for history navigation."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["history"] = ["cmd2", "cmd1"]
        debug.DEBUG_CONSOLE["history_index"] = -1
        result = debug.process_input(curses.KEY_UP)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["history_index"], 0)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "cmd2")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 4)
        result = debug.process_input(curses.KEY_UP)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["history_index"], 1)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "cmd1")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 4)
        result = debug.process_input(curses.KEY_UP)
        self.assertTrue(result)
        self.assertEqual(debug.DEBUG_CONSOLE["history_index"], 1)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "cmd1")

    @patch("debug.execute_command")
    def test_process_input_enter(self, mock_execute):
        """Test Enter key triggers execute_command."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "run this"
        player_state = {"p": 1}
        world_map = [[0]]
        result = debug.process_input(curses.KEY_ENTER, player_state, world_map)
        self.assertTrue(result)
        mock_execute.assert_called_once_with("run this", player_state, world_map)

    @patch("debug.toggle_console")
    def test_process_input_escape(self, mock_toggle):
        """Test Escape key triggers toggle_console."""
        debug.DEBUG_CONSOLE["active"] = True
        result = debug.process_input(27)
        self.assertTrue(result)
        mock_toggle.assert_called_once()

    def test_process_input_unhandled_key(self):
        """Test processing an unhandled key."""
        debug.DEBUG_CONSOLE["active"] = True
        debug.DEBUG_CONSOLE["command"] = "cmd"
        debug.DEBUG_CONSOLE["cursor_pos"] = 3
        result = debug.process_input(curses.KEY_F1)
        self.assertFalse(result)
        self.assertEqual(debug.DEBUG_CONSOLE["command"], "cmd")
        self.assertEqual(debug.DEBUG_CONSOLE["cursor_pos"], 3)


if __name__ == "__main__":
    unittest.main()
