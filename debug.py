import curses

DEBUG_CONSOLE = {
    "active": False,
    "command": "",
    "history": [],
    "history_index": -1,
    "max_history": 20,
    "cursor_pos": 0,
    "last_result": None,
    "initialized": False,
}

COMMANDS = {
    "next": {
        "help": "Move to next level (simulates door interaction)",
        "callback": None,
    },
    "help": {
        "help": "Show available commands or details about a specific command (usage: help [command])",
        "callback": lambda cmd=None: show_help(cmd),
    },
    "clear": {"help": "Clear the console history", "callback": lambda: clear_history()},
    "level": {"help": "Set player level (usage: level <number>)", "callback": None},
    "boss": {"help": "Teleport directly to boss arena", "callback": None},
}


def toggle_console():
    """
    Toggle the visibility and active state of the debug console.

    Resets the command buffer and cursor position when activating.

    :precondition: DEBUG_CONSOLE dictionary must exist.
    :postcondition: Toggles DEBUG_CONSOLE['active'] boolean state.
    :postcondition: If activated, resets DEBUG_CONSOLE['command'] and DEBUG_CONSOLE['cursor_pos'].
    :return: None
    """
    DEBUG_CONSOLE["active"] = not DEBUG_CONSOLE["active"]
    if DEBUG_CONSOLE["active"]:
        DEBUG_CONSOLE["command"] = ""
        DEBUG_CONSOLE["cursor_pos"] = 0


def initialize_commands(player_state=None, change_level_callback=None):
    """
    Initialize command callbacks that require access to game state or external functions.

    Ensures initialization happens only once.

    :param player_state: dict | None, the player's state dictionary.
    :param change_level_callback: function | None, the callback function for the 'next' command.
    :precondition: COMMANDS and DEBUG_CONSOLE dictionaries must exist.
    :postcondition: Sets callbacks for 'next', 'level', and 'boss' commands if not already initialized.
    :postcondition: Sets DEBUG_CONSOLE['initialized'] to True.
    :return: None
    """
    if DEBUG_CONSOLE["initialized"]:
        return

    if change_level_callback:
        COMMANDS["next"]["callback"] = change_level_callback

    COMMANDS["level"]["callback"] = lambda level=None: set_player_level(
        player_state, level
    )
    COMMANDS["boss"]["callback"] = lambda: teleport_to_boss(player_state)

    DEBUG_CONSOLE["initialized"] = True


def process_input(key, player_state=None, world_map=None):
    """
    Process a single key input when the debug console is active.

    Handles character input, navigation (arrows, backspace), history (up/down),
    command execution (Enter), and closing the console (Esc).

    :param key: int, the key code received from curses.
    :param player_state: dict | None, the player's state dictionary (passed to command execution).
    :param world_map: list[list[int]] | None, the current world map (passed to command execution).
    :precondition: DEBUG_CONSOLE must exist. `initialize_commands` should be called beforehand if needed.
    :postcondition: Modifies DEBUG_CONSOLE['command'], DEBUG_CONSOLE['cursor_pos'], DEBUG_CONSOLE['history_index'].
    :postcondition: May call `execute_command` or `toggle_console`.
    :return: bool, True if the input was handled by the console, False otherwise (always True in current implementation when active).
    """
    if not DEBUG_CONSOLE["active"]:
        return False

    initialize_commands(player_state)

    command_executed = False
    input_handled = True

    if key == curses.KEY_ENTER or key == 10 or key == 13:
        execute_command(DEBUG_CONSOLE["command"], player_state, world_map)
        command_executed = True
    elif key == 27:
        toggle_console()
    elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
        if DEBUG_CONSOLE["cursor_pos"] > 0:
            command = DEBUG_CONSOLE["command"]
            pos = DEBUG_CONSOLE["cursor_pos"]
            DEBUG_CONSOLE["command"] = command[: pos - 1] + command[pos:]
            DEBUG_CONSOLE["cursor_pos"] -= 1
    elif key == curses.KEY_LEFT:
        if DEBUG_CONSOLE["cursor_pos"] > 0:
            DEBUG_CONSOLE["cursor_pos"] -= 1
    elif key == curses.KEY_RIGHT:
        if DEBUG_CONSOLE["cursor_pos"] < len(DEBUG_CONSOLE["command"]):
            DEBUG_CONSOLE["cursor_pos"] += 1
    elif key == curses.KEY_UP:
        if (
            DEBUG_CONSOLE["history"]
            and DEBUG_CONSOLE["history_index"] < len(DEBUG_CONSOLE["history"]) - 1
        ):
            DEBUG_CONSOLE["history_index"] += 1
            DEBUG_CONSOLE["command"] = DEBUG_CONSOLE["history"][
                DEBUG_CONSOLE["history_index"]
            ]
            DEBUG_CONSOLE["cursor_pos"] = len(DEBUG_CONSOLE["command"])
    elif key == curses.KEY_DOWN:
        if DEBUG_CONSOLE["history_index"] > 0:
            DEBUG_CONSOLE["history_index"] -= 1
            DEBUG_CONSOLE["command"] = DEBUG_CONSOLE["history"][
                DEBUG_CONSOLE["history_index"]
            ]
            DEBUG_CONSOLE["cursor_pos"] = len(DEBUG_CONSOLE["command"])
        elif DEBUG_CONSOLE["history_index"] == 0:
            DEBUG_CONSOLE["history_index"] = -1
            DEBUG_CONSOLE["command"] = ""
            DEBUG_CONSOLE["cursor_pos"] = 0
    elif 32 <= key <= 126:
        command = DEBUG_CONSOLE["command"]
        pos = DEBUG_CONSOLE["cursor_pos"]
        DEBUG_CONSOLE["command"] = command[:pos] + chr(key) + command[pos:]
        DEBUG_CONSOLE["cursor_pos"] += 1
    else:
        input_handled = False

    return input_handled or command_executed


def execute_command(command_str, player_state=None, world_map=None):
    """
    Parse and execute a debug command string.

    Adds the command to history, finds the corresponding callback, and executes it.
    Stores the result or error message in DEBUG_CONSOLE['last_result'].

    :param command_str: str, the raw command string entered by the user.
    :param player_state: dict | None, the player's state dictionary, passed to callbacks.
    :param world_map: list[list[int]] | None, the current world map, passed to callbacks.
    :precondition: COMMANDS and DEBUG_CONSOLE dictionaries must exist. Callbacks should be initialized.
    :postcondition: Adds command_str to DEBUG_CONSOLE['history'].
    :postcondition: Calls the appropriate command callback if found.
    :postcondition: Updates DEBUG_CONSOLE['last_result'] with the command's return value or an error message.
    :postcondition: Clears DEBUG_CONSOLE['command'] and resets DEBUG_CONSOLE['cursor_pos'].
    :return: None
    """
    command_str = command_str.strip()
    if not command_str:
        return

    if not DEBUG_CONSOLE["history"] or DEBUG_CONSOLE["history"][0] != command_str:
        DEBUG_CONSOLE["history"].insert(0, command_str)

    if len(DEBUG_CONSOLE["history"]) > DEBUG_CONSOLE["max_history"]:
        DEBUG_CONSOLE["history"] = DEBUG_CONSOLE["history"][
            : DEBUG_CONSOLE["max_history"]
        ]

    DEBUG_CONSOLE["history_index"] = -1

    parts = command_str.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd in COMMANDS and COMMANDS[cmd]["callback"]:
        try:
            result = COMMANDS[cmd]["callback"](*args)
            DEBUG_CONSOLE["last_result"] = (
                str(result) if result is not None else "Command executed."
            )
        except TypeError as e:
            DEBUG_CONSOLE["last_result"] = (
                f"Error: Incorrect arguments for '{cmd}'. Usage: {COMMANDS[cmd]['help']}. Details: {e}"
            )
        except Exception as e:
            DEBUG_CONSOLE["last_result"] = f"Error executing command '{cmd}': {e}"
    else:
        DEBUG_CONSOLE["last_result"] = f"Unknown command: {cmd}"

    DEBUG_CONSOLE["command"] = ""
    DEBUG_CONSOLE["cursor_pos"] = 0


def clear_history():
    """
    Clear the debug console's command history.

    :precondition: DEBUG_CONSOLE dictionary must exist.
    :postcondition: Resets DEBUG_CONSOLE['history'] to an empty list.
    :postcondition: Resets DEBUG_CONSOLE['history_index'] to -1.
    :return: str, a confirmation message.
    """
    DEBUG_CONSOLE["history"] = []
    DEBUG_CONSOLE["history_index"] = -1
    return "History cleared"


def show_help(command=None):
    """
    Provide help text for debug commands.

    Shows a list of all commands or detailed help for a specific command.

    :param command: str | None, the specific command to get help for. If None, lists all commands.
    :precondition: COMMANDS dictionary must exist and be populated.
    :postcondition: None.
    :return: str, the help text.
    """
    if not command:
        result = "Available commands: " + ", ".join(sorted(COMMANDS.keys()))
        result += "\nType 'help <command>' for details."
        return result

    command = command.lower()
    if command in COMMANDS:
        return f"{command}: {COMMANDS[command]['help']}"
    else:
        return f"Unknown command: {command}"


def set_player_level(player_state, level_str=None):
    """
    Set the player's level and update related stats (health, XP).

    Requires the player_state dictionary to function.

    :param player_state: dict | None, the player's state dictionary.
    :param level_str: str | None, the desired level as a string. If None, returns current level.
    :precondition: player_state should be a dictionary with 'level', 'max_health', 'health', 'exp', 'exp_to_next' keys.
    :precondition: `ui` module should be available for messaging.
    :postcondition: If level_str is valid, updates player_state['level'], ['max_health'], ['health'], ['exp'], ['exp_to_next'].
    :postcondition: Adds a UI message confirming the change.
    :return: str, a message indicating the result or an error.
    >>> p_state = {'level': 1, 'max_health': 100, 'health': 80, 'exp': 50, 'exp_to_next': 100}
    >>> set_player_level(p_state, '5') # doctest: +SKIP
    'Player level changed from 1 to 5. Health set to 180.'
    >>> p_state['level'] # doctest: +SKIP
    5
    >>> p_state['max_health'] # doctest: +SKIP
    180
    >>> p_state['health'] # doctest: +SKIP
    180
    >>> set_player_level(p_state) # doctest: +SKIP
    'Current level: 5. Use 'level <number>' to change it.'
    >>> set_player_level(p_state, 'abc') # doctest: +SKIP
    'Invalid level. Please provide a number.'
    >>> set_player_level(None, '5') # doctest: +SKIP
    'Player state not available'
    """
    if not player_state:
        return "Player state not available"

    if not level_str:
        return f"Current level: {player_state.get('level', 1)}. Use 'level <number>' to change it."

    try:
        new_level = int(level_str)
        if new_level < 1:
            return "Level must be at least 1"

        old_level = player_state.get("level", 1)
        level_diff = new_level - old_level

        health_gain = level_diff * 20
        new_max_health = player_state.get("max_health", 100) + health_gain

        player_state["level"] = new_level
        player_state["max_health"] = new_max_health
        player_state["health"] = new_max_health
        player_state["exp"] = 0

        base_xp = 100
        xp_multiplier = 1.5
        player_state["exp_to_next"] = int(base_xp * (xp_multiplier ** (new_level - 1)))

        try:
            import ui

            ui.add_message(f"DEBUG: Level set to {new_level}", 3.0, color=6)
        except ImportError:
            pass

        return f"Player level changed from {old_level} to {new_level}. Health set to {player_state['max_health']}."

    except ValueError:
        return "Invalid level. Please provide a number."
    except KeyError as e:
        return f"Player state missing key: {e}"


def teleport_to_boss(player_state=None):
    """
    Teleport the player directly to the boss arena map.

    Switches the map, clears entities, spawns the boss, and updates player position.

    :param player_state: dict | None, the player's state dictionary.
    :precondition: player_state must be a dictionary with 'x' and 'y' keys.
    :precondition: `map.static_map`, `entities`, and `ui` modules must be available.
    :postcondition: Switches the active map to the boss arena.
    :postcondition: Clears existing entities and spawns a boss.
    :postcondition: Updates player_state['x'] and player_state['y'] to the arena entrance.
    :postcondition: Adds UI messages.
    :return: str, a confirmation message.

    # Doctest is not feasible due to heavy dependency on external modules, global state, and side effects.
    """
    if not player_state:
        return "Player state not available"

    try:
        from map.static_map import switch_map
        import entities
        import ui

        _, _, player_spawn, _ = switch_map("boss_arena")

        player_state["x"], player_state["y"] = player_spawn

        entities.clear_entities()
        arena_width = 30
        arena_height = 22
        boss_x, boss_y = arena_width // 2, arena_height // 2
        entities.create_boss(boss_x, boss_y)

        ui.add_message("DEBUG: Teleported to boss arena", 3.0, color=6)
        ui.add_message("BOSS BATTLE INITIALIZED", 4.0, color=1)

        return "Teleported to boss arena. Boss spawned."

    except ImportError as e:
        return f"Error: Missing required module - {e}"
    except Exception as e:
        return f"An error occurred during teleport: {e}"


def render_console(stdscr):
    """
    Render the debug console interface at the top of the screen.

    Displays the command input line and the last command result.

    :param stdscr: curses.Window, the main window object.
    :precondition: DEBUG_CONSOLE must exist. curses must be initialized.
    :postcondition: Draws the console UI elements onto the stdscr.
    :postcondition: Sets the physical cursor position based on DEBUG_CONSOLE['cursor_pos'].
    :return: None
    """
    if not DEBUG_CONSOLE["active"]:
        return

    height, width = stdscr.getmaxyx()

    console_style = curses.A_REVERSE
    prompt_style = curses.A_REVERSE | curses.A_BOLD

    for i in range(2):
        try:
            stdscr.addstr(i, 0, " " * (width - 1), console_style)
        except curses.error:
            pass

    prompt = "> "
    try:
        stdscr.addstr(0, 0, prompt, prompt_style)
        cmd = DEBUG_CONSOLE["command"]
        cursor_screen_pos = len(prompt) + DEBUG_CONSOLE["cursor_pos"]
        available_width = width - len(prompt) - 1

        display_cmd = cmd
        if len(cmd) > available_width:
            start_index = len(cmd) - available_width
            display_cmd = cmd[start_index:]
            cursor_screen_pos = len(prompt) + (
                DEBUG_CONSOLE["cursor_pos"] - start_index
            )
            cursor_screen_pos = max(len(prompt), cursor_screen_pos)

        stdscr.addstr(0, len(prompt), display_cmd, console_style)

        cursor_y, cursor_x = 0, min(width - 1, max(0, cursor_screen_pos))
        curses.setsyx(cursor_y, cursor_x)
        stdscr.move(cursor_y, cursor_x)

    except curses.error:
        pass

    if DEBUG_CONSOLE["last_result"]:
        try:
            result = str(DEBUG_CONSOLE["last_result"])
            if len(result) >= width:
                result = result[: width - 4] + "..."
            stdscr.addstr(1, 0, result.ljust(width - 1), console_style)
        except curses.error:
            pass
