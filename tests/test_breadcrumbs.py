"""Unit tests for breadcrumb trail functionality."""

import pygame
import pytest

import config as cfg
from main import update_path
from menu import Menu


class TestUpdatePath:
    """Tests for the update_path backtrack detection function."""

    def test_first_move_appends_position(self):
        """First move should append the new position."""
        path = [(0, 0)]
        update_path(path, (0, 1))
        assert path == [(0, 0), (0, 1)]

    def test_forward_move_appends_position(self):
        """Moving to a new cell should append position."""
        path = [(0, 0), (0, 1), (0, 2)]
        update_path(path, (0, 3))
        assert path == [(0, 0), (0, 1), (0, 2), (0, 3)]

    def test_backtrack_pops_position(self):
        """Moving back to previous position should pop current position."""
        path = [(0, 0), (0, 1), (0, 2)]
        update_path(path, (0, 1))  # Backtrack to (0, 1)
        assert path == [(0, 0), (0, 1)]

    def test_backtrack_then_forward(self):
        """After backtracking, moving forward should append again."""
        path = [(0, 0), (0, 1), (0, 2)]
        update_path(path, (0, 1))  # Backtrack
        assert path == [(0, 0), (0, 1)]
        update_path(path, (1, 1))  # New direction
        assert path == [(0, 0), (0, 1), (1, 1)]

    def test_multiple_backtracks(self):
        """Multiple backtracks should work correctly."""
        path = [(0, 0), (0, 1), (0, 2), (0, 3)]
        update_path(path, (0, 2))  # Backtrack
        assert path == [(0, 0), (0, 1), (0, 2)]
        update_path(path, (0, 1))  # Backtrack again
        assert path == [(0, 0), (0, 1)]
        update_path(path, (0, 0))  # Backtrack to start
        assert path == [(0, 0)]

    def test_same_position_no_duplicate(self):
        """Moving to the same position should not append duplicate."""
        path = [(0, 0)]
        update_path(path, (0, 0))  # Same position
        assert path == [(0, 0)]

    def test_empty_path_no_change(self):
        """Empty path should remain empty."""
        path = []
        update_path(path, (0, 0))
        assert path == []

    def test_move_to_visited_non_previous_cell(self):
        """Moving to a visited cell that's not the previous one appends."""
        path = [(0, 0), (0, 1), (0, 2), (1, 2)]
        # Move to (0, 0) - visited but not previous position (1, 2) -> not backtrack
        update_path(path, (0, 0))
        assert path == [(0, 0), (0, 1), (0, 2), (1, 2), (0, 0)]

    def test_zigzag_path(self):
        """Complex zigzag path should track correctly."""
        path = [(0, 0)]
        moves = [(0, 1), (1, 1), (1, 0), (2, 0), (2, 1)]
        for pos in moves:
            update_path(path, pos)
        assert path == [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0), (2, 1)]

    def test_zigzag_with_backtrack(self):
        """Zigzag path with backtracking."""
        path = [(0, 0), (0, 1), (1, 1), (1, 0)]
        update_path(path, (1, 1))  # Backtrack
        assert path == [(0, 0), (0, 1), (1, 1)]
        update_path(path, (1, 2))  # New direction
        assert path == [(0, 0), (0, 1), (1, 1), (1, 2)]


class TestMenuBreadcrumbSettings:
    """Tests for Menu breadcrumb settings."""

    @pytest.fixture(autouse=True)
    def init_pygame(self):
        """Initialize pygame for font rendering."""
        pygame.init()
        yield
        pygame.quit()

    def test_default_breadcrumbs_enabled(self):
        """Breadcrumbs should be enabled by default."""
        menu = Menu()
        assert menu.breadcrumbs_enabled is True

    def test_default_shade_is_medium(self):
        """Default shade should be Medium (index 1)."""
        menu = Menu()
        assert menu.shade_index == 1
        assert menu.SHADES[menu.shade_index] == "Medium"

    def test_breadcrumb_opacity_light(self):
        """Light shade should return BREADCRUMB_LIGHT opacity."""
        menu = Menu()
        menu.shade_index = 0
        assert menu.breadcrumb_opacity == cfg.BREADCRUMB_LIGHT

    def test_breadcrumb_opacity_medium(self):
        """Medium shade should return BREADCRUMB_MEDIUM opacity."""
        menu = Menu()
        menu.shade_index = 1
        assert menu.breadcrumb_opacity == cfg.BREADCRUMB_MEDIUM

    def test_breadcrumb_opacity_dark(self):
        """Dark shade should return BREADCRUMB_DARK opacity."""
        menu = Menu()
        menu.shade_index = 2
        assert menu.breadcrumb_opacity == cfg.BREADCRUMB_DARK

    def test_toggle_breadcrumbs_off(self):
        """Toggling breadcrumbs should switch from on to off."""
        menu = Menu()
        menu.breadcrumbs_enabled = not menu.breadcrumbs_enabled
        assert menu.breadcrumbs_enabled is False

    def test_toggle_breadcrumbs_on(self):
        """Toggling breadcrumbs should switch from off to on."""
        menu = Menu()
        menu.breadcrumbs_enabled = False
        menu.breadcrumbs_enabled = not menu.breadcrumbs_enabled
        assert menu.breadcrumbs_enabled is True

    def test_shade_cycle(self):
        """Shade index should cycle through all shades."""
        menu = Menu()
        menu.shade_index = 0  # Light
        menu.shade_index = (menu.shade_index + 1) % len(menu.SHADES)
        assert menu.shade_index == 1  # Medium
        menu.shade_index = (menu.shade_index + 1) % len(menu.SHADES)
        assert menu.shade_index == 2  # Dark
        menu.shade_index = (menu.shade_index + 1) % len(menu.SHADES)
        assert menu.shade_index == 0  # Back to Light


class TestMenuSettingsNavigation:
    """Tests for navigating menu settings."""

    @pytest.fixture(autouse=True)
    def init_pygame(self):
        """Initialize pygame for event handling."""
        pygame.init()
        yield
        pygame.quit()

    def test_menu_items_count_includes_settings(self):
        """Menu should have difficulty options plus 2 settings."""
        menu = Menu()
        assert menu.menu_items_count == len(menu.DIFFICULTIES) + 2

    def test_navigate_to_breadcrumb_toggle(self):
        """Should be able to navigate to breadcrumb toggle."""
        menu = Menu()
        # Navigate down past difficulties
        for _ in range(len(menu.DIFFICULTIES)):
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            menu.handle_event(event)
        assert menu.selected_index == len(menu.DIFFICULTIES)

    def test_navigate_to_shade_selector(self):
        """Should be able to navigate to shade selector."""
        menu = Menu()
        # Navigate down past difficulties and breadcrumb toggle
        for _ in range(len(menu.DIFFICULTIES) + 1):
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            menu.handle_event(event)
        assert menu.selected_index == len(menu.DIFFICULTIES) + 1

    def test_navigate_wraps_around(self):
        """Navigation should wrap from last item to first."""
        menu = Menu()
        menu.selected_index = menu.menu_items_count - 1
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.handle_event(event)
        assert menu.selected_index == 0

    def test_enter_on_breadcrumb_toggles(self):
        """Enter on breadcrumb setting should toggle it."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES)  # Breadcrumb toggle
        initial = menu.breadcrumbs_enabled
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        menu.handle_event(event)
        assert menu.breadcrumbs_enabled != initial

    def test_enter_on_shade_cycles(self):
        """Enter on shade setting should cycle to next shade."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES) + 1  # Shade selector
        menu.shade_index = 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        menu.handle_event(event)
        assert menu.shade_index == 1

    def test_left_on_breadcrumb_toggles(self):
        """Left arrow on breadcrumb setting should toggle it."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES)
        initial = menu.breadcrumbs_enabled
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        menu.handle_event(event)
        assert menu.breadcrumbs_enabled != initial

    def test_right_on_shade_cycles_forward(self):
        """Right arrow on shade setting should cycle forward."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES) + 1
        menu.shade_index = 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        menu.handle_event(event)
        assert menu.shade_index == 1

    def test_left_on_shade_cycles_backward(self):
        """Left arrow on shade setting should cycle backward."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES) + 1
        menu.shade_index = 1
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        menu.handle_event(event)
        assert menu.shade_index == 0

    def test_enter_on_difficulty_starts_game(self):
        """Enter on difficulty should return 'start'."""
        menu = Menu()
        menu.selected_index = 0  # First difficulty
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.handle_event(event)
        assert result == "start"

    def test_enter_on_settings_does_not_start_game(self):
        """Enter on settings should not return 'start'."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES)  # Breadcrumb toggle
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.handle_event(event)
        assert result is None

    def test_selected_difficulty_clamped_when_on_settings(self):
        """selected_difficulty should return last difficulty when on settings."""
        menu = Menu()
        menu.selected_index = len(menu.DIFFICULTIES) + 1  # Shade selector
        # Should return the last difficulty, not error
        difficulty = menu.selected_difficulty
        assert difficulty == menu.DIFFICULTIES[-1][0]
