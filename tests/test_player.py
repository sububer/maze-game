"""Unit tests for the player module."""

import config as cfg
from player import Player


class TestPlayerInitialization:
    """Tests for Player initialization."""

    def test_position_set_from_start_pos(self):
        """Player position should be set from start_pos."""
        player = Player((5, 3))
        assert player.row == 5
        assert player.col == 3

    def test_default_color_applied(self):
        """Player should use default color from config."""
        player = Player((0, 0))
        assert player.color == cfg.PLAYER_COLOR

    def test_custom_color(self):
        """Player should accept custom color."""
        custom_color = (255, 0, 0)
        player = Player((0, 0), color=custom_color)
        assert player.color == custom_color


class TestPlayerMovement:
    """Tests for Player movement."""

    def test_move_up_decrements_row(self):
        """Moving up should decrement row."""
        player = Player((5, 5))
        player.move("up")
        assert player.row == 4
        assert player.col == 5

    def test_move_down_increments_row(self):
        """Moving down should increment row."""
        player = Player((5, 5))
        player.move("down")
        assert player.row == 6
        assert player.col == 5

    def test_move_left_decrements_col(self):
        """Moving left should decrement column."""
        player = Player((5, 5))
        player.move("left")
        assert player.row == 5
        assert player.col == 4

    def test_move_right_increments_col(self):
        """Moving right should increment column."""
        player = Player((5, 5))
        player.move("right")
        assert player.row == 5
        assert player.col == 6

    def test_invalid_direction_no_change(self):
        """Invalid direction should not change position."""
        player = Player((5, 5))
        player.move("invalid")
        assert player.row == 5
        assert player.col == 5

    def test_multiple_moves(self):
        """Multiple moves should accumulate correctly."""
        player = Player((5, 5))
        player.move("up")
        player.move("right")
        player.move("down")
        player.move("left")
        # Should be back at start
        assert player.row == 5
        assert player.col == 5


class TestPlayerPosition:
    """Tests for Player position property."""

    def test_position_returns_tuple(self):
        """Position property should return (row, col) tuple."""
        player = Player((3, 7))
        assert player.position == (3, 7)

    def test_position_updates_after_move(self):
        """Position should reflect movement."""
        player = Player((5, 5))
        player.move("up")
        assert player.position == (4, 5)
