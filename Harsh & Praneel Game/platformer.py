import os
import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 960, 540
FPS = 60

script_dir = os.path.dirname(__file__)

orbitron_dir = os.path.join(script_dir, "Orbitron")
font_name = None
if os.path.isdir(orbitron_dir):
    for entry in os.listdir(orbitron_dir):
        if entry.lower().endswith(".ttf"):
            font_name = os.path.join(orbitron_dir, entry)
            break
if not font_name:
    font_name = os.path.join(script_dir, "SDDystopianDemo.ttf")
if not os.path.isfile(font_name):
    font_name = pygame.font.match_font("orbitron")
if not font_name:
    font_name = pygame.font.match_font("orbit")
if not font_name:
    font_name = pygame.font.match_font("futura")
if not font_name:
    font_name = pygame.font.match_font("arialblack")

window_width = WIDTH + 160
window_height = HEIGHT + 100
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("Cyberpunk Platformer")
clock = pygame.time.Clock()
screen_width, screen_height = screen.get_size()
game_surface = pygame.Surface((WIDTH, HEIGHT))

if font_name:
    font_large = pygame.font.Font(font_name, 44)
    font_medium = pygame.font.Font(font_name, 20)
    font_small = pygame.font.Font(font_name, 16)
else:
    font_large = pygame.font.SysFont("Arial", 44, bold=True)
    font_medium = pygame.font.SysFont("Arial", 20)
    font_small = pygame.font.SysFont("Arial", 16)


def render_futuristic_text(text, font, color):
    base = font.render(text, False, color)
    shadow = font.render(text, False, (0, 0, 0))
    out = pygame.Surface((base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA)
    out.blit(shadow, (1, 1))
    out.blit(base, (0, 0))
    return out

chatgpt_image = None
chatgpt_image_path = os.path.join(script_dir, "ChatGPT Image Jun 28, 2026, 09_13_16 PM.png")
try:
    chatgpt_image = pygame.image.load(chatgpt_image_path).convert_alpha()
    chatgpt_image = pygame.transform.smoothscale(chatgpt_image, (WIDTH, HEIGHT))
except Exception:
    chatgpt_image = None

class MovingPlatform:
    def __init__(self, rect, vel, min_x=None, max_x=None, min_y=None, max_y=None):
        self.rect = rect
        self.vel = pygame.math.Vector2(vel)
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def update(self, obstacles=None):
        next_rect = self.rect.copy()
        next_rect.x += int(self.vel.x)

        if self.min_x is not None and next_rect.left < self.min_x:
            next_rect.left = self.min_x
            self.vel.x *= -1
        if self.max_x is not None and next_rect.right > self.max_x:
            next_rect.right = self.max_x
            self.vel.x *= -1
        if obstacles and any(next_rect.colliderect(ob) for ob in obstacles):
            self.vel.x *= -1
        else:
            self.rect.x = next_rect.x

        next_rect = self.rect.copy()
        next_rect.y += int(self.vel.y)

        if self.min_y is not None and next_rect.top < self.min_y:
            next_rect.top = self.min_y
            self.vel.y *= -1
        if self.max_y is not None and next_rect.bottom > self.max_y:
            next_rect.bottom = self.max_y
            self.vel.y *= -1
        if obstacles and any(next_rect.colliderect(ob) for ob in obstacles):
            self.vel.y *= -1
        else:
            self.rect.y = next_rect.y

class MovingHazard(MovingPlatform):
    pass

class Level:
    def __init__(
        self,
        name,
        bg_colors,
        platform_color,
        hazard_color,
        goal_color,
        platforms,
        hazards,
        goal,
        level_width=WIDTH,
        moving_platforms=None,
        moving_hazards=None,
        warp_pipes=None,
    ):
        self.name = name
        self.bg_colors = bg_colors
        self.platform_color = platform_color
        self.hazard_color = hazard_color
        self.goal_color = goal_color
        self.platforms = platforms
        self.hazards = hazards
        self.goal = goal
        self.level_width = level_width
        self.moving_platforms = moving_platforms or []
        self.moving_hazards = moving_hazards or []
        self.warp_pipes = warp_pipes or []


def get_level_platforms(level):
    return level.platforms + [mp.rect for mp in level.moving_platforms]


def get_level_hazards(level):
    return level.hazards + [mh.rect for mh in level.moving_hazards]


def resolve_moving_overlap(objects):
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            a = objects[i]
            b = objects[j]
            if a.rect.colliderect(b.rect):
                overlap = a.rect.clip(b.rect)
                if overlap.width < overlap.height:
                    shift = overlap.width // 2 + 1
                    if a.rect.centerx < b.rect.centerx:
                        a.rect.x -= shift
                        b.rect.x += shift
                    else:
                        a.rect.x += shift
                        b.rect.x -= shift
                    a.vel.x *= -1
                    b.vel.x *= -1
                else:
                    shift = overlap.height // 2 + 1
                    if a.rect.centery < b.rect.centery:
                        a.rect.y -= shift
                        b.rect.y += shift
                    else:
                        a.rect.y += shift
                        b.rect.y -= shift
                    a.vel.y *= -1
                    b.vel.y *= -1

levels = [
    Level(
        name="Neon Skyline",
        bg_colors=(24, 18, 58),
        platform_color=(107, 60, 255),
        hazard_color=(255, 61, 61),
        goal_color=(19, 255, 149),
        platforms=[
            pygame.Rect(0, 500, 1600, 28),
            pygame.Rect(220, 420, 160, 20),
            pygame.Rect(520, 340, 140, 20),
            pygame.Rect(760, 280, 120, 20),
            pygame.Rect(1120, 380, 180, 20),
            pygame.Rect(1400, 320, 120, 20),
        ],
        hazards=[
            pygame.Rect(560, 420, 80, 20),
            pygame.Rect(820, 340, 60, 20),
            pygame.Rect(1280, 460, 100, 20),
        ],
        moving_platforms=[
            MovingPlatform(pygame.Rect(420, 380, 140, 20), (1.8, 0), min_x=420, max_x=620),
            MovingPlatform(pygame.Rect(1020, 450, 140, 20), (0, -1.2), min_y=380, max_y=450),
        ],
        moving_hazards=[
            MovingHazard(pygame.Rect(720, 460, 80, 20), (1.6, 0), min_x=620, max_x=900),
        ],
        warp_pipes=[
            {"rect": pygame.Rect(240, 380, 48, 40), "target_rect": pygame.Rect(1140, 340, 48, 40)},
            {"rect": pygame.Rect(1140, 340, 48, 40), "target_rect": pygame.Rect(1440, 280, 48, 40)},
            {"rect": pygame.Rect(1440, 280, 48, 40), "target_rect": pygame.Rect(240, 380, 48, 40)},
        ],
        goal=pygame.Rect(1550, 220, 40, 40),
        level_width=1600,
    ),
    Level(
        name="Synth District",
        bg_colors=(11, 15, 33),
        platform_color=(0, 245, 255),
        hazard_color=(255, 61, 61),
        goal_color=(255, 61, 255),
        platforms=[
            pygame.Rect(0, 500, 2400, 28),
            pygame.Rect(120, 430, 130, 18),
            pygame.Rect(340, 380, 130, 18),
            pygame.Rect(620, 320, 160, 18),
            pygame.Rect(920, 270, 140, 18),
            pygame.Rect(1120, 220, 100, 18),
            pygame.Rect(1520, 330, 180, 18),
            pygame.Rect(1920, 280, 140, 18),
        ],
        hazards=[
            pygame.Rect(300, 460, 60, 20),
            pygame.Rect(620, 360, 70, 20),
            pygame.Rect(840, 460, 80, 20),
            pygame.Rect(1360, 210, 90, 20),
            pygame.Rect(1780, 250, 70, 20),
        ],
        moving_platforms=[
            MovingPlatform(pygame.Rect(480, 380, 140, 20), (2.1, 0), min_x=480, max_x=820),
            MovingPlatform(pygame.Rect(1240, 330, 120, 20), (0, 1.3), min_y=260, max_y=380),
            MovingPlatform(pygame.Rect(1760, 420, 160, 20), (1.8, 0), min_x=1760, max_x=2040),
            MovingPlatform(pygame.Rect(2280, 260, 160, 18), (1.6, 0), min_x=2200, max_x=2380),
        ],
        moving_hazards=[
            MovingHazard(pygame.Rect(680, 460, 90, 20), (1.6, 0), min_x=620, max_x=920),
            MovingHazard(pygame.Rect(1440, 260, 80, 20), (0, 1.4), min_y=240, max_y=340),
            MovingHazard(pygame.Rect(1940, 420, 100, 20), (-1.8, 0), min_x=1940, max_x=2140),
        ],
        warp_pipes=[
            {"rect": pygame.Rect(140, 390, 48, 40), "target_rect": pygame.Rect(960, 230, 48, 40)},
            {"rect": pygame.Rect(960, 230, 48, 40), "target_rect": pygame.Rect(1620, 290, 48, 40)},
            {"rect": pygame.Rect(1620, 290, 48, 40), "target_rect": pygame.Rect(140, 390, 48, 40)},
        ],
        goal=pygame.Rect(2340, 219, 40, 40),
        level_width=2400,
    ),
    Level(
        name="Cybercore Spire",
        bg_colors=(13, 5, 21),
        platform_color=(255, 61, 255),
        hazard_color=(255, 61, 61),
        goal_color=(0, 255, 245),
        platforms=[
            pygame.Rect(0, 500, 4200, 28),
            pygame.Rect(100, 430, 120, 18),
            pygame.Rect(340, 360, 140, 18),
            pygame.Rect(620, 320, 120, 18),
            pygame.Rect(920, 280, 140, 18),
            pygame.Rect(1220, 240, 140, 18),
            pygame.Rect(1520, 290, 140, 18),
            pygame.Rect(1840, 340, 140, 18),
            pygame.Rect(2180, 300, 120, 18),
            pygame.Rect(2520, 250, 140, 18),
            pygame.Rect(2860, 210, 120, 18),
            pygame.Rect(3180, 260, 120, 18),
            pygame.Rect(3440, 220, 140, 18),
            pygame.Rect(3760, 260, 120, 18),
            pygame.Rect(4040, 230, 140, 18),
        ],
        hazards=[
            pygame.Rect(420, 460, 80, 20),
            pygame.Rect(1380, 320, 80, 20),
            pygame.Rect(3040, 240, 80, 20),
            pygame.Rect(3680, 300, 80, 20),
        ],
        moving_platforms=[
            MovingPlatform(pygame.Rect(540, 380, 120, 18), (2.4, 0), min_x=540, max_x=760),
            MovingPlatform(pygame.Rect(1660, 320, 120, 18), (0, -1.4), min_y=260, max_y=340),
            MovingPlatform(pygame.Rect(2080, 340, 140, 18), (2.0, 0), min_x=2080, max_x=2340),
        ],
        moving_hazards=[
            MovingHazard(pygame.Rect(760, 250, 80, 20), (1.8, 0), min_x=700, max_x=920),
            MovingHazard(pygame.Rect(2060, 280, 90, 20), (0, -1.6), min_y=240, max_y=320),
            MovingHazard(pygame.Rect(2680, 260, 100, 20), (-2.0, 0), min_x=2580, max_x=2860),
        ],
        warp_pipes=[
            {"rect": pygame.Rect(430, 320, 48, 40), "target_rect": pygame.Rect(2520, 210, 48, 40)},
            {"rect": pygame.Rect(1320, 190, 48, 40), "target_rect": pygame.Rect(2860, 170, 48, 40)},
            {"rect": pygame.Rect(3180, 220, 48, 40), "target_rect": pygame.Rect(4040, 190, 48, 40)},
        ],
        goal=pygame.Rect(4120, 220, 40, 40),
        level_width=4200,
    ),
]

player = pygame.Rect(80, 440, 32, 48)
player_speed = 4.0
player_jump = 10.0
player_vel = pygame.math.Vector2(0, 0)

current_level = 0
state = "playing"
player_can_double_jump = True


def draw_background(level, tick, camera_x):
    if chatgpt_image:
        game_surface.blit(chatgpt_image, (0, 0))
    else:
        top = level.bg_colors
        bottom = (4, 5, 15)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
            g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
            b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
            pygame.draw.line(game_surface, (r, g, b), (0, y), (WIDTH, y))


def draw_platform(platform_rect, fill_color, edge_color, highlight_color):
    pygame.draw.rect(game_surface, fill_color, platform_rect, border_radius=12)
    pygame.draw.rect(game_surface, edge_color, platform_rect, width=3, border_radius=12)
    if platform_rect.w >= 80:
        inner = platform_rect.inflate(-12, -8)
        pygame.draw.rect(game_surface, highlight_color, inner, width=2, border_radius=10)
        shine = pygame.Rect(platform_rect.x + 10, platform_rect.y + 5, platform_rect.w - 20, 6)
        pygame.draw.rect(game_surface, highlight_color, shine, border_radius=3)


def draw_level(level, tick, camera_x):
    draw_background(level, tick, camera_x)
    for platform in level.platforms:
        platform_rect = pygame.Rect(platform.x - camera_x, platform.y, platform.w, platform.h)
        draw_platform(platform_rect, level.platform_color, (255, 255, 255), (210, 220, 255))

    for platform in level.moving_platforms:
        platform_rect = pygame.Rect(platform.rect.x - camera_x, platform.rect.y, platform.rect.w, platform.rect.h)
        draw_platform(platform_rect, level.platform_color, (255, 255, 255), (210, 220, 255))

    for hazard in level.hazards:
        hazard_rect = pygame.Rect(hazard.x - camera_x, hazard.y, hazard.w, hazard.h)
        pygame.draw.rect(game_surface, level.hazard_color, hazard_rect, border_radius=4)
        inner = hazard_rect.inflate(-12, -8)
        pygame.draw.rect(game_surface, (255, 255, 255, 60), inner, border_radius=3)

    for hazard in level.moving_hazards:
        hazard_rect = pygame.Rect(hazard.rect.x - camera_x, hazard.rect.y, hazard.rect.w, hazard.rect.h)
        pygame.draw.rect(game_surface, level.hazard_color, hazard_rect, border_radius=4)
        inner = hazard_rect.inflate(-12, -8)
        pygame.draw.rect(game_surface, (255, 255, 255, 60), inner, border_radius=3)

    for pipe in level.warp_pipes:
        pipe_rect = pygame.Rect(pipe["rect"].x - camera_x, pipe["rect"].y, pipe["rect"].w, pipe["rect"].h)
        pygame.draw.rect(game_surface, (130, 0, 180), pipe_rect, border_radius=12)
        inner_rect = pipe_rect.inflate(-10, -10)
        pygame.draw.rect(game_surface, (70, 0, 130), inner_rect, border_radius=8)
        top_rect = pygame.Rect(pipe_rect.x - 4, pipe_rect.y - 10, pipe_rect.w + 8, 12)
        pygame.draw.rect(game_surface, (255, 140, 255), top_rect, border_radius=6)
        for i in range(1, 3):
            x = pipe_rect.x + 10 + i * 12
            pygame.draw.line(game_surface, (255, 180, 255), (x, pipe_rect.y + 10), (x, pipe_rect.bottom - 10), 2)

    goal_rect = pygame.Rect(level.goal.x - camera_x, level.goal.y, level.goal.w, level.goal.h)
    pygame.draw.rect(game_surface, level.goal_color, goal_rect, border_radius=6)
    pygame.draw.rect(game_surface, (255, 255, 255), goal_rect, width=2, border_radius=6)


def draw_player(camera_x):
    player_rect = pygame.Rect(player.x - camera_x, player.y, player.w, player.h)
    pygame.draw.rect(game_surface, (243, 243, 255), player_rect, border_radius=5)
    if player_vel.y != 0:
        shadow = pygame.Rect(player_rect.x + 10, player_rect.y + player_rect.h, 12, 6)
        pygame.draw.rect(game_surface, (255, 255, 255, 70), shadow, border_radius=3)


def draw_hud(level):
    title = render_futuristic_text(f"Level: {level.name}", font_medium, (255, 255, 255))
    hints = render_futuristic_text("Avoid red hazards, reach the neon gate.", font_small, (200, 200, 255))
    controls = render_futuristic_text("A/D move · W jump/double jump · S warp · E restart · N next level", font_small, (200, 200, 255))

    width = max(title.get_width(), hints.get_width(), controls.get_width()) + 40
    height = title.get_height() + hints.get_height() + controls.get_height() + 42
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 16))
    pygame.draw.rect(overlay, (12, 10, 34, 190), pygame.Rect(2, 2, width - 4, height - 4), border_radius=14)
    game_surface.blit(overlay, (20, 20))

    game_surface.blit(title, (34, 28))
    game_surface.blit(hints, (34, 28 + title.get_height() + 10))
    game_surface.blit(controls, (34, 28 + title.get_height() + 10 + hints.get_height() + 6))


def reset_level():
    global player, player_vel, state, player_can_double_jump
    player.x = 80
    player.y = 440
    player_vel.update(0, 0)
    player_can_double_jump = True
    state = "playing"


def next_level():
    global current_level
    current_level += 1
    if current_level >= len(levels):
        current_level = len(levels) - 1
        return False
    reset_level()
    return True


def collide_rects(rect, rects, dy):
    for target in rects:
        if rect.colliderect(target):
            if dy > 0 and rect.bottom - target.top < 20:
                rect.bottom = target.top
                return True
            if dy < 0 and target.bottom - rect.top < 20:
                rect.top = target.bottom
                return False
    return False


def is_on_ground(rect, platforms):
    if rect.bottom >= HEIGHT:
        return True
    test_rect = rect.copy()
    test_rect.y += 1
    for platform in platforms:
        if test_rect.colliderect(platform):
            return True
    return False


def main():
    global state, current_level, player_can_double_jump, screen, screen_width, screen_height
    tick = 0
    gravity = 0.55

    while True:
        clock.tick(FPS)
        tick += 1

        level = levels[current_level]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if state == "win":
                        if not next_level():
                            state = "complete"
                    else:
                        reset_level()
                if event.key == pygame.K_n and state == "win":
                    if not next_level():
                        state = "complete"
                if event.key == pygame.K_w and state == "playing":
                    if is_on_ground(player, get_level_platforms(level)):
                        player_vel.y = -player_jump
                        player_can_double_jump = True
                    elif player_can_double_jump:
                        player_vel.y = -player_jump
                        player_can_double_jump = False

        static_obstacles = level.platforms + level.hazards
        platform_rects = [p.rect.copy().move(int(p.vel.x), int(p.vel.y)) for p in level.moving_platforms]
        hazard_rects = [h.rect.copy().move(int(h.vel.x), int(h.vel.y)) for h in level.moving_hazards]

        for idx, platform in enumerate(level.moving_platforms):
            other_platforms = [rect for j, rect in enumerate(platform_rects) if j != idx]
            other_hazards = hazard_rects.copy()
            platform.update(obstacles=static_obstacles + other_platforms + other_hazards)

        for idx, hazard in enumerate(level.moving_hazards):
            other_hazards = [rect for j, rect in enumerate(hazard_rects) if j != idx]
            other_platforms = platform_rects.copy()
            hazard.update(obstacles=static_obstacles + other_hazards + other_platforms)

        resolve_moving_overlap(level.moving_platforms + level.moving_hazards)

        if state == "playing":
            for platform in level.moving_platforms:
                if player.bottom >= platform.rect.top - 2 and player.bottom <= platform.rect.top + 2 and player.right > platform.rect.left and player.left < platform.rect.right:
                    player.x += int(platform.vel.x)
                    player.y += int(platform.vel.y)
                    break

        keys = pygame.key.get_pressed()
        if state == "playing":
            player_vel.x = 0
            if keys[pygame.K_a]:
                player_vel.x = -player_speed
            if keys[pygame.K_d]:
                player_vel.x = player_speed

            if keys[pygame.K_s]:
                for pipe in level.warp_pipes:
                    if player.colliderect(pipe["rect"]):
                        if "target_rect" in pipe:
                            dest = pipe["target_rect"]
                            player.x = int(dest.x + (dest.w - player.w) / 2)
                            player.y = int(dest.y - player.h - 1)
                        else:
                            player.x, player.y = pipe["target"]
                        player_vel.update(0, 0)
                        break

            player_vel.y += gravity
            player_vel.y = min(player_vel.y, 14)

            player.x += player_vel.x
            if player.left < 0:
                player.left = 0
            if player.right > level.level_width:
                player.right = level.level_width

            player.y += int(player_vel.y)
            if collide_rects(player, get_level_platforms(level), player_vel.y):
                player_vel.y = 0

            if player.top > HEIGHT:
                state = "dead"

            for hazard in get_level_hazards(level):
                if player.colliderect(hazard):
                    state = "dead"

            if player.colliderect(level.goal):
                state = "win"

        game_surface.fill((0, 0, 0))
        camera_x = max(0, min(int(player.x + player.w / 2 - WIDTH / 2), max(level.level_width - WIDTH, 0)))
        draw_level(level, tick, camera_x)
        draw_player(camera_x)
        draw_hud(level)

        status_text = ""
        if state == "dead":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            game_surface.blit(overlay, (0, 0))
            status = render_futuristic_text("GAME OVER", font_large, (255, 61, 61))
            game_surface.blit(status, (WIDTH // 2 - status.get_width() // 2, 220))
            sub = render_futuristic_text("Press E to restart.", font_medium, (255, 255, 255))
            game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 280))
            status_text = "Dead. Press E to restart."
        elif state == "win":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            game_surface.blit(overlay, (0, 0))
            status = render_futuristic_text("LEVEL COMPLETE", font_large, (0, 245, 255))
            game_surface.blit(status, (WIDTH // 2 - status.get_width() // 2, 220))
            sub = render_futuristic_text("Press N to continue.", font_medium, (255, 255, 255))
            game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 280))
            status_text = "Level cleared. Press N to continue."
        elif state == "complete":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            game_surface.blit(overlay, (0, 0))
            status = render_futuristic_text("CYBERPUNK VICTORY", font_large, (255, 61, 255))
            game_surface.blit(status, (WIDTH // 2 - status.get_width() // 2, 240))
            sub = render_futuristic_text("You cleared all levels! Close the window to exit.", font_medium, (255, 255, 255))
            game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))
            status_text = "All levels complete."

        if state != "complete":
            status_line = font_small.render(status_text, True, (226, 244, 255))
            game_surface.blit(status_line, (20, HEIGHT - 30))

        screen.fill((10, 10, 28))
        x = (screen_width - WIDTH) // 2
        y = (screen_height - HEIGHT) // 2
        screen.blit(game_surface, (x, y))
        pygame.display.flip()


if __name__ == "__main__":
    main()
