import pygame
from .settings import SPRITES_PATH, WORLD_WIDTH, WORLD_HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        super().__init__()

        base_path = SPRITES_PATH

        paths = {
            "idle": {
                "north": [
                    f"{base_path}/Idle/Idle_North_frame_{i}.png" for i in range(4)
                ],
                "south": [
                    f"{base_path}/Idle/Idle_South_frame_{i}.png" for i in range(4)
                ],
                "east": [f"{base_path}/Idle/Idle_East_frame_{i}.png" for i in range(4)],
                "west": [f"{base_path}/Idle/Idle_West_frame_{i}.png" for i in range(4)],
            },
            "walk": {
                "north": [
                    f"{base_path}/Walk/Walk_North_frame_{i}.png" for i in range(4)
                ],
                "south": [
                    f"{base_path}/Walk/Walk_South_frame_{i}.png" for i in range(4)
                ],
                "east": [f"{base_path}/Walk/Walk_East_frame_{i}.png" for i in range(4)],
                "west": [f"{base_path}/Walk/Walk_West_frame_{i}.png" for i in range(4)],
            },
            "jump": {
                "north": [f"{base_path}/Jump/Jump_North_frame_0.png"],
                "south": [f"{base_path}/Jump/Jump_South_frame_0.png"],
                "east": [f"{base_path}/Jump/Jump_East_frame_0.png"],
                "west": [f"{base_path}/Jump/Jump_West_frame_0.png"],
            },
            "attack": {
                "north": [f"{base_path}/Attack/Attack_North_frame_0.png"],
                "south": [f"{base_path}/Attack/Attack_South_frame_0.png"],
                "east": [f"{base_path}/Attack/Attack_East_frame_0.png"],
                "west": [f"{base_path}/Attack/Attack_West_frame_0.png"],
            },
            "run": {
                "north": [f"{base_path}/Run/Run_North_frame_{i}.png" for i in range(4)],
                "south": [f"{base_path}/Run/Run_South_frame_{i}.png" for i in range(4)],
                "east": [f"{base_path}/Run/Run_East_frame_{i}.png" for i in range(4)],
                "west": [f"{base_path}/Run/Run_West_frame_{i}.png" for i in range(4)],
            },
            "hurt": {
                "north": [f"{base_path}/Hurt/Hurt_North_frame_0.png"],
                "south": [f"{base_path}/Hurt/Hurt_South_frame_0.png"],
                "east": [f"{base_path}/Hurt/Hurt_East_frame_0.png"],
                "west": [f"{base_path}/Hurt/Hurt_West_frame_0.png"],
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

        self.image = self.animations[self.state][self.direction][0]
        self.rect = self.image.get_rect()
        self.rect.center = (250, 250)

        self.speed = 2.84
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.ground_y = float(self.rect.y)
        self.velocity_y = 0.00
        self.gravity = 0.45
        self.jumping_power = -6.0
        self.is_jumping = False

        self.is_punching = False
        self.attack_cooldown = 0
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        self.hitstun_timer = 0

        self.max_health = 100
        self.health = 100
        self.enemy_damage_cooldown = 0

        self.has_hit = False

    def update(self):
        keys = pygame.key.get_pressed()
        click = pygame.mouse.get_pressed()

        old_state = self.state
        old_direction = self.direction

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.enemy_damage_cooldown > 0:
            self.enemy_damage_cooldown -= 1

        self.pos_x += self.knockback_x
        self.pos_y += self.knockback_y
        self.knockback_x *= 0.82
        self.knockback_y *= 0.82

        if self.hitstun_timer > 0:
            self.hitstun_timer -= 1
            self.state = "hurt"
        elif self.is_punching:
            self.state = "attack"
        elif self.is_jumping:
            self.state = "jump"
        else:
            self.state = "idle"

            if (
                (click[0] or keys[pygame.K_j])
                and not self.is_jumping
                and self.attack_cooldown == 0
            ):
                self.is_punching = True
                self.frame_index = 0.00
                self.attack_cooldown = 40
                self.state = "attack"

            if not self.is_punching:
                move_speed = self.speed * 1.5 if keys[pygame.K_LSHIFT] else self.speed
                move_state = "run" if keys[pygame.K_LSHIFT] else "walk"

                is_diagonal = (
                    keys[pygame.K_LEFT]
                    or keys[pygame.K_a]
                    or keys[pygame.K_RIGHT]
                    or keys[pygame.K_d]
                ) and (
                    keys[pygame.K_UP]
                    or keys[pygame.K_w]
                    or keys[pygame.K_DOWN]
                    or keys[pygame.K_s]
                )

                if is_diagonal:
                    move_speed *= 0.55

                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.pos_x -= move_speed
                    self.direction = "west"
                    self.state = move_state
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.pos_x += move_speed
                    self.direction = "east"
                    self.state = move_state

                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.direction = "north"
                    self.state = move_state
                    if not self.is_jumping:
                        self.pos_y -= move_speed
                        self.ground_y -= move_speed
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.direction = "south"
                    self.state = move_state
                    if not self.is_jumping:
                        self.pos_y += move_speed
                        self.ground_y += move_speed

                if keys[pygame.K_SPACE] and not self.is_jumping:
                    self.velocity_y = self.jumping_power
                    self.is_jumping = True

        if self.is_jumping:
            self.velocity_y += self.gravity
            self.pos_y += self.velocity_y
            if self.pos_y >= self.ground_y:
                self.pos_y = self.ground_y
                self.velocity_y = 0.00
                if self.state != "hurt":
                    self.state = "idle"
                self.is_jumping = False

        self.pos_x = max(0.0, min(self.pos_x, float(WORLD_WIDTH - self.rect.width)))
        self.pos_y = max(0.0, min(self.pos_y, float(WORLD_HEIGHT - self.rect.height)))

        if not self.is_jumping:
            self.ground_y = self.pos_y

        self.rect.x = round(self.pos_x)
        self.rect.y = round(self.pos_y)

        if self.state != old_state or self.direction != old_direction:
            self.frame_index = 0.0

        current_animation_list = self.animations[self.state][self.direction]
        current_speed = (
            self.animation_speed * 0.9
            if self.state == "attack"
            else self.animation_speed
        )
        self.frame_index += current_speed

        if self.frame_index >= len(current_animation_list):
            if self.state == "attack":
                self.is_punching = False
                self.state = "idle"
                self.frame_index = 0.0
                self.has_hit = False
                current_animation_list = self.animations[self.state][self.direction]
            else:
                self.frame_index = 0.0

        self.image = current_animation_list[int(self.frame_index)]

    def draw_health_bar(self, surface):
        if self.health <= 0:
            return
        bar_width = 160
        bar_height = 18
        hud_x = 20
        hud_y = 20
        pygame.draw.rect(
            surface, (20, 20, 20), (hud_x - 3, hud_y - 3, bar_width + 6, bar_height + 6)
        )
        pygame.draw.rect(surface, (255, 0, 0), (hud_x, hud_y, bar_width, bar_height))
        health_ratio = max(0.0, self.health / self.max_health)
        pygame.draw.rect(
            surface,
            (0, 255, 0),
            (hud_x, hud_y, int(bar_width * health_ratio), bar_height),
        )