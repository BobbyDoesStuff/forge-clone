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
        self.all_sprites = pygame.sprite.Group()  # Initialize the all_sprites group

        self.clock = pygame.time.Clock()

        self.heroes = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.turn_count = 0
        for hero in self.heroes:
            self.all_sprites.add(hero)
        for enemy in self.enemies:
            self.all_sprites.add(enemy)

        self.dragging = False
        self.selected_hero = None
        self.gold = 0
        self.targeted_enemy = None
        self.create_heroes()
        self.create_enemies()

        self.grid_height = GRID_ROWS * SQUARE_SIZE
        self.grid_width = GRID_COLS * SQUARE_SIZE
        
        # Initialize the screen
        self.screen = pygame.display.set_mode((self.grid_width, SCREEN_HEIGHT))
        self.bg_image = pygame.image.load("assets/Desert-Game-Background-midjourney-prompt.jpg").convert()
        self.total_grid_width = (GRID_COLS + 2) * SQUARE_SIZE
        self.bg_image = pygame.transform.scale(self.bg_image, (self.total_grid_width, GRID_ROWS * SQUARE_SIZE))
        self.bg_x = 0 #starting coordinate of the background image
        self.bg_x2 = self.total_grid_width  # Position of the second background image



        # Create button
        self.button = Button(SCREEN_WIDTH - BUTTON_WIDTH, SCREEN_HEIGHT - BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, 'Move')
        self.button_group = pygame.sprite.GroupSingle(self.button)
        self.button_active = True

        self.action_queue = []
        self.initialize_action_queue()
        self.action_delay = 500  # Delay in milliseconds (0.5 seconds)
        self.last_action_time = pygame.time.get_ticks()

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

    def handle_hero_merging(self, hero):
        adjacent_heroes = self.get_adjacent_heroes_of_same_type(hero)
        if len(adjacent_heroes) >= 2:
            self.merge_heroes(hero, adjacent_heroes)
            return True  # Indicate that merging occurred
        return False  # Indicate that no merging occurred

    def get_adjacent_heroes_of_same_type(self, hero):
        return [
            other_hero
            for other_hero in self.heroes
            if other_hero.type == hero.type
            and other_hero != hero
            and self.are_adjacent(hero, other_hero)
        ]

    def are_adjacent(self, hero1, hero2):
        return (abs(hero1.rect.x - hero2.rect.x) <= SQUARE_SIZE and hero1.rect.y == hero2.rect.y) or \
               (abs(hero1.rect.y - hero2.rect.y) <= SQUARE_SIZE and hero1.rect.x == hero2.rect.x)

    def merge_heroes(self, hero, adjacent_heroes):
        # Merge heroes and create a new, more powerful hero
        new_x, new_y = hero.rect.x, hero.rect.y  # Position for the new hero
        new_tier = hero.tier + 1  # Increase the tier
        for h in adjacent_heroes + [hero]:
            self.heroes.remove(h)
            self.all_sprites.remove(h)
        new_hero = Hero(new_x, new_y, hero.type, number=1, tier=new_tier)
        self.heroes.add(new_hero)
        self.all_sprites.add(new_hero)

    def snap_hero_to_grid(self, hero):
        # Calculate the grid cell coordinates
        grid_x = round(hero.rect.x / SQUARE_SIZE) * SQUARE_SIZE
        grid_y = round(hero.rect.y / SQUARE_SIZE) * SQUARE_SIZE

        # Check if within hero grid bounds
        if 0 <= grid_x < 2 * SQUARE_SIZE and 100 <= grid_y < 600:
            if target_hero := next(
                (
                    other_hero
                    for other_hero in self.heroes
                    if other_hero != hero
                    and other_hero.rect.x == grid_x
                    and other_hero.rect.y == grid_y
                ),
                None,
            ):
                # Swap positions with the target hero
                hero.rect.x, target_hero.rect.x = target_hero.rect.x, self.start_x
                hero.rect.y, target_hero.rect.y = target_hero.rect.y, self.start_y
            else:
                # Move the hero to the grid cell if no hero to swap with
                hero.rect.x = grid_x
                hero.rect.y = grid_y
        else:
            # Snap back to the original position if outside bounds
            hero.rect.x = self.start_x
            hero.rect.y = self.start_y
    
    def get_merge_group(self, hero):
        """Find all heroes that form a merge group with the given hero."""
        merge_group = set()
        to_check = [hero]

        while to_check:
            current_hero = to_check.pop()
            merge_group.add(current_hero)

            for other_hero in self.heroes:
                if other_hero.type == hero.type and other_hero not in merge_group and self.are_adjacent(current_hero, other_hero):
                    to_check.append(other_hero)

        return merge_group if len(merge_group) >= 3 else set()


    def handle_hero_merging(self, hero):
        """Handle merging of heroes."""
        if merge_group := self.get_merge_group(hero):
            self.merge_heroes(merge_group)

    def merge_heroes(self, merge_group):
        """Merge the heroes in the merge group."""
        # You can choose any hero's position for the new merged hero
        new_x, new_y = next(iter(merge_group)).rect.x, next(iter(merge_group)).rect.y
        new_tier = next(iter(merge_group)).tier + 1

        for hero in merge_group:
            self.heroes.remove(hero)
            # If using all_sprites, also remove from there
            # self.all_sprites.remove(hero)

        new_hero = Hero(new_x, new_y, next(iter(merge_group)).type, number=1, tier=new_tier)
        self.heroes.add(new_hero)
        # If using all_sprites, also add to there
        # self.all_sprites.add(new_hero)

    def check_for_merge_highlight(self, dragged_hero):
        """Check and apply highlight to heroes that can be merged."""
        if merge_group := self.get_merge_group(dragged_hero):
            for hero in merge_group:
                hero.highlight()
        else:
            # Reset highlight if conditions are not met
            self.reset_all_heroes_background()

    def reset_all_heroes_background(self):
        """Reset background of all heroes."""
        for hero in self.heroes:
            hero.reset_background() #test

    def run(self):
        while True:
            self.handle_events()
            self.process_actions()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_button_up(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

    def handle_mouse_button_down(self, event):
        if event.button == 1:  # Left mouse button
            if self.button.rect.collidepoint(event.pos) and self.button_active:
                self.next_turn()
            elif clicked_enemy := self.get_clicked_enemy(event.pos):
                self.set_target(clicked_enemy)
            else:
                self.start_dragging_hero(event)

    def get_clicked_enemy(self, pos):
        return next(
            (enemy for enemy in self.enemies if enemy.rect.collidepoint(pos)), None
        )

    def set_target(self, enemy):
        if self.targeted_enemy:
            self.targeted_enemy.untarget()
        self.targeted_enemy = enemy
        enemy.target()

    def handle_mouse_button_up(self, event):
        if event.button == 1 and self.dragging:
            self.finish_dragging_hero()

    def handle_mouse_motion(self, event):
        if self.dragging:
            self.drag_hero(event)

    def start_dragging_hero(self, event):
        for hero in self.heroes:
            if hero.rect.collidepoint(event.pos):
                self.dragging = True
                self.selected_hero = hero
                self.start_x = hero.rect.x
                self.start_y = hero.rect.y
                break

    def finish_dragging_hero(self):
        self.snap_hero_to_grid(self.selected_hero)
        self.handle_hero_merging(self.selected_hero)
        self.reset_all_heroes_background()
        self.dragging = False

    def drag_hero(self, event):
        self.selected_hero.rect.x = event.pos[0] - SQUARE_SIZE // 2
        self.selected_hero.rect.y = event.pos[1] - SQUARE_SIZE // 2
        self.check_for_merge_highlight(self.selected_hero)

    def process_actions(self):
        current_time = pygame.time.get_ticks()
        if self.action_queue and current_time - self.last_action_time > self.action_delay:
            self.last_action_time = current_time
            hero = self.action_queue.pop(0)
            self.process_hero_turn(hero)

            # If the attack queue is empty, re-enable the button
            if not self.action_queue and not self.button_active:
                self.button_active = True
                self.button.set_color(BLACK)

    def initialize_action_queue(self):
        # Clear the queue and add all sprites in their turn order
        self.action_queue.clear()
        #self.action_queue.extend(self.enemies.sprites())
        self.action_queue.extend(self.heroes.sprites())

    def next_turn(self):
        self.spawn_enemies()
        # Check if any enemy is in the first column
        enemy_in_first_col = any(enemy.rect.x == 2 * SQUARE_SIZE for enemy in self.enemies)

        if not enemy_in_first_col:
            self.bg_x -= SQUARE_SIZE
            self.bg_x2 -= SQUARE_SIZE

            # Reset the position of the first image if it moves out of the screen
            if self.bg_x <= -self.total_grid_width:
                self.bg_x = self.bg_x2 + self.total_grid_width

            # Reset the position of the second image if it moves out of the screen
            if self.bg_x2 <= -self.total_grid_width:
                self.bg_x2 = self.bg_x + self.total_grid_width

        self.turn_count += 1
        self.initialize_action_queue()
        will_attack = False
        self.process_enemy_turn()
        for hero in self.heroes:
            hero.attacked = False
            if hero.can_attack(self.enemies):  # Check if the hero can attack
                will_attack = True

        if will_attack:
            # Disable the button only if there will be attacks
            self.button_active = False
            self.button.set_color(GREY)

    def process_enemy_turn(self):
        for enemy in self.enemies:
            if not self.should_block_move(enemy):
                self.move_enemy(enemy)

    def process_hero_turn(self, hero):
        if self.targeted_enemy:
            if self.targeted_enemy.health <= 0 or self.targeted_enemy not in self.enemies:
                self.targeted_enemy = None  # Clear the target if it's dead or removed
            elif hero.can_attack_target(self.targeted_enemy):
                hero.attack_target(self.targeted_enemy)
                return
        
        # If no valid target, fall back to normal attack
        hero.attack(self.enemies)

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
        #self.enemies.update()

        # Check for dead enemies and update gold counter
        for enemy in self.enemies.copy():  # Use a copy to safely modify during iteration
            if enemy.health <= 0:
                self.gold += 1  # Increment gold counter
                self.enemies.remove(enemy)  # Remove from the group
                if enemy == self.targeted_enemy:
                    self.targeted_enemy = None  # Clear the target if it's killed
                print(f"Enemy {enemy.number} killed. Gold: {self.gold}")
            else:
                enemy.update()

    def draw(self):
        self.screen.fill(WHITE)

        # Draw the background image
        bg_rect = self.bg_image.get_rect()
        bg_rect.topleft = (2 * SQUARE_SIZE, 100)  # Adjust the position as needed
        self.screen.blit(self.bg_image, bg_rect)
        #pygame.draw.rect(self.screen, GREEN, (0, 100, 2 * SQUARE_SIZE, 5 * SQUARE_SIZE))
        pygame.draw.rect(self.screen, BLACK, (0, 100, 2 * SQUARE_SIZE, 5 * SQUARE_SIZE), 3)
        self.screen.blit(self.bg_image, (self.bg_x, 100))
        self.screen.blit(self.bg_image, (self.bg_x2, 100))


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


