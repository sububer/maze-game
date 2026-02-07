"""Integration tests for tag mode."""

import random
from collections import deque
from unittest.mock import patch

import config as cfg
from maze import Difficulty
from tag_game import TagGame


def _find_path_bfs(maze, start_pos, goal_pos):
    """Find path from start to goal using BFS. Returns list of directions."""
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


class TestTagGameFullRound:
    """Test a full tag round where tagger catches runner."""

    def test_tagger_catches_runner(self):
        """Tagger should be able to navigate to runner and tag them."""
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()

        tagger_idx = game.tagger_player_num - 1
        runner_idx = 1 - tagger_idx

        tagger_pos = game.players[tagger_idx].position
        runner_pos = game.players[runner_idx].position

        # Find path from tagger to runner
        path = _find_path_bfs(game.maze, tagger_pos, runner_pos)
        assert path is not None, "Tagger should be able to reach runner"

        # Move tagger along the path
        for direction in path[:-1]:  # Stop one before the end
            game.process_move(game.tagger_player_num, direction)
            assert game.round_active, "Round should still be active"

        # Last move should trigger tag
        game.process_move(game.tagger_player_num, path[-1])
        assert not game.round_active
        assert game.round_result == "tagged"
        assert game.scores[tagger_idx] == 1

    def test_both_players_can_move(self):
        """Both P1 and P2 should be able to move independently."""
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()

        p1_start = game.players[0].position
        p2_start = game.players[1].position

        # Find valid moves for each player
        p1_moved = False
        for d in ["up", "down", "left", "right"]:
            if game.maze.is_valid_move(p1_start, d):
                game.process_move(1, d)
                p1_moved = True
                break

        p2_moved = False
        for d in ["up", "down", "left", "right"]:
            if game.maze.is_valid_move(p2_start, d):
                game.process_move(2, d)
                p2_moved = True
                break

        assert p1_moved, "P1 should have at least one valid move"
        assert p2_moved, "P2 should have at least one valid move"
        assert game.players[0].position != p1_start
        assert game.players[1].position != p2_start


class TestTagGameMultipleRounds:
    """Test multiple round progression with role swapping."""

    def test_roles_swap_between_rounds(self):
        """Tagger/runner roles should swap after each round."""
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)

        assert game.tagger_player_num == 1

        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1010.0):
            game.end_round("tagged")

        game.swap_roles()
        assert game.tagger_player_num == 2

        game.start_round()
        # P2 should now be tagger (orange-red with "IT" label)
        assert game.players[1].color == cfg.TAGGER_COLOR
        assert game.players[1].label == "IT"
        assert game.players[0].color == cfg.RUNNER_COLOR

    def test_game_ends_at_win_score(self):
        """Game should end when a player reaches the win score."""
        game = TagGame(Difficulty.HARD, win_score=2)

        # Simulate P1 winning 2 rounds
        game.scores = [2, 0]
        assert game.check_game_over() == 1

    def test_full_game_to_completion(self):
        """Simulate a full game from start to game over."""
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=1)
        game.start_round()

        tagger_idx = game.tagger_player_num - 1
        runner_idx = 1 - tagger_idx

        # Move tagger to runner
        path = _find_path_bfs(
            game.maze,
            game.players[tagger_idx].position,
            game.players[runner_idx].position,
        )
        for direction in path:
            game.process_move(game.tagger_player_num, direction)

        assert game.round_result == "tagged"
        assert game.check_game_over() is not None


class TestTagTimeout:
    """Test timeout scenarios."""

    def test_timeout_awards_runner(self):
        """When time expires, the runner should score."""
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.tagger_player_num = 1
        game.start_round()

        # Simulate timer start
        game.round_start_time = 1000.0
        # Simulate timeout
        with patch("tag_game.time.time", return_value=1000.0 + cfg.TAG_TIME_LIMIT + 1):
            timed_out = game.check_timeout()

        assert timed_out
        assert game.round_result == "timeout"
        # Runner is P2 when tagger is P1
        assert game.scores == [0, 1]


class TestMazeTagFeatures:
    """Test maze features specific to tag mode."""

    def test_players_placed_far_apart(self):
        """Players should be placed at maximally distant positions."""
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()

        p1_pos = game.players[0].position
        p2_pos = game.players[1].position

        # Calculate BFS distance between players
        distances = game.maze._bfs_distances(p1_pos)
        player_dist = distances[p2_pos]

        # Should be reasonably far apart (at least 30% of max distance)
        max_dist = max(distances.values())
        assert player_dist >= max_dist * 0.3, (
            f"Players too close: dist={player_dist}, max={max_dist}"
        )

    def test_tag_maze_has_extra_loops(self):
        """Tag mode mazes should have extra walls removed for more loops."""
        random.seed(42)

        # Generate standard Hard maze
        from maze import Maze

        maze_standard = Maze(Difficulty.HARD)
        maze_standard.generate()

        # Count walls in standard maze
        standard_walls = 0
        for row in maze_standard.cells:
            for cell in row:
                standard_walls += sum([cell.top, cell.right, cell.bottom, cell.left])

        # Generate tag maze (same difficulty + extra loop removal)
        random.seed(42)
        maze_tag = Maze(Difficulty.HARD)
        maze_tag.generate()
        maze_tag.remove_extra_walls_percent(cfg.TAG_LOOP_PERCENT)

        # Count walls in tag maze
        tag_walls = 0
        for row in maze_tag.cells:
            for cell in row:
                tag_walls += sum([cell.top, cell.right, cell.bottom, cell.left])

        # Tag maze should have fewer walls
        assert tag_walls < standard_walls
