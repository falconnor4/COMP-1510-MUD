import math
import curses
import time
from debug import toggle_console, process_input, DEBUG_CONSOLE
from utils.collision import would_collide


def create_player(x=1.5, y=1.5, angle=0.0):
    """
    Initialize and return a new player state dictionary with default values.

    :param x: float, initial x-coordinate of the player. Defaults to 1.5.
    :param y: float, initial y-coordinate of the player. Defaults to 1.5.
    :param angle: float, initial viewing angle of the player in radians. Defaults to 0.0.
    :precondition: x, y, angle should be numeric values.
    :postcondition: Returns a dictionary representing the player's state.
    :return: dict, the player state dictionary.
    >>> p = create_player()
    >>> p['x'] == 1.5 and p['y'] == 1.5 and p['angle'] == 0.0
    True
    >>> p['health'] == 100 and p['level'] == 1
    True
    >>> p2 = create_player(x=5.0, y=10.0, angle=math.pi)
    >>> p2['x'] == 5.0 and p2['y'] == 10.0 and p2['angle'] == math.pi
    True
    """
    return {
        "x": x,
        "y": y,
        "angle": angle,
        "velocity_x": 0.0,
        "velocity_y": 0.0,
        "velocity_angle": 0.0,
        "max_speed": 3.0,
        "acceleration": 8.0,
        "friction": 4.0,
        "rotation_acceleration": math.pi,
        "rotation_friction": math.pi * 1.5,
        "bob_amplitude": 0.1,
        "bob_frequency": 7.0,
        "bob_phase": 0.0,
        "bob_offset": 0.0,
        "is_moving": False,
        "base_speed": 3.0,
        "rotation_speed": math.pi,
        "active_keys": set(),
        "key_timestamps": {},
        "map_mode": False,
        "last_shot_time": 0,
        "shot_cooldown": 0.5,
        "health": 100,
        "max_health": 100,
        "level": 1,
        "exp": 0,
        "exp_to_next": 100,
        "stages_descended": 0,
        "kills": 0,
    }


def update_input(player_state, key, pressed=True):
    """
    Update the player's active key set and timestamps based on key events.

    Handles toggling the debug console (';') and map mode ('m').
    Passes input to the debug console if it's active.

    :param player_state: dict, the player's state dictionary.
    :param key: int, the key code received (e.g., from curses.getch()).
    :param pressed: bool, True if the key was pressed, False if released. Defaults to True.
    :precondition: player_state must be a valid player dictionary with 'active_keys' and 'key_timestamps'.
    :precondition: DEBUG_CONSOLE dictionary must exist.
    :postcondition: Modifies player_state['active_keys'] and player_state['key_timestamps'].
    :postcondition: May toggle DEBUG_CONSOLE['active'] or player_state['map_mode'].
    :postcondition: May call debug.process_input if console is active.
    :return: bool, True if the quit key ('q' or 'Q') was pressed and console is inactive, False otherwise.
    """
    if DEBUG_CONSOLE["active"]:
        process_input(key, player_state)
        return False

    if pressed and key != -1:
        if key == ord(";"):
            toggle_console()
            return False

        player_state["active_keys"].add(key)
        player_state["key_timestamps"][key] = time.time()

        if key == ord("m") or key == ord("M"):
            player_state["map_mode"] = not player_state["map_mode"]
    elif not pressed and key != -1:

        if key in player_state["active_keys"]:
            player_state["active_keys"].remove(key)

        if key in player_state["key_timestamps"]:
            del player_state["key_timestamps"][key]

    return key == ord("q") or key == ord("Q")


def check_key_timeout(player_state, current_time, timeout=0.5):
    """
    Remove keys from the active set if they haven't been pressed recently.

    Helps prevent keys getting "stuck" if release events are missed.

    :param player_state: dict, the player's state dictionary.
    :param current_time: float, the current time.
    :param timeout: float, the duration in seconds after which a key is considered timed out. Defaults to 0.5.
    :precondition: player_state must be a valid player dictionary with 'active_keys' and 'key_timestamps'.
    :postcondition: Removes timed-out keys from player_state['active_keys'] and player_state['key_timestamps'].
    :return: None
    """
    keys_to_remove = []

    for key, timestamp in player_state["key_timestamps"].items():
        if current_time - timestamp > timeout:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        player_state["active_keys"].discard(key)
        del player_state["key_timestamps"][key]


def update_player(player_state, delta_time, world_map):
    """
    Update player physics, position, angle, and head bob based on active keys and collisions.

    Calculates forces, applies acceleration and friction, checks for collisions,
    and updates player state accordingly. Also determines if shoot or interact actions
    were triggered.

    :param player_state: dict, the player's state dictionary.
    :param delta_time: float, the time elapsed since the last frame.
    :param world_map: list[list[int]], the current map grid for collision detection.
    :precondition: player_state must be a valid player dictionary. delta_time >= 0.
    :precondition: world_map must be a valid map structure. `would_collide` function must be available.
    :postcondition: Updates player_state['x', 'y', 'angle', 'velocity_x', 'velocity_y', 'velocity_angle', 'is_moving', 'bob_phase', 'bob_offset'].
    :postcondition: Removes shoot (' ') and interact ('e'/'E') keys from 'active_keys' if they were processed.
    :return: tuple[bool, bool], flags indicating if shoot and interact actions should occur this frame.
    """
    check_key_timeout(player_state, time.time())

    active_keys = player_state["active_keys"]

    force_x, force_y = 0, 0
    force_angle = 0

    if ord("w") in active_keys or ord("W") in active_keys:
        force_x += math.cos(player_state["angle"])
        force_y += math.sin(player_state["angle"])
    if ord("s") in active_keys or ord("S") in active_keys:
        force_x -= math.cos(player_state["angle"])
        force_y -= math.sin(player_state["angle"])

    if ord("a") in active_keys or ord("A") in active_keys:
        force_x += math.sin(player_state["angle"])
        force_y -= math.cos(player_state["angle"])
    if ord("d") in active_keys or ord("D") in active_keys:
        force_x -= math.sin(player_state["angle"])
        force_y += math.cos(player_state["angle"])

    if curses.KEY_LEFT in active_keys:
        force_angle -= 1.0
    if curses.KEY_RIGHT in active_keys:
        force_angle += 1.0

    if force_x != 0 or force_y != 0:
        magnitude = math.sqrt(force_x * force_x + force_y * force_y)
        if magnitude > 0:
            force_x /= magnitude
            force_y /= magnitude

    player_state["velocity_x"] += force_x * player_state["acceleration"] * delta_time
    player_state["velocity_y"] += force_y * player_state["acceleration"] * delta_time
    player_state["velocity_angle"] += (
        force_angle * player_state["rotation_acceleration"] * delta_time
    )

    friction_x = -player_state["velocity_x"] * player_state["friction"] * delta_time
    friction_y = -player_state["velocity_y"] * player_state["friction"] * delta_time
    friction_angle = (
        -player_state["velocity_angle"] * player_state["rotation_friction"] * delta_time
    )

    if abs(friction_x) > abs(player_state["velocity_x"]):
        player_state["velocity_x"] = 0
    else:
        player_state["velocity_x"] += friction_x

    if abs(friction_y) > abs(player_state["velocity_y"]):
        player_state["velocity_y"] = 0
    else:
        player_state["velocity_y"] += friction_y

    if abs(friction_angle) > abs(player_state["velocity_angle"]):
        player_state["velocity_angle"] = 0
    else:
        player_state["velocity_angle"] += friction_angle

    speed = math.sqrt(player_state["velocity_x"] ** 2 + player_state["velocity_y"] ** 2)
    if speed > player_state["max_speed"]:
        player_state["velocity_x"] = (
            player_state["velocity_x"] / speed
        ) * player_state["max_speed"]
        player_state["velocity_y"] = (
            player_state["velocity_y"] / speed
        ) * player_state["max_speed"]

    new_x = player_state["x"] + player_state["velocity_x"] * delta_time
    new_y = player_state["y"] + player_state["velocity_y"] * delta_time
    new_angle = player_state["angle"] + player_state["velocity_angle"] * delta_time

    if would_collide(player_state["x"], player_state["y"], new_x, new_y, world_map):

        if not would_collide(
            player_state["x"], player_state["y"], new_x, player_state["y"], world_map
        ):
            new_y = player_state["y"]

            player_state["velocity_y"] *= 0.1

        elif not would_collide(
            player_state["x"], player_state["y"], player_state["x"], new_y, world_map
        ):
            new_x = player_state["x"]

            player_state["velocity_x"] *= 0.1
        else:

            new_x, new_y = player_state["x"], player_state["y"]
            player_state["velocity_x"] *= 0.1
            player_state["velocity_y"] *= 0.1

    player_state["x"], player_state["y"] = new_x, new_y
    player_state["angle"] = new_angle % (2 * math.pi)

    is_moving = (
        abs(player_state["velocity_x"]) > 0.1 or abs(player_state["velocity_y"]) > 0.1
    )
    player_state["is_moving"] = is_moving

    update_head_bob(player_state, delta_time, speed)

    should_shoot = ord(" ") in active_keys
    should_interact = ord("e") in active_keys or ord("E") in active_keys

    if should_shoot:
        player_state["active_keys"].discard(ord(" "))

    if should_interact:
        player_state["active_keys"].discard(ord("e"))
        player_state["active_keys"].discard(ord("E"))

    return should_shoot, should_interact


def update_head_bob(player_state, delta_time, speed):
    """
    Update the head bobbing effect based on player movement speed.

    Calculates a vertical offset using a sine wave that depends on movement speed and time.

    :param player_state: dict, the player's state dictionary.
    :param delta_time: float, the time elapsed since the last frame.
    :param speed: float, the player's current movement speed.
    :precondition: player_state must be a valid player dictionary with bobbing parameters. delta_time >= 0.
    :postcondition: Updates player_state['bob_phase'] and player_state['bob_offset'].
    :return: None
    """
    if player_state["is_moving"]:
        player_state["bob_phase"] += (
            delta_time
            * player_state["bob_frequency"]
            * min(speed, player_state["max_speed"])
        )
        player_state["bob_offset"] = (
            math.sin(player_state["bob_phase"]) * player_state["bob_amplitude"]
        )
    else:
        if abs(player_state["bob_offset"]) > 0.01:
            player_state["bob_offset"] *= 0.8
        else:
            player_state["bob_offset"] = 0
            player_state["bob_phase"] = 0
