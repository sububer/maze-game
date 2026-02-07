import asyncio
import time
from enum import Enum

import pygame

import config as cfg
from maze import Maze
from menu import Menu
from player import Player
from tag_game import TagGame


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    WON = 3
    TAG_PLAYING = 4
    TAG_ROUND_END = 5
    TAG_GAME_OVER = 6


pygame.init()

display_surface = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("MazeGame")

clock = pygame.time.Clock()

# Load retro font for timer display
timer_font_label = pygame.font.Font(cfg.TIMER_FONT_PATH, 12)
timer_font_time = pygame.font.Font(cfg.TIMER_FONT_PATH, 20)

# Load retro font for moves counter display
moves_font_label = pygame.font.Font(cfg.TIMER_FONT_PATH, 12)
moves_font_value = pygame.font.Font(cfg.TIMER_FONT_PATH, 20)


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


def draw_moves(surface: pygame.Surface, move_count: int) -> None:
    """Draw the moves counter in the upper left corner."""
    # "MOVES" label
    label = moves_font_label.render("MOVES", True, cfg.MOVES_COLOR)
    label_rect = label.get_rect(topleft=(20, 10))
    surface.blit(label, label_rect)

    # Move count value
    count_text = moves_font_value.render(str(move_count), True, cfg.MOVES_COLOR)
    count_rect = count_text.get_rect(topleft=(20, 32))
    surface.blit(count_text, count_rect)


def try_move(maze: "Maze", player: "Player", direction: str) -> bool:
    """Attempt to move the player in the given direction.

    Returns True if the move was valid and executed, False otherwise.
    """
    if maze.is_valid_move(player.position, direction):
        player.move(direction)
        return True
    return False


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


def draw_win_screen(surface: pygame.Surface, elapsed: float, move_count: int) -> None:
    """Draw the win overlay with final time and move count."""
    # Semi-transparent overlay
    overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    font_large = pygame.font.Font(None, 96)
    font_medium = pygame.font.Font(None, 48)

    # Win message
    win_text = font_large.render("YOU WIN!", True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 120))
    surface.blit(win_text, win_rect)

    # Final time
    time_str = format_time(elapsed)
    time_label = timer_font_label.render("YOUR TIME", True, cfg.TIMER_COLOR)
    time_label_rect = time_label.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 40))
    surface.blit(time_label, time_label_rect)

    time_value = timer_font_time.render(time_str, True, cfg.TIMER_COLOR)
    time_value_rect = time_value.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 5))
    surface.blit(time_value, time_value_rect)

    # Final move count
    moves_label = moves_font_label.render("YOUR MOVES", True, cfg.MOVES_COLOR)
    moves_label_rect = moves_label.get_rect(
        center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 45)
    )
    surface.blit(moves_label, moves_label_rect)

    moves_value = moves_font_value.render(str(move_count), True, cfg.MOVES_COLOR)
    moves_value_rect = moves_value.get_rect(
        center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 80)
    )
    surface.blit(moves_value, moves_value_rect)

    # Instructions
    hint_text = font_medium.render(
        "Press R to play again, ESC for menu", True, cfg.WHITE
    )
    hint_rect = hint_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 140))
    surface.blit(hint_text, hint_rect)


# --- Tag mode drawing functions ---


def draw_tag_countdown(surface: pygame.Surface, remaining: float) -> None:
    """Draw countdown timer in upper right corner."""
    label = timer_font_label.render("TIME", True, cfg.TIMER_COLOR)
    label_rect = label.get_rect(topright=(cfg.WIDTH - 20, 10))
    surface.blit(label, label_rect)

    time_str = format_time(remaining)
    color = (255, 50, 50) if remaining < 30 else cfg.TIMER_COLOR
    time_text = timer_font_time.render(time_str, True, color)
    time_rect = time_text.get_rect(topright=(cfg.WIDTH - 20, 32))
    surface.blit(time_text, time_rect)


def draw_tag_hud(surface: pygame.Surface, tag_game: TagGame) -> None:
    """Draw tag mode HUD: scores (upper-left), round (upper-center)."""
    font = pygame.font.Font(None, 32)

    # Scores - upper left
    p1_color = cfg.TAGGER_COLOR if tag_game.tagger_player_num == 1 else cfg.RUNNER_COLOR
    p2_color = cfg.TAGGER_COLOR if tag_game.tagger_player_num == 2 else cfg.RUNNER_COLOR

    p1_text = font.render(f"P1: {tag_game.scores[0]}", True, p1_color)
    surface.blit(p1_text, (20, 10))

    sep_text = font.render("|", True, cfg.WHITE)
    surface.blit(sep_text, (20 + p1_text.get_width() + 8, 10))

    p2_text = font.render(f"P2: {tag_game.scores[1]}", True, p2_color)
    surface.blit(
        p2_text, (20 + p1_text.get_width() + 8 + sep_text.get_width() + 8, 10)
    )

    # Round number - upper center
    round_text = font.render(f"Round {tag_game.round_num}", True, cfg.WHITE)
    round_rect = round_text.get_rect(center=(cfg.WIDTH // 2, 22))
    surface.blit(round_text, round_rect)


def draw_tag_round_end(surface: pygame.Surface, tag_game: TagGame) -> None:
    """Draw tag round-end overlay."""
    overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    font_large = pygame.font.Font(None, 96)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)

    cy = cfg.HEIGHT // 2

    # Result header
    if tag_game.round_result == "tagged":
        header = font_large.render("TAGGED!", True, cfg.TAGGER_COLOR)
    else:
        header = font_large.render("TIME'S UP!", True, cfg.RUNNER_COLOR)
    header_rect = header.get_rect(center=(cfg.WIDTH // 2, cy - 100))
    surface.blit(header, header_rect)

    # Tagger moves and elapsed time
    moves_text = font_small.render(
        f"Tagger moves: {tag_game.tagger_moves}", True, cfg.WHITE
    )
    moves_rect = moves_text.get_rect(center=(cfg.WIDTH // 2, cy - 40))
    surface.blit(moves_text, moves_rect)

    elapsed_text = font_small.render(
        f"Time: {format_time(tag_game.round_elapsed)}", True, cfg.WHITE
    )
    elapsed_rect = elapsed_text.get_rect(center=(cfg.WIDTH // 2, cy - 10))
    surface.blit(elapsed_text, elapsed_rect)

    # Scores
    score_text = font_medium.render(
        f"P1: {tag_game.scores[0]}  |  P2: {tag_game.scores[1]}", True, cfg.WHITE
    )
    score_rect = score_text.get_rect(center=(cfg.WIDTH // 2, cy + 40))
    surface.blit(score_text, score_rect)

    # Instructions
    if tag_game.check_game_over():
        hint = font_medium.render("Press ENTER to continue", True, cfg.WHITE)
    else:
        hint = font_medium.render("Press ENTER for next round", True, cfg.WHITE)
    hint_rect = hint.get_rect(center=(cfg.WIDTH // 2, cy + 100))
    surface.blit(hint, hint_rect)


def draw_tag_game_over(surface: pygame.Surface, tag_game: TagGame) -> None:
    """Draw tag game-over overlay."""
    overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    font_large = pygame.font.Font(None, 96)
    font_medium = pygame.font.Font(None, 48)

    cy = cfg.HEIGHT // 2

    winner = tag_game.check_game_over()
    winner_color = cfg.TAGGER_COLOR if winner == 1 else cfg.RUNNER_COLOR

    # Winner announcement
    win_text = font_large.render(f"PLAYER {winner} WINS!", True, winner_color)
    win_rect = win_text.get_rect(center=(cfg.WIDTH // 2, cy - 60))
    surface.blit(win_text, win_rect)

    # Final scores
    score_text = font_medium.render(
        f"P1: {tag_game.scores[0]}  |  P2: {tag_game.scores[1]}", True, cfg.WHITE
    )
    score_rect = score_text.get_rect(center=(cfg.WIDTH // 2, cy + 10))
    surface.blit(score_text, score_rect)

    # Instructions
    hint = font_medium.render("R to play again, ESC for menu", True, cfg.WHITE)
    hint_rect = hint.get_rect(center=(cfg.WIDTH // 2, cy + 80))
    surface.blit(hint, hint_rect)


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
    move_count = 0
    tag_game = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == GameState.MENU:
                result = menu.handle_event(event)
                if result == "start":
                    # Start new solo game with selected difficulty
                    maze = Maze(menu.selected_difficulty)
                    maze.generate()
                    player = Player(maze.start_pos)
                    path_history = [maze.start_pos]
                    breadcrumbs_enabled = menu.breadcrumbs_enabled
                    timer_start = None
                    timer_end = None
                    move_count = 0
                    state = GameState.PLAYING
                elif result == "start_tag":
                    # Start new tag game
                    tag_game = TagGame(menu.tag_difficulty, menu.tag_win_score)
                    tag_game.start_round()
                    state = GameState.TAG_PLAYING

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
                        move_count = 0
                    elif event.key == pygame.K_b:
                        # Toggle breadcrumbs
                        breadcrumbs_enabled = not breadcrumbs_enabled
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

                    if direction and try_move(maze, player, direction):
                        # Start timer on first move
                        if timer_start is None:
                            timer_start = time.time()

                        move_count += 1
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
                        move_count = 0
                        state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

            elif state == GameState.TAG_PLAYING:
                if event.type == pygame.KEYDOWN:
                    # P1 controls: WASD
                    p1_dir = None
                    if event.key == pygame.K_a:
                        p1_dir = "left"
                    elif event.key == pygame.K_d:
                        p1_dir = "right"
                    elif event.key == pygame.K_w:
                        p1_dir = "up"
                    elif event.key == pygame.K_s:
                        p1_dir = "down"

                    if p1_dir:
                        tag_game.process_move(1, p1_dir)

                    # P2 controls: arrow keys
                    p2_dir = None
                    if event.key == pygame.K_LEFT:
                        p2_dir = "left"
                    elif event.key == pygame.K_RIGHT:
                        p2_dir = "right"
                    elif event.key == pygame.K_UP:
                        p2_dir = "up"
                    elif event.key == pygame.K_DOWN:
                        p2_dir = "down"

                    if p2_dir:
                        tag_game.process_move(2, p2_dir)

                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

            elif state == GameState.TAG_ROUND_END:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if tag_game.check_game_over():
                            state = GameState.TAG_GAME_OVER
                        else:
                            tag_game.swap_roles()
                            tag_game.start_round()
                            state = GameState.TAG_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

            elif state == GameState.TAG_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        tag_game = TagGame(
                            menu.tag_difficulty, menu.tag_win_score
                        )
                        tag_game.start_round()
                        state = GameState.TAG_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

        # --- Check tag timeout every frame ---
        if state == GameState.TAG_PLAYING and tag_game and tag_game.round_active:
            if tag_game.check_timeout():
                state = GameState.TAG_ROUND_END

        # --- Draw based on state ---
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
            # Draw timer and moves counter
            elapsed = 0.0 if timer_start is None else time.time() - timer_start
            draw_timer(display_surface, elapsed)
            draw_moves(display_surface, move_count)

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
            draw_moves(display_surface, move_count)
            draw_win_screen(display_surface, elapsed, move_count)

        elif state == GameState.TAG_PLAYING:
            display_surface.fill(cfg.BLACK)
            tag_game.maze.draw(display_surface, draw_markers=False)
            tag_game.players[0].draw(display_surface, tag_game.maze, draw_label=True)
            tag_game.players[1].draw(display_surface, tag_game.maze, draw_label=True)
            draw_tag_hud(display_surface, tag_game)
            draw_tag_countdown(display_surface, tag_game.get_remaining())

        elif state == GameState.TAG_ROUND_END:
            display_surface.fill(cfg.BLACK)
            tag_game.maze.draw(display_surface, draw_markers=False)
            tag_game.players[0].draw(display_surface, tag_game.maze, draw_label=True)
            tag_game.players[1].draw(display_surface, tag_game.maze, draw_label=True)
            draw_tag_hud(display_surface, tag_game)
            draw_tag_countdown(display_surface, tag_game.get_remaining())
            draw_tag_round_end(display_surface, tag_game)

        elif state == GameState.TAG_GAME_OVER:
            display_surface.fill(cfg.BLACK)
            draw_tag_game_over(display_surface, tag_game)

        pygame.display.update()
        clock.tick(cfg.FPS)
        await asyncio.sleep(0)  # Yield to browser event loop (required for pygbag)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
