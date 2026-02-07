"""Tests for moves counter functionality using the production try_move function."""

import random
from collections import deque

from main import try_move
from maze import Difficulty, Maze
from player import Player


def _find_path_bfs(maze, start_pos, goal_pos):
    """Find path from start to goal using BFS.

    Returns list of directions or None if no path exists.
    """
    visited = {start_pos}
    queue = deque([(start_pos, [])])

    while queue:
        pos, path = queue.popleft()
        if pos == goal_pos:
            return path

        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(pos, direction):
                row, col = pos
                if direction == "up":
                    new_pos = (row - 1, col)
                elif direction == "down":
                    new_pos = (row + 1, col)
                elif direction == "left":
                    new_pos = (row, col - 1)
                else:
                    new_pos = (row, col + 1)

                if new_pos not in visited:
                    visited.add(new_pos)
                    queue.append((new_pos, path + [direction]))

    return None


class TestTryMove:
    """Tests for the try_move function."""

    def test_valid_move_returns_true(self):
        """try_move should return True for a valid move."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                assert try_move(maze, player, direction) is True
                break

    def test_valid_move_updates_position(self):
        """try_move should update the player position on valid move."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)
        old_pos = player.position

        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                try_move(maze, player, direction)
                assert player.position != old_pos
                break

    def test_invalid_move_returns_false(self):
        """try_move should return False when blocked by a wall."""
        maze = Maze(Difficulty.EASY)
        # Don't generate - all walls intact
        player = Player((1, 1))

        for direction in ["up", "down", "left", "right"]:
            assert try_move(maze, player, direction) is False

    def test_invalid_move_preserves_position(self):
        """try_move should not change position when blocked by a wall."""
        maze = Maze(Difficulty.EASY)
        player = Player((1, 1))
        old_pos = player.position

        for direction in ["up", "down", "left", "right"]:
            try_move(maze, player, direction)

        assert player.position == old_pos


class TestMovesCounting:
    """Tests for counting moves using try_move."""

    def test_count_increments_only_on_valid_moves(self):
        """Move count should only increment when try_move returns True."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        move_count = 0
        for direction in ["up", "down", "left", "right"]:
            if try_move(maze, player, direction):
                move_count += 1

        # At least one direction should be valid from start
        assert move_count >= 1

    def test_count_does_not_increment_on_wall_collisions(self):
        """Move count should stay zero when all moves are blocked."""
        maze = Maze(Difficulty.EASY)
        # Don't generate - all walls intact
        player = Player((1, 1))

        move_count = 0
        for direction in ["up", "down", "left", "right"]:
            if try_move(maze, player, direction):
                move_count += 1

        assert move_count == 0

    def test_count_matches_solution_length(self):
        """Move count should equal solution path length."""
        random.seed(123)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        solution = _find_path_bfs(maze, player.position, maze.goal_pos)
        assert solution is not None

        move_count = 0
        for direction in solution:
            if try_move(maze, player, direction):
                move_count += 1

        assert player.position == maze.goal_pos
        assert move_count == len(solution)

    def test_count_includes_backtracking(self):
        """Move count should count all moves including backtracking."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        # Find a valid direction
        forward_dir = None
        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                forward_dir = direction
                break
        assert forward_dir is not None

        move_count = 0
        reverse = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }

        # Move forward
        if try_move(maze, player, forward_dir):
            move_count += 1

        # Move back
        if try_move(maze, player, reverse[forward_dir]):
            move_count += 1

        assert move_count == 2
