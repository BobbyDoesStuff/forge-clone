import pygame
from consts import *

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, hero_type, number):
        super().__init__()

        self.image = pygame.Surface([SQUARE_SIZE, SQUARE_SIZE])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.type = hero_type
        self.number = number
        # self.font = pygame.font.Font(None, 36)
        # self.text = self.font.render(f'{self.type}{self.number}', True, BLACK)
        self.rect.x = x
        self.rect.y = y

        self.attacked = False  # flag to indicate if the hero has attacked

        self.max_health = 100
        self.health = self.max_health

        self.frames = []  # List to hold each frame of the animation
        self.load_frames()  # Call a method to extract frames
        self.frame_index = 0  # Index of the current frame
        self.image = self.frames[self.frame_index]  # Set the initial image
        self.animation_interval = 100  # 0.5 seconds in milliseconds
        self.last_update_time = pygame.time.get_ticks()  # Current time

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
        # Calculate the position to center the sprite within the hero square
        image_center_x = self.rect.x + (SQUARE_SIZE - self.image.get_width()) // 2
        image_center_y = self.rect.y + (SQUARE_SIZE - self.image.get_height()) // 2

        # Draw the centered image
        screen.blit(self.image, (image_center_x, image_center_y))

        # Draw the text (if you still want to display the text)
        # text_rect = self.text.get_rect(center=(self.rect.x + SQUARE_SIZE / 2, self.rect.y + SQUARE_SIZE / 2))
        # screen.blit(self.text, text_rect)

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.attacked and current_time - self.last_update_time > self.animation_interval:
            self.last_update_time = current_time
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0  # Reset to the first frame after the animation
                self.attacked = False  # Reset attacked flag after the animation ends

        self.image = self.frames[self.frame_index]  # Update the current frame


    def attack(self, enemies):
        # Define attack range based on hero type
        range_ = FRONTLINE_RANGE if self.type == FRONTLINE else BACKLINE_RANGE

        self.attacked = False

        if target := next(
            (
                enemy
                for enemy in enemies
                if enemy.health > 0 and self.is_in_range(enemy, range_)
            ),
            None,
        ):
            target.damage(20)  # Damage amount
            self.attacked = True
            # Print statement for debugging
            print(f"Hero {self.number} attacked Enemy {target.number}")

    def can_attack(self, enemies):
        range_ = FRONTLINE_RANGE if self.type == FRONTLINE else BACKLINE_RANGE
        return any(self.is_in_range(enemy, range_) for enemy in enemies if enemy.health > 0)


    def is_in_range(self, enemy, range_):
        # Calculate horizontal and vertical distance to the enemy
        distance_x = abs(enemy.rect.x - self.rect.x) // SQUARE_SIZE
        distance_y = abs(enemy.rect.y - self.rect.y) // SQUARE_SIZE

        # Check if the enemy is within the square-shaped attack range
        return distance_x <= range_ and distance_y <= range_
