# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A maze game built with Pygame featuring random maze generation, multiple difficulty levels, and player navigation.

## Commands

```bash
# Install dependencies
uv sync

# Install with dev dependencies (for testing)
uv sync --extra dev

# Run the game
uv run python main.py

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov --cov-report=term-missing

# Run in browser (local dev server at localhost:8000)
uv run python -m pygbag .

# Build for web deployment
uv run python -m pygbag --build .
```

## Architecture

- **main.py** - Main entry point with game state machine (MENU → PLAYING → WON, plus TAG_PLAYING → TAG_ROUND_END → TAG_GAME_OVER), async for pygbag web support
- **maze.py** - `Maze` class with recursive backtracking generation, `Cell` dataclass for wall representation, `Difficulty` enum for presets
- **player.py** - `Player` class with grid-based position, movement, and optional label drawing
- **menu.py** - `Menu` class for mode/difficulty selection (Solo and Tag modes)
- **tag_game.py** - `TagGame` class encapsulating 2-player tag mode state (scores, rounds, roles, countdown)
- **config.py** - Display dimensions, colors, and constants (including tag mode colors/settings)
- **utils.py** - Helper functions

## Key Concepts

### Maze Generation
- Uses recursive backtracking algorithm
- Each `Cell` has 4 boolean walls (top, right, bottom, left)
- Difficulty controls both maze size (10x10 to 40x40) and path complexity
- Extra walls are removed on easier difficulties to create loops

### Coordinate System
- Grid coordinates: (row, col) where row 0 is top
- `maze.grid_to_pixel(row, col)` converts to screen coordinates
- Cell size is calculated dynamically based on window size and maze dimensions

### Game States
- `GameState.MENU` - Mode and difficulty selection
- `GameState.PLAYING` - Active solo gameplay
- `GameState.WON` - Solo win overlay displayed
- `GameState.TAG_PLAYING` - Active 2-player tag gameplay
- `GameState.TAG_ROUND_END` - Tag round result overlay
- `GameState.TAG_GAME_OVER` - Tag final winner overlay

### Controls
- Arrow keys or WASD: Move player (solo mode)
- W/S: Navigate menu (in addition to arrow keys)
- Left/Right: Adjust settings values in menu (mode, shade, win score)
- B: Toggle breadcrumb trail on/off (during solo gameplay)
- R: Restart with new maze
- ESC: Return to menu
- Enter: Start game or toggle settings (from menu), advance rounds (tag mode)

### Tag Mode Controls
- P1: WASD (always)
- P2: Arrow keys (always)
- Roles (tagger/runner) determine color and label, not controls

### Breadcrumb Trail
- Optional visual trail showing the path taken through the maze
- Fading effect: older breadcrumbs are more transparent, newer ones more visible
- Backtrack detection: retracing steps removes breadcrumbs
- Configure in menu: toggle on/off, select shade (Light/Medium/Dark)
- Runtime toggle with B key during gameplay

### Timer
- Tracks how long the player takes to solve the maze
- Starts on first move (not when game loads)
- Stops when the maze is solved
- Displayed in upper right corner with retro 80's arcade font (Press Start 2P)
- Format: MM:SS.T (minutes:seconds.tenths)
- Always active (no toggle option)
- Final time displayed prominently on win screen

### Moves Counter
- Counts the total number of valid moves made by the player
- Increments on each valid move (does not count wall collisions)
- Includes backtracking moves in the count
- Displayed in upper left corner with retro 80's arcade font (Press Start 2P)
- Resets on restart (R key) or new game from menu
- Final move count displayed on win screen alongside time

### Tag Mode
- 2-player tag: one player is tagger ("IT"), the other is runner
- Tagger (orange-red) tries to catch runner (sky blue) within 2-minute countdown
- If tagged: tagger scores a point; if timeout: runner scores a point
- Roles swap each round; first to N wins (configurable: 1, 3, or 5)
- Mazes are Hard or Very Hard with extra loops for chase dynamics
- HUD shows scores (upper-left), round number (upper-center), countdown (upper-right)
- Countdown turns red when < 30 seconds remain
- Round-end screen shows result, tagger moves, elapsed time, scores
- Game-over screen shows winner with R to rematch, ESC for menu
