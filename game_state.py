import random
import math
from config import *

class GameState:
    def __init__(self):
        self.reset()
        self.mass = DEFAULT_MASS
        self.pixels_per_meter = PIXELS_PER_METER
        self.running = True
        self.game_active = True
        self.game_over_reason = ""
        self.frame_count = 0

    def reset(self):
        """Reset physics variables for a new game"""
        self.r = CENTER_R
        self.theta = 0
        self.speed = 0
        self.previous_theta = 0
        self.completed_revolutions = 0
        self.obstacles = self.generate_obstacles()
        self.game_active = True
        self.game_over_reason = ""

    def generate_obstacles(self):
        """Generate random obstacles avoiding the start/finish line"""
        new_obstacles = []
        for _ in range(NUM_OBSTACLES):
            valid = False
            while not valid:
                obs_theta = random.uniform(0, 2*math.pi)
                # Check if obstacle is in safe zone around start/finish line
                angle_diff = abs(obs_theta - START_FINISH_THETA)
                # Handle wrap-around
                if angle_diff > math.pi:
                    angle_diff = 2*math.pi - angle_diff
                if angle_diff > SAFE_ZONE:
                    valid = True
            obs_r = random.uniform(INNER_R + 15, OUTER_R - 15)
            new_obstacles.append((obs_r, obs_theta))
        return new_obstacles
