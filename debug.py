import curses

# Debug console state
DEBUG_CONSOLE = {
    'active': False,
    'command': '',
    'history': [],
    'history_index': -1,
    'max_history': 20,
    'cursor_pos': 0,
    'last_result': None
}

# Command definitions
COMMANDS = {
    'next': {
        'help': 'Move to next level (simulates door interaction)',
        'callback': None  # Will be set during initialization
    },
    'help': {
        'help': 'Show available commands',
        'callback': None
    },
    'clear': {
        'help': 'Clear the console history',
        'callback': None
    }
}

def toggle_console():
    """Toggle the debug console on/off"""
    DEBUG_CONSOLE['active'] = not DEBUG_CONSOLE['active']
    if DEBUG_CONSOLE['active']:
        DEBUG_CONSOLE['command'] = ''
        DEBUG_CONSOLE['cursor_pos'] = 0

def process_input(key, player_state=None, world_map=None, change_level_callback=None):
    """Process input when debug console is active"""
    if not DEBUG_CONSOLE['active']:
        return False

    # Store change level callback for the 'next' command
    if change_level_callback and COMMANDS['next']['callback'] is None:
        COMMANDS['next']['callback'] = change_level_callback
        
        # Set up help command
        COMMANDS['help']['callback'] = lambda: "Available commands: " + ", ".join(COMMANDS.keys())
        
        # Set up clear command
        COMMANDS['clear']['callback'] = lambda: clear_history()
    
    if key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key
        execute_command(DEBUG_CONSOLE['command'], player_state, world_map)
        return True
        
    elif key == 27:  # Escape key
        toggle_console()
        return True
        
    elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:  # Backspace
        if DEBUG_CONSOLE['cursor_pos'] > 0:
            command = DEBUG_CONSOLE['command']
            pos = DEBUG_CONSOLE['cursor_pos']
            DEBUG_CONSOLE['command'] = command[:pos-1] + command[pos:]
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
        
    elif key == curses.KEY_UP:  # Command history up
        if DEBUG_CONSOLE['history'] and DEBUG_CONSOLE['history_index'] < len(DEBUG_CONSOLE['history']) - 1:
            DEBUG_CONSOLE['history_index'] += 1
            DEBUG_CONSOLE['command'] = DEBUG_CONSOLE['history'][DEBUG_CONSOLE['history_index']]
            DEBUG_CONSOLE['cursor_pos'] = len(DEBUG_CONSOLE['command'])
        return True
        
    elif key == curses.KEY_DOWN:  # Command history down
        if DEBUG_CONSOLE['history_index'] > 0:
            DEBUG_CONSOLE['history_index'] -= 1
            DEBUG_CONSOLE['command'] = DEBUG_CONSOLE['history'][DEBUG_CONSOLE['history_index']]
            DEBUG_CONSOLE['cursor_pos'] = len(DEBUG_CONSOLE['command'])
        elif DEBUG_CONSOLE['history_index'] == 0:
            DEBUG_CONSOLE['history_index'] = -1
            DEBUG_CONSOLE['command'] = ''
            DEBUG_CONSOLE['cursor_pos'] = 0
        return True
            
    elif 32 <= key <= 126:  # Printable ASCII characters
        command = DEBUG_CONSOLE['command']
        pos = DEBUG_CONSOLE['cursor_pos']
        DEBUG_CONSOLE['command'] = command[:pos] + chr(key) + command[pos:]
        DEBUG_CONSOLE['cursor_pos'] += 1
        return True
        
    return True  # All inputs are consumed when console is active

def execute_command(command_str, player_state=None, world_map=None):
    """Execute a debug command"""
    if not command_str.strip():
        return
    
    # Add to history
    if DEBUG_CONSOLE['history'] and DEBUG_CONSOLE['history'][0] != command_str:
        DEBUG_CONSOLE['history'].insert(0, command_str)
    elif not DEBUG_CONSOLE['history']:
        DEBUG_CONSOLE['history'].insert(0, command_str)
        
    # Trim history if needed
    if len(DEBUG_CONSOLE['history']) > DEBUG_CONSOLE['max_history']:
        DEBUG_CONSOLE['history'] = DEBUG_CONSOLE['history'][:DEBUG_CONSOLE['max_history']]
    
    DEBUG_CONSOLE['history_index'] = -1
    
    # Parse command and arguments
    parts = command_str.split()
    if not parts:
        return
        
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    # Execute command if it exists
    if cmd in COMMANDS and COMMANDS[cmd]['callback']:
        result = COMMANDS[cmd]['callback'](*args)
        if result:
            DEBUG_CONSOLE['last_result'] = result
    else:
        DEBUG_CONSOLE['last_result'] = f"Unknown command: {cmd}"
    
    # Reset command input
    DEBUG_CONSOLE['command'] = ''
    DEBUG_CONSOLE['cursor_pos'] = 0

def clear_history():
    """Clear command history"""
    DEBUG_CONSOLE['history'] = []
    DEBUG_CONSOLE['history_index'] = -1
    return "History cleared"

def render_console(stdscr):
    """Render the debug console on screen"""
    if not DEBUG_CONSOLE['active']:
        return
    
    height, width = stdscr.getmaxyx()
    
    # Draw console background
    for i in range(2):
        try:
            stdscr.addstr(i, 0, " " * width, curses.A_REVERSE)
        except curses.error:
            pass
    
    # Draw prompt and command
    prompt = "> "
    try:
        stdscr.addstr(0, 0, prompt, curses.A_REVERSE | curses.A_BOLD)
        cmd = DEBUG_CONSOLE['command']
        if len(cmd) + len(prompt) > width:
            # Show only the visible part of command
            visible_cmd = cmd[-(width-len(prompt)):]
            cursor_adjust = len(cmd) - len(visible_cmd)
            stdscr.addstr(0, len(prompt), visible_cmd, curses.A_REVERSE)
            
            # Position cursor
            curses.setsyx(0, len(prompt) + DEBUG_CONSOLE['cursor_pos'] - cursor_adjust)
        else:
            stdscr.addstr(0, len(prompt), cmd, curses.A_REVERSE)
            
            # Position cursor
            curses.setsyx(0, len(prompt) + DEBUG_CONSOLE['cursor_pos'])
    except curses.error:
        pass
    
    # Draw last result
    if DEBUG_CONSOLE['last_result']:
        try:
            result = DEBUG_CONSOLE['last_result']
            if len(result) > width:
                result = result[:width-3] + "..."
            stdscr.addstr(1, 0, result, curses.A_REVERSE)
        except curses.error:
            pass
