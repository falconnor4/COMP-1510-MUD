import curses
import math
from map import TERRAIN_CHARS
from renderer.color_utils import get_cell_style


def render_minimap(
    stdscr, player_x, player_y, player_angle, world_map, world_colors, height, width
):
    """Render an enhanced Aardwolf-style minimap in the corner of the screen"""

    map_size = 16

    map_start_x = width - map_size - 2
    map_start_y = 1

    border_color = curses.color_pair(6) | curses.A_BOLD

    left_border = "╔═"
    right_border = "═╗"
    title_space = map_size - len(left_border) - len(right_border) + 2

    title_padding = (title_space - len(map_title)) // 2
    title_border = (
        "═" * title_padding
        + map_title
        + "═" * (title_space - len(map_title) - title_padding)
    )

    stdscr.addstr(
        map_start_y,
        map_start_x,
        left_border + title_border + right_border,
        border_color,
    )

    for y in range(1, map_size + 1):
        stdscr.addstr(map_start_y + y, map_start_x, "║", border_color)
        stdscr.addstr(map_start_y + y, map_start_x + map_size + 1, "║", border_color)

    stdscr.addstr(
        map_start_y + map_size + 1,
        map_start_x,
        "╚" + "═" * map_size + "╝",
        border_color,
    )

    view_radius = map_size // 2

    center_x = int(player_x)
    center_y = int(player_y)

    start_x = max(0, center_x - view_radius)
    start_y = max(0, center_y - view_radius)
    end_x = min(len(world_map[0]), center_x + view_radius + 1)
    end_y = min(len(world_map), center_y + view_radius + 1)

    terrain_chars = TERRAIN_CHARS

    for map_y in range(start_y, end_y):
        for map_x in range(start_x, end_x):

            mini_x = map_start_x + 1 + (map_x - start_x)
            mini_y = map_start_y + 1 + (map_y - start_y)

            if (
                0 <= mini_y <= map_start_y + map_size
                and 0 <= mini_x <= map_start_x + map_size
            ):
                cell_type = world_map[map_y][map_x]
                cell_color = int(world_colors[map_y][map_x])

                cell_char = terrain_chars.get(cell_type, "?")

                style = get_cell_style(cell_type, cell_color)

                try:
                    stdscr.addch(mini_y, mini_x, cell_char, style)
                except curses.error:
                    pass

    import entities as entity_system

    for entity in entity_system.entities:

        mini_x = map_start_x + 1 + int(entity["x"] - start_x)
        mini_y = map_start_y + 1 + int(entity["y"] - start_y)

        if (
            map_start_y <= mini_y <= map_start_y + map_size
            and map_start_x <= mini_x <= map_start_x + map_size
        ):

            if entity["type"] == entity_system.ENTITY_PROJECTILE:
                char = "*"
                style = (
                    curses.color_pair(entity_system.PROJECTILE_COLOR) | curses.A_BOLD
                )
            elif entity["type"] == entity_system.ENTITY_ENEMY:
                if entity.get("subtype") == "boss":
                    char = "K"
                    style = curses.color_pair(1) | curses.A_BOLD
                elif entity["state"] == "dead":
                    char = "x"
                    style = curses.color_pair(entity_system.ENEMY_DEAD_COLOR)
                else:
                    char = "E"
                    style = curses.color_pair(entity_system.ENEMY_COLOR)
                    if entity["state"] in ["chase", "attack"]:
                        style |= curses.A_BOLD
            elif entity["type"] == entity_system.ENTITY_ENEMY_PROJECTILE:
                char = "o"
                style = curses.color_pair(entity_system.ENEMY_PROJECTILE_COLOR) | curses.A_BOLD
            else:
                char = "?"
                style = curses.color_pair(7)

            try:
                stdscr.addch(mini_y, mini_x, char, style)
            except curses.error:
                pass

    player_mini_x = map_start_x + 1 + int(player_x - start_x)
    player_mini_y = map_start_y + 1 + int(player_y - start_y)

    if (
        map_start_y < player_mini_y < map_start_y + map_size
        and map_start_x < player_mini_x < map_start_x + map_size
    ):
        try:
            player_char = "@"
            player_style = curses.color_pair(1) | curses.A_BOLD
            stdscr.addch(player_mini_y, player_mini_x, player_char, player_style)

            direction_length = 1.0
            dir_x = player_mini_x + int(math.cos(player_angle) * direction_length)
            dir_y = player_mini_y + int(math.sin(player_angle) * direction_length)
            
            angle_normalized = (player_angle % (2 * math.pi))
            
            direction_chars = ["→", "↘", "↓", "↙", "←", "↖", "↑", "↗"]
            direction_idx = int((angle_normalized / (2 * math.pi) * 8 + 0.5) % 8)
            direction_char = direction_chars[direction_idx]
            
            if dir_x == player_mini_x and dir_y == player_mini_y:
                dir_x = player_mini_x + int(round(math.cos(player_angle)))
                dir_y = player_mini_y + int(round(math.sin(player_angle)))
            
            if (
                map_start_y <= dir_y <= map_start_y + map_size
                and map_start_x <= dir_x <= map_start_x + map_size
            ):
                try:
                    stdscr.addch(
                        dir_y, dir_x, direction_char, curses.color_pair(3) | curses.A_BOLD
                    )
                except curses.error:
                    pass
        except curses.error:
            pass
        
    compass_y_top = map_start_y + 1
    compass_y_bottom = map_start_y + map_size
    compass_x_left = map_start_x + 1
    compass_x_right = map_start_x + map_size
    
    compass_style = curses.color_pair(7) | curses.A_DIM
    
    try:
        stdscr.addstr(compass_y_top, compass_x_left, "NW", compass_style)
        stdscr.addstr(compass_y_top, compass_x_right - 1, "NE", compass_style)
        stdscr.addstr(compass_y_bottom, compass_x_left, "SW", compass_style)
        stdscr.addstr(compass_y_bottom, compass_x_right - 1, "SE", compass_style)
    except curses.error:
        pass
