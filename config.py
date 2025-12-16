import math
import pygame

# Initialize pygame to get screen dimensions
pygame.init()
WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]

# Track - Scaled for fullscreen
CENTER = (WIDTH // 2, HEIGHT // 2)
# Scale based on screen size
SCALE_FACTOR = min(WIDTH, HEIGHT) / 800
INNER_R = int(180 * SCALE_FACTOR)
OUTER_R = int(320 * SCALE_FACTOR)
CENTER_R = (INNER_R + OUTER_R) / 2

# Simulation scale: how many pixels represent one meter in the simulation.
PIXELS_PER_METER = 50.0

# Default mass used for force readouts (kg)
DEFAULT_MASS = 1.0

# Speed limits
MIN_SPEED = 40
MAX_SPEED = 140
DRIFT_FACTOR = 0.01
STABILITY_FACTOR = 0.02

# Start and Finish lines (at theta = 0 and theta = pi)
START_FINISH_THETA = 0
SAFE_ZONE = math.pi / 6  # 30 degrees on each side of start/finish

# Obstacles
NUM_OBSTACLES = 6
OBSTACLE_SIZE = int(20 * SCALE_FACTOR)

# Colors
COLOR_BG = (135, 206, 250)
COLOR_GRASS = (40, 150, 40)
COLOR_TRACK = (50, 50, 50)
COLOR_TRACK_BORDER = (30, 30, 30)
COLOR_LINE_WHITE = (255, 255, 255)
COLOR_LINE_YELLOW = (255, 255, 100)
COLOR_START_LINE = (0, 200, 0)
