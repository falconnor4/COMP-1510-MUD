import curses
import time
import math
from anim.hand.fire import FireFrames
from renderer.console_renderer import render_console, DEBUG_CONSOLE

UI_MESSAGE = "message"
UI_STATUS = "status"
UI_INVENTORY = "inventory"
UI_ANIMATION = "animation"

ui_elements = []

current_animation = {
    "active": False,
    "type": None,
    "frame_index": 0,
    "last_frame_time": 0,
    "frame_delay": 0.1,
    "frames": FireFrames,
    "midpoint_callback": None,
    "midpoint_triggered": False,
}


def add_message(text, duration=3.0, color=3, bold=True):
    """Add a message to be displayed on screen for a specified duration"""
    ui_elements.append(
        {
            "type": UI_MESSAGE,
            "text": text,
            "start_time": time.time(),
            "duration": duration,
            "color": color,
            "bold": bold,
        }
    )


def add_status_effect(text, icon, duration=None, color=4):
    """Add a status effect to be displayed until duration expires"""
    ui_elements.append(
        {
            "type": UI_STATUS,
            "text": text,
            "icon": icon,
            "start_time": time.time(),
            "duration": duration,
            "color": color,
        }
    )


def start_animation(animation_type="fire", midpoint_callback=None):
    """Start an animation sequence with optional midpoint callback"""
    global current_animation

    if animation_type == "fire":
        current_animation = {
            "active": True,
            "type": "fire",
            "frame_index": 0,
            "last_frame_time": time.time(),
            "frame_delay": 0.1,
            "frames": FireFrames,
            "midpoint_callback": midpoint_callback,
            "midpoint_triggered": False,
        }


# noinspection PyCallingNonCallable
def update_animation():
    """Update the current animation state"""
    global current_animation

    if not current_animation["active"]:
        current_animation["frame_index"] = 0
        current_animation["midpoint_triggered"] = False
        return False

    current_time = time.time()

    if (
        current_time - current_animation["last_frame_time"]
        > current_animation["frame_delay"]
    ):
        current_animation["frame_index"] += 1
        current_animation["last_frame_time"] = int(time.time())

        if (
            not current_animation["midpoint_triggered"]
            and current_animation["midpoint_callback"]
            and current_animation["frame_index"]
            >= len(current_animation["frames"]) // 2
        ):
            current_animation["midpoint_callback"]()
            current_animation["midpoint_triggered"] = True

        if current_animation["frame_index"] >= len(current_animation["frames"]):
            current_animation["active"] = False
            current_animation["frame_index"] = 0
            current_animation["midpoint_triggered"] = False
            return False

    return True


def _display_end_screen(stdscr, title, title_color, player_state):
    """Display the end screen with a given title and player stats."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(title_color) | curses.A_BOLD)
    stdscr.box()
    stdscr.attroff(curses.color_pair(title_color) | curses.A_BOLD)

    title_x = max(0, (width - len(title)) // 2)
    stdscr.attron(curses.color_pair(title_color) | curses.A_BOLD)
    stdscr.addstr(height // 2 - 5, title_x, title)
    stdscr.attroff(curses.color_pair(title_color) | curses.A_BOLD)

    stats = [
        f"Final Level: {player_state.get('level', 1)}",
        f"Depth Reached: {player_state.get('stages_descended', 0)}",
        f"Enemies Defeated: {player_state.get('kills', 0)}",
    ]

    stats_y = height // 2 - 2
    for i, stat in enumerate(stats):
        stat_x = max(0, (width - len(stat)) // 2)
        stdscr.attron(curses.color_pair(7))
        stdscr.addstr(stats_y + i, stat_x, stat)
        stdscr.attroff(curses.color_pair(7))

    footer_text = "Press any key to return to the menu"
    footer_x = max(0, (width - len(footer_text)) // 2)
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(height - 3, footer_x, footer_text)
    stdscr.attroff(curses.color_pair(3))

    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    stdscr.nodelay(True)


def display_game_over(stdscr, player_state):
    """Display the game over screen with player stats."""
    _display_end_screen(stdscr, "G A M E   O V E R", 1, player_state)


def display_win_screen(stdscr, player_state):
    """Display the win screen with the message."""
    _display_end_screen(stdscr, "and so they left", 6, player_state)


def clear_expired_elements(current_time):
    """Remove any UI elements that have expired"""
    global ui_elements
    ui_elements = [
        elem
        for elem in ui_elements
        if elem["duration"] is None
        or current_time - elem["start_time"] < elem["duration"]
    ]


def draw_player_stats(stdscr, player_state):
    """Draw player health, level and dungeon depth in the top-left corner"""
    if not player_state:
        return

    health = player_state.get("health", 100)
    max_health = player_state.get("max_health", 100)
    level = player_state.get("level", 1)
    depth = player_state.get("stages_descended", 0)
    exp = player_state.get("exp", 0)
    exp_to_next = player_state.get("exp_to_next", 100)
    kills = player_state.get("kills", 0)

    health_percent = health / max_health
    exp_percent = exp / exp_to_next

    bar_width = 20
    filled_health = int(bar_width * health_percent)
    filled_exp = int(bar_width * exp_percent)

    health_bar = f"[{'█' * filled_health}{'░' * (bar_width - filled_health)}]"
    exp_bar = f"[{'█' * filled_exp}{'░' * (bar_width - filled_exp)}]"

    level_text = f"LVL: {level}"
    health_text = f"HP: {health}/{max_health} {health_bar}"
    exp_text = f"XP: {exp}/{exp_to_next} {exp_bar}"
    depth_text = f"DEPTH: {depth}" if depth > 0 else "DEPTH: Surface"
    kills_text = f"KILLS: {kills}"

    try:

        stdscr.addstr(1, 2, level_text, curses.color_pair(3) | curses.A_BOLD)

        health_color = 2
        if health_percent < 0.3:
            health_color = 1
        elif health_percent < 0.7:
            health_color = 3
        stdscr.addstr(
            2, 2, health_text, curses.color_pair(health_color) | curses.A_BOLD
        )

        stdscr.addstr(3, 2, exp_text, curses.color_pair(6) | curses.A_BOLD)

        stdscr.addstr(4, 2, depth_text, curses.color_pair(5) | curses.A_BOLD)

        stdscr.addstr(5, 2, kills_text, curses.color_pair(1) | curses.A_BOLD)
    except curses.error:
        pass


def draw_ui_layer(stdscr, player_state=None):
    """Draw all active UI elements on top of the game view"""
    height, width = stdscr.getmaxyx()
    current_time = time.time()

    clear_expired_elements(current_time)

    if player_state:
        draw_player_stats(stdscr, player_state)

    messages = [elem for elem in ui_elements if elem["type"] == UI_MESSAGE]
    if messages:

        msg_height = min(len(messages) + 2, 5)
        msg_y = height - msg_height - 1

        messages.sort(key=lambda x: x["start_time"], reverse=True)
        for i, msg in enumerate(messages[: msg_height - 2]):

            time_left = msg["duration"] - (current_time - msg["start_time"])
            if time_left < 0.5:

                if time_left < 0.1:
                    continue
                style = curses.color_pair(msg["color"])
            else:
                style = curses.color_pair(msg["color"]) | (
                    curses.A_BOLD if msg["bold"] else 0
                )

            msg_x = (width - len(msg["text"])) // 2
            try:
                stdscr.addstr(msg_y + i + 1, msg_x, msg["text"], style)
            except curses.error:
                pass

    statuses = [elem for elem in ui_elements if elem["type"] == UI_STATUS]
    if statuses:
        status_x = 2
        for status in statuses:

            if status["duration"] is not None:
                time_left = status["duration"] - (current_time - status["start_time"])

                if time_left < 3.0 and int(current_time * (4 - time_left)) % 2 == 0:
                    continue

            try:
                status_text = f"{status['icon']} {status['text']}"
                stdscr.addstr(
                    1,
                    status_x,
                    status_text,
                    curses.color_pair(status["color"]) | curses.A_BOLD,
                )
                status_x += len(status_text) + 2
            except curses.error:
                pass

    draw_weapon_hud(stdscr)

    if current_animation["active"]:
        draw_animation_frame(stdscr)
        update_animation()

    if DEBUG_CONSOLE["active"]:
        render_console(stdscr)

    stdscr.noutrefresh()


def draw_weapon_hud(stdscr):
    """Draw the static weapon HUD using the first animation frame"""
    if not current_animation["active"] and FireFrames:
        draw_fire_frame(stdscr, FireFrames[0])


def draw_animation_frame(stdscr):
    """Draw the current animation frame"""
    if not current_animation["active"]:
        return

    frame_index = current_animation["frame_index"]
    if frame_index >= len(current_animation["frames"]):
        return

    current_frame = current_animation["frames"][frame_index]

    if current_animation["type"] == "fire":
        draw_fire_frame(stdscr, current_frame)


def draw_fire_frame(stdscr, frame):
    """Draw a fire animation frame at the bottom right of the screen"""
    height, width = stdscr.getmaxyx()

    lines = frame.split("\n")

    fixed_x = width - 118
    fixed_y = height - 65

    for i, line in enumerate(lines):
        y_pos = fixed_y + i

        if y_pos >= height or y_pos < 0:
            continue

        for j, char in enumerate(line):
            if char == " " or char == "\t":
                continue

            x_pos = fixed_x + j

            if 0 <= y_pos < height and 0 <= x_pos < width:
                try:

                    stdscr.addch(
                        y_pos, x_pos, char, curses.color_pair(1) | curses.A_BOLD
                    )
                except curses.error:
                    pass


def get_weapon_muzzle_position(screen_height, screen_width):
    """Get the position where projectiles should spawn from the weapon"""

    fixed_x = screen_width - 118
    fixed_y = screen_height - 65

    muzzle_offset_x = 20
    muzzle_offset_y = 16

    screen_x = fixed_x + muzzle_offset_x
    screen_y = fixed_y + muzzle_offset_y

    return {"screen_x": screen_x, "screen_y": screen_y}


def convert_screen_to_world(muzzle_pos, player_x, player_y, player_angle, distance=1.0):
    """Convert screen muzzle position to world coordinates"""

    side_offset = 0.3
    forward_offset = 0.6

    right_vector_x = math.cos(player_angle + math.pi / 2) * side_offset
    right_vector_y = math.sin(player_angle + math.pi / 2) * side_offset

    forward_x = math.cos(player_angle) * forward_offset
    forward_y = math.sin(player_angle) * forward_offset

    world_x = player_x + forward_x + right_vector_x
    world_y = player_y + forward_y + right_vector_y

    return world_x, world_y
