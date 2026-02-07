# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PAC_COLOR = (246, 255, 0)

# display
WIDTH = 900
HEIGHT = 900
MASTHEAD = HEIGHT // 14
PADDING = 5

# maze
MAZE_ROWS = 10
MAZE_COLS = 10
MAZE_COLOR = (70, 19, 212)


# fps
FPS = 60


# player
PLAYER_COLOR = PAC_COLOR

# breadcrumbs
BREADCRUMB_COLOR = PAC_COLOR  # Same yellow as player
# Shade presets (max opacity values)
BREADCRUMB_LIGHT = 60
BREADCRUMB_MEDIUM = 120
BREADCRUMB_DARK = 180

# timer
TIMER_COLOR = PAC_COLOR
TIMER_FONT_PATH = "assets/fonts/PressStart2P-Regular.ttf"

# moves counter
MOVES_COLOR = PAC_COLOR

# tag mode
TAGGER_COLOR = (255, 69, 0)  # orange-red
RUNNER_COLOR = (0, 191, 255)  # sky blue
TAG_TIME_LIMIT = 120  # seconds per round
TAG_LOOP_PERCENT = 10  # extra wall removal for chase dynamics
TAG_WIN_SCORES = [1, 3, 5]  # selectable "first to N" options
