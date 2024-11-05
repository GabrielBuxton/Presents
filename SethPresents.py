import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)  # Dark background color
SNOW_COLOR = (255, 255, 255)  # Snow color (white)
SNOWFLAKE_COUNT = 100  # Number of snowflakes
snowflakes = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(SNOWFLAKE_COUNT)]  # Initial snowflake positions
CHIMNEY_COLOR = (128, 64, 0)
GRAVITY = 0.5
JUMP_FORCE = 10
MAX_HEALTH = 6
SNOW_SLOWDOWN = 3
ICE_SPEEDUP = 5
PARENT_DAMAGE = 1
CEO_DAMAGE = 2
PROJECTILE_SPEED = 5
ENEMY_SPEED = 2

# Set up the display
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Presence of Presents - CEO Projectiles")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))  # Placeholder for Santa
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 4)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = MAX_HEALTH

    def update(self, platforms, enemies, projectiles, chimney):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -5
        if keys[pygame.K_RIGHT]:
            self.vel_x = 5

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False
            

        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Check for collisions with platforms
        self.collide(platforms)

        # Check for collisions with enemies
        self.check_enemy_collision(enemies)

        # Check for collisions with projectiles
        self.check_projectile_collision(projectiles)

        # Check for reaching the chimney
        self.check_chimney_collision(chimney)

        # Ground collision
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.on_ground = True
            self.respawn()

    def collide(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                if platform.type == 'snow':
                    self.rect.y -= SNOW_SLOWDOWN
                elif platform.type == 'ice':
                    self.rect.x += ICE_SPEEDUP if self.vel_x > 0 else -ICE_SPEEDUP

                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def check_enemy_collision(self, enemies):
        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy):
                if isinstance(enemy, Parent):
                    self.take_damage(PARENT_DAMAGE)
                elif isinstance(enemy, CEO):
                    self.take_damage(CEO_DAMAGE)

    def check_projectile_collision(self, projectiles):
        for projectile in projectiles:
            if pygame.sprite.collide_rect(self, projectile):
                self.take_damage(CEO_DAMAGE)
                projectile.kill()  # Remove projectile after collision

    def check_chimney_collision(self, chimney):
        if pygame.sprite.collide_rect(self, chimney):
            global current_level
            current_level += 1
            self.rect.center = (WIDTH // 4, HEIGHT // 4)
            load_level(current_level)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.respawn()

    def respawn(self):
        self.rect.center = (WIDTH // 4, HEIGHT // 4)
        self.health = MAX_HEALTH

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, type):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type

        if type == 'snow':
            self.image.fill(GRAY)
        elif type == 'ice':
            self.image.fill(BLUE)
        else:
            self.image.fill(GREEN)

# Parent class (Melee attacker)
class Parent(pygame.sprite.Sprite):
    def __init__(self, x, y, ice_platform):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.ice_platform = ice_platform

    def update(self):
        # Check if Parent is on the ice platform
        if self.rect.colliderect(self.ice_platform.rect):
            self.rect.x += self.direction * ENEMY_SPEED
            # Reverse direction if hitting ice platform boundaries
            if self.rect.right >= self.ice_platform.rect.right or self.rect.left <= self.ice_platform.rect.left:
                self.direction *= -1
        else:
            self.rect.x = max(self.rect.x, self.ice_platform.rect.left)  # Snap back to ice platform

# CEO class (Ranged attacker)
class CEO(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.shoot_timer = 0

    def update(self, projectiles):
        # Shooting projectiles periodically
        self.shoot_timer += 1
        if self.shoot_timer > 60:  # Shoots every second (at 60 FPS)
            self.shoot_timer = 0
            projectile = Projectile(self.rect.centerx, self.rect.centery, PROJECTILE_SPEED)
            projectiles.add(projectile)

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = speed

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# Chimney class (Goal)
class Chimney(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 100))
        self.image.fill(CHIMNEY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Health bar display
def draw_health_bar(surface, x, y, health):
    bar_width = 200
    bar_height = 20
    fill = (health / MAX_HEALTH) * bar_width
    border_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, border_rect, 2)

# Level loader
def load_level(level):
    platforms.empty()
    enemies.empty()
    projectiles.empty()
    all_sprites.empty()

    # Level 1
    if level == 1:
        platforms.add(Platform(100, 500, 200, 20, 'regular'))
        platforms.add(Platform(350, 450, 150, 20, 'snow'))
        ice_platform = Platform(550, 400, 200, 20, 'ice')
        platforms.add(ice_platform)
        platforms.add(Platform(0, HEIGHT - 20, WIDTH, 20, 'regular'))  # Ground platform
        enemies.add(Parent(550, 352, ice_platform))
        enemies.add(CEO(400, 400))
        chimney.rect.topleft = (700, 300)

    all_sprites.add(player)
    all_sprites.add(platforms)
    all_sprites.add(enemies)
    all_sprites.add(chimney)

    # Level 2 - New Simple Level
    if level == 2:
        platforms.add(Platform(100, 500, 200, 20, 'regular'))
        platforms.add(Platform(300, 450, 150, 20, 'snow'))
        ice_platform = Platform(500, 400, 200, 20, 'ice')
        platforms.add(ice_platform)
        platforms.add(Platform(0, HEIGHT - 20, WIDTH, 20, 'regular'))  # Ground platform

        # Add enemies for Level 2
        enemies.add(Parent(500, 352, ice_platform))
        enemies.add(CEO(350, 400))

        # Position the chimney (goal) for Level 2
        chimney.rect.topleft = (700, 250)
    
    # Level 3 - Complex Level
    if level == 3:
        # Platforms
        platforms.add(Platform(50, 550, 100, 20, 'regular'))
        platforms.add(Platform(200, 500, 150, 20, 'snow'))
        ice_platform_1 = Platform(400, 450, 150, 20, 'ice')
        platforms.add(ice_platform_1)
        platforms.add(Platform(600, 400, 150, 20, 'regular'))
        platforms.add(Platform(750, 350, 100, 20, 'snow'))
        platforms.add(Platform(50, HEIGHT - 20, WIDTH, 20, 'regular'))  # Ground platform
        
        # Enemies on platforms
        enemies.add(Parent(400, 402, ice_platform_1))  # Moves along the ice platform
        enemies.add(Parent(600, 352, ice_platform_1))  # Additional Parent on the same platform
        enemies.add(CEO(300, 500))  # Positioned to challenge near platforms
        enemies.add(CEO(700, 300))  # Adds difficulty near the chimney

        # Chimney positioned higher up for a challenge
        chimney.rect.topleft = (750, 200)

    # Add all sprites to the main group for rendering
    all_sprites.add(player)
    all_sprites.add(platforms)
    all_sprites.add(enemies)
    all_sprites.add(chimney)
    
        

def main():
    global current_level, platforms, enemies, projectiles, all_sprites, player, chimney

    # Initialize variables
    current_level = 1
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    player = Player()
    chimney = Chimney(700, 300)

    # Load the first level
    load_level(current_level)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update player and platforms
        player.update(platforms, enemies, projectiles, chimney)

        # Update enemies and projectiles
        for enemy in enemies:
            if isinstance(enemy, CEO):
                enemy.update(projectiles)
            else:
                enemy.update()
        projectiles.update()

        # Dark background
        window.fill(DARK_GRAY)

        # Snowfall effect
        for i, (x, y) in enumerate(snowflakes):
            pygame.draw.circle(window, SNOW_COLOR, (x, y), 2)  # Draw each snowflake as a small circle
            # Move each snowflake down or reset at top if it reaches the bottom
            snowflakes[i] = (x, y + 1) if y < HEIGHT else (random.randint(0, WIDTH), 0)

        # Draw everything else
        all_sprites.draw(window)
        projectiles.draw(window)

        # Draw health bar
        draw_health_bar(window, 10, 10, player.health)

        # Refresh the display
        pygame.display.flip()

        # Maintain 60 FPS
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
