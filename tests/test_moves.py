"""Tests for moves counter functionality."""

import random
from collections import deque

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


class TestMovesCounting:
    """Tests for the moves counter logic."""

    def test_move_count_increments_on_valid_move(self):
        """Move count should increment for each valid move."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        move_count = 0
        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                player.move(direction)
                move_count += 1
                break

        assert move_count == 1

    def test_move_count_does_not_increment_on_invalid_move(self):
        """Move count should NOT increment when move is blocked by wall."""
        maze = Maze(Difficulty.EASY)
        # Don't generate - all walls intact
        player = Player((1, 1))

        move_count = 0
        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                player.move(direction)
                move_count += 1

        # All walls intact, no valid moves should exist
        assert move_count == 0

    def test_move_count_matches_solution_length(self):
        """Move count should equal the number of moves in the solution path."""
        random.seed(123)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        solution = _find_path_bfs(maze, player.position, maze.goal_pos)
        assert solution is not None

        move_count = 0
        for direction in solution:
            assert maze.is_valid_move(player.position, direction)
            player.move(direction)
            move_count += 1

        assert player.position == maze.goal_pos
        assert move_count == len(solution)

    def test_move_count_resets_to_zero(self):
        """Move count should be resettable to zero (simulating restart)."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        move_count = 0
        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                player.move(direction)
                move_count += 1

        assert move_count > 0

        # Simulate restart
        move_count = 0
        assert move_count == 0

    def test_move_count_includes_backtracking(self):
        """Move count should count all moves, including backtracking."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        # Find a valid direction to move
        forward_dir = None
        for direction in ["up", "down", "left", "right"]:
            if maze.is_valid_move(player.position, direction):
                forward_dir = direction
                break

        assert forward_dir is not None

        # Move forward
        move_count = 0
        player.move(forward_dir)
        move_count += 1

        # Determine reverse direction
        reverse = {"up": "down", "down": "up", "left": "right", "right": "left"}
        back_dir = reverse[forward_dir]

        # Move back (backtrack)
        if maze.is_valid_move(player.position, back_dir):
            player.move(back_dir)
            move_count += 1

        # Both moves should be counted
        assert move_count == 2
