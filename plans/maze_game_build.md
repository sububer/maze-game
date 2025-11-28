# Maze Game Implementation Plan

## Overview
Build a pygame-based maze game with configurable dimensions, difficulty levels, random maze generation using recursive backtracking, and player navigation.

---

## Phase 1: Core Maze Data Structure & Generation

**Goal**: Create the maze generation engine independent of rendering.

### Files to modify/create:
- `maze.py` - Complete rewrite

### Implementation:
1. **Cell-based maze representation**
   - Each cell has 4 walls (top, right, bottom, left) stored as booleans
   - 2D grid of cells: `self.cells[row][col]`

2. **Recursive backtracking algorithm**
   - Start from random cell, mark visited
   - Randomly choose unvisited neighbor, remove wall between them
   - Recurse until no unvisited neighbors, then backtrack
   - Continue until all cells visited

3. **Difficulty parameters**
   ```
   EASY:       10x10,  low dead-end ratio
   MEDIUM:     20x20,  medium complexity
   HARD:       30x30,  high complexity
   VERY_HARD:  40x40,  maximum complexity
   ```

4. **Path complexity control**
   - After base generation, optionally remove extra walls to create loops (easier)
   - Or add more dead ends by selective wall additions (harder)

### Deliverable:
- `Maze` class with `generate()` method that creates solvable maze
- `get_cell(row, col)` returns wall configuration
- `is_valid_move(from_pos, to_pos)` checks if move is allowed

---

## Phase 2: Player Movement & Collision

**Goal**: Player can navigate the maze with arrow keys.

### Files to modify:
- `player.py` - Rewrite for grid-based movement
- `game.py` - Connect input to player movement

### Implementation:
1. **Grid-based player position**
   - Player position as (row, col) in maze coordinates
   - Start & goal positions: randomly placed, guaranteed solvable with reasonable distance apart
   - Use BFS/path-finding to ensure minimum solution path length based on difficulty

2. **Movement validation**
   - On arrow key: check `maze.is_valid_move()` before moving
   - Only move if no wall blocks the path

3. **Win condition**
   - Detect when player reaches goal cell
   - Display win message, option to play again

---

## Phase 3: Rendering System

**Goal**: Draw maze and player correctly at any size.

### Files to modify:
- `maze.py` - Add `draw()` method
- `player.py` - Update `draw()` for grid positioning
- `config.py` - Dynamic sizing based on maze dimensions

### Implementation:
1. **Dynamic cell sizing**
   - Calculate cell_size based on window size and maze dimensions
   - `cell_size = min((WIDTH - 2*PADDING) / cols, (HEIGHT - MASTHEAD - 2*PADDING) / rows)`

2. **Wall rendering**
   - For each cell, draw walls that exist (as lines)
   - Use consistent line width

3. **Player rendering**
   - Center player circle in current cell
   - Size relative to cell_size

4. **Goal marker**
   - Distinct color/shape at goal cell

---

## Phase 4: Menu System

**Goal**: Pre-game menu for configuration.

### Files to create:
- `menu.py` - Menu screen class

### Implementation:
1. **Menu options**
   - Difficulty selection: Easy / Medium / Hard / Very Hard
   - Start Game

2. **Difficulty presets only** (no custom dimensions)
   - Easy: 10x10 + simple paths
   - Medium: 20x20 + moderate complexity
   - Hard: 30x30 + complex paths
   - Very Hard: 40x40 + maximum complexity

3. **Controls**
   - Up/Down: select difficulty
   - Enter: start game

---

## Phase 5: Game Loop Integration

**Goal**: Tie everything together.

### Files to modify:
- `game.py` - Main orchestration
- `config.py` - Add difficulty constants

### Implementation:
1. **Game states**: MENU → PLAYING → WON → MENU
2. **State machine** in main loop
3. **Clean transitions** between states

---

## Future Enhancements (Not in initial scope)

These are noted for later phases:
- Timer display during gameplay
- Persistence (JSON file for high scores)
- Save/load maze seeds for sharing
- Color themes/visual polish
- Hint system (show solution path briefly)

---

## File Structure After Implementation

```
maze-game/
├── game.py          # Main entry, game loop, state machine
├── maze.py          # Maze generation & data structure
├── player.py        # Player state & rendering
├── menu.py          # Menu screen (new)
├── config.py        # All constants & difficulty presets
├── utils.py         # Helper functions
├── plans/
│   └── maze_game_build.md
├── CLAUDE.md
└── README.md
```

---

## Implementation Order

1. **Phase 1**: Maze generation (testable in isolation)
2. **Phase 2**: Player movement with collision
3. **Phase 3**: Rendering system
4. **Phase 4**: Menu system
5. **Phase 5**: Integration & polish

Each phase produces a working increment that can be tested.
