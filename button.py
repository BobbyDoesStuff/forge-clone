import pygame
from consts import *

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render(text, True, WHITE)
        text_rect = self.text.get_rect(center=(width / 2, height / 2))
        self.image.blit(self.text, text_rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_color(self, color):
        self.image.fill(color)
        # Redraw the text over the new background color
        text_surface = self.font.render("Move", True, WHITE)  # Replace "Move" with your button text
        text_rect = text_surface.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.blit(text_surface, text_rect)

