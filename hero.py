import pygame
from consts import *

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, hero_type, number, tier=1):
        super().__init__()

        self.tier = tier
        self.max_health = 100 + 20 * (self.tier - 1)
        self.attack_power = 20 + 20 * (self.tier - 1)

        self.image = pygame.Surface([SQUARE_SIZE, SQUARE_SIZE])
        self.image.fill(WHITE)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()

        self.type = hero_type
        self.number = number
        self.rect.x = x
        self.rect.y = y

        self.attacked = False
        self.health = self.max_health

        self.frames = []
        self.load_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animation_interval = 100
        self.last_update_time = pygame.time.get_ticks()

    def load_frames(self):
        if self.type == FRONTLINE:    
            frame_files = [
                'assets/Player_Attack_R.png',
                'assets/Player_Attack2_R.png',
                'assets/Player_Attack3_R.png',
                'assets/Player_Attack4_R.png',
                'assets/Player_Attack5_R.png'
            ]
        elif self.type == BACKLINE:
            frame_files = [
                'assets/tile000.png',
                'assets/tile001.png',
                'assets/tile002.png',
                'assets/tile003.png',
                'assets/tile004.png',
                'assets/tile005.png',
            ]

        for file_path in frame_files:
            frame_image = pygame.image.load(file_path).convert_alpha()
            self.frames.append(frame_image)

    def draw(self, screen):
        image_center_x = self.rect.x + (SQUARE_SIZE - self.image.get_width()) // 2
        image_center_y = self.rect.y + (SQUARE_SIZE - self.image.get_height()) // 2
        screen.blit(self.image, (image_center_x, image_center_y))

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.attacked and current_time - self.last_update_time > self.animation_interval:
            self.last_update_time = current_time
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
                self.attacked = False

        self.image = self.frames[self.frame_index]

    def attack(self, enemies):
        self.attacked = False
        if target := self.find_target(enemies):
            self.perform_attack(target)

    def find_target(self, enemies):
        return next(
            (
                enemy
                for enemy in enemies
                if enemy.health > 0 and self.is_in_range(enemy, self.get_attack_range())
            ),
            None,
        )

    def perform_attack(self, target):
        if target and target.health > 0:  # Check if target is valid and alive
            target.damage(self.attack_power)
            self.attacked = True
            print(f"Tier {self.tier} Hero {self.number} attacked Enemy {target.number}")
        else:
            print(f"Tier {self.tier} Hero {self.number} couldn't find a valid target to attack")

    def attack_target(self, target):
        if self.can_attack_target(target) and target.health > 0:
            self.perform_attack(target)
        else:
            self.attack(self.enemies)  # Fall back to normal attack if target is invalid or dead

    def can_attack(self, enemies):
        range_ = self.get_attack_range()
        return any(self.is_in_range(enemy, range_) for enemy in enemies if enemy.health > 0)

    def get_attack_range(self):
        return FRONTLINE_RANGE if self.type == FRONTLINE else BACKLINE_RANGE

    def is_in_range(self, enemy, range_):
        distance_x = abs(enemy.rect.x - self.rect.x) // SQUARE_SIZE
        distance_y = abs(enemy.rect.y - self.rect.y) // SQUARE_SIZE
        return distance_x <= range_ and distance_y <= range_

    def highlight(self):
        if not hasattr(self, 'original_image'):
            self.original_image = self.image.copy()

        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                color = self.image.get_at((x, y))
                if color.a != 0:
                    self.image.set_at((x, y), (color.r, color.g, color.b, 156))

    def reset_background(self):
        if hasattr(self, 'original_image'):
            self.image = self.original_image.copy()

    def can_attack_target(self, target):
        return self.is_in_range(target, self.get_attack_range())
