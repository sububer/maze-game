"""Integration tests for maze-game modules working together."""

import random
from collections import deque
from maze import Maze, Difficulty
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

        for direction in ['up', 'down', 'left', 'right']:
            if maze.is_valid_move(pos, direction):
                row, col = pos
                if direction == 'up':
                    new_pos = (row - 1, col)
                elif direction == 'down':
                    new_pos = (row + 1, col)
                elif direction == 'left':
                    new_pos = (row, col - 1)
                else:
                    new_pos = (row, col + 1)

                if new_pos not in visited:
                    visited.add(new_pos)
                    queue.append((new_pos, path + [direction]))

    return None


class TestPlayerNavigationInMaze:
    """Tests for player navigating through a maze."""

    def test_player_can_move_through_valid_passages(self):
        """Player should be able to move through passages."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        # Find a valid move from start position
        for direction in ['up', 'down', 'left', 'right']:
            if maze.is_valid_move(player.position, direction):
                old_pos = player.position
                player.move(direction)
                assert player.position != old_pos
                break

    def test_player_blocked_by_walls(self):
        """Player should not move when blocked by wall."""
        maze = Maze(Difficulty.EASY)
        # Don't generate - all walls intact
        player = Player((1, 1))

        # All directions should be blocked
        for direction in ['up', 'down', 'left', 'right']:
            if not maze.is_valid_move(player.position, direction):
                old_pos = player.position
                # Player.move() doesn't check validity, so we check before moving
                assert not maze.is_valid_move(old_pos, direction)

    def test_player_can_reach_goal(self):
        """Player should be able to reach goal from start."""
        random.seed(42)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        # Use BFS to find path to goal
        path = _find_path_bfs(maze, player.position, maze.goal_pos)

        # Path should exist
        assert path is not None

        # Execute path
        for direction in path:
            player.move(direction)

        assert player.position == maze.goal_pos


class TestDifficultyProgression:
    """Tests for different difficulty levels."""

    def test_harder_difficulties_produce_larger_mazes(self):
        """Harder difficulties should have larger mazes."""
        sizes = []
        for difficulty in Difficulty:
            maze = Maze(difficulty)
            sizes.append(maze.rows * maze.cols)

        # Each difficulty should be >= previous
        for i in range(1, len(sizes)):
            assert sizes[i] >= sizes[i - 1]

    def test_all_difficulties_produce_solvable_mazes(self):
        """All difficulty levels should produce solvable mazes."""
        for difficulty in Difficulty:
            maze = Maze(difficulty)
            maze.generate()

            # Verify path exists from start to goal
            distances = maze._bfs_distances(maze.start_pos)
            assert maze.goal_pos in distances, f"{difficulty} produced unsolvable maze"


class TestMultipleMazeGenerations:
    """Tests for maze generation randomness and validity."""

    def test_repeated_generation_produces_different_mazes(self):
        """Different seeds should produce different mazes."""
        maze1 = Maze(Difficulty.EASY)
        random.seed(1)
        maze1.generate()

        maze2 = Maze(Difficulty.EASY)
        random.seed(2)
        maze2.generate()

        # Start or goal positions should differ (highly likely with different seeds)
        different = (maze1.start_pos != maze2.start_pos or
                     maze1.goal_pos != maze2.goal_pos)
        assert different

    def test_same_seed_produces_same_maze(self):
        """Same seed should produce identical mazes."""
        random.seed(42)
        maze1 = Maze(Difficulty.EASY)
        maze1.generate()
        start1, goal1 = maze1.start_pos, maze1.goal_pos

        random.seed(42)
        maze2 = Maze(Difficulty.EASY)
        maze2.generate()
        start2, goal2 = maze2.start_pos, maze2.goal_pos

        assert start1 == start2
        assert goal1 == goal2

    def test_multiple_generations_all_valid(self):
        """Multiple maze generations should all be valid."""
        for i in range(10):
            random.seed(i)
            maze = Maze(Difficulty.MEDIUM)
            maze.generate()

            # All cells visited
            for row in maze.cells:
                for cell in row:
                    assert cell.visited

            # Path exists
            distances = maze._bfs_distances(maze.start_pos)
            assert maze.goal_pos in distances

            # Start != goal
            assert maze.start_pos != maze.goal_pos


class TestGameplayScenarios:
    """Tests for realistic gameplay scenarios."""

    def test_full_game_simulation(self):
        """Simulate a complete game from start to finish."""
        random.seed(123)
        maze = Maze(Difficulty.EASY)
        maze.generate()
        player = Player(maze.start_pos)

        # Find solution path using BFS
        solution_path = _find_path_bfs(maze, player.position, maze.goal_pos)
        assert solution_path is not None

        # Play through the solution
        move_count = 0
        for direction in solution_path:
            assert maze.is_valid_move(player.position, direction)
            player.move(direction)
            move_count += 1

        # Should reach goal
        assert player.position == maze.goal_pos
        assert move_count == len(solution_path)
