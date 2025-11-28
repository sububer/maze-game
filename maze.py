import random
from collections import deque
from enum import Enum
from dataclasses import dataclass
import pygame
import config as cfg


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4


# Difficulty presets: (rows, cols, extra_walls_removed_percent)
# Higher extra_walls_removed = more loops = easier
DIFFICULTY_SETTINGS = {
    Difficulty.EASY: (10, 10, 15),
    Difficulty.MEDIUM: (20, 20, 8),
    Difficulty.HARD: (30, 30, 3),
    Difficulty.VERY_HARD: (40, 40, 0),
}


@dataclass
class Cell:
    """Represents a single cell in the maze with 4 walls."""
    top: bool = True
    right: bool = True
    bottom: bool = True
    left: bool = True
    visited: bool = False


class Maze:
    def __init__(self, difficulty: Difficulty = Difficulty.EASY):
        self.difficulty = difficulty
        rows, cols, self.extra_removal = DIFFICULTY_SETTINGS[difficulty]
        self.rows = rows
        self.cols = cols
        self.cells: list[list[Cell]] = [
            [Cell() for _ in range(cols)] for _ in range(rows)
        ]
        self.start_pos: tuple[int, int] = (0, 0)
        self.goal_pos: tuple[int, int] = (rows - 1, cols - 1)

    def generate(self) -> None:
        """Generate maze using recursive backtracking, then place start/goal."""
        self._recursive_backtrack(0, 0)
        self._remove_extra_walls()
        self._place_start_and_goal()

    def _recursive_backtrack(self, row: int, col: int) -> None:
        """Carve passages using recursive backtracking algorithm."""
        self.cells[row][col].visited = True

        # Get neighbors in random order
        directions = [(0, 1, 'right', 'left'),    # right
                      (0, -1, 'left', 'right'),   # left
                      (-1, 0, 'top', 'bottom'),   # up
                      (1, 0, 'bottom', 'top')]    # down
        random.shuffle(directions)

        for dr, dc, wall, opposite_wall in directions:
            new_row, new_col = row + dr, col + dc

            if (0 <= new_row < self.rows and
                0 <= new_col < self.cols and
                not self.cells[new_row][new_col].visited):

                # Remove walls between current cell and neighbor
                setattr(self.cells[row][col], wall, False)
                setattr(self.cells[new_row][new_col], opposite_wall, False)

                self._recursive_backtrack(new_row, new_col)

    def _remove_extra_walls(self) -> None:
        """Remove additional walls to create loops (makes maze easier)."""
        if self.extra_removal <= 0:
            return

        # Collect all internal walls
        internal_walls = []
        for row in range(self.rows):
            for col in range(self.cols):
                if col < self.cols - 1 and self.cells[row][col].right:
                    internal_walls.append((row, col, 'right', row, col + 1, 'left'))
                if row < self.rows - 1 and self.cells[row][col].bottom:
                    internal_walls.append((row, col, 'bottom', row + 1, col, 'top'))

        # Remove a percentage of walls
        num_to_remove = len(internal_walls) * self.extra_removal // 100
        walls_to_remove = random.sample(internal_walls, min(num_to_remove, len(internal_walls)))

        for r1, c1, wall1, r2, c2, wall2 in walls_to_remove:
            setattr(self.cells[r1][c1], wall1, False)
            setattr(self.cells[r2][c2], wall2, False)

    def _place_start_and_goal(self) -> None:
        """Place start and goal at random positions with good distance."""
        # Find all cells and their distances using BFS from a random start
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]

        # Pick random start
        self.start_pos = random.choice(all_cells)

        # Find distances from start to all cells
        distances = self._bfs_distances(self.start_pos)

        # Pick goal from cells with distance >= 60% of max distance
        max_dist = max(distances.values())
        min_goal_dist = max(1, int(max_dist * 0.6))

        candidates = [pos for pos, dist in distances.items() if dist >= min_goal_dist]
        if candidates:
            self.goal_pos = random.choice(candidates)
        else:
            # Fallback: pick the farthest cell
            self.goal_pos = max(distances.items(), key=lambda x: x[1])[0]

    def _bfs_distances(self, start: tuple[int, int]) -> dict[tuple[int, int], int]:
        """Calculate shortest path distances from start to all reachable cells."""
        distances = {start: 0}
        queue = deque([start])

        while queue:
            row, col = queue.popleft()
            current_dist = distances[(row, col)]

            for new_row, new_col in self._get_neighbors(row, col):
                if (new_row, new_col) not in distances:
                    distances[(new_row, new_col)] = current_dist + 1
                    queue.append((new_row, new_col))

        return distances

    def _get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        """Get accessible neighbors (no wall between)."""
        neighbors = []
        cell = self.cells[row][col]

        if not cell.top and row > 0:
            neighbors.append((row - 1, col))
        if not cell.bottom and row < self.rows - 1:
            neighbors.append((row + 1, col))
        if not cell.left and col > 0:
            neighbors.append((row, col - 1))
        if not cell.right and col < self.cols - 1:
            neighbors.append((row, col + 1))

        return neighbors

    def is_valid_move(self, from_pos: tuple[int, int], direction: str) -> bool:
        """Check if moving from from_pos in the given direction is valid."""
        row, col = from_pos

        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False

        cell = self.cells[row][col]

        if direction == 'up':
            return not cell.top and row > 0
        elif direction == 'down':
            return not cell.bottom and row < self.rows - 1
        elif direction == 'left':
            return not cell.left and col > 0
        elif direction == 'right':
            return not cell.right and col < self.cols - 1

        return False

    def get_cell(self, row: int, col: int) -> Cell:
        """Get the cell at the given position."""
        return self.cells[row][col]

    def get_cell_size(self) -> float:
        """Calculate cell size based on window dimensions."""
        usable_width = cfg.WIDTH - 2 * cfg.PADDING
        usable_height = cfg.HEIGHT - cfg.MASTHEAD - 2 * cfg.PADDING
        return min(usable_width / self.cols, usable_height / self.rows)

    def grid_to_pixel(self, row: int, col: int) -> tuple[float, float]:
        """Convert grid coordinates to pixel coordinates (center of cell)."""
        cell_size = self.get_cell_size()
        x = cfg.PADDING + col * cell_size + cell_size / 2
        y = cfg.MASTHEAD + cfg.PADDING + row * cell_size + cell_size / 2
        return (x, y)

    def draw(self, surface: pygame.Surface, color: tuple = None) -> None:
        """Draw the maze walls on the given surface."""
        if color is None:
            color = cfg.MAZE_COLOR

        cell_size = self.get_cell_size()
        line_width = max(2, int(cell_size / 10))

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.cells[row][col]
                x = cfg.PADDING + col * cell_size
                y = cfg.MASTHEAD + cfg.PADDING + row * cell_size

                if cell.top:
                    pygame.draw.line(surface, color,
                                   (x, y), (x + cell_size, y), line_width)
                if cell.right:
                    pygame.draw.line(surface, color,
                                   (x + cell_size, y), (x + cell_size, y + cell_size), line_width)
                if cell.bottom:
                    pygame.draw.line(surface, color,
                                   (x, y + cell_size), (x + cell_size, y + cell_size), line_width)
                if cell.left:
                    pygame.draw.line(surface, color,
                                   (x, y), (x, y + cell_size), line_width)

        # Draw start marker (green)
        start_x, start_y = self.grid_to_pixel(*self.start_pos)
        pygame.draw.circle(surface, (0, 200, 0), (int(start_x), int(start_y)),
                          int(cell_size / 4))

        # Draw goal marker (red)
        goal_x, goal_y = self.grid_to_pixel(*self.goal_pos)
        pygame.draw.rect(surface, (200, 0, 0),
                        (int(goal_x - cell_size/4), int(goal_y - cell_size/4),
                         int(cell_size/2), int(cell_size/2)))
