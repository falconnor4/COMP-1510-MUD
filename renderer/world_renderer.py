import curses
import math
import random
import time

import entities as entity_system
from anim.hand.fire import FireFrames
from renderer.color_utils import get_color_pair

DENSE_SHADING = " ░▒▓█"
DETAILED_SHADING = " .,:;i1tfLCG08@"
UNICODE_BLOCKS = " ▏▎▍▌▋▊▉█"

SHADING_CHARS = " .'`,:;!-+=iIl|/\\tfjrxnuvcTYUJCLQ0OZ#MW&8%B@$"

WALL_EDGE_CHARS = {
    "top": "▁",
    "bottom": "▔",
    "left": "▏",
    "right": "▕",
    "top_left": "▗",
    "top_right": "▖",
    "bottom_left": "▝",
    "bottom_right": "▘",
}


def get_shading_set(wall_orientation="vertical"):
    """Get appropriate shading set based on wall orientation"""
    if wall_orientation == "horizontal":
        return "═╤╥╦╣╮╕┐┌╭╓╒╔╔║╠╟╞╡┤╢╖╗╝╜╛┘┙╙╚╔╦╦╤╥"
    return SHADING_CHARS


def get_distance_shade(distance, max_distance=40, wall_x=0, wall_y=0):
    """Get appropriate shading character and attributes based on distance"""
    norm_distance = min(1.0, distance / max_distance)
    shade_idx = min(
        len(SHADING_CHARS) - 1, int((1 - norm_distance) * len(SHADING_CHARS))
    )
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
        _, max_x = stdscr.getmaxyx()
    except:
        return

    frame_lines = FireFrames[0].split("\n")
    anim_height = len(frame_lines)
    anim_width = max(len(line) for line in frame_lines)

    try:
        tmpwin = curses.newpad(anim_height, anim_width)
        prepared_frames = []

        for frame in FireFrames:
            tmpwin.clear()
            lines = frame.split("\n")

            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    if char != " " and char != "\t":
                        try:
                            tmpwin.addch(
                                i, j, char, curses.color_pair(1) | curses.A_BOLD
                            )
                        except:
                            pass

            prepared_frames.append(tmpwin.instr(0, 0, anim_height * anim_width))

        return prepared_frames

    except:
        return None


def render_world(
    stdscr, player_x, player_y, player_angle, world_map, world_colors, player_state=None
):
    """Render the world using ASCII characters with colored walls and Unicode edges"""
    height, width = stdscr.getmaxyx()
    height -= 1
    resolution = 1
    fov = math.pi / 3

    stdscr.erase()

    eye_height_offset = player_state.get("bob_offset", 0) if player_state else 0

    ceiling_chars = ".:'"
    floor_chars = ".,;:"

    for y in range(height // 2):
        stdscr.addstr(
            y,
            0,
            ceiling_chars[
                min(len(ceiling_chars) - 1, int(y / (height / 2) * len(ceiling_chars)))
            ]
            * width,
            curses.color_pair(9),
        )

    for y in range(height // 2, height):
        stdscr.addstr(
            y,
            0,
            floor_chars[
                min(
                    len(floor_chars) - 1,
                    int((y - height // 2) / (height / 2) * len(floor_chars)),
                )
            ]
            * width,
            curses.color_pair(8),
        )

    wall_segments = []
    entity_renders = []

    for column in range(0, width, resolution):
        ray_offset = (column / width - 0.5) * fov
        column_angle = player_angle + ray_offset

        distance_to_wall = 0
        hit_wall = False
        wall_x, wall_y = player_x, player_y
        current_color = 7
        wall_orientation = "vertical"

        while not hit_wall and distance_to_wall < 20:
            distance_to_wall += 0.05
            test_x = player_x + distance_to_wall * math.cos(column_angle)
            test_y = player_y + distance_to_wall * math.sin(column_angle)

            if not (
                0 <= int(test_x) < len(world_map[0])
                and 0 <= int(test_y) < len(world_map)
            ):
                hit_wall = True
                distance_to_wall = 20
            else:
                cell_type = world_map[int(test_y)][int(test_x)]
                if cell_type not in [0, 4, 9]:
                    hit_wall = True
                    wall_x, wall_y = int(test_x), int(test_y)
                    current_color = world_colors[int(test_y)][int(test_x)]
                    wall_orientation = (
                        "vertical"
                        if abs(test_x - int(test_x)) < abs(test_y - int(test_y))
                        else "horizontal"
                    )

        distance_to_wall *= math.cos(ray_offset)
        wall_height = min(height, int(height / distance_to_wall * 2))
        bob_pixels = int(eye_height_offset * height / 4)

        wall_top = max(0, height // 2 - wall_height // 2 + bob_pixels)
        wall_bottom = min(height - 1, height // 2 + wall_height // 2 + bob_pixels)

        if hit_wall and distance_to_wall < 20:
            wall_segments.append(
                {
                    "column": column,
                    "top": wall_top,
                    "bottom": wall_bottom,
                    "distance": distance_to_wall,
                    "color": current_color,
                    "orientation": wall_orientation,
                    "wall_x": wall_x,
                    "wall_y": wall_y,
                }
            )

    for entity in entity_system.entities:
        dx = entity["x"] - player_x
        dy = entity["y"] - player_y
        entity_distance = math.sqrt(dx * dx + dy * dy)

        if entity_distance > 20.0:
            continue

        entity_angle = math.atan2(dy, dx)
        relative_angle = entity_angle - player_angle
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi

        if abs(relative_angle) > fov / 2:
            continue

        screen_x = int(width * (0.5 + relative_angle / fov))
        entity_scale = 1.0 / max(1.0, entity_distance * 0.2)
        entity_height = int(min(height / 2, 8.0 / max(1.0, entity_distance * 0.2)))
        bob_pixels = (
            int(player_state["bob_offset"] * height / 4)
            if player_state and "bob_offset" in player_state
            else 0
        )
        entity_y = height // 2 - entity_height // 2 + bob_pixels

        entity_renders.append(
            {
                "entity": entity,
                "screen_x": screen_x,
                "screen_y": entity_y,
                "height": entity_height,
                "scale": entity_scale,
                "distance": entity_distance,
                "in_view": True,
            }
        )

    for i, segment in enumerate(wall_segments):
        (
            column,
            wall_top,
            wall_bottom,
            distance_to_wall,
            current_color,
            wall_orientation,
            wall_x,
            wall_y,
        ) = (
            segment["column"],
            segment["top"],
            segment["bottom"],
            segment["distance"],
            segment["color"],
            segment["orientation"],
            segment["wall_x"],
            segment["wall_y"],
        )

        is_left_edge = (
            i == 0
            or abs(wall_segments[i - 1]["distance"] - distance_to_wall) > 0.5
            or abs(wall_segments[i - 1]["wall_x"] - wall_x) > 1
            or abs(wall_segments[i - 1]["wall_y"] - wall_y) > 1
        )

        is_right_edge = (
            i == len(wall_segments) - 1
            or abs(wall_segments[i + 1]["distance"] - distance_to_wall) > 0.5
            or abs(wall_segments[i + 1]["wall_x"] - wall_x) > 1
            or abs(wall_segments[i + 1]["wall_y"] - wall_y) > 1
        )

        shade_char, _ = get_distance_shade(distance_to_wall, 20, wall_x, wall_y)

        color_attr = get_color_pair(current_color)
        if distance_to_wall > 10:
            color_attr = color_attr | curses.A_DIM
        elif distance_to_wall < 3:
            color_attr = color_attr | curses.A_BOLD

        if wall_orientation == "horizontal" and distance_to_wall < 20:
            shade_char = get_shading_set("horizontal")[
                min(
                    len(get_shading_set("horizontal")) - 1,
                    get_shading_set().find(shade_char),
                )
            ]
            color_attr = color_attr | curses.A_DIM

        for y in range(wall_top, wall_bottom + 1):
            try:
                position_in_wall = (y - wall_top) / max(1, wall_bottom - wall_top)

                char = (
                    WALL_EDGE_CHARS["top"]
                    if y == wall_top
                    else (
                        WALL_EDGE_CHARS["bottom"]
                        if y == wall_bottom
                        else (
                            WALL_EDGE_CHARS["left"]
                            if is_left_edge and y > wall_top and y < wall_bottom
                            else (
                                WALL_EDGE_CHARS["right"]
                                if is_right_edge and y > wall_top and y < wall_bottom
                                else (
                                    SHADING_CHARS[
                                        min(
                                            len(SHADING_CHARS) - 1,
                                            SHADING_CHARS.find(shade_char) + 1,
                                        )
                                    ]
                                    if position_in_wall > 0.8
                                    else shade_char
                                )
                            )
                        )
                    )
                )

                stdscr.addch(y, column, char, color_attr)
            except curses.error:
                pass

    entity_renders.sort(key=lambda e: e["distance"], reverse=True)

    for er in entity_renders:
        entity, screen_x, screen_y, entity_height, entity_scale, entity_distance = (
            er["entity"],
            er["screen_x"],
            er["screen_y"],
            er["height"],
            er["scale"],
            er["distance"],
        )

        if screen_x < 0 or screen_x >= width:
            continue

        if entity["type"] == entity_system.ENTITY_PROJECTILE:
            if "pattern" in entity:
                pattern = entity["pattern"]
                pattern_height, pattern_width = len(pattern), (
                    len(pattern[0]) if len(pattern) > 0 else 0
                )

                size_scale = min(1.0, 1.5 / max(1.0, entity_distance * 0.3))
                draw_height, draw_width = max(1, int(pattern_height * size_scale)), max(
                    1, int(pattern_width * size_scale)
                )

                start_x, start_y = (
                    screen_x - draw_width // 2,
                    screen_y - draw_height // 2,
                )

                pulse_factor = (
                    0.7
                    + 0.3
                    * math.sin(
                        (time.time() - entity["creation_time"])
                        * entity.get("pulse_rate", 5.0)
                        * 2
                        * math.pi
                    )
                    if entity.get("glow", False)
                    else 1.0
                )

                brightness = min(1.0, pulse_factor / max(0.5, entity_distance * 0.1))

                color_attr = curses.color_pair(entity["color"]) | (
                    curses.A_BOLD
                    if brightness > 0.8
                    else curses.A_DIM if brightness <= 0.4 else 0
                )

                for local_y in range(draw_height):
                    pattern_y = min(
                        pattern_height - 1, int(local_y / draw_height * pattern_height)
                    )
                    screen_pos_y = start_y + local_y

                    if not (0 <= screen_pos_y < height):
                        continue

                    for local_x in range(draw_width):
                        pattern_x = min(
                            pattern_width - 1, int(local_x / draw_width * pattern_width)
                        )
                        screen_pos_x = start_x + local_x

                        if not (0 <= screen_pos_x < width):
                            continue

                        if all(
                            segment["column"] != screen_pos_x
                            or segment["distance"] >= entity_distance
                            for segment in wall_segments
                        ) and pattern_x < len(pattern[pattern_y]):
                            char = pattern[pattern_y][pattern_x]
                            if char != " ":
                                try:
                                    stdscr.addch(
                                        screen_pos_y, screen_pos_x, char, color_attr
                                    )
                                except curses.error:
                                    pass

            else:
                try:
                    if all(
                        segment["column"] != screen_x
                        or segment["distance"] >= entity_distance
                        for segment in wall_segments
                    ):
                        color = curses.color_pair(entity["color"]) | curses.A_BOLD
                        stdscr.addch(screen_y, screen_x, entity.get("char", "*"), color)
                except curses.error:
                    pass

        elif entity["type"] == entity_system.ENTITY_ENEMY:
            display_text = entity_system.get_enemy_display_text(entity, entity_distance)
            color_attr = (
                curses.color_pair(entity_system.ENEMY_DEAD_COLOR)
                if entity["state"] == "dead"
                else (
                    curses.color_pair(entity_system.ENEMY_ALERT_COLOR) | curses.A_BOLD
                    if entity["state"] == "attack" and int(time.time() * 4) % 2 == 0
                    else (
                        curses.color_pair(entity_system.ENEMY_ALERT_COLOR)
                        | curses.A_BOLD
                        if entity["state"] == "attack"
                        else (
                            curses.color_pair(entity_system.ENEMY_ALERT_COLOR)
                            if entity["state"] == "chase"
                            else curses.color_pair(entity["color"])
                        )
                    )
                )
            )

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

                    if not (0 <= screen_pos_x < width and 0 <= screen_pos_y < height):
                        continue

                    if all(
                        segment["column"] != screen_pos_x
                        or segment["distance"] >= entity_distance
                        for segment in wall_segments
                    ) and j < len(line):
                        try:
                            char = line[j]
                            stdscr.addch(screen_pos_y, screen_pos_x, char, color_attr)
                        except curses.error:
                            pass

    from renderer.minimap_renderer import render_minimap

    render_minimap(
        stdscr, player_x, player_y, player_angle, world_map, world_colors, height, width
    )

    status = (
        f"WASD: Move | Arrows: Turn | Space: Shoot | E: Interact | Q: Quit | M: Map"
    )
    stdscr.addstr(height, 0, status[: width - 1], curses.A_BOLD)
