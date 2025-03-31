import math
import random
import time

entities = []
projectiles = []
enemies = []

ENTITY_PROJECTILE = 'projectile'
ENTITY_ENEMY = 'enemy'

ENEMY_ASCII = [
    [
        "ERROR",
        "FATAL",
        "CRASH",
        "#$*@!"
    ],
    [
        "SYNTAX",
        "ERROR!",
        "SEGFLT",
        "-----"
    ],
    [
        "MEMORY",
        "LEAK!",
        "PANIC",
        "/dev/0"
    ],
    [
        "BUFFER",
        "OVRFLW",
        "STACK",
        "SMASHD"
    ],
    [
        "NULLPT",
        "EXCEPT",
        "SYSTEM",
        "FAILED"
    ],
]

DEATH_ASCII = [
    [
        "CORE",
        "DUMP",
        "----",
        "0x00"
    ],
    [
        "EXIT:",
        "CODE1",
        "TERM",
        "INATED"
    ],
    [
        "KILL",
        "SIGNAL",
        "RECVD",
        "-----"
    ],
    [
        "PANIC",
        "ABORT",
        "CRASH",
        "xxxxx"
    ],
]

ENEMY_COLOR = 1
ENEMY_ALERT_COLOR = 5
ENEMY_DEAD_COLOR = 8
PROJECTILE_COLOR = 3
ENEMY_XP_VALUE = 50

PROJECTILE_PATTERNS = [
    [
        "                    ",
        "      ++.:--*.      ",
        "    ==+***#%*=*.    ",
        "   *#%%%%%%%@%%#*   ",
        "  *%@%%%#*##%@@@@*  ",
        "  %%@%%%*:=#%@@@@%  ",
        "  +#@#%%%#%%%@@#*+  ",
        "   -@@@%@#@%@@@@=   ",
        "     *%%@%%@@%#     ",
        "        +#**        ",
        "                    ",
    ],
    [
        "                    ",
        "         **         ",
        "    %:-%@@@@@@@@    ",
        "  #.:+#@@@@@@@%#+%  ",
        " +:--=#%%#####%%%*: ",
        " :=--=%%%*****#%%%- ",
        " %+==+%%%#***##%%%= ",
        " %%***%%%%#**##%%@. ",
        "  %%#%%%%#####%%@@  ",
        "    @%%@%%%%%%%%    ",
        "       @@@@@@       ",
        "                    ",
    ],
    [
        "                    ",
        "                    ",
        "       ---=*#%      ",
        "     -::::-=+#@@    ",
        "    -::..::-+#@@@   ",
        "    =-::::-=*%@@@   ",
        "    #*+==+*#%@@@@   ",
        "     %%%%%%@@@@@    ",
        "       @@@@@@@      ",
        "                    ",
        "                    ",
    ]
]


def create_projectile(x, y, angle, speed=5.0, lifetime=1.5, damage=25):
    """Create a new projectile entity at the given position and angle"""

    pattern = random.choice(PROJECTILE_PATTERNS)

    projectile = {
        'type': ENTITY_PROJECTILE,
        'x': x,
        'y': y,
        'z': 0.5,
        'angle': angle,
        'speed': speed,
        'creation_time': time.time(),
        'lifetime': lifetime,
        'damage': damage,
        'pattern': pattern,
        'width': len(pattern[0]),
        'height': len(pattern),
        'color': PROJECTILE_COLOR,
        'glow': True,
        'pulse_rate': 4.0,
        'remove': False
    }

    projectiles.append(projectile)
    entities.append(projectile)
    return projectile


def create_enemy(x, y, health=100):
    """Create a new enemy entity at the given position"""

    ascii_art = random.choice(ENEMY_ASCII)
    death_art = random.choice(DEATH_ASCII)

    enemy = {
        'type': ENTITY_ENEMY,
        'x': x,
        'y': y,
        'z': 0.5,
        'health': health,
        'max_health': health,
        'state': 'idle',
        'ascii': ascii_art,
        'death_ascii': death_art,
        'width': max(len(line) for line in ascii_art),
        'height': len(ascii_art),
        'color': ENEMY_COLOR,
        'last_move': time.time(),
        'move_delay': random.uniform(0.5, 2.0),
        'detection_range': 10.0,
        'attack_range': 3.0,
        'distortion': 0.0,
        'remove': False,
        'last_state_change': time.time()
    }

    enemies.append(enemy)
    entities.append(enemy)
    return enemy


def update_entities(delta_time, world_map, player_x, player_y, player_angle, player_state=None):
    """Update all entities in the world"""
    current_time = time.time()

    update_projectiles(delta_time, world_map, player_state, player_x, player_y)

    update_enemies(delta_time, world_map, player_x, player_y, player_angle)

    for enemy in enemies[:]:
        if enemy['state'] == 'dead' and not enemy.get('xp_awarded', False):

            if player_state:
                distance_to_player = distance_between({'x': player_x, 'y': player_y}, enemy)
                difficulty_bonus = min(1.5, max(1.0, distance_to_player / 5))
                xp_gained = int(ENEMY_XP_VALUE * difficulty_bonus)

                award_xp(player_state, xp_gained)
                player_state['kills'] += 1

                import ui
                ui.add_message(f"Enemy defeated! +{xp_gained} XP", 2.0, color=2)

                enemy['xp_awarded'] = True

        if enemy['state'] == 'dead' and current_time - enemy.get('death_time', 0) > 5.0:
            enemy['remove'] = True

    cleanup_entities()

    return entities


def update_projectiles(delta_time, world_map, player_state=None, player_x=None, player_y=None):
    """Update all projectile positions and check for collisions"""
    current_time = time.time()

    for proj in projectiles[:]:
        if proj['remove']:
            continue

        if current_time - proj['creation_time'] > proj['lifetime']:
            proj['remove'] = True
            continue

        proj['x'] += math.cos(proj['angle']) * proj['speed'] * delta_time
        proj['y'] += math.sin(proj['angle']) * proj['speed'] * delta_time

        if is_collision(proj['x'], proj['y'], world_map):
            proj['remove'] = True
            continue

        for enemy in enemies[:]:
            if enemy['remove'] or enemy['state'] == 'dead':
                continue

            dx = proj['x'] - enemy['x']
            dy = proj['y'] - enemy['y']
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 0.5:

                enemy['health'] -= proj['damage']

                proj['remove'] = True

                if enemy['health'] <= 0:
                    enemy['state'] = 'dead'
                    enemy['color'] = ENEMY_DEAD_COLOR
                    enemy['death_time'] = current_time
                    enemy['xp_awarded'] = False

                break


def update_enemies(delta_time, world_map, player_x, player_y, player_angle):
    """Update all enemies"""
    current_time = time.time()

    for enemy in enemies:
        if enemy['remove']:
            continue

        if enemy['state'] == 'dead':
            continue

        dx = player_x - enemy['x']
        dy = player_y - enemy['y']
        dist_to_player = math.sqrt(dx * dx + dy * dy)

        angle_to_player = math.atan2(dy, dx)

        angle_diff = abs((angle_to_player - player_angle + math.pi) % (2 * math.pi) - math.pi)
        player_visible = angle_diff < math.pi / 3

        if dist_to_player <= enemy['detection_range'] and has_line_of_sight(enemy['x'], enemy['y'], player_x, player_y,
                                                                            world_map):
            if dist_to_player <= enemy['attack_range']:
                next_state = 'attack'
            else:
                next_state = 'chase'
        else:
            next_state = 'idle'

        if enemy['state'] != next_state:
            enemy['state'] = next_state
            enemy['last_state_change'] = current_time

        if current_time - enemy['last_move'] > enemy['move_delay']:
            enemy['last_move'] = current_time

            if enemy['state'] == 'idle':

                if random.random() < 0.3:
                    move_angle = random.uniform(0, 2 * math.pi)
                    move_dist = random.uniform(0.2, 0.5)
                    try_move_entity(enemy, move_angle, move_dist, world_map)

            elif enemy['state'] == 'chase':

                move_dist = 0.4 * delta_time * 10
                try_move_entity(enemy, angle_to_player, move_dist, world_map)

            elif enemy['state'] == 'attack':

                if random.random() < 0.5:
                    jitter_angle = angle_to_player + random.uniform(-0.5, 0.5)
                    jitter_dist = random.uniform(0.05, 0.2)
                    try_move_entity(enemy, jitter_angle, jitter_dist, world_map)


def try_move_entity(entity, angle, distance, world_map):
    """Try to move an entity and handle collision"""
    new_x = entity['x'] + math.cos(angle) * distance
    new_y = entity['y'] + math.sin(angle) * distance

    if not is_collision(new_x, new_y, world_map):
        entity['x'] = new_x
        entity['y'] = new_y
        return True
    else:

        new_x = entity['x'] + math.cos(angle) * distance
        if not is_collision(new_x, entity['y'], world_map):
            entity['x'] = new_x
            return True

        new_y = entity['y'] + math.sin(angle) * distance
        if not is_collision(entity['x'], new_y, world_map):
            entity['y'] = new_y
            return True

    return False


def cleanup_entities():
    """Remove entities marked for removal"""
    global entities, projectiles, enemies

    entities = [e for e in entities if not e.get('remove', False)]
    projectiles = [p for p in projectiles if not p.get('remove', False)]
    enemies = [e for e in enemies if not e.get('remove', False)]


def clear_entities():
    """Clear all entities from the game - used when changing levels"""
    global entities, projectiles, enemies
    entities = []
    projectiles = []
    enemies = []


def is_collision(x, y, world_map):
    """Check if a position collides with a wall"""
    grid_x, grid_y = int(x), int(y)

    if grid_y < 0 or grid_y >= len(world_map) or grid_x < 0 or grid_x >= len(world_map[0]):
        return True

    walkable_types = [0, 4, 9]
    return world_map[grid_y][grid_x] not in walkable_types


def has_line_of_sight(x1, y1, x2, y2, world_map):
    """Check if there's a clear line of sight between two points"""
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        return True

    dx /= distance
    dy /= distance

    steps = max(1, int(distance * 5))
    step_size = distance / steps

    for i in range(1, steps):
        check_x = x1 + dx * i * step_size
        check_y = y1 + dy * i * step_size

        if is_collision(check_x, check_y, world_map):
            return False

    return True


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

    if enemy['state'] == 'dead':
        ascii_art = enemy['death_ascii']
    else:
        ascii_art = enemy['ascii']

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


def distance_between(entity1, entity2):
    """Calculate the distance between two entities"""
    dx = entity1['x'] - entity2['x']
    dy = entity1['y'] - entity2['y']
    return math.sqrt(dx * dx + dy * dy)


def award_xp(player_state, amount):
    """Award XP to the player and handle level ups"""
    if not player_state:
        return

    player_state['exp'] += amount

    level_up_occurred = False
    while player_state['exp'] >= player_state['exp_to_next']:
        player_state['level'] += 1
        player_state['exp'] -= player_state['exp_to_next']
        player_state['exp_to_next'] = int(player_state['exp_to_next'] * 1.5)
        player_state['max_health'] += 20
        player_state['health'] = player_state['max_health']
        level_up_occurred = True

    if level_up_occurred:
        import ui
        ui.add_message(f"Level up! You're now level {player_state['level']}!", 3.0, color=6)
