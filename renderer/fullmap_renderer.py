import curses
import math


def render_full_map(stdscr, player_x, player_y, player_angle, world_map, world_colors):
    """Render a full-screen map of the world"""
    height, width = stdscr.getmaxyx()
    height -= 1

    stdscr.clear()

    border_style = curses.color_pair(6) | curses.A_BOLD
    stdscr.attron(border_style)
    stdscr.box()
    stdscr.attroff(border_style)

    map_height = len(world_map)
    map_width = len(world_map[0])

    scale_x = (width - 4) / map_width
    scale_y = (height - 4) / map_height

    scale = min(scale_x, scale_y)

    offset_x = int((width - (map_width * scale)) / 2)
    offset_y = int((height - (map_height * scale)) / 2)

    title = "[ FULL MAP ]"
    title_x = max(0, (width - len(title)) // 2)
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(1, title_x, title)
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    terrain_chars = {
        0: ' ',
        1: '#',
        2: '♣',
        3: '~',
        4: '·',
        5: '▲',
        6: '+',
        7: '≡',
        8: '▓',
        9: ':',
    }

    for y in range(map_height):

        if scale < 1 and int(y * scale) == int((y + 1) * scale):
            continue

        for x in range(map_width):

            if scale < 1 and int(x * scale) == int((x + 1) * scale):
                continue

            screen_y = offset_y + int(y * scale) + 2
            screen_x = offset_x + int(x * scale) + 1

            cell_type = world_map[y][x]
            cell_char = terrain_chars.get(cell_type, '?')

            cell_color = int(world_colors[y][x])

            if cell_type in [1, 8]:
                style = curses.color_pair(cell_color) | curses.A_BOLD
            elif cell_type == 3:
                style = curses.color_pair(4) | curses.A_BOLD
            elif cell_type == 2:
                style = curses.color_pair(2) | curses.A_BOLD
            elif cell_type == 4:
                style = curses.color_pair(3)
            elif cell_type == 5:
                style = curses.color_pair(7) | curses.A_BOLD
            elif cell_type == 9:
                style = curses.color_pair(3) | curses.A_DIM
            else:
                style = curses.color_pair(cell_color)

            if 0 <= screen_y < height and 0 <= screen_x < width:
                try:
                    stdscr.addch(screen_y, screen_x, cell_char, style)
                except curses.error:
                    pass

    player_screen_y = offset_y + int(player_y * scale) + 2
    player_screen_x = offset_x + int(player_x * scale) + 1

    if 0 <= player_screen_y < height and 0 <= player_screen_x < width:
        try:

            player_char = '@'
            direction_chars = ['↑', '→', '↓', '←']
            direction_idx = int(((player_angle + math.pi / 4) % (2 * math.pi)) / (math.pi / 2))
            direction = direction_chars[direction_idx]

            stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(player_screen_y, player_screen_x, player_char)
            stdscr.addstr(player_screen_y - 1, player_screen_x, direction)
            stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass

    legend_y = height - 2
    legend_items = [
        ("# - Wall", 7),
        ("♣ - Tree", 2),
        ("~ - Water", 4),
        ("· - Path", 3),
        ("▲ - Mountain", 7),
        ("+ - Door", 5),
        ("≡ - Stairs", 6),
        ("▓ - Stone", 8),
        (": - Sand", 3)
    ]

    legend_width = sum(len(item[0]) + 3 for item in legend_items)
    items_per_line = max(1, min(len(legend_items), width // 15))
    item_width = width // items_per_line

    for i, (text, color) in enumerate(legend_items):
        line = i // items_per_line
        col = i % items_per_line
        legend_x = 2 + col * item_width

        try:
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(legend_y - line, legend_x, text)
            stdscr.attroff(curses.color_pair(color))
        except curses.error:
            pass

    help_text = "Press 'M' to return to 3D view, 'Q' to quit"
    help_x = max(0, (width - len(help_text)) // 2)

    try:
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height - 1, help_x, help_text)
        stdscr.attroff(curses.color_pair(3))
    except curses.error:
        pass

    stdscr.noutrefresh()
