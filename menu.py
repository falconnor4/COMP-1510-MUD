import curses
import time
from renderer.color_utils import init_colors

TITLE_ART = [
    r"                                                                                                    ",
    r"     _____          ____        _____          ____        _____           _____                    ",
    r" ___|\    \    ____|\   \   ___|\    \    ____|\   \   ___|\    \     ____|\    \   _____      _____",
    r"|    |\    \  /    /\    \ |    |\    \  /    /\    \ |    |\    \   /     /\    \  \    \    /    /",
    r"|    | |    ||    |  |    ||    | |    ||    |  |    ||    | |    | /     /  \    \  \    \  /    / ",
    r"|    |/____/||    |__|    ||    |/____/ |    |__|    ||    | |    ||     |    |    |  \____\/____/  ",
    r"|    ||    |||    .--.    ||    |\    \ |    .--.    ||    | |    ||     |    |    |  /    /\    \  ",
    r"|    ||____|/|    |  |    ||    | |    ||    |  |    ||    | |    ||\     \  /    /| /    /  \    \ ",
    r"|____|       |____|  |____||____| |____||____|  |____||____|/____/|| \_____\/____/ |/____/ /\ \____\\",
    r"|    |       |    |  |    ||    | |    ||    |  |    ||    /    | | \ |    ||    | /|    |/  \|    |",
    r"|____|       |____|  |____||____| |____||____|  |____||____|____|/   \|____||____|/ |____|    |____|",
    r"  \(           \(      )/    \(     )/    \(      )/    \(    )/        \(    )/      \(        )/  ",
    r"   '            '      '      '     '      '      '      '    '          '    '        '        '   ",
    r"                                                                                                    ",
    r"Version: -0.1                  A small(ish) 3d adventure game in the terminal!                      ",
]

MENU_OPTIONS = ["Start Game", "Instructions", "Credits", "Exit"]


def draw_title(stdscr, start_y):
    """Draw the ASCII art title with colorful effect"""
    height, width = stdscr.getmaxyx()
    title_x = max(0, (width - len(TITLE_ART[0])) // 2)

    colors = [1, 3, 2, 6, 4, 5]

    for i, line in enumerate(TITLE_ART):
        color = colors[i % len(colors)]
        stdscr.attron(curses.color_pair(color) | curses.A_BOLD)
        stdscr.addstr(start_y + i, title_x, line)
        stdscr.attroff(curses.color_pair(color) | curses.A_BOLD)


def draw_footer(stdscr, footer_text):
    """
    Draw a centered footer at the bottom of the screen

    Args:
        stdscr: The curses window
        footer_text: The text to display in the footer
    """
    height, width = stdscr.getmaxyx()
    footer_y = height - 2
    footer_x = max(0, (width - len(footer_text)) // 2)

    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(footer_y, footer_x, footer_text)
    stdscr.attroff(curses.color_pair(3))

    stdscr.refresh()


def draw_menu(stdscr, selected_idx):
    """Draw the menu with the selected option highlighted"""

    stdscr.clear()

    height, width = stdscr.getmaxyx()

    border_style = curses.color_pair(6) | curses.A_BOLD
    stdscr.attron(border_style)
    stdscr.box()
    stdscr.attroff(border_style)

    title_y = 3
    draw_title(stdscr, title_y)

    menu_y = title_y + len(TITLE_ART) + 3
    menu_width = max(len(option) for option in MENU_OPTIONS) + 4
    menu_x = (width - menu_width) // 2

    for i, option in enumerate(MENU_OPTIONS):
        y = menu_y + i * 2
        x = menu_x

        if i == selected_idx:

            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(y, x, ">" + " " + option + " " + "<")
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            stdscr.attron(curses.color_pair(7))
            stdscr.addstr(y, x, "  " + option + "  ")
            stdscr.attroff(curses.color_pair(7))

    draw_footer(stdscr, "Use UP/DOWN arrows to select, ENTER to confirm")


def display_screen(stdscr, title, content, line_styles=None):
    """
    Display a screen with a title, content, and footer

    Args:
        stdscr: The curses window
        title: The title to display at the top
        content: List of strings to display as content
        line_styles: Optional function to determine style for each line
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Draw border
    border_style = curses.color_pair(6) | curses.A_BOLD
    stdscr.attron(border_style)
    stdscr.box()
    stdscr.attroff(border_style)

    # Draw title
    title_y = 2
    title_x = max(0, (width - len(title)) // 2)
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(title_y, title_x, title)
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    # Draw content
    content_y = 5
    for i, line in enumerate(content):
        if not line:
            continue

        style = line_styles(i, line) if line_styles else curses.color_pair(7)

        content_x = max(0, (width - len(line)) // 2)
        stdscr.attron(style)
        stdscr.addstr(content_y + i, content_x, line)
        stdscr.attroff(style)

    draw_footer(stdscr, "Press any key to return to the menu")
    stdscr.getch()


def show_instructions(stdscr):
    """Display game instructions"""
    instructions = [
        "MOVEMENT CONTROLS:",
        "  W - Move Forward",
        "  S - Move Backward",
        "  A - Strafe Left",
        "  D - Strafe Right",
        "",
        "TURNING:",
        "  LEFT ARROW - Turn Left",
        "  RIGHT ARROW - Turn Right",
        "",
        "ACTIONS:",
        "  SPACEBAR - Shoot",
        "  Q - Quit Game",
        "  M - Toggle Map Mode",
        "",
        "TERRAIN TYPES:",
        "  '#' - Wall       '♣' - Tree",
        "  '~' - Water      '·' - Path",
        "  '▲' - Mountain   '+' - Door",
        "  '≡' - Stairs     '▓' - Stone",
        "  ':' - Sand       ' ' - Empty",
    ]

    def instruction_styles(i, line):
        if (
            "CONTROLS:" in line
            or "TURNING:" in line
            or "ACTIONS:" in line
            or "TERRAIN TYPES:" in line
        ):
            return curses.color_pair(1) | curses.A_BOLD
        else:
            return curses.color_pair(7)

    display_screen(stdscr, "INSTRUCTIONS", instructions, instruction_styles)


def show_credits(stdscr):
    """Display game credits"""
    credits = [
        "COMP-1510-MUD",
        "",
        "A Terminal-Based 3D Adventure Game",
        "",
        "Created by:",
        "  Connor Brown",
        "",
        "Inspired by:",
        "  ID Software's Doom",
        "  Aardwolf MUD",
        "  Classic ASCII Roguelikes",
        "",
        "Special thanks to:",
        "  The Python Community",
        "  The Curses Library",
        "  BCIT",
    ]

    def credit_styles(i, line):
        if i == 0:
            return curses.color_pair(1) | curses.A_BOLD
        elif line.startswith("  "):
            return curses.color_pair(7)
        else:
            return curses.color_pair(6) | curses.A_BOLD

    display_screen(stdscr, "CREDITS", credits, credit_styles)


def display_menu(stdscr):
    """Display the main menu and handle user input"""

    curses.curs_set(0)
    init_colors()

    current_option = 0

    draw_menu(stdscr, current_option)

    while True:

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(MENU_OPTIONS) - 1:
            current_option += 1
        elif key == curses.KEY_ENTER or key == 10 or key == 13:

            if current_option == 0:
                return "start_game"
            elif current_option == 1:
                show_instructions(stdscr)
            elif current_option == 2:
                show_credits(stdscr)
            elif current_option == 3:
                return "exit"

        draw_menu(stdscr, current_option)

        time.sleep(0.01)


def main(stdscr):
    """Main function for standalone testing"""
    result = display_menu(stdscr)
    if result == "start_game":
        stdscr.clear()
        stdscr.addstr(0, 0, "Game would start here!")
        stdscr.refresh()
        stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
