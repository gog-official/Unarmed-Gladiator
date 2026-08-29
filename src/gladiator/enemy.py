import pygame
import random
from .settings import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPRITES_PATH,
    WORLD_WIDTH,
    WORLD_HEIGHT,
)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_reference, spawn_points_list):
        self.rect = pygame.Rect(0, 0, 0, 0)
        super().__init__()

        self.player = player_reference
        self.spawn_points = spawn_points_list
        base_path = SPRITES_PATH
        paths = {
            "idle": {
                "north": [
                    f"{base_path}/Idle/Variant_1/Idle_North_frame_{i}.png"
                    for i in range(4)
                ],
                "south": [
                    f"{base_path}/Idle/Variant_1/Idle_South_frame_{i}.png"
                    for i in range(4)
                ],
                "east": [
                    f"{base_path}/Idle/Variant_1/Idle_East_frame_{i}.png"
                    for i in range(4)
                ],
                "west": [
                    f"{base_path}/Idle/Variant_1/Idle_West_frame_{i}.png"
                    for i in range(4)
                ],
            },
            "walk": {
                "north": [
                    f"{base_path}/Walk/Variant_1/Walk_North_frame_{i}.png"
                    for i in range(4)
                ],
                "south": [
                    f"{base_path}/Walk/Variant_1/Walk_South_frame_{i}.png"
                    for i in range(4)
                ],
                "east": [
                    f"{base_path}/Walk/Variant_1/Walk_East_frame_{i}.png"
                    for i in range(4)
                ],
                "west": [
                    f"{base_path}/Walk/Variant_1/Walk_West_frame_{i}.png"
                    for i in range(4)
                ],
            },
            "run": {
                "north": [
                    f"{base_path}/Run/Variant_1/Run_North_frame_{i}.png"
                    for i in range(4)
                ],
                "south": [
                    f"{base_path}/Run/Variant_1/Run_South_frame_{i}.png"
                    for i in range(4)
                ],
                "east": [
                    f"{base_path}/Run/Variant_1/Run_East_frame_{i}.png"
                    for i in range(4)
                ],
                "west": [
                    f"{base_path}/Run/Variant_1/Run_West_frame_{i}.png"
                    for i in range(4)
                ],
            },
            "jump": {
                "north": [f"{base_path}/Jump/Variant_1/Jump_North_frame_0.png"],
                "south": [f"{base_path}/Jump/Variant_1/Jump_South_frame_0.png"],
                "east": [f"{base_path}/Jump/Variant_1/Jump_East_frame_0.png"],
                "west": [f"{base_path}/Jump/Variant_1/Jump_West_frame_0.png"],
            },
            "attack": {
                "north": [f"{base_path}/Attack/Variant_1/Attack_North_frame_0.png"],
                "south": [f"{base_path}/Attack/Variant_1/Attack_South_frame_0.png"],
                "east": [f"{base_path}/Attack/Variant_1/Attack_East_frame_0.png"],
                "west": [f"{base_path}/Attack/Variant_1/Attack_West_frame_0.png"],
            },
            "hurt": {
                "north": [f"{base_path}/Hurt/Variant_1/Hurt_North_frame_0.png"],
                "south": [f"{base_path}/Hurt/Variant_1/Hurt_South_frame_0.png"],
                "east": [f"{base_path}/Hurt/Variant_1/Hurt_East_frame_0.png"],
                "west": [f"{base_path}/Hurt/Variant_1/Hurt_West_frame_0.png"],
            },
        }

        self.animations = {}
        for state in paths:
            self.animations[state] = {}
            for direction in paths[state]:
                self.animations[state][direction] = [
                    pygame.transform.scale_by(pygame.image.load(p).convert_alpha(), 1)
                    for p in paths[state][direction]
                ]

        self.state = "idle"
        self.direction = "south"
        self.frame_index = 0.0
        self.animation_speed = 0.15
        self.speed = 1.0

        self.image = self.animations[self.state][self.direction][0]
        self.rect = self.image.get_rect()

        self.max_health = 100
        self.health = 100
        self.is_punching = False
        self.attack_cooldown = 0
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        self.hitstun_timer = 0
        self.is_dead = False
        self.corpse_timer = 7200

        self.respawn()

    def respawn(self):
        import random

        spn_x, spn_y = random.choice(self.spawn_points)

        self.rect = self.animations["idle"]["south"][0].get_rect()

        self.pos_x = float(spn_x)
        self.pos_y = float(spn_y)

        self.rect.x = round(self.pos_x)
        self.rect.y = round(self.pos_y)

        self.health = 100
        self.is_dead = False
        self.corpse_timer = 7200

    def update(self):
        old_state = self.state
        old_direction = self.direction

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.pos_x += self.knockback_x
        self.pos_y += self.knockback_y
        self.knockback_x *= 0.82
        self.knockback_y *= 0.82

        if self.is_dead:
            self.state = "idle"
            base_surface = self.animations["idle"][self.direction][0]
            self.image = pygame.transform.rotate(base_surface, 90)

            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

            self.corpse_timer -= 1
            if self.corpse_timer <= 0:
                self.respawn()
                return
            return

        if self.hitstun_timer > 0:
            self.hitstun_timer -= 1
            self.state = "hurt"
        elif self.is_punching:
            self.state = "attack"
        else:
            dx = self.player.pos_x - self.pos_x
            dy = self.player.pos_y - self.pos_y
            distance = pygame.math.Vector2(dx, dy).length()

            if distance < 18 and self.attack_cooldown == 0:
                self.is_punching = True
                self.state = "attack"
                self.frame_index = 0.0
            elif distance > 0:
                self.state = "walk"

                step_x = 0.0
                step_y = 0.0

                if abs(dx) > 0.5:
                    step_x = self.speed if dx > 0 else -self.speed
                if abs(dy) > 0.5:
                    step_y = self.speed if dy > 0 else -self.speed

                if abs(dx) > 1.0 and abs(dy) > 1.0:
                    step_x *= 0.7071
                    step_y *= 0.7071

                self.pos_x += step_x
                self.pos_y += step_y

                if abs(dx) > abs(dy) + 4:
                    self.direction = "east" if dx > 0 else "west"
                elif abs(dy) > abs(dx) + 4:
                    self.direction = "south" if dy > 0 else "north"
            else:
                self.state = "idle"

        self.pos_x = max(0.0, min(self.pos_x, float(WORLD_WIDTH - self.rect.width)))
        self.pos_y = max(0.0, min(self.pos_y, float(WORLD_HEIGHT - self.rect.height)))

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        if self.state != old_state or self.direction != old_direction:
            self.frame_index = 0.0

        current_animation_list = self.animations[self.state][self.direction]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(current_animation_list):
            if self.state == "attack":
                self.is_punching = False
                self.state = "idle"
                self.frame_index = 0.0
                self.attack_cooldown = 69
                current_animation_list = self.animations[self.state][self.direction]
            else:
                self.frame_index = 0.0
        self.image = current_animation_list[int(self.frame_index)]

    def draw_health_bar(self, surface):
        if self.health <= 0:
            return
        bar_width = 20
        bar_height = 4

        bar_x = self.rect.centerx - (bar_width // 2)
        bar_y = self.rect.top - 8

        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(
            surface,
            (0, 255, 0),
            (bar_x, bar_y, int(bar_width * health_ratio), bar_height),
        )