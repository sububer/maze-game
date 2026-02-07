"""Unit tests for the tag_game module."""

import random
from unittest.mock import patch

import config as cfg
from maze import Difficulty
from tag_game import TagGame


class TestTagGameInitialization:
    """Tests for TagGame initialization."""

    def test_initial_scores_zero(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        assert game.scores == [0, 0]

    def test_initial_round_zero(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        assert game.round_num == 0

    def test_initial_tagger_is_p1(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        assert game.tagger_player_num == 1

    def test_win_score_stored(self):
        game = TagGame(Difficulty.HARD, win_score=5)
        assert game.win_score == 5

    def test_difficulty_stored(self):
        game = TagGame(Difficulty.VERY_HARD, win_score=1)
        assert game.difficulty == Difficulty.VERY_HARD


class TestStartRound:
    """Tests for TagGame.start_round()."""

    def test_round_number_increments(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.round_num == 1
        game.round_active = False
        game.start_round()
        assert game.round_num == 2

    def test_maze_created(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.maze is not None
        assert game.maze.rows == 30
        assert game.maze.cols == 30

    def test_players_created(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.players[0] is not None
        assert game.players[1] is not None

    def test_players_at_different_positions(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.players[0].position != game.players[1].position

    def test_tagger_has_correct_color_p1(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.tagger_player_num = 1
        game.start_round()
        assert game.players[0].color == cfg.TAGGER_COLOR
        assert game.players[0].label == "IT"
        assert game.players[1].color == cfg.RUNNER_COLOR

    def test_tagger_has_correct_color_p2(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.tagger_player_num = 2
        game.start_round()
        assert game.players[1].color == cfg.TAGGER_COLOR
        assert game.players[1].label == "IT"
        assert game.players[0].color == cfg.RUNNER_COLOR

    def test_tagger_moves_reset(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.tagger_moves == 0

    def test_round_active(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.round_active is True


class TestProcessMove:
    """Tests for TagGame.process_move()."""

    def test_valid_move_returns_true(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        p1 = game.players[0]
        # Find a valid direction
        for d in ["up", "down", "left", "right"]:
            if game.maze.is_valid_move(p1.position, d):
                assert game.process_move(1, d) is True
                break

    def test_invalid_move_returns_false(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        # All walls on boundary should fail for certain directions
        assert game.process_move(1, "invalid_dir") is False

    def test_tagger_moves_counted(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        p1 = game.players[0]
        # P1 is tagger, find valid move
        for d in ["up", "down", "left", "right"]:
            if game.maze.is_valid_move(p1.position, d):
                game.process_move(1, d)
                break
        assert game.tagger_moves == 1

    def test_runner_moves_not_counted_as_tagger(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        p2 = game.players[1]
        for d in ["up", "down", "left", "right"]:
            if game.maze.is_valid_move(p2.position, d):
                game.process_move(2, d)
                break
        assert game.tagger_moves == 0

    def test_move_when_not_active_returns_false(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        game.round_active = False
        assert game.process_move(1, "up") is False


class TestCheckTag:
    """Tests for TagGame.check_tag()."""

    def test_different_positions_no_tag(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.check_tag() is False

    def test_same_position_is_tag(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        # Force players to same position
        game.players[1].row = game.players[0].row
        game.players[1].col = game.players[0].col
        assert game.check_tag() is True


class TestEndRound:
    """Tests for TagGame.end_round()."""

    def test_tagged_awards_tagger(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.tagger_player_num = 1
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1010.0):
            game.end_round("tagged")
        assert game.scores == [1, 0]

    def test_timeout_awards_runner(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.tagger_player_num = 1
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1120.0):
            game.end_round("timeout")
        assert game.scores == [0, 1]

    def test_round_deactivated(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1010.0):
            game.end_round("tagged")
        assert game.round_active is False

    def test_result_stored(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1010.0):
            game.end_round("timeout")
        assert game.round_result == "timeout"


class TestSwapRoles:
    """Tests for TagGame.swap_roles()."""

    def test_swap_from_p1_to_p2(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        assert game.tagger_player_num == 1
        game.swap_roles()
        assert game.tagger_player_num == 2

    def test_swap_from_p2_to_p1(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        game.tagger_player_num = 2
        game.swap_roles()
        assert game.tagger_player_num == 1

    def test_double_swap_returns_to_original(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        game.swap_roles()
        game.swap_roles()
        assert game.tagger_player_num == 1


class TestCheckGameOver:
    """Tests for TagGame.check_game_over()."""

    def test_no_winner_at_start(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        assert game.check_game_over() is None

    def test_p1_wins(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        game.scores = [3, 1]
        assert game.check_game_over() == 1

    def test_p2_wins(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        game.scores = [2, 3]
        assert game.check_game_over() == 2

    def test_no_winner_below_threshold(self):
        game = TagGame(Difficulty.HARD, win_score=3)
        game.scores = [2, 2]
        assert game.check_game_over() is None

    def test_win_score_1(self):
        game = TagGame(Difficulty.HARD, win_score=1)
        game.scores = [1, 0]
        assert game.check_game_over() == 1


class TestCheckTimeout:
    """Tests for TagGame.check_timeout()."""

    def test_no_timeout_before_start(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        # Timer not started yet
        assert game.check_timeout() is False

    def test_no_timeout_within_limit(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1060.0):
            assert game.check_timeout() is False

    def test_timeout_after_limit(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1121.0):
            assert game.check_timeout() is True
        assert game.round_result == "timeout"
        assert game.round_active is False


class TestGetRemaining:
    """Tests for TagGame.get_remaining()."""

    def test_full_time_before_start(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        assert game.get_remaining() == cfg.TAG_TIME_LIMIT

    def test_remaining_decreases(self):
        random.seed(42)
        game = TagGame(Difficulty.HARD, win_score=3)
        game.start_round()
        game.round_start_time = 1000.0
        with patch("tag_game.time.time", return_value=1030.0):
            assert game.get_remaining() == cfg.TAG_TIME_LIMIT - 30.0
