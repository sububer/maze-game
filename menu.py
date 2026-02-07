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

    TAG_DIFFICULTIES = [
        (Difficulty.HARD, "Hard", "30x30 maze"),
        (Difficulty.VERY_HARD, "Very Hard", "40x40 maze"),
    ]

    SHADES = ["Light", "Medium", "Dark"]

    GAME_MODES = ["Solo", "Tag"]

    def __init__(self):
        self.selected_index = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        # Settings state
        self.breadcrumbs_enabled = True
        self.shade_index = 1  # Default to Medium

        # Game mode state
        self.game_mode_index = 0  # 0=Solo, 1=Tag

        # Tag mode settings
        self.tag_difficulty_index = 0  # index into TAG_DIFFICULTIES
        self.tag_win_score_index = 1  # index into TAG_WIN_SCORES (default "3")

        self._update_menu_items_count()

    def _update_menu_items_count(self) -> None:
        """Update menu item count based on current game mode."""
        if self.game_mode == "Solo":
            # mode selector + difficulties + breadcrumbs + shade
            self.menu_items_count = 1 + len(self.DIFFICULTIES) + 2
        else:
            # mode selector + tag difficulties + first-to selector
            self.menu_items_count = 1 + len(self.TAG_DIFFICULTIES) + 1

    @property
    def game_mode(self) -> str:
        return self.GAME_MODES[self.game_mode_index]

    @property
    def selected_difficulty(self) -> Difficulty:
        if self.game_mode == "Solo":
            # Offset by 1 for mode selector row
            diff_index = min(self.selected_index - 1, len(self.DIFFICULTIES) - 1)
            diff_index = max(0, diff_index)
            return self.DIFFICULTIES[diff_index][0]
        else:
            return self.tag_difficulty

    @property
    def tag_difficulty(self) -> Difficulty:
        return self.TAG_DIFFICULTIES[self.tag_difficulty_index][0]

    @property
    def tag_win_score(self) -> int:
        return cfg.TAG_WIN_SCORES[self.tag_win_score_index]

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
        """Handle menu input. Returns 'start', 'start_tag', or None."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selected_index = (self.selected_index - 1) % self.menu_items_count
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selected_index = (self.selected_index + 1) % self.menu_items_count
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self._handle_left_right(-1)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self._handle_left_right(1)
        elif event.key == pygame.K_RETURN:
            return self._handle_enter()

        return None

    def _handle_left_right(self, direction: int) -> None:
        """Handle left/right input for the current selection."""
        # Row 0: mode selector
        if self.selected_index == 0:
            self.game_mode_index = (self.game_mode_index + direction) % len(
                self.GAME_MODES
            )
            self.selected_index = 0
            self._update_menu_items_count()
            return

        if self.game_mode == "Solo":
            solo_offset = self.selected_index - 1  # offset past mode selector
            bc_idx = len(self.DIFFICULTIES)
            shade_idx = len(self.DIFFICULTIES) + 1
            if solo_offset == bc_idx:
                self.breadcrumbs_enabled = not self.breadcrumbs_enabled
            elif solo_offset == shade_idx:
                self.shade_index = (self.shade_index + direction) % len(self.SHADES)
        else:
            tag_offset = self.selected_index - 1  # offset past mode selector
            win_idx = len(self.TAG_DIFFICULTIES)
            if tag_offset == win_idx:
                self.tag_win_score_index = (
                    self.tag_win_score_index + direction
                ) % len(cfg.TAG_WIN_SCORES)

    def _handle_enter(self) -> str | None:
        """Handle enter key press."""
        # Row 0: mode selector toggles mode
        if self.selected_index == 0:
            self.game_mode_index = (self.game_mode_index + 1) % len(self.GAME_MODES)
            self._update_menu_items_count()
            return None

        if self.game_mode == "Solo":
            solo_offset = self.selected_index - 1
            if solo_offset < len(self.DIFFICULTIES):
                return "start"
            elif solo_offset == len(self.DIFFICULTIES):
                self.breadcrumbs_enabled = not self.breadcrumbs_enabled
            elif solo_offset == len(self.DIFFICULTIES) + 1:
                self.shade_index = (self.shade_index + 1) % len(self.SHADES)
        else:
            tag_offset = self.selected_index - 1
            if tag_offset < len(self.TAG_DIFFICULTIES):
                self.tag_difficulty_index = tag_offset
                return "start_tag"
            elif tag_offset == len(self.TAG_DIFFICULTIES):
                self.tag_win_score_index = (self.tag_win_score_index + 1) % len(
                    cfg.TAG_WIN_SCORES
                )

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

        y = 200

        # Game mode selector (row 0)
        is_selected = self.selected_index == 0
        color = cfg.PAC_COLOR if is_selected else cfg.WHITE
        prefix = "> " if is_selected else "  "
        mode_text = self.font_medium.render(
            f"{prefix}Mode: {self.game_mode}", True, color
        )
        mode_rect = mode_text.get_rect(center=(cfg.WIDTH // 2, y))
        surface.blit(mode_text, mode_rect)
        if is_selected:
            hint = self.font_small.render(
                "LEFT/RIGHT to switch mode", True, (200, 200, 200)
            )
            hint_rect = hint.get_rect(center=(cfg.WIDTH // 2, y + 25))
            surface.blit(hint, hint_rect)

        y += 60

        if self.game_mode == "Solo":
            self._draw_solo_options(surface, y)
        else:
            self._draw_tag_options(surface, y)

    def _draw_solo_options(self, surface: pygame.Surface, y_start: int) -> None:
        """Draw solo mode menu options."""
        # Difficulty options (rows 1..4)
        for i, (diff, name, desc) in enumerate(self.DIFFICULTIES):
            menu_idx = i + 1  # offset by mode selector
            is_selected = menu_idx == self.selected_index

            color = cfg.PAC_COLOR if is_selected else cfg.WHITE
            prefix = "> " if is_selected else "  "

            text = self.font_medium.render(f"{prefix}{name}", True, color)
            text_rect = text.get_rect(center=(cfg.WIDTH // 2, y_start + i * 60))
            surface.blit(text, text_rect)

            desc_color = (200, 200, 200) if is_selected else (100, 100, 100)
            desc_text = self.font_small.render(desc, True, desc_color)
            desc_rect = desc_text.get_rect(
                center=(cfg.WIDTH // 2, y_start + i * 60 + 25)
            )
            surface.blit(desc_text, desc_rect)

        # Settings section
        settings_y = y_start + len(self.DIFFICULTIES) * 60 + 40

        header = self.font_small.render("─── Settings ───", True, (150, 150, 150))
        header_rect = header.get_rect(center=(cfg.WIDTH // 2, settings_y))
        surface.blit(header, header_rect)

        # Breadcrumbs toggle
        bc_menu_idx = 1 + len(self.DIFFICULTIES)
        is_selected = self.selected_index == bc_menu_idx
        color = cfg.PAC_COLOR if is_selected else cfg.WHITE
        prefix = "> " if is_selected else "  "
        on_off = "ON" if self.breadcrumbs_enabled else "OFF"
        bc_text = self.font_medium.render(
            f"{prefix}Breadcrumbs: {on_off}", True, color
        )
        bc_rect = bc_text.get_rect(center=(cfg.WIDTH // 2, settings_y + 50))
        surface.blit(bc_text, bc_rect)

        # Shade selector
        shade_menu_idx = 1 + len(self.DIFFICULTIES) + 1
        is_selected = self.selected_index == shade_menu_idx
        color = cfg.PAC_COLOR if is_selected else cfg.WHITE
        prefix = "> " if is_selected else "  "
        shade_name = self.SHADES[self.shade_index]
        shade_text = self.font_medium.render(
            f"{prefix}Trail Shade: {shade_name}", True, color
        )
        shade_rect = shade_text.get_rect(center=(cfg.WIDTH // 2, settings_y + 100))
        surface.blit(shade_text, shade_rect)

        # Controls hint
        controls = self.font_small.render(
            "In game: WASD to move, B to toggle breadcrumbs, R restart, ESC menu",
            True,
            (100, 100, 100),
        )
        controls_rect = controls.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT - 50))
        surface.blit(controls, controls_rect)

    def _draw_tag_options(self, surface: pygame.Surface, y_start: int) -> None:
        """Draw tag mode menu options."""
        # Difficulty options
        for i, (diff, name, desc) in enumerate(self.TAG_DIFFICULTIES):
            menu_idx = i + 1
            is_selected = menu_idx == self.selected_index

            color = cfg.PAC_COLOR if is_selected else cfg.WHITE
            prefix = "> " if is_selected else "  "

            text = self.font_medium.render(f"{prefix}{name}", True, color)
            text_rect = text.get_rect(center=(cfg.WIDTH // 2, y_start + i * 60))
            surface.blit(text, text_rect)

            desc_color = (200, 200, 200) if is_selected else (100, 100, 100)
            desc_text = self.font_small.render(desc, True, desc_color)
            desc_rect = desc_text.get_rect(
                center=(cfg.WIDTH // 2, y_start + i * 60 + 25)
            )
            surface.blit(desc_text, desc_rect)

        # Settings section
        settings_y = y_start + len(self.TAG_DIFFICULTIES) * 60 + 40

        header = self.font_small.render("─── Settings ───", True, (150, 150, 150))
        header_rect = header.get_rect(center=(cfg.WIDTH // 2, settings_y))
        surface.blit(header, header_rect)

        # First-to selector
        win_menu_idx = 1 + len(self.TAG_DIFFICULTIES)
        is_selected = self.selected_index == win_menu_idx
        color = cfg.PAC_COLOR if is_selected else cfg.WHITE
        prefix = "> " if is_selected else "  "
        win_text = self.font_medium.render(
            f"{prefix}First to: {self.tag_win_score}", True, color
        )
        win_rect = win_text.get_rect(center=(cfg.WIDTH // 2, settings_y + 50))
        surface.blit(win_text, win_rect)

        # Controls hint
        controls = self.font_small.render(
            "P1: WASD | P2: Arrows | Tagger catches runner!",
            True,
            (100, 100, 100),
        )
        controls_rect = controls.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT - 50))
        surface.blit(controls, controls_rect)
