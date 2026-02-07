# Maze Game

A maze game built with Pygame featuring random maze generation, multiple difficulty levels, player navigation, and a 2-player tag mode.

## Features

- **Random maze generation** using recursive backtracking algorithm
- **4 difficulty levels**: Easy (10x10), Medium (20x20), Hard (30x30), Very Hard (40x40)
- **Random start/goal placement** with guaranteed solvability
- **Path complexity control** - easier difficulties have more alternate paths
- **Timer** - tracks solving time from first move, displayed in retro arcade font (MM:SS.T)
- **Moves counter** - counts valid moves during gameplay, displayed alongside the timer
- **Breadcrumb trail** - optional fading trail showing your path, with backtrack detection and configurable shade (Light/Medium/Dark)
- **Win screen** - shows final time and move count when the maze is solved
- **2-player tag mode** - one player chases another through large mazes with loops (see below)

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/sububer/maze-game.git
cd maze-game

# Install dependencies
uv sync
```

## Running the Game

```bash
uv run python main.py
```

## Controls

### Menu

| Key | Action |
|-----|--------|
| Up/Down or W/S | Navigate menu |
| Left/Right | Switch game mode, adjust settings |
| Enter | Start game or toggle setting |

### Solo Mode

| Key | Action |
|-----|--------|
| Arrow keys or WASD | Move player |
| B | Toggle breadcrumb trail |
| R | Restart with new maze |
| ESC | Return to menu |

### Tag Mode

| Key | Action |
|-----|--------|
| WASD | Move Player 1 |
| Arrow keys | Move Player 2 |
| ESC | Return to menu |
| Enter | Next round (round end) |
| R | Rematch (game over) |

## Development

### Setup

```bash
# Install with dev dependencies
uv sync --extra dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov --cov-report=term-missing
```

### Project Structure

```
maze-game/
├── main.py          # Main entry point, game loop, state machine
├── maze.py          # Maze generation (recursive backtracking) & data structures
├── player.py        # Player state and movement
├── menu.py          # Mode/difficulty selection menu
├── tag_game.py      # 2-player tag mode logic
├── config.py        # Game constants (dimensions, colors, etc.)
├── utils.py         # Helper functions
├── assets/fonts/    # Retro arcade font (Press Start 2P)
├── tests/           # Test suite
│   ├── test_maze.py            # Maze unit tests
│   ├── test_player.py          # Player unit tests
│   ├── test_moves.py           # Moves counter tests
│   ├── test_breadcrumbs.py     # Breadcrumb trail tests
│   ├── test_timer.py           # Timer formatting tests
│   ├── test_tag_game.py        # Tag mode unit tests
│   ├── test_tag_integration.py # Tag mode integration tests
│   └── test_integration.py     # Solo mode integration tests
├── pyproject.toml   # Project configuration
└── README.md
```

## How It Works

### Maze Generation

The maze is generated using the **recursive backtracking** algorithm:
1. Start from a random cell, mark it as visited
2. Randomly choose an unvisited neighbor
3. Remove the wall between current cell and neighbor
4. Recurse until no unvisited neighbors remain, then backtrack
5. Continue until all cells are visited

### Difficulty System

Difficulty affects both maze size and complexity:
- **Size**: Larger mazes at higher difficulties
- **Complexity**: Easier difficulties remove extra walls to create multiple solution paths

### Start/Goal Placement

Start and goal positions are randomly placed with a minimum distance requirement (60% of the maximum possible path length) to ensure challenging gameplay.

## Tag Mode

Tag mode is a 2-player game where one player (the **tagger**) chases the other (the **runner**) through large mazes.

- Select **Tag** mode from the menu using Left/Right on the mode selector
- Choose **Hard** or **Very Hard** difficulty and a **First to N** win target (1, 3, or 5)
- **Tagger** (orange-red, labeled "IT") tries to catch the **runner** (sky blue) within a 2-minute countdown
- If tagged, the tagger scores a point; if time runs out, the runner scores
- Roles swap each round; first player to the target score wins
- Mazes have extra loops removed for better chase dynamics
- Players start at maximally distant positions
- HUD shows scores, round number, and countdown timer (turns red under 30s)

## License

MIT
