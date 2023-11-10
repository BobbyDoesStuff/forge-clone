import itertools
import random
import pygame
from hero import Hero
from enemy import Enemy
from button import Button
import sys
from consts import *

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
        # Check if diagonal squares are occupied
        up_diag_occupied = self.is_occupied(dest_x, dest_y - SQUARE_SIZE, enemy)
        down_diag_occupied = self.is_occupied(dest_x, dest_y + SQUARE_SIZE, enemy)

        # Move diagonally up if the square is not occupied and within grid bounds
        if not up_diag_occupied and dest_y - SQUARE_SIZE >= 100:
            enemy.rect.y -= SQUARE_SIZE
            enemy.rect.x = dest_x
        elif not down_diag_occupied and dest_y + SQUARE_SIZE < self.grid_height:
            enemy.rect.y += SQUARE_SIZE
            enemy.rect.x = dest_x

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
            hero.attack(self.enemies)

    def update(self):
        self.heroes.update()

        # Check for dead enemies and update gold counter
        for enemy in self.enemies.sprites():
            if enemy.health <= 0:
                if enemy in self.enemies:  # Check if enemy is still in the group before removing and updating gold
                    self.gold += 1  # Increase gold counter
                    self.enemies.remove(enemy)  # Remove dead enemy
                    print(f"enemy {enemy.number} killed")
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


