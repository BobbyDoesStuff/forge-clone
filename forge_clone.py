import itertools
import random
import pygame
import sys

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (200, 200, 200)  # A light grey color


# Screen dimensions
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 700  # Updated screen height to include white space

# Grid dimensions
GRID_ROWS = 5
GRID_COLS = 15
SQUARE_SIZE = 100

# Button dimensions
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

# Hero classes
FRONTLINE = 'F'
BACKLINE = 'B'

# Enemy class
ENEMY = 'E'
enemy_spawn_counter = 1

# Range of attack for backline and frontline heroes
BACKLINE_RANGE = 3
FRONTLINE_RANGE = 1

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, hero_type, number):
        super().__init__()

        self.image = pygame.Surface([SQUARE_SIZE, SQUARE_SIZE])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.type = hero_type
        self.number = number
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render(f'{self.type}{self.number}', True, BLACK)
        self.rect.x = x
        self.rect.y = y

        self.attacked = False  # flag to indicate if the hero has attacked

        self.max_health = 100
        self.health = self.max_health

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        text_rect = self.text.get_rect(center=(self.rect.x + SQUARE_SIZE / 2, self.rect.y + SQUARE_SIZE / 2))
        screen.blit(self.text, text_rect)

    def update(self):
        pass

    def attack(self, enemy):
        if not self.attacked:
            enemy.damage(20)  # Damage amount
            self.attacked = True

class Enemy(pygame.sprite.Sprite):
    enemy_count = 0

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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption("Battle Stage")

        self.clock = pygame.time.Clock()

        self.heroes = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.turn_count = 0

        self.dragging = False
        self.selected_hero = None
        self.gold = 0
        self.create_heroes()
        self.create_enemies()

        self.grid_height = GRID_ROWS * SQUARE_SIZE
        self.grid_width = GRID_COLS * SQUARE_SIZE
        
        # Initialize the screen
        self.screen = pygame.display.set_mode((self.grid_width, SCREEN_HEIGHT))

        # Create button
        self.button = Button(SCREEN_WIDTH - BUTTON_WIDTH, SCREEN_HEIGHT - BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, 'Move')
        self.button_group = pygame.sprite.GroupSingle(self.button)

    def create_heroes(self):
        for row, col in itertools.product(range(GRID_ROWS), range(2)):
            x = col * SQUARE_SIZE
            y = 100 + row * SQUARE_SIZE  # Added white space

            if col == 0 and row < 2:
                hero = Hero(x, y, FRONTLINE, row + 1)
                self.heroes.add(hero)
            elif col == 1 and row < 3:
                hero = Hero(x, y, BACKLINE, row + 1)
                self.heroes.add(hero)

    def create_enemies(self):
        enemy = Enemy(7 * SQUARE_SIZE, 2 * SQUARE_SIZE + 100)  # Added white space
        self.enemies.add(enemy)

    def draw_health_bar(self, x, y, health, max_health):
        length = SQUARE_SIZE
        move = max_health / length
        bar_length = int(health / move)
        pygame.draw.rect(self.screen, GREY, (x, y, length, 5))  # Grey background for missing health
        pygame.draw.rect(self.screen, (0, 128, 0), (x, y, bar_length, 5))  # Dark green bar for remaining health
        pygame.draw.rect(self.screen, BLACK, (x, y, length, 5), 1)  # Black border



    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.button.rect.collidepoint(event.pos):
                            self.next_turn()
                        else:
                            for hero in self.heroes:
                                if hero.rect.collidepoint(event.pos):
                                    self.dragging = True
                                    self.selected_hero = hero
                                    self.start_x = hero.rect.x  # store starting position
                                    self.start_y = hero.rect.y
                                    break

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging:
                        self.dragging = False
                        # Snap to nearest grid cell
                        grid_x = round(self.selected_hero.rect.x / SQUARE_SIZE) * SQUARE_SIZE
                        grid_y = round(self.selected_hero.rect.y / SQUARE_SIZE) * SQUARE_SIZE
                        if grid_x < 2 * SQUARE_SIZE and 100 <= grid_y < 600:  # Updated grid_y condition
                            self.selected_hero.rect.x = grid_x
                            self.selected_hero.rect.y = grid_y
                            # Check for hero at the new position
                            for hero in self.heroes:
                                if hero != self.selected_hero and hero.rect.collidepoint(grid_x, grid_y):
                                    # Swap positions
                                    hero.rect.x = self.start_x
                                    hero.rect.y = self.start_y

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.selected_hero.rect.x = event.pos[0] - SQUARE_SIZE / 2
                        self.selected_hero.rect.y = event.pos[1] - SQUARE_SIZE / 2

            self.update()
            self.draw()

    def next_turn(self):
        self.spawn_enemies()
        self.turn_count += 1

        for hero in self.heroes:
            hero.attacked = False

        for enemy in self.enemies:
            if not self.should_block_move(enemy):
                self.move_enemy(enemy)

        self.attack_enemies()
        self.update()
        self.draw()

    def should_block_move(self, enemy):
        return any(
            enemy.rect.x - hero.rect.x == SQUARE_SIZE
            and enemy.rect.y == hero.rect.y
            for hero in self.heroes
        )

    def move_enemy(self, enemy):
        dest_x = enemy.rect.x - SQUARE_SIZE
        if 2 * SQUARE_SIZE <= dest_x < self.grid_width:
            dest_y = enemy.rect.y

            if not self.is_occupied(dest_x, dest_y, enemy):
                enemy.rect.x = dest_x
            else:
                self.move_diagonally(enemy, dest_x, dest_y)

    def is_occupied(self, x, y, enemy):
        return any(
            e.rect.x == x and e.rect.y == y
            for e in self.enemies if e != enemy
        )

    def move_diagonally(self, enemy, dest_x, dest_y):
        up_diag_occupied = self.is_occupied(dest_x + SQUARE_SIZE, dest_y - SQUARE_SIZE, enemy)
        down_diag_occupied = self.is_occupied(dest_x + SQUARE_SIZE, dest_y + SQUARE_SIZE, enemy)

        if dest_y - SQUARE_SIZE >= 100 and not up_diag_occupied:
            enemy.rect.x = dest_x
            enemy.rect.y = dest_y - SQUARE_SIZE
        elif dest_y + SQUARE_SIZE < self.grid_height and not down_diag_occupied:
            enemy.rect.x = dest_x
            enemy.rect.y = dest_y + SQUARE_SIZE
        elif dest_y == 100 and not down_diag_occupied:
            enemy.rect.x = dest_x
            enemy.rect.y = dest_y + SQUARE_SIZE
        elif dest_y == self.grid_height - SQUARE_SIZE and not up_diag_occupied:
            enemy.rect.x = dest_x
            enemy.rect.y = dest_y - SQUARE_SIZE

    def spawn_enemies(self):

        if self.turn_count % 2 == 0:
            global enemy_spawn_counter
            enemy_spawn_counter += 2
            print(f"Enemy spawned! Count: {enemy_spawn_counter}")
            print(f"Enemies alive: {enemy_spawn_counter - self.gold}")
            for _ in range(2):
                enemy = Enemy(SCREEN_WIDTH - SQUARE_SIZE, random.randint(1, 5) * SQUARE_SIZE + 100 - SQUARE_SIZE)
                self.enemies.add(enemy)

    def attack_enemies(self):
        for hero in self.heroes:
            range_ = FRONTLINE_RANGE if hero.type == FRONTLINE else BACKLINE_RANGE
            for enemy in self.enemies:
                distance = abs(enemy.rect.x - hero.rect.x) / SQUARE_SIZE
                if distance <= range_ and abs(enemy.rect.y - hero.rect.y) <= range_ * SQUARE_SIZE:
                    hero.attack(enemy)

    def update(self):
        self.heroes.update()

        # Check for dead enemies and update gold counter
        for enemy in self.enemies.sprites():
            if enemy.health <= 0:
                if enemy in self.enemies:  # Check if enemy is still in the group before removing and updating gold
                    self.gold += 1  # Increase gold counter
                    self.enemies.remove(enemy)  # Remove dead enemy
            else:
                enemy.update()

    def draw(self):
        self.screen.fill(WHITE)

        pygame.draw.rect(self.screen, GREEN, (0, 100, 2 * SQUARE_SIZE, 5 * SQUARE_SIZE))
        pygame.draw.rect(self.screen, BLACK, (0, 100, 2 * SQUARE_SIZE, 5 * SQUARE_SIZE), 3)  

        for x in range(SQUARE_SIZE, 2 * SQUARE_SIZE, SQUARE_SIZE):
            pygame.draw.line(self.screen, BLACK, (x, 100), (x, 600), 1)
        for y in range(200, 600, SQUARE_SIZE):
            pygame.draw.line(self.screen, BLACK, (0, y), (2 * SQUARE_SIZE, y), 1)

        for x in range(2 * SQUARE_SIZE, SCREEN_WIDTH, SQUARE_SIZE):
            pygame.draw.line(self.screen, BLACK, (x, 100), (x, 600), 1)
        for y in range(200, 600, SQUARE_SIZE):
            pygame.draw.line(self.screen, BLACK, (2 * SQUARE_SIZE, y), (SCREEN_WIDTH, y), 1)

        # Draw the upper and bottom lines of the enemy grid
        pygame.draw.line(self.screen, BLACK, (2 * SQUARE_SIZE, 100), (SCREEN_WIDTH, 100), 1)
        pygame.draw.line(self.screen, BLACK, (2 * SQUARE_SIZE, 600), (SCREEN_WIDTH, 600), 1)

        # Draw sequential numbers for enemy grid
        font = pygame.font.Font(None, 24)
        for number, (row, col) in enumerate(itertools.product(range(GRID_ROWS), range(2, GRID_COLS)), start=1):
            text = font.render(str(number), True, BLACK)
            x = col * SQUARE_SIZE + SQUARE_SIZE / 2 - text.get_width() / 2
            y = 100 + row * SQUARE_SIZE + SQUARE_SIZE / 2 - text.get_height() / 2
            self.screen.blit(text, (x, y))
        for hero in self.heroes:
            hero.draw(self.screen)
            self.draw_health_bar(hero.rect.x, hero.rect.y, hero.health, hero.max_health)

        for enemy in self.enemies.sprites():  # Get a list of all sprites in the group
            if enemy.health <= 0:
                self.enemies.remove(enemy)  # Remove dead enemy
            else:
                enemy.draw(self.screen)
                self.draw_health_bar(enemy.rect.x, enemy.rect.y, enemy.health, enemy.max_health)

        self.button.draw(self.screen)

        font = pygame.font.Font(None, 36)
        text = font.render(f"Gold: {self.gold}", True, BLACK)
        self.screen.blit(text, (SCREEN_WIDTH - 150, 50))  # Adjust position as needed

        pygame.display.flip()
        self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
