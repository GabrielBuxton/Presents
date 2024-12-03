##NOTES:
#Fix Santa sprite
#Enemy sprites
#Add heart health system
#Textures for platforms and ground
#More levels

#Weapons (Presents/Candy Canes)
#Double Jump

## ROUGH DRAFT ##

## ROUGH DRAFT ##
## Presents/Santa/Mario Clone/Platformer Game ##

## Vermont State University
## Game Design Team
## Gabriel Buxton
## Seth Barrett
## Logan Hayes
## John Luce
## December 2024

import pygame
import random
from pygame import mixer

# Initialize Pygame
pygame.init()

#Music
mixer.music.load('galacticrap.mp3')
mixer.music.play(-1)

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
MAX_HEALTH = 70
SNOW_SLOWDOWN = 3
ICE_SPEEDUP = 5
PARENT_DAMAGE = 1
CEO_DAMAGE = 2
PROJECTILE_SPEED = 5
ENEMY_SPEED = 2

# Set up the display
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Presence of Presents - CEO Projectiles")

background_image = pygame.image.load("presents.jpeg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

RUN_LEFT_ROW = 9
RUN_RIGHT_ROW = 9
JUMP_LEFT_ROW = 12
JUMP_RIGHT_ROW = 14
FRAMES_PER_ROW = 6
FRAME_WIDTH = 50
FRAME_HEIGHT = 50
NUM_FRAMES = 16
ANIMATION_SPEED = 0.1

# Define the win screen function
def show_win_screen():
    """Display a simple 'You Win' screen and wait for a few seconds."""
    window.fill(DARK_GRAY)
    font = pygame.font.Font(None, 74)
    text = font.render("You Win!", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(3000)  # Pause for 3 seconds

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.sprite_sheet = pygame.image.load("Sprite Sheet .png").convert_alpha()

        self.animations = {
            "run_left": self.load_frames(RUN_LEFT_ROW),
            "run_right": self.load_frames(RUN_RIGHT_ROW),
            "jump_left": self.load_frames(JUMP_LEFT_ROW),
            "jump_right": self.load_frames(JUMP_RIGHT_ROW),
            "idle": [self.get_sprite_frame(0)]

            }

        self.current_action = "idle"
        self.current_frame = 0
        self.image = self.animations[self.current_action][self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 4)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = MAX_HEALTH

    def check_chimney_collision(self, chimney):
        global current_level
        if pygame.sprite.collide_rect(self, chimney):
                if current_level == 3:  # Assuming level 3 is the last level
                    show_win_screen()  # Show the win screen and exit
                else:
                    current_level += 1
                self.rect.center = (WIDTH // 4, HEIGHT // 4)  # Reset player position
                load_level(current_level)


    def load_frames(self, row):
        #load all frames from a specific row
        frames = []
        for col in range(FRAMES_PER_ROW):
            x_pos = col * FRAME_WIDTH
            y_pos = row * FRAME_HEIGHT
            frame = self.sprite_sheet.subsurface(pygame.Rect(x_pos, y_pos, FRAME_WIDTH, FRAME_HEIGHT))
            frames.append(pygame.transform.scale(frame, (FRAME_WIDTH, FRAME_HEIGHT)))
        return frames

    def get_sprite_frame(self, frame_index):
        """returns a sprite frame from the sprite sheet given the index"""
        frame = self.sprite_sheet.subsurface(
            pygame.Rect(
                frame_index * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT
                )
            )
        return pygame.transform.scale(frame, (FRAME_WIDTH * 1.2, FRAME_HEIGHT *1.2))

    def update(self, platforms, enemies, projectiles, chimney):
        keys = pygame.key.get_pressed()

        previous_action = self.current_action

        if keys[pygame.K_LEFT] and keys[pygame.K_SPACE]:
            self.current_action = "jump_left"

        elif keys[pygame.K_RIGHT] and keys[pygame.K_SPACE]:
            self.current_action = "jump_right"
            
        elif keys[pygame.K_LEFT]:
            self.current_action = "run_left"
            self.vel_x = -5
            
        elif keys[pygame.K_RIGHT]:
            self.current_action = "run_right"
            self.vel_x = 5

        else:
            self.current_action = "idle"
            self.vel_x = 0

        if self.current_action != previous_action:
            self.current_frames = 0
        
        action_frames = self.animations.get(self.current_action, [self.image])

        self.animations["idle"] = [self.get_sprite_frame(0)]
        self.current_action = "idle"
        self.current_frame += ANIMATION_SPEED    
        if self.current_frame >= len(action_frames):
            self.current_frame = 0
            
        self.image = action_frames[int(self.current_frame)]

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
    def __init__(self, x, y, width, height, type, texture_file=None):
        """
        Initialize the platform with position, dimensions, type, and optional texture.
        :param x: X position of the platform
        :param y: Y position of the platform
        :param width: Width of the platform
        :param height: Height of the platform
        :param type: Type of platform ('snow', 'ice', 'regular')
        :param texture_file: Optional file path for the texture image
        """
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Transparent surface
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type

        if texture_file:
            # Load the texture image and scale it to the platform size
            texture = pygame.image.load(texture_file).convert_alpha()
            self.image.blit(pygame.transform.scale(texture, (width, height)), (0, 0))
        else:
            # Default solid color based on platform type
            if type == 'snow':
                self.image.fill((200, 200, 200))  # Light gray
            elif type == 'ice':
                self.image.fill((0, 255, 255))  # Cyan
            else:
                self.image.fill((0, 255, 0))  # Green

# Parent class (Melee attacker, now represents a demon)
class Parent(pygame.sprite.Sprite):
    def __init__(self, x, y, platform):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # Transparent surface
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.platform = platform

        # Draw a simple demon-like appearance
        pygame.draw.circle(self.image, (255, 0, 0), (25, 25), 25)  # Red body
        pygame.draw.polygon(self.image, (0, 0, 0), [(10, 10), (25, 0), (40, 10)])  # Horns
        pygame.draw.circle(self.image, (255, 255, 0), (25, 30), 5)  # Glowing yellow eye

    def update(self):
        # Move the Parent enemy left and right on the platform
        self.rect.x += self.direction * ENEMY_SPEED
        if self.rect.left <= self.platform.rect.left or self.rect.right >= self.platform.rect.right:
            self.direction *= -1  # Reverse direction

# CEO class (Ranged attacker)
# CEO class (Ranged attacker, now represents a demonic spellcaster)
class CEO(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # Transparent surface
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1

        # Draw a demonic caster appearance
        pygame.draw.rect(self.image, (50, 0, 50), (0, 0, 50, 50))  # Dark purple body
        pygame.draw.circle(self.image, (255, 0, 0), (25, 10), 10)  # Red glowing head
        pygame.draw.polygon(self.image, (0, 0, 0), [(10, 10), (25, 0), (40, 10)])  # Horns

        self.shoot_timer = 0

    def update(self, projectiles):
        # Move the CEO enemy back and forth
        self.rect.x += self.direction * ENEMY_SPEED
        if self.rect.left <= 300 or self.rect.right >= 500:  # Patrol bounds
            self.direction *= -1  # Reverse direction

        # Shooting projectiles periodically
        self.shoot_timer += 1
        if self.shoot_timer > 60:  # Shoots every second
            self.shoot_timer = 0
            projectile = Projectile(self.rect.centerx, self.rect.centery, PROJECTILE_SPEED * self.direction)
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
        self.width = 70
        self.height = 120
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Transparent surface
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Draw the main house structure
        pygame.draw.rect(self.image, (139, 69, 19), (10, 50, 50, 70))  # Brown house
        pygame.draw.rect(self.image, (0, 0, 0), (25, 85, 20, 35))      # Door

        # Draw the roof
        pygame.draw.polygon(self.image, (128, 0, 0), [(5, 50), (35, 10), (65, 50)])  # Red triangle roof

# Health bar display
def draw_health_hearts(surface, x, y, health, max_health):
    """Draws heart-based health representation."""
    heart_image = pygame.image.load('heart full sprite.png')  # Load the heart image
    heart_image = pygame.transform.scale(heart_image, (30, 30))  # Resize heart image

    for i in range(max_health):
        if i < health:
            # Draw full hearts for remaining health
            surface.blit(heart_image, (x + i * 35, y))
        else:
            # Draw empty placeholder hearts for lost health
            empty_heart = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.rect(empty_heart, (150, 0, 0, 128), empty_heart.get_rect())  # Red tint for empty hearts
            surface.blit(empty_heart, (x + i * 35, y))
            
# Level loader
def load_level(level):
    platforms.empty()
    enemies.empty()
    projectiles.empty()
    all_sprites.empty()

    # Level 1
    if level == 1:

        # Platforms that create a path toward the house chimney
        platforms.add(Platform(100, 500, 200, 20, 'regular', texture_file="building icy sprite.png"))  # Regular platform with default color
        platforms.add(Platform(350, 450, 150, 20, 'snow', texture_file="building icy sprite.png"))     # Snow platform with default color
        platforms.add(Platform(550, 400, 100, 20, 'ice', texture_file="building icy sprite.png"))  # Icy platform with texture
        platforms.add(Platform(700, 350, 100, 20, 'regular', texture_file="building icy sprite.png"))  # Regular platform with default color

        # Ground platform
        platforms.add(Platform(0, HEIGHT - 20, WIDTH, 20, 'regular'))  # Ground platform
        
        # Ice platform (introducing ice mechanics)
        ice_platform = Platform(300, 300, 150, 20, 'ice')
        platforms.add(ice_platform)

        # Enemies
        enemies.add(Parent(550, 352, ice_platform))  # Enemy on the ice platform
        enemies.add(CEO(400, 400))                  # Enemy between start and chimney

        # Position the chimney (goal)
        chimney.rect.topleft = (700, 250)

    # Add all sprites to the main group for rendering
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
    
# Level 3 - Improved Complex Level
    if level == 3:
        # Platforms
        platforms.add(Platform(50, 550, 120, 20, 'regular'))   # Start platform
        platforms.add(Platform(200, 500, 150, 20, 'snow'))     # Snow platform
        ice_platform_1 = Platform(400, 450, 180, 20, 'ice')    # Large ice platform
        platforms.add(ice_platform_1)
        platforms.add(Platform(650, 400, 120, 20, 'regular'))  # Middle platform
        platforms.add(Platform(800, 350, 100, 20, 'snow'))     # Small snow platform
        platforms.add(Platform(50, HEIGHT - 20, WIDTH, 20, 'regular'))  # Ground platform

        # Platforms to create a vertical challenge
        platforms.add(Platform(250, 300, 100, 20, 'regular'))  # Vertical stepping
        platforms.add(Platform(500, 250, 150, 20, 'ice'))      # Icy challenge
        platforms.add(Platform(750, 200, 120, 20, 'snow'))     # Final snow platform leading to the chimney

        # Enemies strategically placed
        enemies.add(Parent(400, 402, ice_platform_1))           # Moves on the large ice platform
        enemies.add(Parent(650, 352, ice_platform_1))           # Additional Parent enemy for difficulty
        enemies.add(CEO(300, 500))                              # Challenges players at the middle section
        enemies.add(CEO(750, 300))                              # Protects the chimney and final area

        # Chimney positioned as the final goal
    chimney.rect.topleft = (750, 150)

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

        #Draw the background image 
        window.blit(background_image, (0, 0))

        # Snowfall effect
        for i, (x, y) in enumerate(snowflakes):
            pygame.draw.circle(window, SNOW_COLOR, (x, y), 2)  # Draw each snowflake as a small circle
            # Move each snowflake down or reset at top if it reaches the bottom
            snowflakes[i] = (x, y + 1) if y < HEIGHT else (random.randint(0, WIDTH), 0)

        # Draw everything else
        all_sprites.draw(window)
        projectiles.draw(window)

        # With the new heart system:
        draw_health_hearts(window, 10, 10, player.health, MAX_HEALTH)

        # Refresh the display
        pygame.display.flip()

        # Maintain 60 FPS
        clock.tick(60)
       
    pygame.quit()

if __name__ == "__main__":
    main()
    
