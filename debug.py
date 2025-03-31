import curses

DEBUG_CONSOLE = {
    'active': False,
    'command': '',
    'history': [],
    'history_index': -1,
    'max_history': 20,
    'cursor_pos': 0,
    'last_result': None,
    'initialized': False
}

COMMANDS = {
    'next': {
        'help': 'Move to next level (simulates door interaction)',
        'callback': None
    },
    'help': {
        'help': 'Show available commands or details about a specific command (usage: help [command])',
        'callback': lambda cmd=None: show_help(cmd)
    },
    'clear': {
        'help': 'Clear the console history',
        'callback': lambda: clear_history()
    },
    'level': {
        'help': 'Set player level (usage: level <number>)',
        'callback': None
    },
    'boss': {
        'help': 'Teleport directly to boss arena',
        'callback': None
    }
}


def toggle_console():
    """Toggle the debug console on/off"""
    DEBUG_CONSOLE['active'] = not DEBUG_CONSOLE['active']
    if DEBUG_CONSOLE['active']:
        DEBUG_CONSOLE['command'] = ''
        DEBUG_CONSOLE['cursor_pos'] = 0


def initialize_commands(player_state=None, change_level_callback=None):
    """Initialize command callbacks that need references to game state"""
    if DEBUG_CONSOLE['initialized']:
        return

    if change_level_callback:
        COMMANDS['next']['callback'] = change_level_callback

    COMMANDS['level']['callback'] = lambda level=None: set_player_level(player_state, level)

    COMMANDS['boss']['callback'] = lambda: teleport_to_boss(player_state)

    DEBUG_CONSOLE['initialized'] = True


def process_input(key, player_state=None, world_map=None):
    """Process input when debug console is active"""
    if not DEBUG_CONSOLE['active']:
        return False

    initialize_commands(player_state)

    if key == curses.KEY_ENTER or key == 10 or key == 13:
        execute_command(DEBUG_CONSOLE['command'], player_state, world_map)
        return True

    elif key == 27:
        toggle_console()
        return True

    elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
        if DEBUG_CONSOLE['cursor_pos'] > 0:
            command = DEBUG_CONSOLE['command']
            pos = DEBUG_CONSOLE['cursor_pos']
            DEBUG_CONSOLE['command'] = command[:pos - 1] + command[pos:]
            DEBUG_CONSOLE['cursor_pos'] -= 1
        return True

    elif key == curses.KEY_LEFT:
        if DEBUG_CONSOLE['cursor_pos'] > 0:
            DEBUG_CONSOLE['cursor_pos'] -= 1
        return True

    elif key == curses.KEY_RIGHT:
        if DEBUG_CONSOLE['cursor_pos'] < len(DEBUG_CONSOLE['command']):
            DEBUG_CONSOLE['cursor_pos'] += 1
        return True

    elif key == curses.KEY_UP:
        if DEBUG_CONSOLE['history'] and DEBUG_CONSOLE['history_index'] < len(DEBUG_CONSOLE['history']) - 1:
            DEBUG_CONSOLE['history_index'] += 1
            DEBUG_CONSOLE['command'] = DEBUG_CONSOLE['history'][DEBUG_CONSOLE['history_index']]
            DEBUG_CONSOLE['cursor_pos'] = len(DEBUG_CONSOLE['command'])
        return True

    elif key == curses.KEY_DOWN:
        if DEBUG_CONSOLE['history_index'] > 0:
            DEBUG_CONSOLE['history_index'] -= 1
            DEBUG_CONSOLE['command'] = DEBUG_CONSOLE['history'][DEBUG_CONSOLE['history_index']]
            DEBUG_CONSOLE['cursor_pos'] = len(DEBUG_CONSOLE['command'])
        elif DEBUG_CONSOLE['history_index'] == 0:
            DEBUG_CONSOLE['history_index'] = -1
            DEBUG_CONSOLE['command'] = ''
            DEBUG_CONSOLE['cursor_pos'] = 0
        return True

    elif 32 <= key <= 126:
        command = DEBUG_CONSOLE['command']
        pos = DEBUG_CONSOLE['cursor_pos']
        DEBUG_CONSOLE['command'] = command[:pos] + chr(key) + command[pos:]
        DEBUG_CONSOLE['cursor_pos'] += 1
        return True

    return True


def execute_command(command_str, player_state=None, world_map=None):
    """Execute a debug command"""
    if not command_str.strip():
        return

    if DEBUG_CONSOLE['history'] and DEBUG_CONSOLE['history'][0] != command_str:
        DEBUG_CONSOLE['history'].insert(0, command_str)
    elif not DEBUG_CONSOLE['history']:
        DEBUG_CONSOLE['history'].insert(0, command_str)

    if len(DEBUG_CONSOLE['history']) > DEBUG_CONSOLE['max_history']:
        DEBUG_CONSOLE['history'] = DEBUG_CONSOLE['history'][:DEBUG_CONSOLE['max_history']]

    DEBUG_CONSOLE['history_index'] = -1

    parts = command_str.split()
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    if cmd in COMMANDS and COMMANDS[cmd]['callback']:
        try:
            result = COMMANDS[cmd]['callback'](*args)
            if result:
                DEBUG_CONSOLE['last_result'] = result
        except Exception as e:
            DEBUG_CONSOLE['last_result'] = f"Error executing command: {e}"
    else:
        DEBUG_CONSOLE['last_result'] = f"Unknown command: {cmd}"

    DEBUG_CONSOLE['command'] = ''
    DEBUG_CONSOLE['cursor_pos'] = 0


def clear_history():
    """Clear command history"""
    DEBUG_CONSOLE['history'] = []
    DEBUG_CONSOLE['history_index'] = -1
    return "History cleared"


def show_help(command=None):
    """Show help for all commands or details about a specific command"""
    if not command:
        result = "Available commands: " + ", ".join(COMMANDS.keys())
        result += "\nType 'help <command>' for more details about a specific command"
        return result

    command = command.lower()
    if command in COMMANDS:
        return f"{command}: {COMMANDS[command]['help']}"
    else:
        return f"Unknown command: {command}"


def set_player_level(player_state, level_str=None):
    """Set the player's level"""
    if not player_state:
        return "Player state not available"

    if not level_str:
        return f"Current level: {player_state.get('level', 1)}. Use 'level <number>' to change it."

    try:
        new_level = int(level_str)
        if new_level < 1:
            return "Level must be at least 1"

        old_level = player_state['level']
        player_state['level'] = new_level

        level_diff = new_level - old_level
        health_gain = level_diff * 20
        player_state['max_health'] += health_gain
        player_state['health'] = player_state['max_health']

        player_state['exp'] = 0
        player_state['exp_to_next'] = 100 * (1.5 ** (new_level - 1))

        import ui
        ui.add_message(f"DEBUG: Level set to {new_level}", 3.0, color=6)
        return f"Player level changed from {old_level} to {new_level}. Health set to {player_state['max_health']}."
    except ValueError:
        return "Invalid level. Please provide a number."


def teleport_to_boss(player_state=None):
    """Teleport player directly to boss arena"""
    if not player_state:
        return "Player state not available"

    from map.static_map import switch_map, ACTIVE_MAP, ACTIVE_COLORS
    import entities
    import ui

    new_map, new_colors, player_spawn, _ = switch_map('boss_arena')

    player_state['x'], player_state['y'] = player_spawn

    entities.clear_entities()
    entities.create_boss(15, 10)

    ui.add_message("DEBUG: Teleported to boss arena", 3.0, color=6)
    ui.add_message("BOSS BATTLE INITIALIZED", 4.0, color=1)

    return "Teleported to boss arena. Boss spawned."


def render_console(stdscr):
    """Render the debug console on screen"""
    if not DEBUG_CONSOLE['active']:
        return

    height, width = stdscr.getmaxyx()

    for i in range(2):
        try:
            stdscr.addstr(i, 0, " " * width, curses.A_REVERSE)
        except curses.error:
            pass

    prompt = "> "
    try:
        stdscr.addstr(0, 0, prompt, curses.A_REVERSE | curses.A_BOLD)
        cmd = DEBUG_CONSOLE['command']
        if len(cmd) + len(prompt) > width:

            visible_cmd = cmd[-(width - len(prompt)):]
            cursor_adjust = len(cmd) - len(visible_cmd)
            stdscr.addstr(0, len(prompt), visible_cmd, curses.A_REVERSE)

            curses.setsyx(0, len(prompt) + DEBUG_CONSOLE['cursor_pos'] - cursor_adjust)
        else:
            stdscr.addstr(0, len(prompt), cmd, curses.A_REVERSE)

            curses.setsyx(0, len(prompt) + DEBUG_CONSOLE['cursor_pos'])
    except curses.error:
        pass

    if DEBUG_CONSOLE['last_result']:
        try:
            result = DEBUG_CONSOLE['last_result']
            if len(result) > width:
                result = result[:width - 3] + "..."
            stdscr.addstr(1, 0, result, curses.A_REVERSE)
        except curses.error:
            pass
