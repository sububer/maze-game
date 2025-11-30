import asyncio
import time
from enum import Enum

import pygame

import config as cfg
from maze import Maze
from menu import Menu
from player import Player


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    WON = 3


pygame.init()

display_surface = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("MazeGame")

clock = pygame.time.Clock()

# Load retro font for timer display
timer_font_label = pygame.font.Font(cfg.TIMER_FONT_PATH, 12)
timer_font_time = pygame.font.Font(cfg.TIMER_FONT_PATH, 20)


def update_path(path: list[tuple[int, int]], new_pos: tuple[int, int]) -> None:
    """Update path history with backtrack detection."""
    if not path or new_pos == path[-1]:
        # No path or same position - no change
        return
    if len(path) >= 2 and new_pos == path[-2]:
        # Moving back to where we came from - backtracking
        path.pop()
    else:
        # New exploration
        path.append(new_pos)


def format_time(elapsed: float) -> str:
    """Format elapsed time as MM:SS.T (minutes:seconds.tenths)."""
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    tenths = int((elapsed * 10) % 10)
    return f"{minutes:02d}:{seconds:02d}.{tenths}"


def draw_timer(surface: pygame.Surface, elapsed: float) -> None:
    """Draw the timer in the upper right corner."""
    # "TIME" label
    label = timer_font_label.render("TIME", True, cfg.TIMER_COLOR)
    label_rect = label.get_rect(topright=(cfg.WIDTH - 20, 10))
    surface.blit(label, label_rect)

    # Time value
    time_str = format_time(elapsed)
    time_text = timer_font_time.render(time_str, True, cfg.TIMER_COLOR)
    time_rect = time_text.get_rect(topright=(cfg.WIDTH - 20, 32))
    surface.blit(time_text, time_rect)


def draw_breadcrumbs(
    surface: pygame.Surface,
    path: list[tuple[int, int]],
    maze: "Maze",
    base_opacity: int,
) -> None:
    """Draw breadcrumb trail with fading effect (older = more transparent)."""
    if len(path) <= 1:
        return

    cell_size = maze.get_cell_size()
    radius = int(cell_size / 6)  # Smaller than player (cell_size / 3)

    # Minimum opacity so oldest breadcrumbs remain visible (30% of base)
    min_opacity = max(20, int(base_opacity * 0.3))

    # Draw all positions except the current one (last in path)
    for i, (row, col) in enumerate(path[:-1]):
        # Fade: older = lower opacity, newer = higher opacity
        # Interpolate between min_opacity and base_opacity
        fade = (i + 1) / len(path)
        opacity = int(min_opacity + (base_opacity - min_opacity) * fade)

        x, y = maze.grid_to_pixel(row, col)
        # Create surface with alpha for transparency
        crumb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            crumb, (*cfg.BREADCRUMB_COLOR, opacity), (radius, radius), radius
        )
        surface.blit(crumb, (x - radius, y - radius))


def draw_win_screen(surface: pygame.Surface, elapsed: float) -> None:
    """Draw the win overlay with final time."""
    # Semi-transparent overlay
    overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    font_large = pygame.font.Font(None, 96)
    font_medium = pygame.font.Font(None, 48)

    # Win message
    win_text = font_large.render("YOU WIN!", True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 80))
    surface.blit(win_text, win_rect)

    # Final time
    time_str = format_time(elapsed)
    time_label = timer_font_label.render("YOUR TIME", True, cfg.TIMER_COLOR)
    time_label_rect = time_label.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2))
    surface.blit(time_label, time_label_rect)

    time_value = timer_font_time.render(time_str, True, cfg.TIMER_COLOR)
    time_value_rect = time_value.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 35))
    surface.blit(time_value, time_value_rect)

    # Instructions
    hint_text = font_medium.render(
        "Press R to play again, ESC for menu", True, cfg.WHITE
    )
    hint_rect = hint_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 100))
    surface.blit(hint_text, hint_rect)


async def main():
    running = True
    state = GameState.MENU
    menu = Menu()
    maze = None
    player = None
    path_history = []
    breadcrumbs_enabled = True
    timer_start = None
    timer_end = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == GameState.MENU:
                result = menu.handle_event(event)
                if result == "start":
                    # Start new game with selected difficulty
                    maze = Maze(menu.selected_difficulty)
                    maze.generate()
                    player = Player(maze.start_pos)
                    path_history = [maze.start_pos]
                    breadcrumbs_enabled = menu.breadcrumbs_enabled
                    timer_start = None
                    timer_end = None
                    state = GameState.PLAYING

            elif state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    direction = None
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        direction = "left"
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        direction = "right"
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        direction = "up"
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        direction = "down"
                    elif event.key == pygame.K_r:
                        # Restart with same difficulty
                        maze = Maze(menu.selected_difficulty)
                        maze.generate()
                        player = Player(maze.start_pos)
                        path_history = [maze.start_pos]
                        breadcrumbs_enabled = menu.breadcrumbs_enabled
                        timer_start = None
                        timer_end = None
                    elif event.key == pygame.K_b:
                        # Toggle breadcrumbs
                        breadcrumbs_enabled = not breadcrumbs_enabled
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

                    if direction and maze.is_valid_move(player.position, direction):
                        # Start timer on first move
                        if timer_start is None:
                            timer_start = time.time()

                        player.move(direction)
                        update_path(path_history, player.position)

                        # Check win condition
                        if player.position == maze.goal_pos:
                            timer_end = time.time()
                            state = GameState.WON

            elif state == GameState.WON:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart with same difficulty
                        maze = Maze(menu.selected_difficulty)
                        maze.generate()
                        player = Player(maze.start_pos)
                        path_history = [maze.start_pos]
                        breadcrumbs_enabled = menu.breadcrumbs_enabled
                        timer_start = None
                        timer_end = None
                        state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

        # Draw based on state
        if state == GameState.MENU:
            menu.draw(display_surface)

        elif state == GameState.PLAYING:
            display_surface.fill(cfg.BLACK)
            maze.draw(display_surface)
            if breadcrumbs_enabled:
                draw_breadcrumbs(
                    display_surface, path_history, maze, menu.breadcrumb_opacity
                )
            player.draw(display_surface, maze)
            # Draw timer
            elapsed = 0.0 if timer_start is None else time.time() - timer_start
            draw_timer(display_surface, elapsed)

        elif state == GameState.WON:
            display_surface.fill(cfg.BLACK)
            maze.draw(display_surface)
            if breadcrumbs_enabled:
                draw_breadcrumbs(
                    display_surface, path_history, maze, menu.breadcrumb_opacity
                )
            player.draw(display_surface, maze)
            # Calculate final elapsed time
            if timer_start is not None and timer_end is not None:
                elapsed = timer_end - timer_start
            else:
                elapsed = 0.0
            draw_timer(display_surface, elapsed)
            draw_win_screen(display_surface, elapsed)

        pygame.display.update()
        clock.tick(cfg.FPS)
        await asyncio.sleep(0)  # Yield to browser event loop (required for pygbag)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
