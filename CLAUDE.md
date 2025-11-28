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
uv run python game.py

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=. --cov-report=term-missing
```

## Architecture

- **game.py** - Main entry point with game state machine (MENU → PLAYING → WON)
- **maze.py** - `Maze` class with recursive backtracking generation, `Cell` dataclass for wall representation, `Difficulty` enum for presets
- **player.py** - `Player` class with grid-based position and movement
- **menu.py** - `Menu` class for difficulty selection screen
- **config.py** - Display dimensions, colors, and constants
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
- `GameState.MENU` - Difficulty selection
- `GameState.PLAYING` - Active gameplay
- `GameState.WON` - Win overlay displayed

### Controls
- Arrow keys: Move player
- R: Restart with new maze
- ESC: Return to menu
- Enter: Start game (from menu)
