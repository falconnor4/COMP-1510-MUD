import time
import curses
from curses import wrapper

# Import our modules
from renderer import init_colors, render_world, render_full_map, shoot_animation
from player import create_player, update_input, update_player
from map import ACTIVE_MAP, ACTIVE_COLORS, interact_raycast, switch_map
from menu import display_menu
import ui  # Import our new UI module

# pip install windows-curses  # Only for Windows users as unix-based systems have curses pre-installed

def run_game(stdscr):
    """Run the main game loop"""
    # Setup terminal
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
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
        

        if not player_state['map_mode']:
            should_shoot, should_interact = update_player(player_state, delta_time, current_map)
            
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
                    ui.add_message("You found stairs, but they don't lead anywhere yet.", 3.0)
                    
                elif object_type == 'wall':
                    ui.add_message("There's nothing to interact with here.", 2.0, color=7)
                    
                elif object_type is None:
                    ui.add_message("Nothing to interact with.", 2.0, color=7)
        else:
            should_shoot, should_interact = False, False
        
        # Render the appropriate view based on current mode
        if player_state['map_mode']:
            render_full_map(stdscr, player_state['x'], player_state['y'], 
                          player_state['angle'], current_map, current_colors)
        else:
            render_world(stdscr, player_state['x'], player_state['y'], 
                       player_state['angle'], current_map, current_colors)
            
            if should_shoot and current_time - player_state['last_shot_time'] > player_state['shot_cooldown']:
                shoot_animation(stdscr, stdscr.getmaxyx()[0], stdscr.getmaxyx()[1])
                player_state['last_shot_time'] = current_time
                ui.add_status_effect("Shot fired", "!", duration=1.0, color=1)
        ui.draw_ui_layer(stdscr)
        curses.doupdate()
        
        # Cap frame rate
        if delta_time < 0.033:  # Target ~30 FPS
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
#Doom Sprites in a modern format: https://www.spriters-resource.com/pc_computer/doomdoomii/