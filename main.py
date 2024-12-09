import random
import time

import pygame
from sys import exit

# pygame Setup
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()
game_font = pygame.font.SysFont("Atari", 30)

background_surf = pygame.image.load("images/background.webp").convert()
background_surf = pygame.transform.rotozoom(background_surf, 0, 0.8)

background_music = pygame.mixer.Sound("soundtrack/background-music.mp3")
background_music.set_volume(.5)
background_music.play(loops=-1)

explosion_sound = pygame.mixer.Sound("soundtrack/explosion.mp3")
explosion_sound.set_volume(.5)

laser_sound = pygame.mixer.Sound("soundtrack/laser-gun.mp3")
laser_sound.set_volume(.25)

alien_shot_sound = pygame.mixer.Sound("soundtrack/alien-shot.mp3")
alien_shot_sound.set_volume(.25)


class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/spaceship.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=(300, 500))
        self.state = 0

    def spaceship_input(self):
        if game_on:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT] and self.rect.x < 550:
                self.rect.x += 5
            if keys[pygame.K_LEFT] and self.rect.x > 0:
                self.rect.x -= 5

    def animate(self):
        if self.state == 1:
            current_center = self.rect.center
            image = pygame.image.load("images/blast.png").convert_alpha()
            self.image = pygame.transform.rotozoom(image, 0, 0.5)
            self.rect = self.image.get_rect(center=current_center)

    def update(self):
        self.spaceship_input()
        self.animate()


class Laser(pygame.sprite.Sprite):
    def __init__(self, spaceship_pos):
        super().__init__()
        image = pygame.image.load("images/bullet.png").convert_alpha()
        self.image = pygame.transform.rotozoom(image, 0, .5)
        self.rect = self.image.get_rect(midtop=spaceship_pos)

    def travel(self):
        if self.rect.y > 0:
            self.rect.y -= 5
        else:
            self.kill()

    def update(self):
        self.travel()


class Missile(pygame.sprite.Sprite):
    def __init__(self, alien_pos):
        super().__init__()
        image = pygame.image.load("images/alien_missile.png").convert_alpha()
        self.image = pygame.transform.rotozoom(image, 0, .75)
        self.rect = self.image.get_rect(midbottom=alien_pos)

    def travel(self):
        self.rect.y += 5

    def update(self):
        self.travel()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, type):
        super().__init__()
        self.type = type
        if self.type == 1:
            self.image = pygame.image.load("images/alien1.png").convert_alpha()
        elif self.type == 2:
            image = pygame.image.load("images/alien2.png").convert_alpha()
            self.image = pygame.transform.rotozoom(image, 0, .5)
        else:
            image = pygame.image.load("images/alien3.png").convert_alpha()
            self.image = pygame.transform.rotozoom(image, 0, .25)

        self.rect = self.image.get_rect(midtop=(x_pos, y_pos))
        self.state = 0
        self.displacement_state = 0
        self.explosion_start = None

    def animate_expolsion(self):
        if self.state == 1:
            current_center = self.rect.center
            time_passage = time.time() - self.explosion_start
            image = pygame.image.load("images/blast.png").convert_alpha()
            self.image = pygame.transform.rotozoom(image, 0, 0.5)
            self.rect = self.image.get_rect(center=current_center)
            if int(time_passage) > 0:
                self.state += 1
        elif self.state == 2:
            self.kill()

    def animate_movement(self):
        if self.type == 1:
            self.movement_mechanism(20)
        elif self.type == 2:
            self.movement_mechanism(-20)
        else:
            self.movement_mechanism(20)

    def movement_mechanism(self, displacement):
        if random.randint(1, 35) == 1 and self.state < 1:
            if self.displacement_state == 0:
                self.rect.x += displacement
                self.displacement_state = 1
            else:
                self.rect.x -= displacement
                self.displacement_state = 0

    def update(self):
        self.animate_expolsion()
        self.animate_movement()


spaceship = pygame.sprite.GroupSingle()
spaceship.add(Spaceship())

laser_group = pygame.sprite.Group()

missile_group = pygame.sprite.Group()

alien_group = pygame.sprite.Group()


def display_starting_screen():
    line1_surf = game_font.render("Press Space to shoot laser", True, (129, 191, 218))
    line2_surf = game_font.render("Press Right and Left to control movement", True, (129, 191, 218))
    line3_surf = game_font.render("Press Return to start the game", True, (129, 191, 218))
    screen.blit(line1_surf, (150, 150))
    screen.blit(line2_surf, (100, 200))
    screen.blit(line3_surf, (150, 250))
    if score > 0:
        latest_score_surf = game_font.render(f"Latest Score: {score}", True, (245, 240, 205))
        with open("hs.txt") as file:
            hs = file.read()
        highest_score_surf = game_font.render(f"Highest Score: {hs}", True, (245, 240, 205))
        screen.blit(latest_score_surf, (220, 300))
        screen.blit(highest_score_surf, (220, 350))


def display_score():
    global score
    score_surf = game_font.render(f"Score: {score}", True, (217, 22, 86))
    score_rect = score_surf.get_rect(center=(50, 25))
    screen.blit(score_surf, score_rect)


def display_level_up():
    global level
    level_up_surf = game_font.render(f"Cleared level {level - 1}! "
                                     f"Your Score: {score}", True, (255, 178, 0))
    level_up_rect = level_up_surf.get_rect(center=(300, 300))
    screen.blit(level_up_surf, level_up_rect)


def create_aliens(x_pos, y_pos, num, type):
    for i in range(0, num):
        alien_group.add(Alien(x_pos=x_pos - i * 60, y_pos=y_pos, type=type))


def shoot_missile():
    if alien_group.sprites():
        if len(alien_group.sprites()) < 20:
            frequency = int((40 / (1.25 ** (level - 1))) * 1.5)
        else:
            frequency = int(40 / (1.25 ** (level - 1)))

        if random.randint(0, frequency) == 1:
            random_alien = random.choice(alien_group.sprites())
            missile_group.add(Missile(random_alien.rect.midbottom))
            alien_shot_sound.play()


def shoot_laser():
    # Laser shots increase with every two increment in level
    add_laser = level // 2
    if len(laser_group.sprites()) < (1 + add_laser):
        laser_group.add(Laser(spaceship_pos=spaceship.sprite.rect.midtop))
        laser_sound.play()


def detect_coll_btn_alien_n_laser():
    global score

    def collide_with_center(sprite1, sprite2):
        """
        Check if the rect of sprite1 contains the center of sprite2.
        """
        collidepoint_1 = sprite1.rect.collidepoint(sprite2.rect.center)
        collidepoint_2 = sprite1.rect.collidepoint((sprite2.rect.center[0] + 5, sprite2.rect.center[1]))
        collidepoint_3 = sprite1.rect.collidepoint((sprite2.rect.center[0] - 5, sprite2.rect.center[1]))
        if collidepoint_1 or collidepoint_2 or collidepoint_3:
            return True
        else:
            return False

    if alien_group.sprites() and laser_group.sprites():
        collisions = pygame.sprite.groupcollide(laser_group, alien_group, True, False, collided=collide_with_center)
        if collisions:
            alien = next(iter(collisions.values()))
            if alien[0].state == 0:
                explosion_sound.play()
                alien[0].state += 1
                alien[0].explosion_start = time.time()
                score += 20 * level


def detect_coll_btn_spaceship_n_missile():
    def collide_with_center(sprite1, sprite2):
        """
        Check if the rect of sprite1 contains the center and the peripheries of sprite2.
        """
        collidepoint_1 = sprite2.rect.collidepoint(sprite1.rect.center)
        collidepoint_2 = sprite2.rect.collidepoint((sprite1.rect.center[0] + 10, sprite1.rect.center[1]))
        collidepoint_3 = sprite2.rect.collidepoint((sprite1.rect.center[0] - 10, sprite1.rect.center[1]))

        if collidepoint_1 or collidepoint_2 or collidepoint_3:
            return True
        else:
            return False

    if missile_group.sprites():
        collisions = pygame.sprite.spritecollide(spaceship.sprite, missile_group, True, collided=collide_with_center)
        if collisions:
            explosion_sound.play()
            spaceship.sprite.state = 1
            missile_group.empty()
            laser_group.empty()
            alien_group.empty()
            return True


score = 0
level = 1
level_cleared_start = None
game_on = False
while True:
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not game_on:
                spaceship.sprite.state = 0
                game_on = True
                #Update Highest Score (H.S.)
                with open("hs.txt", mode="r+") as file:
                    hs = int(file.read())
                    if hs < score:
                        file.seek(0)
                        file.write(f"{score}")
                        file.truncate()
                    score = 0
                create_aliens(575, 50, 10, random.randint(1, 3))
                create_aliens(575, 100, 10, random.randint(1, 3))
                create_aliens(575, 150, 10, random.randint(1, 3))
                create_aliens(575, 200, 10, random.randint(1, 3))
                spaceship.sprite.image = pygame.image.load("images/spaceship.png").convert_alpha()
                spaceship.sprite.rect.center = (300, 500)
            if event.key == pygame.K_SPACE and game_on:
                shoot_laser()

    screen.blit(background_surf, (0, 0))

    spaceship.draw(screen)
    spaceship.update()

    display_score()

    if game_on:
        alien_group.draw(screen)
        alien_group.update()

        shoot_missile()
        missile_group.draw(screen)
        missile_group.update()

        laser_group.draw(screen)
        laser_group.update()

        detect_coll_btn_alien_n_laser()
        if detect_coll_btn_spaceship_n_missile():
            game_on = False
            level = 1

        if not alien_group.sprites() and game_on:
            if not level_cleared_start:
                level_cleared_start = time.time()
                level += 1
                missile_group.empty()
            display_level_up()
            time_passage = time.time() - level_cleared_start
            if int(time_passage) > 5:
                create_aliens(575, 50, 10, random.randint(1, 3))
                create_aliens(575, 100, 10, random.randint(1, 3))
                create_aliens(575, 150, 10, random.randint(1, 3))
                create_aliens(575, 200, 10, random.randint(1, 3))
                level_cleared_start = None

    else:
        display_starting_screen()

    # pygame.draw.line(screen, "gold", (0, 0), pygame.mouse.get_pos())
    pygame.display.update()
    # Maximum fps for the Game
    clock.tick(60)
