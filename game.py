import config as cfg
from player import Player
from maze import Maze
import pygame


pygame.init()

# surface
display_surface = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption('MazeGame')

clock = pygame.time.Clock()



def main():
    
    running = True

    maze_board = Maze()
    maze_board.draw(display_surface)

    player = Player()
    player.draw(display_surface)

    pygame.display.update()


    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pass
                if event.key == pygame.K_RIGHT:
                    pass
                if event.key == pygame.K_UP:
                    pass
                if event.key == pygame.K_DOWN:
                    pass
        
        pygame.display.update()
    
    pygame.quit()


if __name__ == '__main__':
    main()
