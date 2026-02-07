import time

import config as cfg
from maze import Difficulty, Maze
from player import Player


class TagGame:
    """Encapsulates all state and logic for 2-player tag mode."""

    def __init__(self, difficulty: Difficulty, win_score: int):
        self.difficulty = difficulty
        self.win_score = win_score
        self.scores = [0, 0]  # [P1_score, P2_score]
        self.round_num = 0
        self.tagger_player_num = 1  # 1 or 2; who is "it"

        # Per-round state (set in start_round)
        self.maze: Maze | None = None
        self.players: list[Player | None] = [None, None]  # index 0=P1, 1=P2
        self.tagger_moves = 0
        self.round_start_time: float | None = None
        self.round_elapsed: float = 0.0
        self.round_result: str | None = None  # "tagged" or "timeout"
        self.round_active = False

        # Future hook for power-ups
        self.cell_effects: dict[tuple, str] = {}

    def start_round(self) -> None:
        """Initialize a new round with a fresh maze and player positions."""
        self.round_num += 1
        self.tagger_moves = 0
        self.round_start_time = None
        self.round_elapsed = 0.0
        self.round_result = None
        self.round_active = True
        self.cell_effects = {}

        # Generate maze with extra loops for chase dynamics
        self.maze = Maze(self.difficulty)
        self.maze.generate()
        self.maze.remove_extra_walls_percent(cfg.TAG_LOOP_PERCENT)

        # Place players at maximally distant positions
        pos1, pos2 = self.maze.place_two_players()

        # Assign colors and labels based on who is tagger
        if self.tagger_player_num == 1:
            self.players[0] = Player(pos1, color=cfg.TAGGER_COLOR, label="IT")
            self.players[1] = Player(pos2, color=cfg.RUNNER_COLOR, label="P2")
        else:
            self.players[0] = Player(pos1, color=cfg.RUNNER_COLOR, label="P1")
            self.players[1] = Player(pos2, color=cfg.TAGGER_COLOR, label="IT")

    def process_move(self, player_num: int, direction: str) -> bool:
        """Process a move for the given player (1 or 2).

        Returns True if the move was valid and executed.
        """
        if not self.round_active or self.maze is None:
            return False

        player = self.players[player_num - 1]
        if player is None:
            return False

        if not self.maze.is_valid_move(player.position, direction):
            return False

        # Start timer on first move of the round
        if self.round_start_time is None:
            self.round_start_time = time.time()

        player.move(direction)

        # Track tagger moves
        if player_num == self.tagger_player_num:
            self.tagger_moves += 1

        # Check for cell effects (future hook)
        pos = player.position
        if pos in self.cell_effects:
            pass  # Future: handle power-ups/glue/tunnels

        # Check if tag occurred
        if self.check_tag():
            self.end_round("tagged")

        return True

    def check_tag(self) -> bool:
        """Check if tagger and runner are on the same cell."""
        if self.players[0] is None or self.players[1] is None:
            return False
        return self.players[0].position == self.players[1].position

    def check_timeout(self) -> bool:
        """Check if the round time limit has expired.

        Returns True if timeout occurred and round was ended.
        """
        if not self.round_active or self.round_start_time is None:
            return False

        elapsed = time.time() - self.round_start_time
        if elapsed >= cfg.TAG_TIME_LIMIT:
            self.round_elapsed = cfg.TAG_TIME_LIMIT
            self.end_round("timeout")
            return True
        return False

    def get_elapsed(self) -> float:
        """Get current elapsed time for the round."""
        if self.round_start_time is None:
            return 0.0
        if not self.round_active:
            return self.round_elapsed
        return time.time() - self.round_start_time

    def get_remaining(self) -> float:
        """Get remaining time in the round."""
        return max(0.0, cfg.TAG_TIME_LIMIT - self.get_elapsed())

    def end_round(self, result: str) -> None:
        """End the current round and award a point."""
        self.round_active = False
        self.round_result = result
        if self.round_start_time is not None:
            self.round_elapsed = time.time() - self.round_start_time

        if result == "tagged":
            # Tagger wins the round
            self.scores[self.tagger_player_num - 1] += 1
        elif result == "timeout":
            # Runner wins the round (runner is the other player)
            runner_num = 2 if self.tagger_player_num == 1 else 1
            self.scores[runner_num - 1] += 1

    def swap_roles(self) -> None:
        """Swap tagger/runner roles for the next round."""
        self.tagger_player_num = 2 if self.tagger_player_num == 1 else 1

    def check_game_over(self) -> int | None:
        """Check if a player has reached the win score.

        Returns the winning player number (1 or 2), or None.
        """
        if self.scores[0] >= self.win_score:
            return 1
        if self.scores[1] >= self.win_score:
            return 2
        return None
