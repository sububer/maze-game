import config as cfg
import pygame

class Player:

    def __init__(self, color=cfg.PLAYER_COLOR):
        self.color = color
        self.radius = 10
        self.width = 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (cfg.PADDING, cfg.MASTHEAD + cfg.PADDING) * 3, self.radius)
    
    def move(self):
        pass

    def draw(self):
        pass