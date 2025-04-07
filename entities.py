import math
import random
import time
import ui
from utils.collision import is_collision
from utils.math_utils import distance_between, has_line_of_sight
from anim.enemies.enemy_art import (
    ENEMY_ASCII,
    DEATH_ASCII,
    BOSS_ASCII,
    BOSS_DEATH_ASCII,
)
from anim.projectiles.projectile_art import (
    PROJECTILE_PATTERNS,
    ENEMY_PROJECTILE_PATTERNS,
)

entities = []
projectiles = []
enemies = []
enemy_projectiles = []

ENTITY_PROJECTILE = "projectile"
ENTITY_ENEMY = "enemy"
ENTITY_ENEMY_PROJECTILE = "enemy_projectile"

ENEMY_COLOR = 1
ENEMY_ALERT_COLOR = 5
ENEMY_DEAD_COLOR = 8
PROJECTILE_COLOR = 3
ENEMY_XP_VALUE = 50
ENEMY_PROJECTILE_COLOR = 1
ENEMY_PROJECTILE_DAMAGE = 15


def create_projectile(x, y, angle, speed=5.0, lifetime=1.5, damage=25):
    """
    Create a new projectile entity at the given position and angle.
    :param x: x-coordinate of the projectile's starting position
    :param y: y-coordinate of the projectile's starting position
    :param angle: direction in radians that the projectile will travel
    :param speed: velocity of the projectile (default 5.0)
    :param lifetime: duration in seconds before projectile disappears (default 1.5)
    :param damage: amount of damage the projectile inflicts (default 25)
    :precondition: x and y must be valid coordinates in the game world
    :precondition: angle must be in radians between 0 and 2π
    :precondition: speed, lifetime, and damage must be positive numbers
    :postcondition: creates a projectile entity at the specified position with the given properties
    :return: the newly created projectile entity as a dictionary
    >>> proj = create_projectile(5.0, 5.0, 0.0)
    >>> proj["type"] == ENTITY_PROJECTILE
    True
    >>> proj["x"] == 5.0 and proj["y"] == 5.0 and proj["angle"] == 0.0
    True
    >>> proj["speed"] == 5.0 and proj["damage"] == 25
    True
    """

    pattern = random.choice(PROJECTILE_PATTERNS)

    projectile = {
        "type": ENTITY_PROJECTILE,
        "x": x,
        "y": y,
        "z": 0.5,
        "angle": angle,
        "speed": speed,
        "creation_time": time.time(),
        "lifetime": lifetime,
        "damage": damage,
        "pattern": pattern,
        "width": len(pattern[0]),
        "height": len(pattern),
        "color": PROJECTILE_COLOR,
        "glow": True,
        "pulse_rate": 4.0,
        "remove": False,
    }

    projectiles.append(projectile)
    entities.append(projectile)
    return projectile


def create_enemy_projectile(
    x, y, angle, speed=4.0, lifetime=2.0, damage=ENEMY_PROJECTILE_DAMAGE
):
    """
    Create a new enemy projectile entity.
    :param x: x-coordinate of the projectile's starting position
    :param y: y-coordinate of the projectile's starting position
    :param angle: direction in radians that the projectile will travel
    :param speed: velocity of the projectile (default 4.0)
    :param lifetime: duration in seconds before projectile disappears (default 2.0)
    :param damage: amount of damage the projectile inflicts (default ENEMY_PROJECTILE_DAMAGE)
    :precondition: x and y must be valid coordinates in the game world
    :precondition: angle must be in radians between 0 and 2π
    :precondition: speed, lifetime, and damage must be positive numbers
    :postcondition: creates an enemy projectile entity at the specified position with the given properties
    :return: the newly created enemy projectile entity as a dictionary
    >>> proj = create_enemy_projectile(10.0, 8.0, 1.5)
    >>> proj["type"] == ENTITY_ENEMY_PROJECTILE
    True
    >>> proj["x"] == 10.0 and proj["y"] == 8.0
    True
    >>> proj["damage"] == ENEMY_PROJECTILE_DAMAGE
    True
    """
    pattern = random.choice(ENEMY_PROJECTILE_PATTERNS)
    projectile = {
        "type": ENTITY_ENEMY_PROJECTILE,
        "x": x,
        "y": y,
        "z": 0.5,
        "angle": angle,
        "speed": speed,
        "creation_time": time.time(),
        "lifetime": lifetime,
        "damage": damage,
        "pattern": pattern,
        "width": len(pattern[0]) if pattern else 0,
        "height": len(pattern),
        "color": ENEMY_PROJECTILE_COLOR,
        "glow": True,
        "pulse_rate": 3.0,
        "remove": False,
    }
    enemy_projectiles.append(projectile)
    entities.append(projectile)
    return projectile


def create_enemy(x, y, health=100):
    """
    Create a new enemy entity at the given position.
    :param x: x-coordinate of the enemy's position
    :param y: y-coordinate of the enemy's position
    :param health: initial health points of the enemy (default 100)
    :precondition: x and y must be valid coordinates in the game world
    :precondition: health must be a positive integer
    :postcondition: creates an enemy entity at the specified position with the given properties
    :return: the newly created enemy entity as a dictionary
    >>> larry = create_enemy(5.0, 5.0)
    >>> larry["type"] == ENTITY_ENEMY
    True
    >>> larry["x"] == 5.0 and larry["y"] == 5.0
    True
    >>> larry["health"] == 100 and larry["max_health"] == 100
    True
    """

    ascii_art = random.choice(ENEMY_ASCII)
    death_art = random.choice(DEATH_ASCII)

    enemy = {
        "type": ENTITY_ENEMY,
        "x": x,
        "y": y,
        "z": 0.5,
        "health": health,
        "max_health": health,
        "state": "idle",
        "ascii": ascii_art,
        "death_ascii": death_art,
        "width": max(len(line) for line in ascii_art),
        "height": len(ascii_art),
        "color": ENEMY_COLOR,
        "last_move": time.time(),
        "move_delay": random.uniform(0.5, 2.0),
        "detection_range": 10.0,
        "attack_range": 3.0,
        "distortion": 0.0,
        "remove": False,
        "last_state_change": time.time(),
        "attack_cooldown": 1.5,
        "last_attack": 0,
    }

    enemies.append(enemy)
    entities.append(enemy)
    return enemy


def create_boss(x, y):
    """
    Create a boss entity at the given position.
    :param x: x-coordinate of the boss's position
    :param y: y-coordinate of the boss's position
    :precondition: x and y must be valid coordinates in the game world
    :postcondition: creates a boss entity at the specified position with predefined boss properties
    :return: the newly created boss entity as a dictionary
    >>> biff = create_boss(15.0, 15.0)
    >>> biff["type"] == ENTITY_ENEMY and biff["subtype"] == "boss"
    True
    >>> biff["x"] == 15.0 and biff["y"] == 15.0
    True
    >>> biff["health"] == 500 and biff["max_health"] == 500
    True
    """

    boss = {
        "type": ENTITY_ENEMY,
        "subtype": "boss",
        "x": x,
        "y": y,
        "z": 0.5,
        "health": 500,
        "max_health": 500,
        "state": "idle",
        "ascii": BOSS_ASCII,
        "death_ascii": BOSS_DEATH_ASCII,
        "width": len(BOSS_ASCII[0]),
        "height": len(BOSS_ASCII),
        "color": 1,
        "last_move": time.time(),
        "move_delay": 0.8,
        "detection_range": 40.0,
        "attack_range": 8.0,
        "distortion": 0.0,
        "remove": False,
        "last_state_change": time.time(),
        "xp_value": 500,
        "attack_cooldown": 2.0,
        "last_attack": 0,
        "attack_patterns": ["projectile", "summon", "charge"],
        "current_pattern": 0,
        "pattern_timer": time.time(),
    }

    entities.append(boss)
    enemies.append(boss)

    ui.add_message("Kanka", 5.0, color=1)

    return boss


def update_entities(delta_time, world_map, player_x, player_y, player_state=None):
    """
    Update the state of all active entities in the game world.

    This function orchestrates the updates for projectiles, enemy projectiles,
    and enemies (including bosses). It also handles awarding XP to the player
    when enemies are defeated and manages the removal of dead enemies after a delay.

    :param delta_time: float, the time elapsed since the last frame.
    :param world_map: list[list[int]], the current game map layout.
    :param player_x: float, the player's current x-coordinate.
    :param player_y: float, the player's current y-coordinate.
    :param player_state: dict | None, the player's state dictionary, or None.
    :precondition: delta_time must be a non-negative float.
    :precondition: world_map must be a valid map structure.
    :precondition: player_x and player_y must be valid coordinates.
    :postcondition: All entities (projectiles, enemies) are updated based on delta_time and game logic.
    :postcondition: XP is awarded to the player if enemies are defeated nearby.
    :postcondition: Entities marked for removal are cleaned up.
    :return: list[dict], the updated list of all entities.
    """
    current_time = time.time()

    update_projectiles(delta_time, world_map, current_time)
    update_enemy_projectiles(
        delta_time, world_map, player_x, player_y, player_state, current_time
    )

    update_enemies(
        delta_time, world_map, player_x, player_y, player_state, current_time
    )

    for enemy in enemies[:]:
        if enemy["state"] == "dead" and not enemy.get("xp_awarded", False):

            if player_state:
                distance_to_player = distance_between(
                    {"x": player_x, "y": player_y}, enemy
                )
                difficulty_bonus = min(1.5, max(1.0, distance_to_player / 5))
                xp_gained = int(ENEMY_XP_VALUE * difficulty_bonus)

                award_xp(player_state, xp_gained)
                player_state["kills"] += 1

                ui.add_message(f"Enemy defeated! +{xp_gained} XP", 2.0, color=2)

                enemy["xp_awarded"] = True

        if enemy["state"] == "dead" and current_time - enemy.get("death_time", 0) > 5.0:
            enemy["remove"] = True

    cleanup_entities()

    return entities


def _update_projectile_movement(proj, delta_time, world_map, current_time):
    """
    Update a single projectile's position and check for lifetime expiry or collision.

    Helper function for projectile update logic. Modifies the projectile dictionary directly.

    :param proj: dict, the projectile entity dictionary.
    :param delta_time: float, the time elapsed since the last frame.
    :param world_map: list[list[int]], the game map for collision checks.
    :param current_time: float, the current game time.
    :precondition: proj must be a valid projectile dictionary.
    :precondition: delta_time must be non-negative.
    :precondition: world_map must be a valid map.
    :precondition: current_time must be a valid timestamp.
    :postcondition: Updates proj['x'], proj['y'] based on speed, angle, and delta_time.
    :postcondition: Sets proj['remove'] to True if lifetime expires or collision occurs.
    :return: bool, True if the projectile should be removed, False otherwise.
    """
    if proj["remove"]:
        return True

    if current_time - proj["creation_time"] > proj["lifetime"]:
        proj["remove"] = True
        return True

    proj["x"] += math.cos(proj["angle"]) * proj["speed"] * delta_time
    proj["y"] += math.sin(proj["angle"]) * proj["speed"] * delta_time

    if is_collision(proj["x"], proj["y"], world_map):
        proj["remove"] = True
        return True

    return False


def update_projectiles(delta_time, world_map, current_time):
    """
    Update all active player projectiles.

    Moves projectiles, checks for collisions with the world map and enemies.
    Marks projectiles and hit enemies accordingly.

    :param delta_time: float, time elapsed since the last frame.
    :param world_map: list[list[int]], the game map for collision checks.
    :param current_time: float, the current game time.
    :precondition: delta_time must be non-negative.
    :precondition: world_map must be a valid map.
    :precondition: current_time must be a valid timestamp.
    :postcondition: Player projectiles are moved.
    :postcondition: Projectiles colliding with walls or enemies are marked for removal.
    :postcondition: Enemies hit by projectiles take damage and may change state to 'dead'.
    """
    for proj in projectiles[:]:
        if _update_projectile_movement(proj, delta_time, world_map, current_time):
            continue

        for enemy in enemies[:]:
            if enemy["remove"] or enemy["state"] == "dead":
                continue

            dx = proj["x"] - enemy["x"]
            dy = proj["y"] - enemy["y"]
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 0.5:
                enemy["health"] -= proj["damage"]
                proj["remove"] = True

                if enemy["health"] <= 0:
                    enemy["state"] = "dead"
                    enemy["color"] = ENEMY_DEAD_COLOR
                    enemy["death_time"] = current_time
                    enemy["xp_awarded"] = False

                break


def update_enemy_projectiles(
    delta_time, world_map, player_x, player_y, player_state, current_time
):
    """
    Update all active enemy projectiles.

    Moves projectiles, checks for collisions with the world map and the player.
    Marks projectiles for removal and applies damage to the player if hit.

    :param delta_time: float, time elapsed since the last frame.
    :param world_map: list[list[int]], the game map for collision checks.
    :param player_x: float, the player's current x-coordinate.
    :param player_y: float, the player's current y-coordinate.
    :param player_state: dict | None, the player's state dictionary for applying damage.
    :param current_time: float, the current game time.
    :precondition: delta_time must be non-negative.
    :precondition: world_map must be a valid map.
    :precondition: player_x, player_y must be valid coordinates.
    :precondition: current_time must be a valid timestamp.
    :postcondition: Enemy projectiles are moved.
    :postcondition: Projectiles colliding with walls or the player are marked for removal.
    :postcondition: Player health is reduced if hit by a projectile.
    """
    for proj in enemy_projectiles[:]:
        if _update_projectile_movement(proj, delta_time, world_map, current_time):
            continue

        if player_state:
            dx = proj["x"] - player_x
            dy = proj["y"] - player_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 0.5:
                player_state["health"] -= proj["damage"]
                proj["remove"] = True
                ui.add_message(f"HIT! -{proj['damage']} HP", 1.0, color=1)

                if player_state["health"] <= 0:
                    player_state["health"] = 0
                continue


def update_enemies(
    delta_time, world_map, player_x, player_y, player_state, current_time
):
    """
    Update the state and behavior of all non-boss enemies.

    Handles enemy AI state transitions (idle, chase, attack), movement,
    and firing projectiles based on player proximity and line of sight.

    :param delta_time: float, time elapsed since the last frame.
    :param world_map: list[list[int]], the game map for navigation and LOS checks.
    :param player_x: float, the player's current x-coordinate.
    :param player_y: float, the player's current y-coordinate.
    :param player_state: dict | None, the player's state (used by boss logic indirectly).
    :param current_time: float, the current game time.
    :precondition: delta_time must be non-negative.
    :precondition: world_map must be a valid map.
    :precondition: player_x, player_y must be valid coordinates.
    :precondition: current_time must be a valid timestamp.
    :postcondition: Enemies update their state (idle, chase, attack).
    :postcondition: Enemies move based on their state and pathfinding/collision checks.
    :postcondition: Enemies in attack state may fire projectiles at the player.
    """
    for enemy in enemies:
        if enemy["remove"] or enemy["state"] == "dead":
            continue

        if enemy.get("subtype") == "boss":
            update_boss_behavior(
                enemy,
                delta_time,
                world_map,
                player_x,
                player_y,
                current_time,
            )
            continue

        dx = player_x - enemy["x"]
        dy = player_y - enemy["y"]
        dist_to_player = math.sqrt(dx * dx + dy * dy)

        angle_to_player = math.atan2(dy, dx)

        if dist_to_player <= enemy["detection_range"] and has_line_of_sight(
            enemy["x"], enemy["y"], player_x, player_y, world_map
        ):
            if dist_to_player <= enemy["attack_range"]:
                next_state = "attack"
            else:
                next_state = "chase"
        else:
            next_state = "idle"

        if enemy["state"] != next_state:
            enemy["state"] = next_state
            enemy["last_state_change"] = current_time
            if next_state == "attack":
                enemy["last_attack"] = current_time - enemy[
                    "attack_cooldown"
                ] * random.uniform(0.5, 1.0)

        if current_time - enemy["last_move"] > enemy["move_delay"]:
            enemy["last_move"] = current_time

            if enemy["state"] == "idle":

                if random.random() < 0.3:
                    move_angle = random.uniform(0, 2 * math.pi)
                    move_dist = random.uniform(0.2, 0.5)
                    try_move_entity(enemy, move_angle, move_dist, world_map)

            elif enemy["state"] == "chase":

                move_dist = 0.4 * delta_time * 10
                try_move_entity(enemy, angle_to_player, move_dist, world_map)

            elif enemy["state"] == "attack":
                if current_time - enemy["last_attack"] > enemy["attack_cooldown"]:
                    if has_line_of_sight(
                        enemy["x"], enemy["y"], player_x, player_y, world_map
                    ):
                        create_enemy_projectile(
                            enemy["x"],
                            enemy["y"],
                            angle_to_player,
                            speed=3.0,
                            lifetime=2.5,
                        )
                        enemy["last_attack"] = current_time
                        enemy["move_delay"] = random.uniform(0.8, 1.5)
                    else:
                        jitter_angle = angle_to_player + random.uniform(-0.5, 0.5)
                        jitter_dist = random.uniform(0.05, 0.2)
                        try_move_entity(enemy, jitter_angle, jitter_dist, world_map)
                else:
                    if random.random() < 0.5:
                        strafe_angle = angle_to_player + math.pi / 2 * random.choice(
                            [-1, 1]
                        )
                        strafe_dist = 0.1
                        try_move_entity(enemy, strafe_angle, strafe_dist, world_map)


def update_boss_behavior(boss, delta_time, world_map, player_x, player_y, current_time):
    """
    Update the state and behavior of a boss enemy.

    Handles boss-specific AI, including state transitions, movement,
    attack patterns (projectiles, summoning, charging), and pattern switching.

    :param boss: dict, the boss entity dictionary.
    :param delta_time: float, time elapsed since the last frame.
    :param world_map: list[list[int]], the game map for navigation and LOS checks.
    :param player_x: float, the player's current x-coordinate.
    :param player_y: float, the player's current y-coordinate.
    :param current_time: float, the current game time.
    :precondition: boss must be a valid boss entity dictionary.
    :precondition: delta_time must be non-negative.
    :precondition: world_map must be a valid map.
    :precondition: player_x, player_y must be valid coordinates.
    :precondition: current_time must be a valid timestamp.
    :postcondition: Boss updates its state (idle, chase, attack).
    :postcondition: Boss switches attack patterns periodically.
    :postcondition: Boss moves based on its state.
    :postcondition: Boss executes attacks based on its current pattern and cooldowns.
    """
    dx = player_x - boss["x"]
    dy = player_y - boss["y"]
    dist_to_player = math.sqrt(dx * dx + dy * dy)
    angle_to_player = math.atan2(dy, dx)

    if current_time - boss.get("pattern_timer", 0) > 10.0:
        boss["current_pattern"] = (boss["current_pattern"] + 1) % len(
            boss["attack_patterns"]
        )
        boss["pattern_timer"] = current_time

    if dist_to_player <= boss["detection_range"] and has_line_of_sight(
        boss["x"], boss["y"], player_x, player_y, world_map
    ):
        if dist_to_player <= boss["attack_range"]:
            boss["state"] = "attack"
        else:
            boss["state"] = "chase"
    else:
        boss["state"] = "idle"

    pattern = boss["attack_patterns"][boss["current_pattern"]]
    attack_cooldown = boss.get("attack_cooldown", 1.5)

    if (
        boss["state"] == "attack"
        and current_time - boss.get("last_attack", 0) > attack_cooldown
    ):
        if pattern == "projectile":
            for angle_offset in [-0.5, -0.25, 0, 0.25, 0.5]:
                create_enemy_projectile(
                    boss["x"],
                    boss["y"],
                    angle_to_player + angle_offset,
                    speed=4.0,
                    lifetime=2.5,
                    damage=10,
                )
            boss["last_attack"] = current_time

        elif pattern == "summon":
            for _ in range(2):
                offset_x = random.uniform(-2.0, 2.0)
                offset_y = random.uniform(-2.0, 2.0)
                if not is_collision(
                    boss["x"] + offset_x, boss["y"] + offset_y, world_map
                ):
                    create_enemy(boss["x"] + offset_x, boss["y"] + offset_y, health=50)
            boss["last_attack"] = current_time

        elif pattern == "charge":
            charge_dist = min(dist_to_player * 0.5, 3.0)
            try_move_entity(boss, angle_to_player, charge_dist, world_map)
            boss["last_attack"] = current_time

    if (
        boss["state"] == "chase"
        and current_time - boss.get("last_move", 0) > boss["move_delay"]
    ):
        move_dist = 0.4 * delta_time * 10
        try_move_entity(boss, angle_to_player, move_dist, world_map)
        boss["last_move"] = current_time

    elif (
        boss["state"] == "idle"
        and current_time - boss.get("last_move", 0) > boss["move_delay"]
    ):
        if random.random() < 0.4:
            move_angle = random.uniform(0, 2 * math.pi)
            move_dist = random.uniform(0.2, 0.8)
            try_move_entity(boss, move_angle, move_dist, world_map)
        boss["last_move"] = current_time


def try_move_entity(entity, angle, distance, world_map):
    """Try to move an entity and handle collision"""
    new_x = entity["x"] + math.cos(angle) * distance
    new_y = entity["y"] + math.sin(angle) * distance

    if not is_collision(new_x, new_y, world_map):
        entity["x"] = new_x
        entity["y"] = new_y
        return True

    if not is_collision(new_x, entity["y"], world_map):
        entity["x"] = new_x
        return True

    if not is_collision(entity["x"], new_y, world_map):
        entity["y"] = new_y
        return True

    return False


def cleanup_entities():
    """Remove entities marked for removal"""
    global entities, projectiles, enemies, enemy_projectiles

    entities = [
        e
        for e in entities
        if not e.get("remove", False)
        or (e.get("subtype") == "boss" and e.get("state") == "dead")
    ]
    projectiles = [p for p in projectiles if not p.get("remove", False)]
    enemies = [
        e
        for e in enemies
        if not e.get("remove", False)
        or (e.get("subtype") == "boss" and e.get("state") == "dead")
    ]
    enemy_projectiles = [p for p in enemy_projectiles if not p.get("remove", False)]


def clear_entities():
    """Clear all entities from the game - used when changing levels"""
    global entities, projectiles, enemies, enemy_projectiles
    entities = []
    projectiles = []
    enemies = []
    enemy_projectiles = []


def distort_text(text, distortion_level):
    """Apply distortion to text based on distance"""
    if distortion_level <= 0:
        return text

    glitch_chars = "!@#$%^&*()-_=+[]{}|;:,.<>/?`~"
    result = ""

    for char in text:

        if random.random() < distortion_level:
            if random.random() < 0.7:
                result += random.choice(glitch_chars)
            else:
                offset = random.randint(-5, 5)
                result += chr((ord(char) + offset) % 127)
        else:
            result += char

    return result


def get_enemy_display_text(enemy, distance):
    """Get the display text for an enemy based on state and distance"""

    distortion = min(0.9, distance / 20.0)

    if enemy["state"] == "dead":
        ascii_art = enemy["death_ascii"]
    else:
        ascii_art = enemy["ascii"]

    distorted_art = []
    for line in ascii_art:
        distorted_art.append(distort_text(line, distortion))

    return distorted_art


def spawn_enemies(world_map, count=5):
    """Spawn a number of enemies at valid locations in the world"""
    map_height = len(world_map)
    map_width = len(world_map[0]) if map_height > 0 else 0

    if map_height == 0 or map_width == 0:
        return

    for _ in range(count):

        for attempt in range(100):
            x = random.uniform(1.5, map_width - 1.5)
            y = random.uniform(1.5, map_height - 1.5)

            if not is_collision(x, y, world_map):
                create_enemy(x, y)
                break


def award_xp(player_state, amount):
    """Award XP to the player and handle level ups"""
    if not player_state:
        return

    player_state["exp"] += amount

    level_up_occurred = False
    while player_state["exp"] >= player_state["exp_to_next"]:
        player_state["level"] += 1
        player_state["exp"] -= player_state["exp_to_next"]
        player_state["exp_to_next"] = int(player_state["exp_to_next"] * 1.5)
        player_state["max_health"] += 20
        player_state["health"] = player_state["max_health"]
        level_up_occurred = True

    if level_up_occurred:
        ui.add_message(
            f"Level up! You're now level {player_state['level']}!", 3.0, color=6
        )
