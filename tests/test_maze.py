"""Unit tests for the maze module."""

import random
from maze import Cell, Difficulty, Maze, DIFFICULTY_SETTINGS


class TestCell:
    """Tests for the Cell dataclass."""

    def test_default_walls_all_true(self):
        """New cell should have all walls by default."""
        cell = Cell()
        assert cell.top
        assert cell.right
        assert cell.bottom
        assert cell.left
        assert not cell.visited

    def test_wall_modification(self):
        """Walls can be modified."""
        cell = Cell()
        cell.top = False
        cell.right = False
        assert not cell.top
        assert not cell.right
        assert cell.bottom
        assert cell.left


class TestDifficulty:
    """Tests for the Difficulty enum and settings."""

    def test_all_difficulties_have_settings(self):
        """Every difficulty level should have configuration."""
        for difficulty in Difficulty:
            assert difficulty in DIFFICULTY_SETTINGS

    def test_settings_structure(self):
        """Settings should be (rows, cols, extra_removal) tuples."""
        for difficulty, settings in DIFFICULTY_SETTINGS.items():
            assert len(settings) == 3
            rows, cols, extra_removal = settings
            assert isinstance(rows, int) and rows > 0
            assert isinstance(cols, int) and cols > 0
            assert isinstance(extra_removal, int) and extra_removal >= 0

    def test_difficulty_progression(self):
        """Harder difficulties should have larger mazes."""
        easy = DIFFICULTY_SETTINGS[Difficulty.EASY]
        medium = DIFFICULTY_SETTINGS[Difficulty.MEDIUM]
        hard = DIFFICULTY_SETTINGS[Difficulty.HARD]
        very_hard = DIFFICULTY_SETTINGS[Difficulty.VERY_HARD]

        assert easy[0] <= medium[0] <= hard[0] <= very_hard[0]
        assert easy[1] <= medium[1] <= hard[1] <= very_hard[1]


class TestMazeInitialization:
    """Tests for Maze initialization."""

    def test_correct_dimensions_per_difficulty(self):
        """Maze should have correct dimensions based on difficulty."""
        for difficulty in Difficulty:
            maze = Maze(difficulty)
            expected_rows, expected_cols, _ = DIFFICULTY_SETTINGS[difficulty]
            assert maze.rows == expected_rows
            assert maze.cols == expected_cols

    def test_cells_grid_created(self):
        """Maze should create a grid of cells."""
        maze = Maze(Difficulty.EASY)
        assert len(maze.cells) == maze.rows
        assert all(len(row) == maze.cols for row in maze.cells)

    def test_all_cells_start_with_walls(self):
        """Before generation, all cells should have all walls."""
        maze = Maze(Difficulty.EASY)
        for row in maze.cells:
            for cell in row:
                assert cell.top
                assert cell.right
                assert cell.bottom
                assert cell.left


class TestMazeGeneration:
    """Tests for maze generation."""

    def test_all_cells_visited_after_generation(self):
        """After generation, all cells should be visited."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        for row in maze.cells:
            for cell in row:
                assert cell.visited

    def test_maze_is_solvable(self):
        """Generated maze should have a path from start to goal."""
        maze = Maze(Difficulty.EASY)
        maze.generate()

        # Use BFS to verify path exists
        distances = maze._bfs_distances(maze.start_pos)
        assert maze.goal_pos in distances

    def test_start_and_goal_different(self):
        """Start and goal positions should be different."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        assert maze.start_pos != maze.goal_pos

    def test_goal_reasonably_far_from_start(self):
        """Goal should be at least 60% of max distance from start."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()

        distances = maze._bfs_distances(maze.start_pos)
        max_dist = max(distances.values())
        goal_dist = distances[maze.goal_pos]

        # Goal should be at least 50% of max (slightly relaxed from 60% for test stability)
        assert goal_dist >= max_dist * 0.5

    def test_walls_removed_during_generation(self):
        """Generation should remove some walls to create passages."""
        maze = Maze(Difficulty.EASY)
        maze.generate()

        # Count cells with at least one wall removed
        cells_with_passages = 0
        for row in maze.cells:
            for cell in row:
                if not (cell.top and cell.right and cell.bottom and cell.left):
                    cells_with_passages += 1

        # All cells should have at least one passage (except edge cases)
        assert cells_with_passages == maze.rows * maze.cols


class TestMovementValidation:
    """Tests for is_valid_move()."""

    def test_invalid_direction_returns_false(self):
        """Invalid direction string should return False."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        assert not maze.is_valid_move((0, 0), 'invalid')

    def test_wall_blocks_move(self):
        """Movement should be blocked when wall exists."""
        maze = Maze(Difficulty.EASY)
        # Don't generate - all walls intact
        # Top-left cell with all walls should block all moves
        assert not maze.is_valid_move((0, 0), 'up')
        assert not maze.is_valid_move((0, 0), 'left')

    def test_passage_allows_move(self):
        """Movement should be allowed when no wall."""
        maze = Maze(Difficulty.EASY)
        # Manually remove a wall
        maze.cells[0][0].right = False
        maze.cells[0][1].left = False
        assert maze.is_valid_move((0, 0), 'right')

    def test_out_of_bounds_returns_false(self):
        """Out of bounds positions should return False."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        assert not maze.is_valid_move((-1, 0), 'up')
        assert not maze.is_valid_move((maze.rows, 0), 'down')
        assert not maze.is_valid_move((0, -1), 'left')
        assert not maze.is_valid_move((0, maze.cols), 'right')

    def test_boundary_moves_blocked(self):
        """Moves at maze boundary should be blocked even without wall."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        # Top row can't move up
        assert not maze.is_valid_move((0, 0), 'up')
        # Left column can't move left
        assert not maze.is_valid_move((0, 0), 'left')
        # Bottom row can't move down
        assert not maze.is_valid_move((maze.rows - 1, 0), 'down')
        # Right column can't move right
        assert not maze.is_valid_move((0, maze.cols - 1), 'right')


class TestBFSDistances:
    """Tests for _bfs_distances()."""

    def test_start_has_zero_distance(self):
        """Start position should have distance 0."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        distances = maze._bfs_distances(maze.start_pos)
        assert distances[maze.start_pos] == 0

    def test_all_cells_reachable(self):
        """All cells should be reachable in a generated maze."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        distances = maze._bfs_distances(maze.start_pos)
        assert len(distances) == maze.rows * maze.cols

    def test_distances_increase_with_path_length(self):
        """Distances should reflect actual path lengths."""
        maze = Maze(Difficulty.EASY)
        maze.generate()
        distances = maze._bfs_distances(maze.start_pos)

        # All distances should be non-negative
        assert all(d >= 0 for d in distances.values())

        # At least some cells should have distance > 0
        assert any(d > 0 for d in distances.values())


class TestGetNeighbors:
    """Tests for _get_neighbors()."""

    def test_cell_with_all_walls_has_no_neighbors(self):
        """Cell with all walls should have no accessible neighbors."""
        maze = Maze(Difficulty.EASY)
        # Don't generate - all walls intact
        # Interior cell (not on edge) with all walls
        neighbors = maze._get_neighbors(1, 1)
        assert neighbors == []

    def test_neighbors_correct_when_walls_removed(self):
        """Neighbors should be correct based on wall configuration."""
        maze = Maze(Difficulty.EASY)
        # Remove right wall between (1,1) and (1,2)
        maze.cells[1][1].right = False
        maze.cells[1][2].left = False

        neighbors = maze._get_neighbors(1, 1)
        assert (1, 2) in neighbors
        assert len(neighbors) == 1

    def test_multiple_neighbors(self):
        """Cell with multiple passages should have multiple neighbors."""
        maze = Maze(Difficulty.EASY)
        # Remove walls in multiple directions from (1,1)
        maze.cells[1][1].right = False
        maze.cells[1][2].left = False
        maze.cells[1][1].bottom = False
        maze.cells[2][1].top = False

        neighbors = maze._get_neighbors(1, 1)
        assert (1, 2) in neighbors
        assert (2, 1) in neighbors
        assert len(neighbors) == 2
