import pygame

import config as cfg


class Player:
    _font_cache: dict[int, pygame.font.Font] = {}

    def __init__(
        self, start_pos: tuple[int, int], color: tuple = None, label: str = None
    ):
        self.row, self.col = start_pos
        self.color = color if color else cfg.PLAYER_COLOR
        self.label = label

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

    def draw(self, surface: pygame.Surface, maze, draw_label: bool = False) -> None:
        """Draw player at current grid position."""
        cell_size = maze.get_cell_size()
        x, y = maze.grid_to_pixel(self.row, self.col)
        radius = int(cell_size / 3)
        pygame.draw.circle(surface, self.color, (int(x), int(y)), radius)

        if draw_label and self.label:
            font_size = max(10, int(cell_size / 3))
            if font_size not in Player._font_cache:
                Player._font_cache[font_size] = pygame.font.Font(None, font_size)
            font = Player._font_cache[font_size]
            label_surface = font.render(self.label, True, cfg.WHITE)
            label_rect = label_surface.get_rect(center=(int(x), int(y) - radius - 6))
            surface.blit(label_surface, label_rect)
