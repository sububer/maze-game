from ctypes import util
from socket import has_ipv6
import pygame
from pyparsing import col
import utils
import config as cfg

class Maze():
    def __init__(self, rows=cfg.MAZE_ROWS, cols=cfg.MAZE_COLS, color=cfg.MAZE_COLOR):
        self.rows = rows
        self.cols = cols
        self.color = color
        self.player_row = None
        self.player_col = None
        self.has_player = False
        
    def place_player(self, row, col, player):
        self.player_row = row
        self.player_col = col
        self.has_player = True
        return True
    
    def get_player_position(self):
        return (self.player_row, self.player_col)
    
    def move_player(self, row, col):
        self.place_player(row, col)
        return True

    def __is_valid_move__(self, cur_row, cur_col, to_row, to_col):
        return True

    def draw(self, surface, color=cfg.MAZE_COLOR):
        # draw cols
        # left col
        pygame.draw.line(surface, color, (cfg.PADDING, cfg.MASTHEAD + cfg.PADDING), (cfg.PADDING, cfg.HEIGHT - cfg.PADDING), 5)

        for column in range(cfg.MAZE_COLS):
            x_pos = cfg.PADDING + ((column + 1) * (cfg.WIDTH - (2 * cfg.PADDING))//cfg.MAZE_COLS)
            pygame.draw.line(surface, color, (x_pos, cfg.MASTHEAD + cfg.PADDING), (x_pos, cfg.HEIGHT - cfg.PADDING), 5)


        # draw rows
        pygame.draw.line(surface, color, (cfg.PADDING, cfg.MASTHEAD + cfg.PADDING), (cfg.WIDTH  - cfg.PADDING, cfg.MASTHEAD + cfg.PADDING), 5)

        for row in range(cfg.MAZE_ROWS):
            y_pos = cfg.MASTHEAD + cfg.PADDING + ((1 + row) * (cfg.HEIGHT - cfg.MASTHEAD - (2 * cfg.PADDING))//cfg.MAZE_ROWS)
            pygame.draw.line(surface, color, (cfg.PADDING, y_pos), (cfg.WIDTH - cfg.PADDING, y_pos), 5)