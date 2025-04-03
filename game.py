import curses
import time
from curses import wrapper

import debug
import entities
import ui
from map.static_map import ACTIVE_MAP, ACTIVE_COLORS, interact_raycast, switch_map
from menu import display_menu
from player import create_player, update_input, update_player

# Import our modules
from renderer import init_colors, render_world, render_full_map


# pip install windows-curses  # Only for Windows users as Unix-based systems have curses pre-installed


def run_game(stdscr):
    """Run the main game loop"""
    # Setup terminal
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.keypad(True)  # Enable special keys
    stdscr.clear()
    init_colors()

    player_state = create_player(x=10.5, y=8.5)
    running = True
    last_frame_time = time.time()

    # Get initial map data
    current_map = ACTIVE_MAP
    current_colors = ACTIVE_COLORS

    # Initialize entities
    entities.spawn_enemies(current_map, 5)  # Spawn 5 enemies

    def _handle_level_change(level_id):
        """Handles the logic for changing levels/maps."""
        nonlocal current_map, current_colors
        new_map, new_colors, player_spawn, is_new_dungeon = switch_map(
            level_id, player_state["level"]
        )
        current_map = new_map
        current_colors = new_colors

        # Move player to spawn point
        player_state["x"], player_state["y"] = player_spawn

        # Track stage descent if entering a new dungeon level
        if is_new_dungeon:
            player_state["stages_descended"] += 1
            from map.static_map import CURRENT_COLOR_SHIFT

            dungeon_types = {
                0: "Cave",
                1: "Ancient Ruins",
                2: "Forgotten Crypt",
                3: "Overgrown Forest",
                4: "Abandoned Tech Facility",
            }
            dungeon_type = dungeon_types.get(CURRENT_COLOR_SHIFT, "Strange Area")
            ui.add_message(
                f"Entered {dungeon_type} - Depth {player_state['stages_descended']}",
                3.5,
                color=5,
            )

        # Update enemies for the new level
        entities.clear_entities()
        enemy_count = 5 + player_state["stages_descended"] // 2
        entities.spawn_enemies(current_map, enemy_count)

        return f"Changed to level {player_state['stages_descended']}"

    # Setup debug commands
    def change_level():
        """Debug command to change level"""
        level_to_switch = 2 if current_map == ACTIVE_MAP else 1
        return _handle_level_change(level_to_switch)

    debug.COMMANDS["next"]["callback"] = change_level
    debug.initialize_commands(player_state, change_level)

    # Welcome message :)
    ui.add_message("Welcome to the game! Press 'E' to interact with objects.", 5.0)

    while running:
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        delta_time = min(delta_time, 0.1)

        # Process all queued input events
        while True:
            key = stdscr.getch()
            if key == -1:  # No more keys in buffer
                break

            # Update key states and check for quit
            quit_pressed = update_input(player_state, key, True)
            if quit_pressed:
                running = False

        if not player_state["map_mode"] and not debug.DEBUG_CONSOLE["active"]:
            should_shoot, should_interact = update_player(
                player_state, delta_time, current_map
            )

            # Handle shooting
            if (
                should_shoot
                and current_time - player_state["last_shot_time"]
                > player_state["shot_cooldown"]
            ):
                height, width = stdscr.getmaxyx()

                # Create a closure that captures the current player state and screen dimensions
                def create_delayed_projectile():
                    muzzle_pos = ui.get_weapon_muzzle_position(height, width)
                    world_x, world_y = ui.convert_screen_to_world(
                        muzzle_pos,
                        player_state["x"],
                        player_state["y"],
                        player_state["angle"],
                    )

                    # Create the projectile from the calculated position
                    entities.create_projectile(
                        world_x, world_y, player_state["angle"], speed=7.0, lifetime=1.5
                    )

                # Start fire animation with midpoint callback
                ui.start_animation("fire", midpoint_callback=create_delayed_projectile)

                # Update cooldown and status immediately
                player_state["last_shot_time"] = current_time
                ui.add_status_effect("Shot fired", "!", duration=1.0, color=1)

            # Update entities with player state for XP
            entities.update_entities(
                delta_time,
                current_map,
                player_state["x"],
                player_state["y"],
                player_state["angle"],
                player_state,
            )

            # Handle interaction
            if should_interact:
                # Cast ray to see if something can be interacted with
                object_type, obj_x, obj_y = interact_raycast(
                    player_state["x"],
                    player_state["y"],
                    player_state["angle"],
                    current_map,
                )

                if object_type == "door":
                    level_to_switch = 2 if current_map == ACTIVE_MAP else 1
                    _handle_level_change(level_to_switch)
                    ui.add_message(
                        f"You descended to dungeon depth {player_state['stages_descended']}...",
                        3.0,
                        color=5,
                    )

                elif object_type == "boss_door":
                    # Enter the randomly generated boss arena
                    new_map, new_colors, player_spawn, _ = switch_map("boss_arena")
                    current_map = new_map
                    current_colors = new_colors

                    # Move player to spawn point
                    player_state["x"], player_state["y"] = player_spawn
                    
                    # Block the entrance behind the player (no way out)
                    entrance_x, entrance_y = int(player_spawn[0]), int(player_spawn[1])
                    wall_y = entrance_y + 2
                    for offset_x in range(-2, 3):
                        try:
                            # Make sure we're not placing walls on the player's position
                            if 0 <= entrance_y + 2 < len(current_map) and 0 <= entrance_x + offset_x < len(current_map[0]):
                                current_map[wall_y][entrance_x + offset_x] = 8  # Stone wall
                        except IndexError:
                            pass  # Skip if out of bounds

                    # Spawn boss in the arena - at center of the map
                    entities.clear_entities()
                    boss_x, boss_y = len(current_map[0]) // 2, len(current_map) // 2
                    entities.create_boss(boss_x, boss_y)

                    ui.add_message(
                        "You entered the Boss Arena! The entrance collapses behind you!", 5.0, color=1
                    )

                elif object_type == "stairs":
                    ui.add_message(
                        "Well. You found stairs, but they don't lead anywhere yet.", 3.0
                    )

                elif object_type == "wall":
                    ui.add_message(
                        "There's nothing to interact with here.", 2.0, color=7
                    )

                elif object_type is None:
                    ui.add_message("Nothing to interact with.", 2.0, color=7)

        # First clear the screen - ONCE per frame
        stdscr.erase()

        # Render the appropriate view based on current mode
        if player_state["map_mode"]:
            render_full_map(
                stdscr,
                player_state["x"],
                player_state["y"],
                player_state["angle"],
                current_map,
                current_colors,
            )
        else:
            render_world(
                stdscr,
                player_state["x"],
                player_state["y"],
                player_state["angle"],
                current_map,
                current_colors,
                player_state,
            )  # Pass player_state for head-bob
        ui.draw_ui_layer(stdscr, player_state)  # Pass player_state for UI stats

        # SINGLE screen update per frame - this is key to eliminating flicker
        if debug.DEBUG_CONSOLE["active"]:
            stdscr.move(0, len("> ") + debug.DEBUG_CONSOLE["cursor_pos"])
            curses.curs_set(1)  # Show cursor in debug mode
        else:
            curses.curs_set(0)  # Hide cursor in gameplay

        curses.doupdate()

        # Cap frame rate
        if delta_time < 0.033:  # Target ~30 FPS ish....
            time.sleep(0.033 - delta_time)

    # Return to menu after game ends
    return "menu"


def main(stdscr):
    """Main function that handles the flow between menu and game"""
    state = "menu"

    while state != "exit":
        if state == "menu":
            # Reset terminal settings for menu
            stdscr.nodelay(False)
            curses.curs_set(0)
            stdscr.clear()

            # Show menu and get result
            state = display_menu(stdscr)

        elif state == "start_game":
            # Run the game
            state = run_game(stdscr)


if __name__ == "__main__":
    try:
        wrapper(main)  # Initialize and restore terminal properly
    except KeyboardInterrupt:
        print("Game terminated by user")

###Citations###
# Doom: https://github.com/id-Software/DOOM
