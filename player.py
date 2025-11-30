import pygame

import config as cfg


class Player:
    def __init__(self, start_pos: tuple[int, int], color: tuple = None):
        self.row, self.col = start_pos
        self.color = color if color else cfg.PLAYER_COLOR

    @property
    def position(self) -> tuple[int, int]:
        return (self.row, self.col)

    def move(self, direction: str) -> None:
        """Move player in the given direction. Assumes move is valid."""
        if direction == "up":
            self.row -= 1
        elif direction == "down":
            self.row += 1
        elif direction == "left":
            self.col -= 1
        elif direction == "right":
            self.col += 1

    def draw(self, surface: pygame.Surface, maze) -> None:
        """Draw player at current grid position."""
        cell_size = maze.get_cell_size()
        x, y = maze.grid_to_pixel(self.row, self.col)
        radius = int(cell_size / 3)
        pygame.draw.circle(surface, self.color, (int(x), int(y)), radius)
