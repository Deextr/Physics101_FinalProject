import math
from config import *

def calculate_physics_values(r, theta, previous_theta, dt_s, pixels_per_meter):
    """
    Calculate physics parameters for circular motion.
    Returns: (omega, v_phys, v_m_s, a_c_m, T, F_c)
    """
    # Angular velocity (ω) from change in theta
    delta_theta = theta - previous_theta
    # Handle wrap-around for delta_theta
    if delta_theta > math.pi:
        delta_theta -= 2 * math.pi
    elif delta_theta < -math.pi:
        delta_theta += 2 * math.pi
    
    omega = delta_theta / dt_s if dt_s > 0 else 0
    
    # Linear speed in pixels/sec (v = r * ω)
    v_phys = r * omega

    # Convert to SI units using pixels_per_meter
    r_m = r / pixels_per_meter
    v_m_s = v_phys / pixels_per_meter

    # Centripetal acceleration in m/s^2: a_c = v^2 / r
    a_c_m = (v_m_s ** 2) / r_m if r_m != 0 else 0.0

    # Period T = 2π / ω (if ω is non-zero)
    T = (2 * math.pi / omega) if abs(omega) > 1e-6 else float('inf')
    
    return omega, v_phys, v_m_s, a_c_m, T

def apply_drift_physics(r, speed):
    """
    Apply drift effects to the car's radius based on speed.
    Returns the new radius.
    """
    new_r = r
    if speed < MIN_SPEED:
        new_r -= (MIN_SPEED - speed) * DRIFT_FACTOR
    elif speed > MAX_SPEED:
        new_r += (speed - MAX_SPEED) * DRIFT_FACTOR
    else:
        new_r += (CENTER_R - r) * STABILITY_FACTOR
    return new_r

def check_track_bounds(r):
    """
    Check if the car is within the track limits.
    Returns (is_valid, reason)
    """
    if r < INNER_R or r > OUTER_R:
        return False, "You fell off the track!"
    return True, ""

def check_obstacle_collision(x, y, obstacles):
    """
    Check if the car has hit any obstacles.
    Returns (collision_detected, reason)
    """
    for obs_r, obs_theta in obstacles:
        obs_x = CENTER[0] + obs_r * math.cos(obs_theta)
        obs_y = CENTER[1] + obs_r * math.sin(obs_theta)
        distance = math.hypot(x - obs_x, y - obs_y)
        if distance < OBSTACLE_SIZE + 12:
            return True, "You hit a traffic cone!"
    return False, ""
