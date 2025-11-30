# Maze Game

A maze game built with Pygame featuring random maze generation, multiple difficulty levels, and player navigation.

## Features

- **Random maze generation** using recursive backtracking algorithm
- **4 difficulty levels**: Easy (10x10), Medium (20x20), Hard (30x30), Very Hard (40x40)
- **Random start/goal placement** with guaranteed solvability
- **Path complexity control** - easier difficulties have more alternate paths

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
uv run python game.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move player |
| R | Restart with new maze |
| ESC | Return to menu |
| Enter | Start game (from menu) |

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
├── game.py          # Main entry point, game loop, state machine
├── maze.py          # Maze generation (recursive backtracking) & data structures
├── player.py        # Player state and movement
├── menu.py          # Difficulty selection menu
├── config.py        # Game constants (dimensions, colors, etc.)
├── utils.py         # Helper functions
├── tests/           # Test suite
│   ├── test_maze.py        # Maze unit tests
│   ├── test_player.py      # Player unit tests
│   └── test_integration.py # Integration tests
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

## License

MIT
