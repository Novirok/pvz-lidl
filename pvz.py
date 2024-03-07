import os
import pygame
import sys
import random

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Plants vs Zombies Lidl edition")

white = (255, 255, 255)

script_dir = os.path.dirname(__file__)
background_img = pygame.image.load(os.path.join(script_dir, "background.jpg"))
background_img = pygame.transform.scale(background_img, (width, height))


PLANT_SCALE_FACTOR = 1.5 
ZOMBIE_SCALE_FACTOR = 2  

image_names = {
    "plant": "plant-removebg-preview.png",
    "zombie": "zombie-removebg-preview.png",
    "projectile": "blob.jfif"
}

images = {}
for name, filename in image_names.items():
    path = os.path.join(script_dir, filename)
    image = pygame.image.load(path)
    if name == "plant":
        image = pygame.transform.scale(image, (int(30 * PLANT_SCALE_FACTOR), int(30 * PLANT_SCALE_FACTOR)))
    elif name == "zombie":
        image = pygame.transform.scale(image, (int(30 * ZOMBIE_SCALE_FACTOR), int(60 * ZOMBIE_SCALE_FACTOR)))
    images[name] = image

font_color = (0, 0, 0)  
font = pygame.font.Font(None, 36)
place_plant_cooldown = 8000
shoot_cooldown = 3000

last_plant_placement = pygame.time.get_ticks()
last_shoot = pygame.time.get_ticks()

class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = images["plant"]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.shoot_cooldown = shoot_cooldown
        self.last_shoot = pygame.time.get_ticks()
        self.hits = 0

    def can_shoot(self):
        return pygame.time.get_ticks() - self.last_shoot >= self.shoot_cooldown

    def shoot(self, zombies):
        if self.can_shoot():
            zombies_ahead = [zombie for zombie in zombies if zombie.rect.x > self.rect.x]
            if zombies_ahead:
                projectile = Projectile(self.rect.right, self.rect.centery)
                all_sprites.add(projectile)
                projectiles.add(projectile)
                self.last_shoot = pygame.time.get_ticks()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = images["zombie"]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.hits = 0
        self.x_pos = float(x)
        self.is_attacking = False
        self.attack_cooldown = 1000
        self.last_attack = pygame.time.get_ticks()
        self.attack_range_y = 30
        self.attack_range_x = 30

    def is_dead(self):
        return self.hits >= 6

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack >= self.attack_cooldown

    def update(self):
        if not self.is_attacking:
            self.x_pos -= 0.2
            self.rect.x = int(self.x_pos)

            plants_ahead = [plant for plant in plants if self.in_attack_range(plant)]
            if plants_ahead:
                self.is_attacking = True
        else:
            if self.can_attack():
                for plant in plants:
                    if self.in_attack_range(plant):
                        plant.hits += 1
                        if plant.hits >= 5:
                            plant.kill()
                self.last_attack = pygame.time.get_ticks()

                self.is_attacking = False

                if self.rect.right < 0:
                    self.kill()

    def in_attack_range(self, plant):
        return (
            abs(plant.rect.y - self.rect.y) <= self.attack_range_y
            and plant.rect.right > self.rect.x
        )

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = images["projectile"]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        self.rect.x += 5
        if self.rect.x > width:
            self.kill()

all_sprites = pygame.sprite.Group()
plants = pygame.sprite.Group()
zombies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

def place_plant(x, y):
    global last_plant_placement
    if pygame.time.get_ticks() - last_plant_placement > place_plant_cooldown:
        plant = Plant(x, y)
        all_sprites.add(plant)
        plants.add(plant)
        last_plant_placement = pygame.time.get_ticks()

def spawn_zombie():
    if random.randint(0, 100) < 70:
        zombie = Zombie(width - 30, random.randint(50, height - 30))
        all_sprites.add(zombie)
        zombies.add(zombie)

def check_game_over():
    for zombie in zombies:
        if zombie.rect.left <= 0:
            return True
    return False

clock = pygame.time.Clock()

last_zombie_spawn = pygame.time.get_ticks()
zombie_spawn_delay = 5000

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            place_plant(*event.pos)
            for plant in plants:
                plant.shoot(zombies)

    now = pygame.time.get_ticks()
    if now - last_zombie_spawn > zombie_spawn_delay:
        spawn_zombie()
        last_zombie_spawn = now

    hits = pygame.sprite.groupcollide(projectiles, zombies, True, False)
    for projectile, zombies_hit in hits.items():
        for zombie in zombies_hit:
            zombie.hits += 1
            if zombie.is_dead():
                zombie.kill()

    all_sprites.update()

    screen.blit(background_img, (0, 0))

    if len(plants) > 0:
        for plant in plants:
            plant.shoot(zombies)

        cooldown_time = max(0, (last_plant_placement + place_plant_cooldown - now) // 1000)
        cooldown_text = font.render(f"Cooldown: {cooldown_time}s", True, font_color)
        screen.blit(cooldown_text, (width // 2 - cooldown_text.get_width() // 2, height - 20))

    all_sprites.draw(screen)
    pygame.display.flip()

    if check_game_over():
        pygame.quit()
        sys.exit()

    clock.tick(60)