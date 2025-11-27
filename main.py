import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Racing Game")
clock = pygame.time.Clock()

# Track - Scaled for fullscreen
CENTER = (WIDTH // 2, HEIGHT // 2)
# Scale based on screen size
SCALE_FACTOR = min(WIDTH, HEIGHT) / 800
INNER_R = int(180 * SCALE_FACTOR)
OUTER_R = int(320 * SCALE_FACTOR)
CENTER_R = (INNER_R + OUTER_R) / 2

# Car physics
r = CENTER_R
theta = 0
speed = 0
stability_factor = 0.02
previous_theta = 0
completed_revolutions = 0

# Speed limits
MIN_SPEED = 40
MAX_SPEED = 140
DRIFT_FACTOR = 0.01

# Start and Finish lines (at theta = 0 and theta = pi)
START_FINISH_THETA = 0
SAFE_ZONE = math.pi / 6  # 30 degrees on each side of start/finish

# Obstacles - Traffic cones
NUM_OBSTACLES = 6

def generate_obstacles():
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

obstacles = generate_obstacles()

OBSTACLE_SIZE = int(20 * SCALE_FACTOR)

def draw_car(surface, x, y, angle, color=(220, 50, 50)):
    """Draw a top-down car sprite"""
    car_length = int(35 * SCALE_FACTOR)
    car_width = int(22 * SCALE_FACTOR)
    
    # Create car surface
    car_surf = pygame.Surface((car_length, car_width), pygame.SRCALPHA)
    
    # Main body (red)
    pygame.draw.rect(car_surf, color, (int(5*SCALE_FACTOR), int(2*SCALE_FACTOR), car_length-int(10*SCALE_FACTOR), car_width-int(4*SCALE_FACTOR)))
    pygame.draw.rect(car_surf, color, (0, int(4*SCALE_FACTOR), car_length, car_width-int(8*SCALE_FACTOR)))
    
    # Windshield (darker blue)
    pygame.draw.rect(car_surf, (100, 150, 200), (int(6*SCALE_FACTOR), int(4*SCALE_FACTOR), int(8*SCALE_FACTOR), car_width-int(8*SCALE_FACTOR)))
    
    # Rear window
    pygame.draw.rect(car_surf, (100, 150, 200), (car_length-int(12*SCALE_FACTOR), int(4*SCALE_FACTOR), int(6*SCALE_FACTOR), car_width-int(8*SCALE_FACTOR)))
    
    # Wheels (black)
    wheel_w = int(5 * SCALE_FACTOR)
    wheel_h = int(8 * SCALE_FACTOR)
    # Front wheels
    pygame.draw.rect(car_surf, (30, 30, 30), (int(3*SCALE_FACTOR), 0, wheel_w, wheel_h))
    pygame.draw.rect(car_surf, (30, 30, 30), (int(3*SCALE_FACTOR), car_width-wheel_h, wheel_w, wheel_h))
    # Rear wheels
    pygame.draw.rect(car_surf, (30, 30, 30), (car_length-int(7*SCALE_FACTOR), 0, wheel_w, wheel_h))
    pygame.draw.rect(car_surf, (30, 30, 30), (car_length-int(7*SCALE_FACTOR), car_width-wheel_h, wheel_w, wheel_h))
    
    # Headlights (yellow)
    pygame.draw.circle(car_surf, (255, 255, 100), (int(2*SCALE_FACTOR), int(5*SCALE_FACTOR)), int(3*SCALE_FACTOR))
    pygame.draw.circle(car_surf, (255, 255, 100), (int(2*SCALE_FACTOR), car_width-int(5*SCALE_FACTOR)), int(3*SCALE_FACTOR))
    
    # Rotate car to face direction of travel
    rotated = pygame.transform.rotate(car_surf, -math.degrees(angle) + 90)
    rect = rotated.get_rect(center=(x, y))
    surface.blit(rotated, rect)

def draw_traffic_cone(surface, x, y):
    """Draw a traffic cone obstacle"""
    cone_height = int(18 * SCALE_FACTOR)
    cone_base = int(12 * SCALE_FACTOR)
    points = [
        (x, y - cone_height),  # top
        (x - cone_base, y + cone_base),  # bottom left
        (x + cone_base, y + cone_base)   # bottom right
    ]
    # Orange cone
    pygame.draw.polygon(surface, (255, 140, 0), points)
    # White stripe
    stripe_w = int(8 * SCALE_FACTOR)
    pygame.draw.line(surface, (255, 255, 255), (x - stripe_w, y), (x + stripe_w, y), max(2, int(3*SCALE_FACTOR)))

def draw_background(surface, frame_count):
    """Draw animated background with sky, clouds, and scenery"""
    # Fill entire screen with light blue first to ensure no black edges
    surface.fill((135, 206, 250))
    
    # Sky gradient (light blue to darker blue) - ensure it covers entire width
    for i in range(HEIGHT):
        blue_value = 180 - int(i / HEIGHT * 50)
        color = (135, 206, min(250, blue_value))
        pygame.draw.line(surface, color, (0, i), (WIDTH, i), 1)
    
    # Animated clouds
    cloud_positions = [
        (WIDTH * 0.2 + (frame_count * 0.3) % WIDTH, HEIGHT * 0.15),
        (WIDTH * 0.5 + (frame_count * 0.2) % WIDTH, HEIGHT * 0.1),
        (WIDTH * 0.8 + (frame_count * 0.25) % WIDTH, HEIGHT * 0.2),
    ]
    
    for cx, cy in cloud_positions:
        # Wrap around
        cloud_x = cx if cx < WIDTH else cx - WIDTH
        # Draw fluffy cloud
        cloud_radius = int(40 * SCALE_FACTOR)
        pygame.draw.circle(surface, (255, 255, 255), (int(cloud_x), int(cy)), cloud_radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(cloud_x - 30 * SCALE_FACTOR), int(cy + 10 * SCALE_FACTOR)), int(35 * SCALE_FACTOR))
        pygame.draw.circle(surface, (255, 255, 255), (int(cloud_x + 30 * SCALE_FACTOR), int(cy + 10 * SCALE_FACTOR)), int(30 * SCALE_FACTOR))
    
    # Draw grass area (larger than track)
    grass_radius = int(OUTER_R * 1.8)
    pygame.draw.circle(surface, (40, 150, 40), CENTER, grass_radius)
    
    # Draw trees around the track
    tree_distance = int(OUTER_R * 1.4)
    num_trees = 16
    for i in range(num_trees):
        angle = (2 * math.pi * i) / num_trees
        tree_x = CENTER[0] + tree_distance * math.cos(angle)
        tree_y = CENTER[1] + tree_distance * math.sin(angle)
        # Tree trunk
        trunk_width = int(12 * SCALE_FACTOR)
        trunk_height = int(30 * SCALE_FACTOR)
        pygame.draw.rect(surface, (101, 67, 33), 
                        (int(tree_x - trunk_width/2), int(tree_y - trunk_height/2), trunk_width, trunk_height))
        # Tree foliage (3 circles for fluffy look)
        foliage_radius = int(25 * SCALE_FACTOR)
        pygame.draw.circle(surface, (34, 139, 34), (int(tree_x), int(tree_y - trunk_height/2 - foliage_radius/2)), foliage_radius)
        pygame.draw.circle(surface, (34, 139, 34), (int(tree_x - foliage_radius/2), int(tree_y - trunk_height/2)), int(foliage_radius * 0.8))
        pygame.draw.circle(surface, (34, 139, 34), (int(tree_x + foliage_radius/2), int(tree_y - trunk_height/2)), int(foliage_radius * 0.8))
    
    # Draw grandstands
    stand_positions = [(WIDTH * 0.15, HEIGHT * 0.5), (WIDTH * 0.85, HEIGHT * 0.5)]
    for sx, sy in stand_positions:
        stand_width = int(100 * SCALE_FACTOR)
        stand_height = int(60 * SCALE_FACTOR)
        # Stand structure
        pygame.draw.rect(surface, (150, 150, 150), (int(sx - stand_width/2), int(sy), stand_width, stand_height))
        # Rows
        for row in range(4):
            row_y = sy + row * stand_height // 4
            pygame.draw.line(surface, (100, 100, 100), (int(sx - stand_width/2), int(row_y)), 
                           (int(sx + stand_width/2), int(row_y)), 2)
        # Roof
        pygame.draw.polygon(surface, (180, 50, 50), [
            (int(sx - stand_width/2 - 10 * SCALE_FACTOR), int(sy)),
            (int(sx + stand_width/2 + 10 * SCALE_FACTOR), int(sy)),
            (int(sx), int(sy - 30 * SCALE_FACTOR))
        ])

def draw_racetrack(surface):
    """Draw a detailed racetrack"""
    # Track is now drawn on top of background
    
    # Outer track border (darker)
    border_width = int(20 * SCALE_FACTOR)
    pygame.draw.circle(surface, (30, 30, 30), CENTER, OUTER_R + border_width)
    
    # Track surface (asphalt)
    pygame.draw.circle(surface, (50, 50, 50), CENTER, OUTER_R)
    
    # Inner grass circle
    pygame.draw.circle(surface, (40, 150, 40), CENTER, INNER_R)
    
    # Track lines
    # Outer white line
    line_width = max(3, int(5 * SCALE_FACTOR))
    pygame.draw.circle(surface, (255, 255, 255), CENTER, OUTER_R, line_width)
    # Inner white line
    pygame.draw.circle(surface, (255, 255, 255), CENTER, INNER_R, line_width)
    
    # Center dashed line (yellow)
    num_dashes = 50
    dash_width = max(2, int(3 * SCALE_FACTOR))
    for i in range(num_dashes):
        angle = (2 * math.pi * i) / num_dashes
        if i % 2 == 0:  # Draw every other dash
            x1 = CENTER[0] + CENTER_R * math.cos(angle)
            y1 = CENTER[1] + CENTER_R * math.sin(angle)
            angle2 = (2 * math.pi * (i + 0.5)) / num_dashes
            x2 = CENTER[0] + CENTER_R * math.cos(angle2)
            y2 = CENTER[1] + CENTER_R * math.sin(angle2)
            pygame.draw.line(surface, (255, 255, 100), (x1, y1), (x2, y2), dash_width)
    
    # Draw starting and finish lines
    line_thickness = max(8, int(12 * SCALE_FACTOR))
    
    # Starting line (bright green)
    start_x1 = CENTER[0] + INNER_R * math.cos(START_FINISH_THETA)
    start_y1 = CENTER[1] + INNER_R * math.sin(START_FINISH_THETA)
    start_x2 = CENTER[0] + OUTER_R * math.cos(START_FINISH_THETA)
    start_y2 = CENTER[1] + OUTER_R * math.sin(START_FINISH_THETA)
    pygame.draw.line(surface, (0, 200, 0), (start_x1, start_y1), (start_x2, start_y2), line_thickness)

def draw_game_over_menu(surface, game_over_reason, laps):
    """Draw game over screen with menu options"""
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.SysFont(None, int(80 * SCALE_FACTOR), bold=True)
    title = title_font.render("GAME OVER", True, (255, 0, 0))
    title_rect = title.get_rect(center=(CENTER[0], CENTER[1] - int(200 * SCALE_FACTOR)))
    surface.blit(title, title_rect)
    
    # Reason text
    reason_font = pygame.font.SysFont(None, int(40 * SCALE_FACTOR))
    reason = reason_font.render(game_over_reason, True, (255, 200, 0))
    reason_rect = reason.get_rect(center=(CENTER[0], CENTER[1] - int(100 * SCALE_FACTOR)))
    surface.blit(reason, reason_rect)
    
    # Laps text
    laps_font = pygame.font.SysFont(None, int(40 * SCALE_FACTOR))
    laps_text = laps_font.render(f"Total Laps Completed: {laps}", True, (100, 200, 255))
    laps_rect = laps_text.get_rect(center=(CENTER[0], CENTER[1]))
    surface.blit(laps_text, laps_rect)
    
    # Menu options
    button_font = pygame.font.SysFont(None, int(45 * SCALE_FACTOR), bold=True)
    button_y_offset = int(150 * SCALE_FACTOR)
    
    # Try Again button
    try_again = button_font.render("SPACE - Try Again", True, (0, 255, 0))
    try_again_rect = try_again.get_rect(center=(CENTER[0], CENTER[1] + button_y_offset))
    surface.blit(try_again, try_again_rect)
    
    # Exit button
    exit_btn = button_font.render("ESC - Exit", True, (255, 100, 100))
    exit_rect = exit_btn.get_rect(center=(CENTER[0], CENTER[1] + button_y_offset + int(80 * SCALE_FACTOR)))
    surface.blit(exit_btn, exit_rect)

def reset_game():
    """Reset game variables for a new game"""
    global r, theta, speed, previous_theta, completed_revolutions, obstacles
    r = CENTER_R
    theta = 0
    speed = 0
    previous_theta = 0
    completed_revolutions = 0
    obstacles = generate_obstacles()

running = True
game_active = True
game_over_reason = ""
frame_count = 0

while running:
    dt = clock.tick(60) / 1.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_active:
                    running = False
                else:
                    running = False
            if event.key == pygame.K_SPACE:
                if not game_active:
                    game_active = True
                    reset_game()

    if game_active:
        # Controls
        keys = pygame.key.get_pressed()
        
        # Acceleration and braking (forward/backward movement along track)
        if keys[pygame.K_UP]:
            speed += 0.5
        if keys[pygame.K_DOWN]:
            speed -= 0.5
        speed = max(0, min(speed, 200))
        
        # Left and right arrows move inward/outward on the track
        if keys[pygame.K_LEFT]:
            r -= 1.5  # Move inward (toward center)
        if keys[pygame.K_RIGHT]:
            r += 1.5  # Move outward (away from center)

        # Update angle based on speed (movement along the circular track)
        theta += (speed / r) * 0.05
        
        # Detect lap completion
        if theta >= 2 * math.pi:
            completed_revolutions += 1
            theta -= 2 * math.pi
            print(f"Lap completed! Total laps: {completed_revolutions}")
            obstacles = generate_obstacles()
        
        previous_theta = theta

        # Drift physics
        if speed < MIN_SPEED:
            r -= (MIN_SPEED - speed) * DRIFT_FACTOR
        elif speed > MAX_SPEED:
            r += (speed - MAX_SPEED) * DRIFT_FACTOR
        else:
            r += (CENTER_R - r) * stability_factor

        # Check track limits
        if r < INNER_R or r > OUTER_R:
            game_over_reason = "You fell off the track!"
            game_active = False

        # Convert polar to cartesian
        x = CENTER[0] + r * math.cos(theta)
        y = CENTER[1] + r * math.sin(theta)

        # Check collision with obstacles
        for obs_r, obs_theta in obstacles:
            obs_x = CENTER[0] + obs_r * math.cos(obs_theta)
            obs_y = CENTER[1] + obs_r * math.sin(obs_theta)
            distance = math.hypot(x - obs_x, y - obs_y)
            if distance < OBSTACLE_SIZE + 12:
                game_over_reason = "You hit a traffic cone!"
                game_active = False

    # DRAW
    frame_count += 1
    draw_background(screen, frame_count)
    draw_racetrack(screen)
    
    # Draw obstacles (traffic cones)
    for obs_r, obs_theta in obstacles:
        obs_x = CENTER[0] + obs_r * math.cos(obs_theta)
        obs_y = CENTER[1] + obs_r * math.sin(obs_theta)
        draw_traffic_cone(screen, obs_x, obs_y)

    # Draw car
    draw_car(screen, int(x), int(y), theta)

    # Display speed and instructions
    font_size = max(24, int(32 * SCALE_FACTOR))
    font = pygame.font.SysFont(None, font_size, bold=True)
    text = font.render(f"Speed: {int(speed)} km/h | Laps: {completed_revolutions}", True, (255, 255, 255))
    # Add shadow effect
    shadow = font.render(f"Speed: {int(speed)} km/h | Laps: {completed_revolutions}", True, (0, 0, 0))
    screen.blit(shadow, (12, 12))
    screen.blit(text, (10, 10))
    
    font_small_size = max(18, int(24 * SCALE_FACTOR))
    font_small = pygame.font.SysFont(None, font_small_size)
    instructions = font_small.render("LEFT/RIGHT arrows to move inward/outward | UP/DOWN arrows to accelerate/brake | ESC to exit", True, (255, 255, 255))
    instructions_shadow = font_small.render("LEFT/RIGHT arrows to move inward/outward | UP/DOWN arrows to accelerate/brake | ESC to exit", True, (0, 0, 0))
    screen.blit(instructions_shadow, (12, 42))
    screen.blit(instructions, (10, 40))

    # Draw game over menu if not active
    if not game_active:
        draw_game_over_menu(screen, game_over_reason, completed_revolutions)

    pygame.display.update()

pygame.quit()