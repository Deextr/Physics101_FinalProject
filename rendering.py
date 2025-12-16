import pygame
import math
from config import *

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

def draw_arrow(surface, start, end, color, width=3):
    """Draw a line with a triangular arrowhead from start to end."""
    pygame.draw.line(surface, color, start, end, width)
    # Arrowhead
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    head_length = max(8, int(10 * SCALE_FACTOR))
    head_angle = math.radians(25)
    left = (end[0] - head_length * math.cos(angle - head_angle), end[1] - head_length * math.sin(angle - head_angle))
    right = (end[0] - head_length * math.cos(angle + head_angle), end[1] - head_length * math.sin(angle + head_angle))
    pygame.draw.polygon(surface, color, [end, left, right])

def draw_physics_overlay(surface, center, pos, theta, r, omega, v_m_s, a_c_m, T, Fc, mass, pixels_per_meter):
    """Render numeric readouts, formulas (SI) and a short centrifugal/centripetal note."""
    font_small_size = max(18, int(20 * SCALE_FACTOR))
    font_small = pygame.font.SysFont(None, font_small_size)

    # Convert m/s to km/h for easier reading
    v_kmh = v_m_s * 3.6
    lines = [
        f"ω = {omega:.2f} rad/s",
        f"v = {v_m_s:.2f} m/s ({v_kmh:.1f} km/h)",
        f"a_c = {a_c_m:.2f} m/s²",
        f"T = {T:.2f} s" if T != float('inf') else "T = ∞",
        f"F_c = m·a_c = {Fc:.2f} N (m={mass:.1f} kg)"
    ]

    # Draw background box
    box_w = int(320 * SCALE_FACTOR)
    box_h = int(len(lines) * (font_small_size + 6) + 12 * SCALE_FACTOR)
    box_x = 10
    box_y = HEIGHT - box_h - 10
    overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (box_x, box_y))

    for i, line in enumerate(lines):
        txt = font_small.render(line, True, (255, 255, 255))
        surface.blit(txt, (box_x + 8, box_y + 6 + i * (font_small_size + 6)))

    # Formula overlay (brief) - expressed in SI (r in meters)
    formula_font = pygame.font.SysFont(None, int(18 * SCALE_FACTOR))
    f1 = formula_font.render("a_c = v² / r = 4π² r / T²  (r in m)", True, (255, 220, 180))
    f2 = formula_font.render("F_c = m a_c = m v² / r = m 4π² r / T²", True, (255, 220, 180))
    surface.blit(f1, (box_x + 8, box_y - int(30 * SCALE_FACTOR)))
    surface.blit(f2, (box_x + 8, box_y - int(12 * SCALE_FACTOR)))

    # Short clarifying note
    note = formula_font.render("Centripetal: inward force. 'Centrifugal' is apparent outward in rotating frame.", True, (200, 200, 200))
    surface.blit(note, (box_x + 8, box_y - int(48 * SCALE_FACTOR)))

    # Show current mass and pixels-per-meter
    misc = formula_font.render(f"mass = {mass:.1f} kg   scale = {pixels_per_meter:.0f} px/m (use M/N, [/] keys)", True, (210, 210, 210))
    surface.blit(misc, (box_x + 8, box_y - int(66 * SCALE_FACTOR)))


def draw_centripetal_force_arrow(surface, car_pos, center, Fc, r_m, v_m_s, mass):
    """Draw a prominent centripetal force arrow pointing toward center."""
    x, y = car_pos
    
    # Direction toward center
    dir_to_center = (center[0] - x, center[1] - y)
    dist = math.hypot(dir_to_center[0], dir_to_center[1]) or 1
    unit_vec = (dir_to_center[0] / dist, dir_to_center[1] / dist)
    
    # Scale arrow length based on force magnitude
    base_length = 40 * SCALE_FACTOR
    force_scale = 3.0
    arrow_length = base_length + (Fc * force_scale)
    arrow_length = min(arrow_length, 150 * SCALE_FACTOR)
    
    # Calculate end point
    end_x = x + unit_vec[0] * arrow_length
    end_y = y + unit_vec[1] * arrow_length
    
    # Draw arrow (magenta)
    arrow_color = (255, 0, 255)
    arrow_width = max(3, int(4 * SCALE_FACTOR))
    
    pygame.draw.line(surface, arrow_color, (x, y), (end_x, end_y), arrow_width)
    
    # Arrowhead
    angle = math.atan2(unit_vec[1], unit_vec[0])
    head_length = max(12, int(15 * SCALE_FACTOR))
    head_angle = math.radians(25)
    left = (end_x - head_length * math.cos(angle - head_angle), 
            end_y - head_length * math.sin(angle - head_angle))
    right = (end_x - head_length * math.cos(angle + head_angle), 
             end_y - head_length * math.sin(angle + head_angle))
    pygame.draw.polygon(surface, arrow_color, [(end_x, end_y), left, right])
    
    # Label
    font_lab = pygame.font.SysFont(None, max(20, int(22 * SCALE_FACTOR)), bold=True)
    label = font_lab.render(f"F_c = {Fc:.2f}N", True, (255, 200, 255))
    label_bg = pygame.Surface((label.get_width() + 8, label.get_height() + 4), pygame.SRCALPHA)
    label_bg.fill((0, 0, 0, 180))
    
    label_x = x + unit_vec[0] * (arrow_length * 0.6)
    label_y = y + unit_vec[1] * (arrow_length * 0.6) - 20
    
    surface.blit(label_bg, (label_x - 4, label_y - 2))
    surface.blit(label, (label_x, label_y))

def draw_force_meter(surface, Fc, v_m_s, r_m, mass, x=None, y=None):
    """Draw an enhanced force meter showing Fc and its components."""
    meter_w = int(280 * SCALE_FACTOR)
    meter_h = int(80 * SCALE_FACTOR)
    if x is None:
        x = WIDTH - meter_w - 20
    if y is None:
        y = 20
    
    panel = pygame.Surface((meter_w, meter_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 200))
    surface.blit(panel, (x, y))
    
    pygame.draw.rect(surface, (255, 0, 255), (x, y, meter_w, meter_h), 3)
    
    font_title = pygame.font.SysFont(None, max(20, int(24 * SCALE_FACTOR)), bold=True)
    title = font_title.render("CENTRIPETAL FORCE", True, (255, 100, 255))
    surface.blit(title, (x + 8, y + 6))
    
    bar_y = y + 32
    bar_h = int(16 * SCALE_FACTOR)
    bar_w = meter_w - 16
    
    pygame.draw.rect(surface, (40, 40, 40), (x + 8, bar_y, bar_w, bar_h))
    
    max_f = max(10.0, abs(Fc) * 2.0)
    fill_frac = min(1.0, abs(Fc) / max_f)
    fill_w = int(fill_frac * bar_w)
    
    if fill_frac < 0.3:
        bar_color = (100, 255, 100)
    elif fill_frac < 0.7:
        bar_color = (255, 255, 100)
    else:
        bar_color = (255, 100, 100)
    
    pygame.draw.rect(surface, bar_color, (x + 8, bar_y, fill_w, bar_h))
    pygame.draw.rect(surface, (200, 200, 200), (x + 8, bar_y, bar_w, bar_h), 2)
    
    font_info = pygame.font.SysFont(None, max(16, int(18 * SCALE_FACTOR)))
    force_text = font_info.render(f"F_c = {Fc:.2f} N  (max: {max_f:.1f} N)", True, (255, 255, 255))
    surface.blit(force_text, (x + 8, bar_y + bar_h + 4))
    
    components = font_info.render(f"m={mass:.1f}kg  v={v_m_s:.2f}m/s  r={r_m:.2f}m", True, (200, 200, 200))
    surface.blit(components, (x + 8, bar_y + bar_h + 22))

def draw_background(surface, frame_count):
    """Draw animated background"""
    surface.fill(COLOR_BG)
    
    # Sky gradient
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
        cloud_x = cx if cx < WIDTH else cx - WIDTH
        cloud_radius = int(40 * SCALE_FACTOR)
        pygame.draw.circle(surface, (255, 255, 255), (int(cloud_x), int(cy)), cloud_radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(cloud_x - 30 * SCALE_FACTOR), int(cy + 10 * SCALE_FACTOR)), int(35 * SCALE_FACTOR))
        pygame.draw.circle(surface, (255, 255, 255), (int(cloud_x + 30 * SCALE_FACTOR), int(cy + 10 * SCALE_FACTOR)), int(30 * SCALE_FACTOR))
    
    # Grass
    grass_radius = int(OUTER_R * 1.8)
    pygame.draw.circle(surface, COLOR_GRASS, CENTER, grass_radius)
    
    # Trees
    tree_distance = int(OUTER_R * 1.4)
    num_trees = 16
    for i in range(num_trees):
        angle = (2 * math.pi * i) / num_trees
        tree_x = CENTER[0] + tree_distance * math.cos(angle)
        tree_y = CENTER[1] + tree_distance * math.sin(angle)
        trunk_width = int(12 * SCALE_FACTOR)
        trunk_height = int(30 * SCALE_FACTOR)
        pygame.draw.rect(surface, (101, 67, 33), 
                        (int(tree_x - trunk_width/2), int(tree_y - trunk_height/2), trunk_width, trunk_height))
        foliage_radius = int(25 * SCALE_FACTOR)
        pygame.draw.circle(surface, (34, 139, 34), (int(tree_x), int(tree_y - trunk_height/2 - foliage_radius/2)), foliage_radius)
        pygame.draw.circle(surface, (34, 139, 34), (int(tree_x - foliage_radius/2), int(tree_y - trunk_height/2)), int(foliage_radius * 0.8))
        pygame.draw.circle(surface, (34, 139, 34), (int(tree_x + foliage_radius/2), int(tree_y - trunk_height/2)), int(foliage_radius * 0.8))
    
    # Grandstands
    stand_positions = [(WIDTH * 0.15, HEIGHT * 0.5), (WIDTH * 0.85, HEIGHT * 0.5)]
    for sx, sy in stand_positions:
        stand_width = int(100 * SCALE_FACTOR)
        stand_height = int(60 * SCALE_FACTOR)
        pygame.draw.rect(surface, (150, 150, 150), (int(sx - stand_width/2), int(sy), stand_width, stand_height))
        for row in range(4):
            row_y = sy + row * stand_height // 4
            pygame.draw.line(surface, (100, 100, 100), (int(sx - stand_width/2), int(row_y)), 
                           (int(sx + stand_width/2), int(row_y)), 2)
        pygame.draw.polygon(surface, (180, 50, 50), [
            (int(sx - stand_width/2 - 10 * SCALE_FACTOR), int(sy)),
            (int(sx + stand_width/2 + 10 * SCALE_FACTOR), int(sy)),
            (int(sx), int(sy - 30 * SCALE_FACTOR))
        ])

def draw_racetrack(surface):
    """Draw a detailed racetrack"""
    border_width = int(20 * SCALE_FACTOR)
    pygame.draw.circle(surface, COLOR_TRACK_BORDER, CENTER, OUTER_R + border_width)
    pygame.draw.circle(surface, COLOR_TRACK, CENTER, OUTER_R)
    pygame.draw.circle(surface, COLOR_GRASS, CENTER, INNER_R)
    
    line_width = max(3, int(5 * SCALE_FACTOR))
    pygame.draw.circle(surface, COLOR_LINE_WHITE, CENTER, OUTER_R, line_width)
    pygame.draw.circle(surface, COLOR_LINE_WHITE, CENTER, INNER_R, line_width)
    
    num_dashes = 50
    dash_width = max(2, int(3 * SCALE_FACTOR))
    for i in range(num_dashes):
        angle = (2 * math.pi * i) / num_dashes
        if i % 2 == 0:
            x1 = CENTER[0] + CENTER_R * math.cos(angle)
            y1 = CENTER[1] + CENTER_R * math.sin(angle)
            angle2 = (2 * math.pi * (i + 0.5)) / num_dashes
            x2 = CENTER[0] + CENTER_R * math.cos(angle2)
            y2 = CENTER[1] + CENTER_R * math.sin(angle2)
            pygame.draw.line(surface, COLOR_LINE_YELLOW, (x1, y1), (x2, y2), dash_width)
    
    line_thickness = max(8, int(12 * SCALE_FACTOR))
    start_x1 = CENTER[0] + INNER_R * math.cos(START_FINISH_THETA)
    start_y1 = CENTER[1] + INNER_R * math.sin(START_FINISH_THETA)
    start_x2 = CENTER[0] + OUTER_R * math.cos(START_FINISH_THETA)
    start_y2 = CENTER[1] + OUTER_R * math.sin(START_FINISH_THETA)
    pygame.draw.line(surface, COLOR_START_LINE, (start_x1, start_y1), (start_x2, start_y2), line_thickness)

def draw_game_over_menu(surface, game_over_reason, laps):
    """Draw game over screen with menu options"""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    
    title_font = pygame.font.SysFont(None, int(80 * SCALE_FACTOR), bold=True)
    title = title_font.render("GAME OVER", True, (255, 0, 0))
    title_rect = title.get_rect(center=(CENTER[0], CENTER[1] - int(200 * SCALE_FACTOR)))
    surface.blit(title, title_rect)
    
    reason_font = pygame.font.SysFont(None, int(40 * SCALE_FACTOR))
    reason = reason_font.render(game_over_reason, True, (255, 200, 0))
    reason_rect = reason.get_rect(center=(CENTER[0], CENTER[1] - int(100 * SCALE_FACTOR)))
    surface.blit(reason, reason_rect)
    
    laps_font = pygame.font.SysFont(None, int(40 * SCALE_FACTOR))
    laps_text = laps_font.render(f"Total Laps Completed: {laps}", True, (100, 200, 255))
    laps_rect = laps_text.get_rect(center=(CENTER[0], CENTER[1]))
    surface.blit(laps_text, laps_rect)
    
    button_font = pygame.font.SysFont(None, int(45 * SCALE_FACTOR), bold=True)
    button_y_offset = int(150 * SCALE_FACTOR)
    
    try_again = button_font.render("SPACE - Try Again", True, (0, 255, 0))
    try_again_rect = try_again.get_rect(center=(CENTER[0], CENTER[1] + button_y_offset))
    surface.blit(try_again, try_again_rect)
    
    exit_btn = button_font.render("ESC - Exit", True, (255, 100, 100))
    exit_rect = exit_btn.get_rect(center=(CENTER[0], CENTER[1] + button_y_offset + int(80 * SCALE_FACTOR)))
    surface.blit(exit_btn, exit_rect)
