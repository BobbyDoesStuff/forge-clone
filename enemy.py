import pygame
from consts import *

class Enemy(pygame.sprite.Sprite):
    enemy_count = 1

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.health = 100
        self.max_health = 100

        self.number = Enemy.enemy_count
        Enemy.enemy_count += 1

        # Set up font
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render(str(self.number), True, (0, 0, 0))
        self.text_rect = self.text.get_rect(center=(SQUARE_SIZE / 2, SQUARE_SIZE / 2))

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))
        window.blit(self.text, (self.rect.x + self.text_rect.x, self.rect.y + self.text_rect.y))

    def update(self):
        if self.health <= 0:
            print(f"Enemy {self.number} died.")
            self.kill()

    def damage(self, amount):
        self.health -= amount
        print(f"{self.number}'s remaining health:{self.health}")
        self.health = max(self.health, 0)
