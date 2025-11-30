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

    SHADES = ["Light", "Medium", "Dark"]

    def __init__(self):
        self.selected_index = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        # Settings state
        self.breadcrumbs_enabled = True
        self.shade_index = 1  # Default to Medium

        # Navigation indices: difficulties first, then breadcrumbs toggle, then shade
        self.menu_items_count = len(self.DIFFICULTIES) + 2

    @property
    def selected_difficulty(self) -> Difficulty:
        # Clamp to difficulty range in case we're on a settings item
        diff_index = min(self.selected_index, len(self.DIFFICULTIES) - 1)
        return self.DIFFICULTIES[diff_index][0]

    @property
    def breadcrumb_opacity(self) -> int:
        """Return the opacity value for the selected shade."""
        shade_map = {
            0: cfg.BREADCRUMB_LIGHT,
            1: cfg.BREADCRUMB_MEDIUM,
            2: cfg.BREADCRUMB_DARK,
        }
        return shade_map[self.shade_index]

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle menu input. Returns 'start' if game should start."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % self.menu_items_count
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % self.menu_items_count
            elif event.key == pygame.K_RETURN:
                # If on a difficulty, start game
                if self.selected_index < len(self.DIFFICULTIES):
                    return "start"
                # If on breadcrumbs toggle, toggle it
                elif self.selected_index == len(self.DIFFICULTIES):
                    self.breadcrumbs_enabled = not self.breadcrumbs_enabled
                # If on shade, cycle through shades
                elif self.selected_index == len(self.DIFFICULTIES) + 1:
                    self.shade_index = (self.shade_index + 1) % len(self.SHADES)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                # Left/right to adjust settings
                if self.selected_index == len(self.DIFFICULTIES):
                    self.breadcrumbs_enabled = not self.breadcrumbs_enabled
                elif self.selected_index == len(self.DIFFICULTIES) + 1:
                    self.shade_index = (self.shade_index - 1) % len(self.SHADES)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.selected_index == len(self.DIFFICULTIES):
                    self.breadcrumbs_enabled = not self.breadcrumbs_enabled
                elif self.selected_index == len(self.DIFFICULTIES) + 1:
                    self.shade_index = (self.shade_index + 1) % len(self.SHADES)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the menu screen."""
        surface.fill(cfg.BLACK)

        # Title
        title = self.font_large.render("MAZE GAME", True, cfg.WHITE)
        title_rect = title.get_rect(center=(cfg.WIDTH // 2, 80))
        surface.blit(title, title_rect)

        # Instructions
        instructions = self.font_small.render(
            "Use UP/DOWN to select, ENTER to start/toggle, LEFT/RIGHT to adjust",
            True,
            (150, 150, 150),
        )
        inst_rect = instructions.get_rect(center=(cfg.WIDTH // 2, 140))
        surface.blit(instructions, inst_rect)

        # Difficulty options
        y_start = 200
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
            text_rect = text.get_rect(center=(cfg.WIDTH // 2, y_start + i * 60))
            surface.blit(text, text_rect)

            # Description
            desc_color = (200, 200, 200) if is_selected else (100, 100, 100)
            desc_text = self.font_small.render(desc, True, desc_color)
            desc_y = y_start + i * 60 + 25
            desc_rect = desc_text.get_rect(center=(cfg.WIDTH // 2, desc_y))
            surface.blit(desc_text, desc_rect)

        # Settings section
        settings_y = y_start + len(self.DIFFICULTIES) * 60 + 40

        # Settings header
        header = self.font_small.render("─── Settings ───", True, (150, 150, 150))
        header_rect = header.get_rect(center=(cfg.WIDTH // 2, settings_y))
        surface.blit(header, header_rect)

        # Breadcrumbs toggle
        breadcrumb_idx = len(self.DIFFICULTIES)
        is_selected = self.selected_index == breadcrumb_idx
        color = cfg.PAC_COLOR if is_selected else cfg.WHITE
        prefix = "> " if is_selected else "  "
        on_off = "ON" if self.breadcrumbs_enabled else "OFF"
        bc_text = self.font_medium.render(f"{prefix}Breadcrumbs: {on_off}", True, color)
        bc_rect = bc_text.get_rect(center=(cfg.WIDTH // 2, settings_y + 50))
        surface.blit(bc_text, bc_rect)

        # Shade selector
        shade_idx = len(self.DIFFICULTIES) + 1
        is_selected = self.selected_index == shade_idx
        color = cfg.PAC_COLOR if is_selected else cfg.WHITE
        prefix = "> " if is_selected else "  "
        shade_name = self.SHADES[self.shade_index]
        shade_text = self.font_medium.render(
            f"{prefix}Trail Shade: {shade_name}", True, color
        )
        shade_rect = shade_text.get_rect(center=(cfg.WIDTH // 2, settings_y + 100))
        surface.blit(shade_text, shade_rect)

        # Controls hint at bottom
        controls = self.font_small.render(
            "In game: WASD to move, B to toggle breadcrumbs, R restart, ESC menu",
            True,
            (100, 100, 100),
        )
        controls_rect = controls.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT - 50))
        surface.blit(controls, controls_rect)
