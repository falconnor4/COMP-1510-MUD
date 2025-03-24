import time
import curses
from curses import wrapper

# Import our modules
from renderer import init_colors, render_world, render_full_map
from player import create_player, update_input, update_player
from map import ACTIVE_MAP, ACTIVE_COLORS, interact_raycast, switch_map
from menu import display_menu
import ui  # Import our new UI module
import entities


# pip install windows-curses  # Only for Windows users as Unix-based systems have curses pre-installed

def run_game(stdscr):
    """Run the main game loop"""
    # Setup terminal
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.keypad(True)  # Enable special keys
    stdscr.clear()
    init_colors()

    # Create player state
    player_state = create_player(x=10.5, y=8.5)

    # Game loop variables
    running = True
    last_frame_time = time.time()

    # Get initial map data
    current_map = ACTIVE_MAP
    current_colors = ACTIVE_COLORS

    # Initialize entities
    entities.spawn_enemies(current_map, 5)  # Spawn 5 enemies

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

        # Update player based on current active keys
        if not player_state['map_mode']:
            should_shoot, should_interact = update_player(player_state, delta_time, current_map)

            # Handle shooting
            if should_shoot and current_time - player_state['last_shot_time'] > player_state['shot_cooldown']:
                # Get screen dimensions for muzzle position calculation
                height, width = stdscr.getmaxyx()

                # Create a closure that captures the current player state and screen dimensions
                def create_delayed_projectile():
                    # Get the muzzle position in screen coordinates
                    muzzle_pos = ui.get_weapon_muzzle_position(height, width)

                    # Convert screen position to world position
                    world_x, world_y = ui.convert_screen_to_world(
                        muzzle_pos,
                        player_state['x'],
                        player_state['y'],
                        player_state['angle']
                    )

                    # Create the projectile from the calculated position
                    entities.create_projectile(
                        world_x,
                        world_y,
                        player_state['angle'],
                        speed=7.0,
                        lifetime=1.5
                    )

                # Start fire animation with midpoint callback
                ui.start_animation('fire', midpoint_callback=create_delayed_projectile)

                # Update cooldown and status immediately
                player_state['last_shot_time'] = current_time
                ui.add_status_effect("Shot fired", "!", duration=1.0, color=1)

            # Update entities
            entities.update_entities(
                delta_time,
                current_map,
                player_state['x'],
                player_state['y'],
                player_state['angle']
            )

            # Handle interaction
            if should_interact:
                # Cast ray to see if something can be interacted with
                object_type, obj_x, obj_y = interact_raycast(
                    player_state['x'], player_state['y'], player_state['angle'], current_map
                )

                if object_type == 'door':
                    # Handle door interaction - switch maps
                    new_map, new_colors = switch_map(2 if current_map == ACTIVE_MAP else 1)
                    current_map = new_map
                    current_colors = new_colors
                    ui.add_message("You entered a door to a new area!", 3.0, color=5)

                elif object_type == 'stairs':
                    ui.add_message("Well. You found stairs, but they don't lead anywhere yet.", 3.0)

                elif object_type == 'wall':
                    ui.add_message("There's nothing to interact with here.", 2.0, color=7)

                elif object_type is None:
                    ui.add_message("Nothing to interact with.", 2.0, color=7)

        # First clear the screen - ONCE per frame
        stdscr.erase()

        # Render the appropriate view based on current mode
        if player_state['map_mode']:
            render_full_map(stdscr, player_state['x'], player_state['y'],
                            player_state['angle'], current_map, current_colors)
        else:
            render_world(stdscr, player_state['x'], player_state['y'],
                         player_state['angle'], current_map, current_colors,
                         player_state)  # Pass player_state for head-bob
        ui.draw_ui_layer(stdscr, player_state)  # Pass player_state for UI stats

        # SINGLE screen update per frame - this is key to eliminating flicker
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
#Doom: https://github.com/id-Software/DOOM