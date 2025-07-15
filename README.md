# Paradox v(-1.0) - Terminal-Based 3D Dungeon Crawler

## Overview

Paradox v(-1.0) is a terminal-based 3D dungeon crawler implemented in Python using the `curses` library. The game utilizes a raycasting engine, based on classic games such as Wolfenstein 3D / Doom 1993. Rendering a pseudo-3D first-person perspective within a terminal window.

## Features

*   **3D Raycasting Engine:** Experience a 3d game... In your terminal!
*   **Procedurally Generated Dungeons:** Each floor of the dungeon is procedurally generated. good luck.
*   **Enemies and Combat:** Battle various enemies using your ranged spells (fireball everything you see!).
*   **Debug Console:** Use the integrated debug console for testing and development (you can toggle it with `;`). (it doesn't currently work properly.)

## How to Play

1.  **Prerequisites:**
    *   Python 3.x
    *   `curses` library (usually pre-installed on Linux/macOS, may require installation on Windows)

2.  **Installation:**

    ```bash
    git clone https://github.com/falconnor4/Termi-Mud
    cd Termi-Mud
    ```

3.  **Running the Game:**

    ```bash
    python3 game.py
    ```

4.  **Controls:**

    *   `W/A/S/D`: Move forward, left, backward, right
    *   `Left/Right Arrows`: Turn left/right
    *   `Spacebar`: Throw Fireball
    *   `E`: Interact with doors and objects
    *   `Q`: Return to menu
    *   `M`: Toggle map view
    *   `;`: Toggle debug console

## Module Structure

*   `game.py`: Main game loop and initialization.
*   `menu.py`: Handles the main menu and navigation.
*   `player.py`: Manages player state and actions.
*   `entities.py`: Handles entity creation, updates, and interactions.
*   `map/`: Contains map generation and management code.
    *   `dungeon_generator.py`: Generates dungeon layouts.
    *   `static_map.py`: Defines static maps (e.g., start map).
*   `renderer/`: Rendering-related modules.
    *   `world_renderer.py`: Renders the 3D world view.
    *   `color_utils.py`: Initializes color pairs for the terminal.
    *   `console_renderer.py`: Renders the debug console.
*   `ui.py`: Manages the user interface elements (messages, stats, animations).
*   `anim/`: Contains ASCII art animations such as our hand and the projectiles.
*   `debug.py`: Implements the debug console and commands.

## Flowchart (also can be found [here](game.pdf))

![Flowchart Image](https://github.com/falconnor4/Termi-Mud/blob/main/game.png?raw=true)
