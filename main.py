import pygame
import math
from config import *
from physics import *
from rendering import *
from game_state import GameState

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Physics Racing Game")
clock = pygame.time.Clock()

# Game state
game = GameState()

# Main game loop
while game.running:
    dt = clock.tick(60) / 1.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game.game_active:
                    game.running = False
                else:
                    game.running = False
            if event.key == pygame.K_SPACE:
                if not game.game_active:
                    game.reset()
            # Runtime controls
            if event.key == pygame.K_m:
                game.mass += 0.5
                if game.mass > 50:
                    game.mass = 50
            if event.key == pygame.K_n:
                game.mass -= 0.5
                if game.mass < 0.1:
                    game.mass = 0.1
            if event.key == pygame.K_RIGHTBRACKET:  # ] increase scale
                game.pixels_per_meter += 5
            if event.key == pygame.K_LEFTBRACKET:   # [ decrease scale
                game.pixels_per_meter = max(5.0, game.pixels_per_meter - 5)

    if game.game_active:
        # Controls
        keys = pygame.key.get_pressed()
        
        # Acceleration
        if keys[pygame.K_UP]:
            game.speed += 0.5
        if keys[pygame.K_DOWN]:
            game.speed -= 0.5
        game.speed = max(0, min(game.speed, 200))
        
        # Steering (Radius change)
        if keys[pygame.K_LEFT]:
            game.r -= 1.5  # Move inward
        if keys[pygame.K_RIGHT]:
            game.r += 1.5  # Move outward

        # Update theta
        game.theta += (game.speed / game.r) * 0.05

        # Lap detection
        if game.theta >= 2 * math.pi:
            game.completed_revolutions += 1
            game.theta -= 2 * math.pi
            print(f"Lap completed! Total laps: {game.completed_revolutions}")
            game.obstacles = game.generate_obstacles()

        # Physics calculations
        dt_s = max(dt / 1000.0, 1/240.0)
        
        omega, v_phys, v_m_s, a_c_m, T = calculate_physics_values(
            game.r, game.theta, game.previous_theta, dt_s, game.pixels_per_meter
        )
        
        # Calculate Force
        F_c = game.mass * a_c_m

        game.previous_theta = game.theta

        # Drift physics
        game.r = apply_drift_physics(game.r, game.speed)

        # Check limits
        is_safe, reason = check_track_bounds(game.r)
        if not is_safe:
            game.game_over_reason = reason
            game.game_active = False

        # Cartesian coordinates
        x = CENTER[0] + game.r * math.cos(game.theta)
        y = CENTER[1] + game.r * math.sin(game.theta)

        # Collision detection
        collision, reason = check_obstacle_collision(x, y, game.obstacles)
        if collision:
            game.game_over_reason = reason
            game.game_active = False

        # Store values for rendering
        last_omega = omega
        last_v_phys = v_phys
        last_v_m_s = v_m_s
        last_a_c_m = a_c_m
        last_T = T
        last_Fc = F_c

    # DRAW
    game.frame_count += 1
    draw_background(screen, game.frame_count)
    draw_racetrack(screen)
    
    # Draw obstacles
    for obs_r, obs_theta in game.obstacles:
        obs_x = CENTER[0] + obs_r * math.cos(obs_theta)
        obs_y = CENTER[1] + obs_r * math.sin(obs_theta)
        draw_traffic_cone(screen, obs_x, obs_y)

    # Draw car
    # Need to calculate x,y if not active (use last known position)
    car_x = CENTER[0] + game.r * math.cos(game.theta)
    car_y = CENTER[1] + game.r * math.sin(game.theta)
    draw_car(screen, int(car_x), int(car_y), game.theta)

    # Draw physics vectors (only if active and we have values)
    if game.game_active and 'last_omega' in locals():
        # Tangential velocity vector
        sign = 1 if last_omega >= 0 else -1
        tang_dir = ( -math.sin(game.theta) * sign, math.cos(game.theta) * sign )
        tang_len = max(30 * SCALE_FACTOR, abs(last_v_phys) * 0.08)
        tang_end = (car_x + tang_dir[0] * tang_len, car_y + tang_dir[1] * tang_len)
        draw_arrow(screen, (car_x, car_y), tang_end, (50, 150, 255), width=max(2, int(3 * SCALE_FACTOR)))
        
        # Label v
        font_lab = pygame.font.SysFont(None, max(18, int(20 * SCALE_FACTOR)))
        v_label = font_lab.render("v", True, (200, 230, 255))
        screen.blit(v_label, (tang_end[0] + 6, tang_end[1] + 6))

        # Centripetal acceleration vector
        dir_to_center = (CENTER[0] - car_x, CENTER[1] - car_y)
        dist_to_center = math.hypot(dir_to_center[0], dir_to_center[1]) or 1
        c_unit = (dir_to_center[0] / dist_to_center, dir_to_center[1] / dist_to_center)
        
        a_px_s2 = last_a_c_m * game.pixels_per_meter
        acc_len = max(20 * SCALE_FACTOR, a_px_s2 * 0.06)
        acc_end = (car_x + c_unit[0] * acc_len, car_y + c_unit[1] * acc_len)
        draw_arrow(screen, (car_x, car_y), acc_end, (100, 255, 100), width=max(2, int(3 * SCALE_FACTOR)))
        
        a_label = font_lab.render("a_c", True, (200, 255, 200))
        screen.blit(a_label, (acc_end[0] + 6, acc_end[1] + 6))

        # Centripetal Force Arrow
        # Convert r to meters for display consistency check? No, drawing uses pixels
        # But we need r_m for the label if we want to show it? No, label shows force.
        # But draw_centripetal_force_arrow signature includes r_m... let's check rendering.py
        # def draw_centripetal_force_arrow(surface, car_pos, center, Fc, r_m, v_m_s, mass):
        # It doesn't actually use r_m in the function body! Just Fc.
        # Wait, let me check the function in rendering.py
        # Yes, I checked the code I wrote. It takes r_m but doesn't seem to use it for the calculation of length or label.
        # Ah, wait. In the original code it didn't use it.
        # Let's pass it anyway.
        
        r_m = game.r / game.pixels_per_meter
        draw_centripetal_force_arrow(screen, (car_x, car_y), CENTER, last_Fc, r_m, last_v_m_s, game.mass)

        # Physics Overlay
        draw_physics_overlay(
            screen, CENTER, (car_x, car_y), game.theta, game.r, 
            last_omega, last_v_m_s, last_a_c_m, last_T, last_Fc,
            game.mass, game.pixels_per_meter
        )
        
        # Force Meter
        draw_force_meter(screen, last_Fc, last_v_m_s, r_m, game.mass)

    # UI Text
    font_size = max(24, int(32 * SCALE_FACTOR))
    font = pygame.font.SysFont(None, font_size, bold=True)
    text = font.render(f"Speed: {int(game.speed)} km/h | Laps: {game.completed_revolutions}", True, (255, 255, 255))
    shadow = font.render(f"Speed: {int(game.speed)} km/h | Laps: {game.completed_revolutions}", True, (0, 0, 0))
    screen.blit(shadow, (12, 12))
    screen.blit(text, (10, 10))
    
    font_small_size = max(18, int(24 * SCALE_FACTOR))
    font_small = pygame.font.SysFont(None, font_small_size)
    instr = "LEFT/RIGHT arrows to move inward/outward | UP/DOWN arrows to accelerate/brake | ESC to exit"
    instructions = font_small.render(instr, True, (255, 255, 255))
    instructions_shadow = font_small.render(instr, True, (0, 0, 0))
    screen.blit(instructions_shadow, (12, 42))
    screen.blit(instructions, (10, 40))

    # Game Over Menu
    if not game.game_active:
        draw_game_over_menu(screen, game.game_over_reason, game.completed_revolutions)

    pygame.display.update()

pygame.quit()