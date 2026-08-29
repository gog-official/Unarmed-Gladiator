import pygame
import pytmx
import sys
import random

from .settings import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_COLOR,
    FPS,
    WORLD_WIDTH,
    WORLD_HEIGHT,
    SPRITES_PATH,
)

from .player import Player
from .enemy import Enemy


pygame.init()

screen = pygame.display.set_mode(
    (0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
)

pygame.display.set_caption("Gladiator Arena")

clock = pygame.time.Clock()


GAME_WIDTH = SCREEN_WIDTH
GAME_HEIGHT = SCREEN_HEIGHT

virtual_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))


ZOOM = 3.0

CAMERA_WIDTH = max(1, int(GAME_WIDTH / ZOOM))

CAMERA_HEIGHT = max(1, int(GAME_HEIGHT / ZOOM))

camera_surface = pygame.Surface((CAMERA_WIDTH, CAMERA_HEIGHT))


kill_count = 0
is_game_over = False

shake_intensity = 0
shake_duration = 0


hud_font = pygame.font.Font(None, 24)

PIXEL_FONT_PATH = f"{SPRITES_PATH}/UI/PixelOperator.ttf"

try:
    death_title_font = pygame.font.Font(PIXEL_FONT_PATH, 34)

    death_font = pygame.font.Font(PIXEL_FONT_PATH, 16)

    death_small_font = pygame.font.Font(PIXEL_FONT_PATH, 13)

except:
    death_title_font = pygame.font.Font(None, 34)

    death_font = pygame.font.Font(None, 16)

    death_small_font = pygame.font.Font(None, 13)


DEATH_WIDTH = 320
DEATH_HEIGHT = 180

death_surface = pygame.Surface((DEATH_WIDTH, DEATH_HEIGHT))


player = Player()


all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

all_sprites.add(player)


tmx_file = pytmx.load_pygame(f"{SPRITES_PATH}/Tiles/arena.tmx", pixelalpha=True)

obstacles_rect = []
valid_spawn_points = []


for layer in tmx_file.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            tile_props = tmx_file.get_tile_properties_by_gid(gid)

            if tile_props:
                if tile_props.get("solid") == True:
                    world_x = x * tmx_file.tilewidth

                    world_y = y * tmx_file.tileheight

                    block = pygame.Rect(
                        world_x, world_y, tmx_file.tilewidth, tmx_file.tileheight
                    )

                    obstacles_rect.append(block)

                if tile_props.get("spawn") == True:
                    world_x = x * tmx_file.tilewidth

                    world_y = y * tmx_file.tileheight

                    valid_spawn_points.append((world_x, world_y))


if not valid_spawn_points:
    valid_spawn_points.append((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))


def enforce_wall_physics(sprite):

    if sprite.pos_x < 0:
        sprite.pos_x = 0.0

    elif sprite.pos_x > WORLD_WIDTH - sprite.rect.width:
        sprite.pos_x = float(WORLD_WIDTH - sprite.rect.width)

    if sprite.pos_y < 0:
        sprite.pos_y = 0.0

    elif sprite.pos_y > WORLD_HEIGHT - sprite.rect.height:
        sprite.pos_y = float(WORLD_HEIGHT - sprite.rect.height)

    sprite.rect.x = round(sprite.pos_x)

    sprite.rect.y = round(sprite.pos_y)

    for wall in obstacles_rect:
        if sprite.rect.colliderect(wall):
            overlap_x = min(sprite.rect.right, wall.right) - max(
                sprite.rect.left, wall.left
            )

            overlap_y = min(sprite.rect.bottom, wall.bottom) - max(
                sprite.rect.top, wall.top
            )

            if overlap_x < overlap_y:
                if sprite.rect.centerx < wall.centerx:
                    sprite.pos_x -= overlap_x

                else:
                    sprite.pos_x += overlap_x

            else:
                if sprite.rect.centery < wall.centery:
                    sprite.pos_y -= overlap_y

                else:
                    sprite.pos_y += overlap_y

            sprite.rect.x = round(sprite.pos_x)

            sprite.rect.y = round(sprite.pos_y)


def spawn_new_enemy():

    new_guy = Enemy(player, valid_spawn_points)

    all_sprites.add(new_guy)

    enemy_group.add(new_guy)


def reset_game():

    global kill_count
    global is_game_over
    global shake_intensity
    global shake_duration
    global player

    kill_count = 0

    is_game_over = False

    shake_intensity = 0
    shake_duration = 0

    all_sprites.empty()
    enemy_group.empty()

    player = Player()

    all_sprites.add(player)

    spawn_new_enemy()


def get_camera():

    camera_x = player.rect.centerx - CAMERA_WIDTH // 2

    camera_y = player.rect.centery - CAMERA_HEIGHT // 2

    max_camera_x = max(0, WORLD_WIDTH - CAMERA_WIDTH)

    max_camera_y = max(0, WORLD_HEIGHT - CAMERA_HEIGHT)

    camera_x = max(0, min(camera_x, max_camera_x))

    camera_y = max(0, min(camera_y, max_camera_y))

    return camera_x, camera_y


def draw_hud():

    BORDER_COLOR = (60, 55, 55)

    BG_COLOR = (30, 28, 28)

    TEXT_COLOR = (255, 255, 255)

    BOX_HEIGHT = 28
    LINE_THICK = 4

    hb_x = 55
    hb_y = 20
    hb_w = 180

    pygame.draw.rect(
        virtual_surface,
        BORDER_COLOR,
        (hb_x, hb_y, hb_w, BOX_HEIGHT),
        LINE_THICK,
        border_radius=6,
    )

    pygame.draw.rect(
        virtual_surface,
        BG_COLOR,
        (hb_x + 4, hb_y + 4, hb_w - 8, BOX_HEIGHT - 8),
        border_radius=4,
    )

    health_ratio = max(0.0, min(1.0, player.health / player.max_health))

    if health_ratio > 0:
        fill_w = int((hb_w - 8) * health_ratio)

        pygame.draw.rect(
            virtual_surface,
            (190, 40, 40),
            (hb_x + 4, hb_y + 4, fill_w, BOX_HEIGHT - 8),
            border_radius=2,
        )

    hx = 32
    hy = 32

    pygame.draw.circle(virtual_surface, (230, 45, 45), (hx - 8, hy - 4), 9)

    pygame.draw.circle(virtual_surface, (230, 45, 45), (hx + 4, hy - 4), 9)

    pygame.draw.polygon(
        virtual_surface,
        (230, 45, 45),
        [(hx - 17, hy - 2), (hx + 13, hy - 2), (hx - 2, hy + 13)],
    )

    k_x = 55
    k_y = 54
    k_w = 85

    pygame.draw.rect(
        virtual_surface,
        BORDER_COLOR,
        (k_x, k_y, k_w, BOX_HEIGHT),
        LINE_THICK,
        border_radius=6,
    )

    pygame.draw.rect(
        virtual_surface,
        BG_COLOR,
        (k_x + 4, k_y + 4, k_w - 8, BOX_HEIGHT - 8),
        border_radius=4,
    )

    pygame.draw.circle(virtual_surface, (245, 245, 250), (k_x + 16, k_y + 12), 6)

    pygame.draw.rect(virtual_surface, (245, 245, 250), (k_x + 13, k_y + 15, 6, 5))

    pygame.draw.circle(virtual_surface, BG_COLOR, (k_x + 14, k_y + 12), 1)

    pygame.draw.circle(virtual_surface, BG_COLOR, (k_x + 18, k_y + 12), 1)

    kill_text = hud_font.render(str(kill_count), True, TEXT_COLOR)

    kill_rect = kill_text.get_rect(center=(k_x + 55, k_y + 14))

    virtual_surface.blit(kill_text, kill_rect)

    g_x = 150
    g_y = 54
    g_w = 85

    pygame.draw.rect(
        virtual_surface,
        BORDER_COLOR,
        (g_x, g_y, g_w, BOX_HEIGHT),
        LINE_THICK,
        border_radius=6,
    )

    pygame.draw.rect(
        virtual_surface,
        BG_COLOR,
        (g_x + 4, g_y + 4, g_w - 8, BOX_HEIGHT - 8),
        border_radius=4,
    )

    pygame.draw.circle(virtual_surface, (235, 165, 35), (g_x + 16, g_y + 14), 7)

    pygame.draw.circle(virtual_surface, (255, 220, 60), (g_x + 16, g_y + 14), 4)

    gold_text = hud_font.render("0", True, TEXT_COLOR)

    gold_rect = gold_text.get_rect(center=(g_x + 55, g_y + 14))

    virtual_surface.blit(gold_text, gold_rect)


def draw_world(camera_x, camera_y):

    camera_surface.fill(SCREEN_COLOR)

    for layer in tmx_file.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile_image = tmx_file.get_tile_image_by_gid(gid)

                if tile_image:
                    tile_render_x = x * tmx_file.tilewidth - camera_x

                    tile_render_y = y * tmx_file.tileheight - camera_y

                    camera_surface.blit(
                        tile_image, (int(tile_render_x), int(tile_render_y))
                    )

    for sprite in all_sprites:
        render_x = sprite.rect.x - camera_x

        render_y = sprite.rect.y - camera_y

        camera_surface.blit(sprite.image, (int(render_x), int(render_y)))

    for target_enemy in enemy_group:
        if target_enemy.health > 0 and not target_enemy.is_dead:
            temp_rect = target_enemy.rect.copy()

            temp_rect.x = target_enemy.rect.x - int(camera_x)

            temp_rect.y = target_enemy.rect.y - int(camera_y)

            actual_rect = target_enemy.rect

            target_enemy.rect = temp_rect

            target_enemy.draw_health_bar(camera_surface)

            target_enemy.rect = actual_rect

    zoomed_world = pygame.transform.scale(camera_surface, (GAME_WIDTH, GAME_HEIGHT))

    virtual_surface.blit(zoomed_world, (0, 0))


respawn_button_rect = None
quit_button_rect = None


def draw_death_screen():

    global respawn_button_rect, quit_button_rect

    BLACK = (5, 5, 5)
    DARK_GREY = (25, 25, 25)

    GREY = (105, 105, 105)
    DARKER_GREY = (75, 75, 75)

    LIGHT_GREY = (185, 185, 185)
    RED = (200, 35, 35)

    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 145))

    virtual_surface.blit(overlay, (0, 0))

    panel_w = 420
    panel_h = 390

    panel_x = (GAME_WIDTH - panel_w) // 2
    panel_y = (GAME_HEIGHT - panel_h) // 2

    pygame.draw.rect(virtual_surface, DARK_GREY, (panel_x, panel_y, panel_w, panel_h))

    pygame.draw.rect(virtual_surface, GREY, (panel_x, panel_y, panel_w, panel_h), 5)

    corner = 8

    pygame.draw.rect(virtual_surface, BLACK, (panel_x, panel_y, corner, corner))

    pygame.draw.rect(
        virtual_surface, BLACK, (panel_x + panel_w - corner, panel_y, corner, corner)
    )

    pygame.draw.rect(
        virtual_surface, BLACK, (panel_x, panel_y + panel_h - corner, corner, corner)
    )

    pygame.draw.rect(
        virtual_surface,
        BLACK,
        (panel_x + panel_w - corner, panel_y + panel_h - corner, corner, corner),
    )

    cx = GAME_WIDTH // 2
    skull_y = panel_y + 65

    pygame.draw.rect(virtual_surface, LIGHT_GREY, (cx - 25, skull_y - 25, 50, 48))

    pygame.draw.rect(virtual_surface, LIGHT_GREY, (cx - 17, skull_y - 32, 34, 8))

    pygame.draw.rect(virtual_surface, LIGHT_GREY, (cx - 17, skull_y + 23, 34, 12))

    pygame.draw.rect(virtual_surface, BLACK, (cx - 15, skull_y - 11, 10, 12))

    pygame.draw.rect(virtual_surface, BLACK, (cx + 5, skull_y - 11, 10, 12))

    pygame.draw.rect(virtual_surface, BLACK, (cx - 4, skull_y + 5, 8, 7))

    for x in range(-13, 14, 7):
        pygame.draw.rect(virtual_surface, BLACK, (cx + x, skull_y + 23, 4, 12))

    death_text = death_title_font.render("YOU DIED", False, RED)

    death_rect = death_text.get_rect(center=(cx, panel_y + 135))

    virtual_surface.blit(death_text, death_rect)

    kills_text = death_font.render(f"KILLS: {kill_count}", False, LIGHT_GREY)

    kills_rect = kills_text.get_rect(center=(cx, panel_y + 185))

    virtual_surface.blit(kills_text, kills_rect)

    def draw_button(y, text):

        button_w = 290
        button_h = 48

        base_rect = pygame.Rect((GAME_WIDTH - button_w) // 2, y, button_w, button_h)

        display_w, display_h = screen.get_size()

        scale = min(display_w / GAME_WIDTH, display_h / GAME_HEIGHT)

        scaled_w = int(GAME_WIDTH * scale)
        scaled_h = int(GAME_HEIGHT * scale)

        screen_x = (display_w - scaled_w) // 2
        screen_y = (display_h - scaled_h) // 2

        mouse_x, mouse_y = pygame.mouse.get_pos()

        virtual_mouse_x = (mouse_x - screen_x) / scale

        virtual_mouse_y = (mouse_y - screen_y) / scale

        mouse_inside = base_rect.collidepoint(virtual_mouse_x, virtual_mouse_y)

        mouse_pressed = pygame.mouse.get_pressed()[0]

        is_pressed = mouse_inside and mouse_pressed

        if is_pressed:
            shrink = 4

            button_rect = pygame.Rect(
                base_rect.x + shrink,
                base_rect.y + shrink,
                base_rect.width - shrink * 2,
                base_rect.height - shrink * 2,
            )

        else:
            button_rect = base_rect.copy()

        if mouse_inside:
            background_color = (15, 15, 15)
            border_color = DARKER_GREY
            text_color = LIGHT_GREY

        else:
            background_color = BLACK
            border_color = GREY
            text_color = LIGHT_GREY

        pygame.draw.rect(virtual_surface, background_color, button_rect)

        pygame.draw.rect(virtual_surface, border_color, button_rect, 4)

        if not is_pressed:
            pygame.draw.rect(
                virtual_surface,
                LIGHT_GREY,
                (button_rect.x + 4, button_rect.y + 4, button_rect.width - 8, 3),
            )

        text_surface = death_small_font.render(text, False, text_color)

        text_rect = text_surface.get_rect(center=button_rect.center)

        virtual_surface.blit(text_surface, text_rect)

        return base_rect

    respawn_button_rect = draw_button(panel_y + 230, "[R] RESPAWN")

    quit_button_rect = draw_button(panel_y + 295, "[Q] QUIT")


spawn_new_enemy()


running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if is_game_over:
                if event.key == pygame.K_r:
                    reset_game()

                elif event.key == pygame.K_q:
                    running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_game_over:
                display_w, display_h = screen.get_size()
                scale = min(display_w / GAME_WIDTH, display_h / GAME_HEIGHT)
                scaled_w = int(GAME_WIDTH * scale)
                scaled_h = int(GAME_HEIGHT * scale)
                screen_x = (display_w - scaled_w) // 2
                screen_y = (display_h - scaled_h) // 2
                mouse_x, mouse_y = event.pos
                virtual_mouse_x = (mouse_x - screen_x) / scale
                virtual_mouse_y = (mouse_y - screen_y) / scale
                if respawn_button_rect and respawn_button_rect.collidepoint(virtual_mouse_x, virtual_mouse_y):
                    reset_game()
                elif quit_button_rect and quit_button_rect.collidepoint(virtual_mouse_x, virtual_mouse_y):
                    running = False

    virtual_surface.fill(SCREEN_COLOR)

    if not is_game_over:
        all_sprites.update()

        enforce_wall_physics(player)

        for runner in enemy_group:
            enforce_wall_physics(runner)

        for individual_enemy in enemy_group:
            if pygame.sprite.collide_rect(player, individual_enemy):
                player_feet = player.pos_y + player.rect.height

                is_above_obstacle = player_feet < individual_enemy.pos_y + 10

                if player.is_jumping and is_above_obstacle:
                    pass

                else:
                    p_center = pygame.math.Vector2(player.rect.center)

                    e_center = pygame.math.Vector2(individual_enemy.rect.center)

                    push_direction = p_center - e_center

                    distance = push_direction.length()

                    min_gap = 24 if individual_enemy.is_dead else 11

                    if 0 < distance < min_gap:
                        push_amount = min_gap - distance

                        push_direction = push_direction.normalize() * push_amount

                        player.pos_x += push_direction.x

                        player.pos_y += push_direction.y

                        player.rect.x = round(player.pos_x)

                        player.rect.y = round(player.pos_y)

        if player.state == "attack" and not player.has_hit:
            hit_list = pygame.sprite.spritecollide(player, enemy_group, False)

            for victim in hit_list:
                if victim.health > 0 and not victim.is_dead:
                    victim.health -= 10

                    player.has_hit = True

                    p_center = pygame.math.Vector2(player.rect.center)

                    e_center = pygame.math.Vector2(victim.rect.center)

                    direction = e_center - p_center

                    if direction.length_squared() > 0:
                        launch_dir = direction.normalize()

                    else:
                        launch_dir = pygame.math.Vector2(1, 0)

                    victim.knockback_x = launch_dir.x * 6.0

                    victim.knockback_y = launch_dir.y * 6.0

                    victim.hitstun_timer = 20

                    pygame.time.delay(65)

                    if victim.health <= 0:
                        victim.is_dead = True

                        kill_count += 1

                        spawn_new_enemy()

        for active_enemy in enemy_group:
            if active_enemy.state == "attack" and not active_enemy.is_dead:
                if pygame.sprite.collide_rect(player, active_enemy):
                    if player.enemy_damage_cooldown == 0:
                        player.health -= 10

                        player.enemy_damage_cooldown = 50

                        p_center = pygame.math.Vector2(player.rect.center)

                        e_center = pygame.math.Vector2(active_enemy.rect.center)

                        direction = p_center - e_center

                        if direction.length_squared() > 0:
                            launch_dir = direction.normalize()

                        else:
                            launch_dir = pygame.math.Vector2(-1, 0)

                        player.knockback_x = launch_dir.x * 10.0

                        player.knockback_y = launch_dir.y * 10.0

                        player.hitstun_timer = 18

                        shake_intensity = 3
                        shake_duration = 14

                        pygame.time.delay(65)

                        if player.health <= 0:
                            is_game_over = True

    camera_x, camera_y = get_camera()

    offset_x = 0
    offset_y = 0

    if shake_duration > 0:
        offset_x = random.randint(-shake_intensity, shake_intensity)

        offset_y = random.randint(-shake_intensity, shake_intensity)

        shake_duration -= 1

    draw_world(camera_x - offset_x, camera_y - offset_y)

    if player.hitstun_timer > 0:
        red_flash = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        red_flash.fill((255, 0, 0))

        red_flash.set_alpha(55)

        virtual_surface.blit(red_flash, (0, 0))

    if not is_game_over:
        draw_hud()

    else:
        draw_death_screen()

    display_width, display_height = screen.get_size()

    scale = min(display_width / GAME_WIDTH, display_height / GAME_HEIGHT)

    scaled_width = int(GAME_WIDTH * scale)

    scaled_height = int(GAME_HEIGHT * scale)

    scaled_view = pygame.transform.scale(virtual_surface, (scaled_width, scaled_height))

    screen.fill((0, 0, 0))

    screen_x = (display_width - scaled_width) // 2

    screen_y = (display_height - scaled_height) // 2

    screen.blit(scaled_view, (screen_x, screen_y))

    pygame.display.flip()


pygame.quit()
sys.exit()