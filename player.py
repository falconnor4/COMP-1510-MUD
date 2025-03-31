import math
import curses
import time
from debug import toggle_console, process_input, DEBUG_CONSOLE


def create_player(x=1.5, y=1.5, angle=0.0):
    """Create a new player state dictionary"""

    return {

        'x': x,
        'y': y,
        'angle': angle,

        'velocity_x': 0.0,
        'velocity_y': 0.0,
        'velocity_angle': 0.0,
        'max_speed': 3.0,
        'acceleration': 8.0,
        'friction': 4.0,
        'rotation_acceleration': math.pi,
        'rotation_friction': math.pi * 1.5,

        'bob_amplitude': 0.1,
        'bob_frequency': 7.0,
        'bob_phase': 0.0,
        'bob_offset': 0.0,
        'is_moving': False,

        'base_speed': 3.0,
        'rotation_speed': math.pi,

        'active_keys': set(),
        'key_timestamps': {},

        'map_mode': False,

        'last_shot_time': 0,
        'shot_cooldown': 0.5,

        'health': 100,
        'max_health': 100,  #HP actually stands for Hopeful Perserverance,
        'level': 1,  #LVL actually stands for lost vital links,
        'exp': 0,
        'exp_to_next': 100,
        'stages_descended': 0,
        'kills': 0
    }


def update_input(player_state, key, pressed=True):
    """Update key state based on input"""
    # Check if debug console is active
    if DEBUG_CONSOLE['active']:
        # Process all keys through debug console with player state
        process_input(key, player_state)
        return False  # Don't quit while in debug console

    if pressed and key != -1:
        # Add semicolon key to activate debug console
        if key == ord(';'):
            toggle_console()
            return False

        player_state['active_keys'].add(key)
        player_state['key_timestamps'][key] = time.time()

        if key == ord('m') or key == ord('M'):
            player_state['map_mode'] = not player_state['map_mode']
    elif not pressed and key != -1:

        if key in player_state['active_keys']:
            player_state['active_keys'].remove(key)

        if key in player_state['key_timestamps']:
            del player_state['key_timestamps'][key]

    return key == ord('q') or key == ord('Q')


def check_key_timeout(player_state, current_time, timeout=0.5):
    """Check if any keys have timed out from inactivity"""
    keys_to_remove = []

    for key, timestamp in player_state['key_timestamps'].items():
        if current_time - timestamp > timeout:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        player_state['active_keys'].discard(key)
        del player_state['key_timestamps'][key]


def update_player(player_state, delta_time, world_map):
    """Update player position and state based on inputs"""

    check_key_timeout(player_state, time.time())

    active_keys = player_state['active_keys']

    force_x, force_y = 0, 0
    force_angle = 0

    if ord('w') in active_keys or ord('W') in active_keys:
        force_x += math.cos(player_state['angle'])
        force_y += math.sin(player_state['angle'])
    if ord('s') in active_keys or ord('S') in active_keys:
        force_x -= math.cos(player_state['angle'])
        force_y -= math.sin(player_state['angle'])

    if ord('a') in active_keys or ord('A') in active_keys:
        force_x += math.sin(player_state['angle'])
        force_y -= math.cos(player_state['angle'])
    if ord('d') in active_keys or ord('D') in active_keys:
        force_x -= math.sin(player_state['angle'])
        force_y += math.cos(player_state['angle'])

    if curses.KEY_LEFT in active_keys:
        force_angle -= 1.0
    if curses.KEY_RIGHT in active_keys:
        force_angle += 1.0

    if force_x != 0 or force_y != 0:
        magnitude = math.sqrt(force_x * force_x + force_y * force_y)
        if magnitude > 0:
            force_x /= magnitude
            force_y /= magnitude

    player_state['velocity_x'] += force_x * player_state['acceleration'] * delta_time
    player_state['velocity_y'] += force_y * player_state['acceleration'] * delta_time
    player_state['velocity_angle'] += force_angle * player_state['rotation_acceleration'] * delta_time

    friction_x = -player_state['velocity_x'] * player_state['friction'] * delta_time
    friction_y = -player_state['velocity_y'] * player_state['friction'] * delta_time
    friction_angle = -player_state['velocity_angle'] * player_state['rotation_friction'] * delta_time

    if abs(friction_x) > abs(player_state['velocity_x']):
        player_state['velocity_x'] = 0
    else:
        player_state['velocity_x'] += friction_x

    if abs(friction_y) > abs(player_state['velocity_y']):
        player_state['velocity_y'] = 0
    else:
        player_state['velocity_y'] += friction_y

    if abs(friction_angle) > abs(player_state['velocity_angle']):
        player_state['velocity_angle'] = 0
    else:
        player_state['velocity_angle'] += friction_angle

    speed = math.sqrt(player_state['velocity_x'] ** 2 + player_state['velocity_y'] ** 2)
    if speed > player_state['max_speed']:
        player_state['velocity_x'] = (player_state['velocity_x'] / speed) * player_state['max_speed']
        player_state['velocity_y'] = (player_state['velocity_y'] / speed) * player_state['max_speed']

    new_x = player_state['x'] + player_state['velocity_x'] * delta_time
    new_y = player_state['y'] + player_state['velocity_y'] * delta_time
    new_angle = player_state['angle'] + player_state['velocity_angle'] * delta_time

    if would_collide(player_state['x'], player_state['y'], new_x, new_y, world_map):

        if not would_collide(player_state['x'], player_state['y'], new_x, player_state['y'], world_map):
            new_y = player_state['y']

            player_state['velocity_y'] *= 0.1

        elif not would_collide(player_state['x'], player_state['y'], player_state['x'], new_y, world_map):
            new_x = player_state['x']

            player_state['velocity_x'] *= 0.1
        else:

            new_x, new_y = player_state['x'], player_state['y']
            player_state['velocity_x'] *= 0.1
            player_state['velocity_y'] *= 0.1

    player_state['x'], player_state['y'] = new_x, new_y
    player_state['angle'] = new_angle % (2 * math.pi)

    is_moving = (abs(player_state['velocity_x']) > 0.1 or abs(player_state['velocity_y']) > 0.1)
    player_state['is_moving'] = is_moving

    update_head_bob(player_state, delta_time, speed)

    should_shoot = ord(' ') in active_keys
    should_interact = ord('e') in active_keys or ord('E') in active_keys

    if should_shoot:
        player_state['active_keys'].discard(ord(' '))

    if should_interact:
        player_state['active_keys'].discard(ord('e'))
        player_state['active_keys'].discard(ord('E'))

    return should_shoot, should_interact


def update_head_bob(player_state, delta_time, speed):
    """Update head bobbing offset based on movement"""
    if player_state['is_moving']:

        player_state['bob_phase'] += delta_time * player_state['bob_frequency'] * min(speed, player_state['max_speed'])

        player_state['bob_offset'] = math.sin(player_state['bob_phase']) * player_state['bob_amplitude']
    else:

        if abs(player_state['bob_offset']) > 0.01:

            player_state['bob_offset'] *= 0.8
        else:
            player_state['bob_offset'] = 0
            player_state['bob_phase'] = 0


def is_collision(x, y, world_map):
    """Check if the player would collide with a wall"""
    grid_x = int(x)
    grid_y = int(y)

    if grid_y < 0 or grid_y >= len(world_map) or grid_x < 0 or grid_x >= len(world_map[0]):
        return True

    walkable_types = [0, 4, 9]
    if world_map[grid_y][grid_x] not in walkable_types:
        return True

    return False


def would_collide(x, y, new_x, new_y, world_map):
    """Advanced collision check with buffer zone"""

    if is_collision(new_x, new_y, world_map):
        return True

    steps = 3
    for i in range(1, steps):

        check_x = x + (new_x - x) * i / steps
        check_y = y + (new_y - y) * i / steps

        if is_collision(check_x, check_y, world_map):
            return True

    return False
