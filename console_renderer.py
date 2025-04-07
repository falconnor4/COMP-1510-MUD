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
