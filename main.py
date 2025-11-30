import asyncio
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


def draw_win_screen(surface: pygame.Surface) -> None:
    """Draw the win overlay."""
    # Semi-transparent overlay
    overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    font_large = pygame.font.Font(None, 96)
    font_medium = pygame.font.Font(None, 48)

    # Win message
    win_text = font_large.render("YOU WIN!", True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 50))
    surface.blit(win_text, win_rect)

    # Instructions
    hint_text = font_medium.render(
        "Press R to play again, ESC for menu", True, cfg.WHITE
    )
    hint_rect = hint_text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 50))
    surface.blit(hint_text, hint_rect)


async def main():
    running = True
    state = GameState.MENU
    menu = Menu()
    maze = None
    player = None

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
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

                    if direction and maze.is_valid_move(player.position, direction):
                        player.move(direction)

                        # Check win condition
                        if player.position == maze.goal_pos:
                            state = GameState.WON

            elif state == GameState.WON:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart with same difficulty
                        maze = Maze(menu.selected_difficulty)
                        maze.generate()
                        player = Player(maze.start_pos)
                        state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU

        # Draw based on state
        if state == GameState.MENU:
            menu.draw(display_surface)

        elif state == GameState.PLAYING:
            display_surface.fill(cfg.BLACK)
            maze.draw(display_surface)
            player.draw(display_surface, maze)

        elif state == GameState.WON:
            display_surface.fill(cfg.BLACK)
            maze.draw(display_surface)
            player.draw(display_surface, maze)
            draw_win_screen(display_surface)

        pygame.display.update()
        clock.tick(cfg.FPS)
        await asyncio.sleep(0)  # Yield to browser event loop (required for pygbag)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
