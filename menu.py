import pygame

import config as cfg
from maze import Difficulty


class Menu:
    DIFFICULTIES = [
        (Difficulty.EASY, "Easy", "10x10 maze, simple paths"),
        (Difficulty.MEDIUM, "Medium", "20x20 maze, moderate complexity"),
        (Difficulty.HARD, "Hard", "30x30 maze, complex paths"),
        (Difficulty.VERY_HARD, "Very Hard", "40x40 maze, maximum complexity"),
    ]

    def __init__(self):
        self.selected_index = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

    @property
    def selected_difficulty(self) -> Difficulty:
        return self.DIFFICULTIES[self.selected_index][0]

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle menu input. Returns 'start' if game should start."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.DIFFICULTIES)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.DIFFICULTIES)
            elif event.key == pygame.K_RETURN:
                return "start"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the menu screen."""
        surface.fill(cfg.BLACK)

        # Title
        title = self.font_large.render("MAZE GAME", True, cfg.WHITE)
        title_rect = title.get_rect(center=(cfg.WIDTH // 2, 100))
        surface.blit(title, title_rect)

        # Instructions
        instructions = self.font_small.render(
            "Use UP/DOWN to select, ENTER to start", True, (150, 150, 150)
        )
        inst_rect = instructions.get_rect(center=(cfg.WIDTH // 2, 180))
        surface.blit(instructions, inst_rect)

        # Difficulty options
        y_start = 280
        for i, (diff, name, desc) in enumerate(self.DIFFICULTIES):
            is_selected = i == self.selected_index

            # Selection indicator
            if is_selected:
                color = cfg.PAC_COLOR
                prefix = "> "
            else:
                color = cfg.WHITE
                prefix = "  "

            # Difficulty name
            text = self.font_medium.render(f"{prefix}{name}", True, color)
            text_rect = text.get_rect(center=(cfg.WIDTH // 2, y_start + i * 80))
            surface.blit(text, text_rect)

            # Description
            desc_color = (200, 200, 200) if is_selected else (100, 100, 100)
            desc_text = self.font_small.render(desc, True, desc_color)
            desc_y = y_start + i * 80 + 30
            desc_rect = desc_text.get_rect(center=(cfg.WIDTH // 2, desc_y))
            surface.blit(desc_text, desc_rect)

        # Controls hint at bottom
        controls = self.font_small.render(
            "In game: Arrow keys to move, R to restart, ESC for menu",
            True,
            (100, 100, 100),
        )
        controls_rect = controls.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT - 50))
        surface.blit(controls, controls_rect)
