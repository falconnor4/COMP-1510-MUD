import curses


def init_colors():
    """Initialize color pairs for terminal rendering"""
    curses.start_color()
    for i, color in enumerate([curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_BLUE,
                               curses.COLOR_MAGENTA, curses.COLOR_CYAN, curses.COLOR_WHITE, curses.COLOR_WHITE,
                               curses.COLOR_BLACK]):
        curses.init_pair(i + 1, color, curses.COLOR_BLACK)

    for i in range(10, 16):
        intensity = max(0, min(1000, int(1000 * (16 - i) / 6)))
        curses.init_color(i + 10, intensity, intensity, intensity)
        curses.init_pair(i, i + 10, curses.COLOR_BLACK)


def get_color_pair(color_code):
    """Convert color code to curses color pair"""
    try:
        return curses.color_pair(int(color_code))
    except:
        return curses.color_pair(7)
