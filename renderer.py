import math
import random
import curses
import time
from anim.hand.fire import FireFrames

DENSE_SHADING = " ░▒▓█"
DETAILED_SHADING = " .,:;i1tfLCG08@"
UNICODE_BLOCKS = " ▏▎▍▌▋▊▉█"

SHADING_CHARS = " .'`,:;!-+=iIl|/\\tfjrxnuvcTYUJCLQ0OZ#MW&8%B@$"

WALL_EDGE_CHARS = {
    'top': '▁',
    'bottom': '▔',
    'left': '▏',
    'right': '▕',
    'top_left': '▗',
    'top_right': '▖',
    'bottom_left': '▝',
    'bottom_right': '▘',
}


def init_colors():
    """Initialize color pairs for terminal rendering"""

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_BLACK)

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


def get_shading_set(wall_orientation='vertical'):
    """Get appropriate shading set based on wall orientation"""
    if (wall_orientation == 'horizontal'):
        return "═╤╥╦╣╮╕┐┌╭╓╒╔╔║╠╟╞╡┤╢╖╗╝╜╛┘┙╙╚╔╦╦╤╥"
    return SHADING_CHARS


def get_distance_shade(distance, max_distance=20, wall_x=0, wall_y=0):
    """Get appropriate shading character and attributes based on distance"""

    norm_distance = min(1.0, distance / max_distance)

    shade_idx = min(len(SHADING_CHARS) - 1, int((1 - norm_distance) * len(SHADING_CHARS)))
    shade_char = SHADING_CHARS[shade_idx]

    if random.random() < 0.2 and shade_idx > 0:
        shade_idx = max(0, shade_idx - 1)
        shade_char = SHADING_CHARS[shade_idx]

    color = 7
    if norm_distance < 0.3:
        color = 7
    elif norm_distance < 0.6:
        color = 8
    else:
        color = 8

    return shade_char, color


def shoot_animation(stdscr, height, width):
    """Advanced shooting animation using imported fire frames"""

    if not FireFrames or len(FireFrames) == 0:
        return

    try:
        max_y, max_x = stdscr.getmaxyx()
    except:
        return

    frame_lines = FireFrames[0].split('\n')
    anim_height = len(frame_lines)
    anim_width = max(len(line) for line in frame_lines)

    try:
        tmpwin = curses.newpad(anim_height, anim_width)

        prepared_frames = []

        for frame in FireFrames:
            tmpwin.clear()
            lines = frame.split('\n')

            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    if char != ' ' and char != '\t':
                        try:
                            tmpwin.addch(i, j, char, curses.color_pair(1) | curses.A_BOLD)
                        except:
                            pass

            prepared_frames.append(tmpwin.instr(0, 0, anim_height * anim_width))

        return prepared_frames

    except:
        return None


def render_world(stdscr, player_x, player_y, player_angle, world_map, world_colors, player_state=None):
    """Render the world using ASCII characters with colored walls and Unicode edges"""
    height, width = stdscr.getmaxyx()
    height -= 1
    resolution = 1

    FOV = math.pi / 3

    stdscr.erase()

    eye_height_offset = 0
    if player_state and 'bob_offset' in player_state:
        eye_height_offset = player_state['bob_offset']

    ceiling_chars = ".:'"
    floor_chars = ".,;:"

    for y in range(height // 2):
        gradient_idx = min(len(ceiling_chars) - 1, int(y / (height / 2) * len(ceiling_chars)))
        ceiling_char = ceiling_chars[gradient_idx]

        pattern = ceiling_char * width
        stdscr.addstr(y, 0, pattern, curses.color_pair(9))

    for y in range(height // 2, height):
        gradient_idx = min(len(floor_chars) - 1, int((y - height // 2) / (height / 2) * len(floor_chars)))
        floor_char = floor_chars[gradient_idx]

        pattern = floor_char * width
        stdscr.addstr(y, 0, pattern, curses.color_pair(8))

    wall_segments = []

    entity_renders = []

    import entities as entity_system

    for column in range(0, width, resolution):

        ray_offset = (column / width - 0.5) * FOV
        column_angle = player_angle + ray_offset

        distance_to_wall = 0
        hit_wall = False
        wall_x, wall_y = player_x, player_y
        current_color = 7
        wall_orientation = 'vertical'

        while not hit_wall and distance_to_wall < 20:
            distance_to_wall += 0.05

            test_x = player_x + distance_to_wall * math.cos(column_angle)
            test_y = player_y + distance_to_wall * math.sin(column_angle)

            if int(test_x) < 0 or int(test_x) >= len(world_map[0]) or int(test_y) < 0 or int(test_y) >= len(world_map):
                hit_wall = True
                distance_to_wall = 20
            else:

                cell_type = world_map[int(test_y)][int(test_x)]
                if cell_type != 0 and cell_type != 4 and cell_type != 9:
                    hit_wall = True
                    wall_x, wall_y = int(test_x), int(test_y)
                    current_color = world_colors[int(test_y)][int(test_x)]

                    x_fraction = test_x - int(test_x)
                    y_fraction = test_y - int(test_y)

                    if abs(x_fraction) < abs(y_fraction):
                        wall_orientation = 'vertical'
                    else:
                        wall_orientation = 'horizontal'

        distance_to_wall *= math.cos(ray_offset)

        wall_height = min(height, int(height / distance_to_wall * 2))

        bob_pixels = int(eye_height_offset * height / 4)

        wall_top = max(0, height // 2 - wall_height // 2 + bob_pixels)
        wall_bottom = min(height - 1, height // 2 + wall_height // 2 + bob_pixels)

        if hit_wall and distance_to_wall < 20:
            wall_segments.append({
                'column': column,
                'top': wall_top,
                'bottom': wall_bottom,
                'distance': distance_to_wall,
                'color': current_color,
                'orientation': wall_orientation,
                'wall_x': wall_x,
                'wall_y': wall_y
            })

    for entity in entity_system.entities:

        dx = entity['x'] - player_x
        dy = entity['y'] - player_y
        entity_distance = math.sqrt(dx * dx + dy * dy)

        if entity_distance > 20.0:
            continue

        entity_angle = math.atan2(dy, dx)

        relative_angle = entity_angle - player_angle
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi

        if abs(relative_angle) > FOV / 2:
            continue

        screen_x = int(width * (0.5 + relative_angle / FOV))

        entity_scale = 1.0 / max(1.0, entity_distance * 0.2)

        entity_height = int(min(height / 2, 8.0 / max(1.0, entity_distance * 0.2)))

        bob_pixels = 0
        if player_state and 'bob_offset' in player_state:
            bob_pixels = int(player_state['bob_offset'] * height / 4)

        entity_y = height // 2 - entity_height // 2 + bob_pixels

        entity_renders.append({
            'entity': entity,
            'screen_x': screen_x,
            'screen_y': entity_y,
            'height': entity_height,
            'scale': entity_scale,
            'distance': entity_distance,
            'in_view': True
        })

    for i, segment in enumerate(wall_segments):
        column = segment['column']
        wall_top = segment['top']
        wall_bottom = segment['bottom']
        distance_to_wall = segment['distance']
        current_color = segment['color']
        wall_orientation = segment['orientation']
        wall_x = segment['wall_x']
        wall_y = segment['wall_y']

        is_left_edge = (i == 0 or column - wall_segments[i - 1]['column'] > resolution or
                        abs(wall_segments[i - 1]['distance'] - distance_to_wall) > 1)
        is_right_edge = (i == len(wall_segments) - 1 or wall_segments[i + 1]['column'] - column > resolution or
                         abs(wall_segments[i + 1]['distance'] - distance_to_wall) > 1)

        shade_char, shade_intensity = get_distance_shade(distance_to_wall, 20, wall_x, wall_y)

        color_attr = get_color_pair(current_color)
        if distance_to_wall > 10:

            color_attr = color_attr | curses.A_DIM
        elif distance_to_wall < 3:

            color_attr = color_attr | curses.A_BOLD

        if wall_orientation == 'horizontal' and distance_to_wall < 20:
            shade_char = get_shading_set('horizontal')[min(len(get_shading_set('horizontal')) - 1,
                                                           get_shading_set().find(shade_char))]

            color_attr = color_attr | curses.A_DIM

        for y in range(wall_top, wall_bottom + 1):
            try:

                position_in_wall = (y - wall_top) / max(1, wall_bottom - wall_top)

                if y == wall_top:
                    char = WALL_EDGE_CHARS['top']
                elif y == wall_bottom:
                    char = WALL_EDGE_CHARS['bottom']
                else:

                    if is_left_edge and y > wall_top and y < wall_bottom:
                        char = WALL_EDGE_CHARS['left']
                    elif is_right_edge and y > wall_top and y < wall_bottom:
                        char = WALL_EDGE_CHARS['right']
                    else:

                        if position_in_wall > 0.8:

                            char = SHADING_CHARS[min(len(SHADING_CHARS) - 1, SHADING_CHARS.find(shade_char) + 1)]
                        else:
                            char = shade_char

                stdscr.addch(y, column, char, color_attr)
            except curses.error:
                pass

    entity_renders.sort(key=lambda e: e['distance'], reverse=True)

    for er in entity_renders:
        entity = er['entity']
        screen_x = er['screen_x']
        screen_y = er['screen_y']
        entity_height = er['height']
        entity_scale = er['scale']
        entity_distance = er['distance']

        if screen_x < 0 or screen_x >= width:
            continue

        if entity['type'] == entity_system.ENTITY_PROJECTILE:

            if 'pattern' in entity:
                pattern = entity['pattern']
                pattern_height = len(pattern)
                pattern_width = len(pattern[0]) if pattern_height > 0 else 0

                size_scale = min(1.0, 1.5 / max(1.0, entity_distance * 0.3))
                draw_height = max(1, int(pattern_height * size_scale))
                draw_width = max(1, int(pattern_width * size_scale))

                start_x = screen_x - draw_width // 2
                start_y = screen_y - draw_height // 2

                pulse_factor = 1.0
                if entity.get('glow', False):
                    elapsed = time.time() - entity['creation_time']
                    pulse_phase = elapsed * entity.get('pulse_rate', 5.0)
                    pulse_factor = 0.7 + 0.3 * math.sin(pulse_phase * 2 * math.pi)

                brightness = min(1.0, pulse_factor / max(0.5, entity_distance * 0.1))

                if brightness > 0.8:
                    color_attr = curses.color_pair(entity['color']) | curses.A_BOLD
                elif brightness > 0.4:
                    color_attr = curses.color_pair(entity['color'])
                else:
                    color_attr = curses.color_pair(entity['color']) | curses.A_DIM

                for local_y in range(draw_height):
                    pattern_y = min(pattern_height - 1, int(local_y / draw_height * pattern_height))
                    screen_pos_y = start_y + local_y

                    if screen_pos_y < 0 or screen_pos_y >= height:
                        continue

                    for local_x in range(draw_width):
                        pattern_x = min(pattern_width - 1, int(local_x / draw_width * pattern_width))
                        screen_pos_x = start_x + local_x

                        if screen_pos_x < 0 or screen_pos_x >= width:
                            continue

                        is_visible = True
                        for segment in wall_segments:
                            if segment['column'] == screen_pos_x and segment['distance'] < entity_distance:
                                is_visible = False
                                break

                        if is_visible and pattern_x < len(pattern[pattern_y]):
                            char = pattern[pattern_y][pattern_x]
                            if char != ' ':
                                try:
                                    stdscr.addch(screen_pos_y, screen_pos_x, char, color_attr)
                                except curses.error:
                                    pass

            else:

                try:

                    is_visible = True
                    for segment in wall_segments:
                        if segment['column'] == screen_x and segment['distance'] < entity_distance:
                            is_visible = False
                            break

                    if is_visible:
                        color = curses.color_pair(entity['color']) | curses.A_BOLD
                        stdscr.addch(screen_y, screen_x, entity.get('char', '*'), color)
                except curses.error:
                    pass

        elif entity['type'] == entity_system.ENTITY_ENEMY:

            display_text = entity_system.get_enemy_display_text(entity, entity_distance)

            if entity['state'] == 'dead':
                color_attr = curses.color_pair(entity_system.ENEMY_DEAD_COLOR)
            elif entity['state'] == 'attack':

                if int(time.time() * 4) % 2 == 0:
                    color_attr = curses.color_pair(entity_system.ENEMY_COLOR) | curses.A_BOLD
                else:
                    color_attr = curses.color_pair(entity_system.ENEMY_ALERT_COLOR) | curses.A_BOLD
            elif entity['state'] == 'chase':
                color_attr = curses.color_pair(entity_system.ENEMY_ALERT_COLOR)
            else:
                color_attr = curses.color_pair(entity['color'])

            text_height = len(display_text)
            scaled_height = max(1, min(text_height, int(text_height * entity_scale)))

            for i in range(scaled_height):
                if i >= len(display_text):
                    break

                line = display_text[i]
                text_width = len(line)

                scaled_width = max(1, min(text_width, int(text_width * entity_scale)))

                text_start_x = screen_x - scaled_width // 2

                for j in range(scaled_width):
                    screen_pos_x = text_start_x + j
                    screen_pos_y = screen_y + i

                    if screen_pos_x < 0 or screen_pos_x >= width or screen_pos_y < 0 or screen_pos_y >= height:
                        continue

                    is_visible = True
                    for segment in wall_segments:
                        if segment['column'] == screen_pos_x and segment['distance'] < entity_distance:
                            is_visible = False
                            break

                    if is_visible and j < len(line):

                        try:
                            char = line[j]
                            stdscr.addch(screen_pos_y, screen_pos_x, char, color_attr)
                        except curses.error:
                            pass

    render_minimap(stdscr, player_x, player_y, player_angle, world_map, world_colors, height, width)

    status = f"WASD: Move | Arrows: Turn | Space: Shoot | E: Interact | Q: Quit | M: Map"
    stdscr.addstr(height, 0, status[:width - 1], curses.A_BOLD)

    stdscr.noutrefresh()


def render_minimap(stdscr, player_x, player_y, player_angle, world_map, world_colors, height, width):
    """Render an enhanced Aardwolf-style minimap in the corner of the screen"""

    map_size = 16

    map_start_x = width - map_size - 2
    map_start_y = 1

    border_color = curses.color_pair(7) | curses.A_BOLD

    map_title = "[ MAP ]"
    left_border = "╔═"
    right_border = "═╗"
    title_space = map_size - len(left_border) - len(right_border) + 2

    title_padding = (title_space - len(map_title)) // 2
    title_border = "═" * title_padding + map_title + "═" * (title_space - len(map_title) - title_padding)

    stdscr.addstr(map_start_y, map_start_x, left_border + title_border + right_border, border_color)

    for y in range(1, map_size + 1):
        stdscr.addstr(map_start_y + y, map_start_x, "║", border_color)
        stdscr.addstr(map_start_y + y, map_start_x + map_size + 1, "║", border_color)

    stdscr.addstr(map_start_y + map_size + 1, map_start_x, "╚" + "═" * map_size + "╝", border_color)

    view_radius = map_size // 2

    center_x = int(player_x)
    center_y = int(player_y)

    start_x = max(0, center_x - view_radius)
    start_y = max(0, center_y - view_radius)
    end_x = min(len(world_map[0]), center_x + view_radius + 1)
    end_y = min(len(world_map), center_y + view_radius + 1)

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

    for map_y in range(start_y, end_y):
        for map_x in range(start_x, end_x):

            mini_x = map_start_x + 1 + (map_x - start_x)
            mini_y = map_start_y + 1 + (map_y - start_y)

            if 0 <= mini_y <= map_start_y + map_size and 0 <= mini_x <= map_start_x + map_size:
                cell_type = world_map[map_y][map_x]
                cell_color = int(world_colors[map_y][map_x])

                cell_char = terrain_chars.get(cell_type, '?')

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

                try:
                    stdscr.addch(mini_y, mini_x, cell_char, style)
                except curses.error:
                    pass

    import entities as entity_system

    for entity in entity_system.entities:

        mini_x = map_start_x + 1 + int(entity['x'] - start_x)
        mini_y = map_start_y + 1 + int(entity['y'] - start_y)

        if (map_start_y <= mini_y <= map_start_y + map_size and
                map_start_x <= mini_x <= map_start_x + map_size):

            if entity['type'] == entity_system.ENTITY_PROJECTILE:
                char = '⊙'
                style = curses.color_pair(entity_system.PROJECTILE_COLOR) | curses.A_BOLD
            elif entity['type'] == entity_system.ENTITY_ENEMY:
                if entity['state'] == 'dead':
                    char = 'x'
                    style = curses.color_pair(entity_system.ENEMY_DEAD_COLOR)
                else:
                    char = 'E'
                    style = curses.color_pair(entity_system.ENEMY_COLOR)
                    if entity['state'] in ['chase', 'attack']:
                        style |= curses.A_BOLD
            else:
                char = '?'
                style = curses.color_pair(7)

            try:
                stdscr.addch(mini_y, mini_x, char, style)
            except curses.error:
                pass

    player_mini_x = map_start_x + 1 + int(player_x - start_x)
    player_mini_y = map_start_y + 1 + int(player_y - start_y)

    if (map_start_y < player_mini_y < map_start_y + map_size and
            map_start_x < player_mini_x < map_start_x + map_size):
        try:

            player_char = '@'
            player_style = curses.color_pair(1) | curses.A_BOLD
            stdscr.addch(player_mini_y, player_mini_x, player_char, player_style)

            dir_x = int(player_mini_x + math.cos(player_angle))
            dir_y = int(player_mini_y + math.sin(player_angle))
            if (map_start_y < dir_y < map_start_y + map_size and
                    map_start_x < dir_x < map_start_x + map_size):
                try:
                    stdscr.addch(dir_y, dir_x, '*', curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
        except curses.error:
            pass

    compass_x = map_start_x + 2
    compass_y = map_start_y + map_size
    try:
        stdscr.addstr(compass_y, compass_x, "N↑", curses.color_pair(7) | curses.A_DIM)
    except curses.error:
        pass


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
