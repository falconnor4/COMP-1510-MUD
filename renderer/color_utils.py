import curses


def init_colors():
    """Initialize color pairs for terminal rendering"""
    curses.start_color()
    for i, color in enumerate(
        [
            curses.COLOR_RED,
            curses.COLOR_GREEN,
            curses.COLOR_YELLOW,
            curses.COLOR_BLUE,
            curses.COLOR_MAGENTA,
            curses.COLOR_CYAN,
            curses.COLOR_WHITE,
            curses.COLOR_WHITE,
            curses.COLOR_BLACK,
        ]
    ):
        curses.init_pair(i + 1, color, curses.COLOR_BLACK)

    for i in range(10, 16):
        intensity = max(0, min(1000, int(1000 * (16 - i) / 6)))
        curses.init_color(i + 10, intensity, intensity, intensity)
        curses.init_pair(i, i + 10, curses.COLOR_BLACK)


# noinspection PyBroadException
def get_color_pair(color_code):
    """Convert color code to curses color pair"""
    try:
        return curses.color_pair(int(color_code))
    except:
        return curses.color_pair(7)


def get_cell_style(cell_type, cell_color):
    """Get the appropriate style for a cell based on its type and color"""
    if cell_type in [1, 8]:  # Wall, Stone
        return curses.color_pair(cell_color) | curses.A_BOLD
    elif cell_type == 3:  # Water
        return curses.color_pair(4) | curses.A_BOLD
    elif cell_type == 2:  # Tree
        return curses.color_pair(2) | curses.A_BOLD
    elif cell_type == 4:  # Path
        return curses.color_pair(3)
    elif cell_type == 5:  # Mountain
        return curses.color_pair(7) | curses.A_BOLD
    elif cell_type == 9:  # Sand
        return curses.color_pair(3) | curses.A_DIM
    else:
        return curses.color_pair(cell_color)
