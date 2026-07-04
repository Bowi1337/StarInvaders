import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "pics", relative_path)

pygame.mixer.music.load(resource_path('start.wav'))
# pygame.mixer.music.play()

# Display settings
background_colour = (233, 40, 255)
RESOLUTIONS = [
    (1280, 720),
    (1920, 1080),
    (2560, 1440),
]
current_resolution_index = 1
width, height = RESOLUTIONS[current_resolution_index]
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
fps = 120
fps_clock = pygame.time.Clock()
show_fps = False

# Key state tracking
escape_pressed = False
f3_pressed = False
up_pressed = False
down_pressed = False
enter_pressed = False

# Colors
Aqua = (0, 255, 255)
Black = (0, 0, 0)
Blue = (0, 0, 255)
Fuchsia = (255, 0, 255)
Gray = (128, 128, 128)
Green = (0, 128, 0)
Lime = (0, 255, 0)
Maroon = (128, 0, 0)
Navy_Blue = (0, 0, 128)
Olive = (128, 128, 0)
Purple = (128, 0, 128)
Dark_purple = (78, 34, 117)
Red = (255, 0, 0)
Silver = (192, 192, 192)
Teal = (0, 128, 128)
White = (255, 255, 255)
Yellow = (255, 255, 0)
Cyan = (0, 255, 255)
marginal = 20
Orange = (255, 91, 0)
Bright_green = (0, 255, 0)

# Fonts and UI
font = pygame.font.Font('freesansbold.ttf', 32)
small_font = pygame.font.Font('freesansbold.ttf', 24)
tiny_font = pygame.font.Font('freesansbold.ttf', 16)
gameover_msg = font.render("GAME OVER", True, Red)
restart = font.render("Press SPACE to restart!", True, Aqua)
quit_msg = font.render("Press ESC to quit", True, Red)

# Load images once
ailenimg = pygame.image.load(resource_path("Ailenship.png"))
blue_ailenimg = pygame.image.load(resource_path("blue_enemy_ship.png"))
playership = pygame.image.load(resource_path("spaceship.png"))
laserimg = pygame.image.load(resource_path("laser.png"))
flipped_laserimg = pygame.transform.flip(laserimg, False, True)
main_bg = pygame.image.load(resource_path("bg_pic.jpg"))
main_bg = pygame.transform.scale(main_bg, (width, height))
heart_icon = pygame.image.load(resource_path("heart_icon.png"))
extra_life_icon = pygame.image.load(resource_path("extra_life.png"))
quickshot_icon = pygame.image.load(resource_path("quick_shot.png"))

# Sound effects
laser_sound = pygame.mixer.Sound(resource_path("laser_sound.mp3"))
gameover_sound = pygame.mixer.Sound(resource_path("game_over.mp3"))

# Music state
music_on = False

def apply_music_state():
    if music_on:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()


# Menu background
menu_bg = pygame.image.load(resource_path("bg_pic.jpg"))
menu_bg = pygame.transform.scale(menu_bg, (width, height))


class Enemy:

    def __init__(self, x, y):
        self.x = random.randint(40, width - 40)
        self.y = 40
        self.xchange = 5
        self.ychange = 0
        self.direction1 = "höger"


class BlueEnemy:
    def __init__(self):
        self.x = random.randint(40, width - 40)
        self.y = random.randint(60, 160)
        self.xchange = 4
        self.direction1 = "höger"
        self.shot_timer = Time()
        self.shot_timer.start()
        self.shot_cooldown = random.randint(1500, 3000)

    def update(self):
        # Hovers side to side near the top instead of descending
        if self.direction1 == "höger":
            self.x += self.xchange
            if self.x >= width - 40:
                self.direction1 = "vänster"
        else:
            self.x -= self.xchange
            if self.x <= 40:
                self.direction1 = "höger"


class EnemyShot:
    def __init__(self, x, y, target_x, target_y, speed=7):
        self.x = x
        self.y = y
        dx = target_x - x
        dy = target_y - y
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.xchange = dx / dist * speed
        self.ychange = dy / dist * speed

    def update(self):
        self.x += self.xchange
        self.y += self.ychange

    def is_offscreen(self):
        return self.y > height + 50 or self.y < -50 or self.x > width + 50 or self.x < -50


class Drop:
    def __init__(self, x, y, drop_type):
        self.x = x
        self.y = y
        self.drop_type = drop_type  # "life", "golden", or "rapidfire"
        self.fall_speed = 4

    def update(self):
        self.y += self.fall_speed

    def is_offscreen(self):
        return self.y > height + 50


class Time:
    def __init__(self):
        self.last = pygame.time.get_ticks()
        self.cooldown = 300
        self.elapsed = 0

    def start(self):
        self.last = pygame.time.get_ticks()
        self.elapsed = 0

    def peek(self):
        return pygame.time.get_ticks() - self.last


class Shot:
    def __init__(self, x, y, laserspeed=-10):
        self.x = x
        self.y = y
        self.laserspeed = laserspeed
        self.image = flipped_laserimg if laserspeed > 0 else laserimg

    def update(self):
        self.y += self.laserspeed

    def is_offscreen(self):
        return self.y < -50 or self.y > height + 50 or self.x > width + 50 or self.x < -50


class Player:
    x_change = 0
    y_change = 0
    x = 0
    y = 0

    def __init__(self):
        self.x = width // 2
        self.y = height // 2
        self.x_change = 0
        self.y_change = 0

    def updateposition(self, keys):
        # Right movement
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_change = 5
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x_change = -5
            else:
                self.x_change = 0
        # Down movement
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y_change = 5
        else:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y_change = -5
            else:
                self.y_change = 0

    def apply_boundaries(self):
        # Prevent player from leaving screen
        if self.x < 33:
            self.x = 33
        elif self.x > width - 33:
            self.x = width - 33
        if self.y < 40:
            self.y = 40
        elif self.y > height - 40:
            self.y = height - 40


pygame.display.set_caption('Star Invaders')

t = Time()  # Shot timer
f = Time()  # Flip timer


def draw_fps():
    # Draw FPS counter in top right
    fps_text = tiny_font.render("FPS: {:.1f}".format(fps_clock.get_fps()), True, Bright_green)
    screen.blit(fps_text, (width - 150, marginal))


def draw_pause_menu():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(128)
    overlay.fill(Black)
    screen.blit(overlay, (0, 0))

    # Draw pause dialog
    pause_text = font.render("PAUSED", True, White)
    resume_text = small_font.render("Press SPACE to Resume", True, Bright_green)
    menu_text = small_font.render("Press ESC to Menu", True, Orange)

    screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, height // 2 - 100))
    screen.blit(resume_text, (width // 2 - resume_text.get_width() // 2, height // 2))
    screen.blit(menu_text, (width // 2 - menu_text.get_width() // 2, height // 2 + 50))


def maybe_spawn_drop(x, y, lives, has_extra_life, drops, ball_list):
    # Rarer the more enemies are already on screen, so drops don't pile up
    enemy_count = len(ball_list)
    drop_chance = max(0.05, 0.15 - 0.01 * enemy_count)
    if random.random() > drop_chance:
        return
    options = ["rapidfire"]
    if lives < 3:
        options.append("life")
    elif not has_extra_life:
        options.append("golden")
    drops.append(Drop(x, y, random.choice(options)))



def credits_screen():
    # Rolling credits
    credit_line1 = "Star Invaders:"
    credit_line2 = "by Westeros Game Studios"
    credit_line3 = "Made by Bowi1337"
    credit_line4 = "Music by Adrian Productions"

    credit_text1 = small_font.render(credit_line1, True, White)
    credit_text2 = small_font.render(credit_line2, True, White)
    credit_text3 = small_font.render(credit_line3, True, White)
    credit_text4 = small_font.render(credit_line4, True, White)

    y_pos = height

    while True:
        screen.blit(menu_bg, (0, 0))

        screen.blit(credit_text1, (width // 2 - credit_text1.get_width() // 2, y_pos))
        screen.blit(credit_text2, (width // 2 - credit_text2.get_width() // 2, y_pos + 50))
        screen.blit(credit_text3, (width // 2 - credit_text3.get_width() // 2, y_pos + 100))
        screen.blit(credit_text4, (width // 2 - credit_text4.get_width() // 2, y_pos + 150))

        y_pos -= 2

        if y_pos < -100:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return

        pygame.display.update()
        fps_clock.tick(60)



def settings_screen():
    global current_resolution_index, width, height, screen, main_bg, menu_bg, up_pressed, down_pressed

    selected = 0

    while True:
        screen.blit(menu_bg, (0, 0))

        title = font.render("SETTINGS", True, White)
        resolution_text = small_font.render("Resolution", True, White)

        back_text = small_font.render("Back (ESC)", True, Orange)

        screen.blit(title, (width // 2 - title.get_width() // 2, height * 0.1))
        screen.blit(resolution_text, (width // 4, height * 0.3))

        # Draw resolution options with selection indicator
        for i, res in enumerate(RESOLUTIONS):
            if i == selected:
                # Highlight selected option
                res_text = small_font.render(f"> {res[0]}x{res[1]} <", True, Bright_green)
                if i == current_resolution_index:
                    res_text = small_font.render(f"> {res[0]}x{res[1]} (CURRENT) <", True, Yellow)
            else:
                res_text = small_font.render(f"{res[0]}x{res[1]}", True, White)
                if i == current_resolution_index:
                    res_text = small_font.render(f"{res[0]}x{res[1]} (CURRENT)", True, Cyan)

            screen.blit(res_text, (width // 4, height * 0.4 + i * 50))

        screen.blit(back_text, (width // 4, height * 0.75))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_DOWN]:
                if not down_pressed:
                    selected += 1
                    down_pressed = True
            else:
                down_pressed = False

            if keys[pygame.K_UP]:
                if not up_pressed:
                    selected -= 1
                    up_pressed = True
            else:
                up_pressed = False

            if keys[pygame.K_RETURN]:
                if selected < len(RESOLUTIONS):
                    current_resolution_index = selected
                    width, height = RESOLUTIONS[current_resolution_index]
                    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                    main_bg = pygame.image.load(resource_path("main_bg.jpg"))
                    main_bg = pygame.transform.scale(main_bg, (width, height))
                    menu_bg = pygame.image.load(resource_path("bg_pic.jpg"))
                    menu_bg = pygame.transform.scale(menu_bg, (width, height))

            if keys[pygame.K_ESCAPE]:
                return

        if selected < 0:
            selected = 0
        elif selected > len(RESOLUTIONS) - 1:
            selected = len(RESOLUTIONS) - 1

        pygame.display.update()
        fps_clock.tick(60)


def intro():
    global font, show_fps, escape_pressed, f3_pressed, up_pressed, down_pressed, music_on, enter_pressed

    intro_title = font.render("STAR INVADERS", True, White)
    menu_play = font.render("Play", True, White)
    menu_credits = font.render("Credits", True, White)
    menu_settings = font.render("Settings", True, White)
    menu_music = font.render("Music: ON", True, White)
    menu_music_off = font.render("Music: OFF", True, White)
    select_music = font.render("MUSIC: ON", True, Bright_green)
    select_music_off = font.render("MUSIC: OFF", True, Bright_green)
    menu_quit = font.render("Quit", True, White)
    select_play = font.render("PLAY", True, Bright_green)
    select_credits = font.render("CREDITS", True, Orange)
    select_settings = font.render("SETTINGS", True, Orange)
    select_quit = font.render("QUIT", True, Red)

    selected = 0

    while True:

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # returns bool of keys pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            if not down_pressed:
                selected += 1
                down_pressed = True
        else:
            down_pressed = False

        if keys[pygame.K_UP]:
            if not up_pressed:
                selected -= 1
                up_pressed = True
        else:
            up_pressed = False

        # F3 toggle (single press only)
        if keys[pygame.K_F3]:
            if not f3_pressed:
                show_fps = not show_fps
                f3_pressed = True
        else:
            f3_pressed = False

        if keys[pygame.K_RETURN]:
            if not enter_pressed:
                if selected == 0:  # Play button
                    main()
                elif selected == 1:  # Credits
                    credits_screen()
                elif selected == 2:  # Settings
                    settings_screen()
                elif selected == 3:  # Music toggle
                    music_on = not music_on
                    apply_music_state()
                elif selected == 4:  # Quit button
                    quit()
                enter_pressed = True
        else:
            enter_pressed = False

        screen.blit(menu_bg, (0, 0))

        if selected > 4:
            selected = 0
        elif selected < 0:
            selected = 4

        screen.blit(intro_title, (width // 2 - intro_title.get_width() // 2, height * 0.08))
        if selected == 0:
            screen.blit(select_play, (width // 4, height * 0.35))
        else:
            screen.blit(menu_play, (width // 4, height * 0.35))

        if selected == 1:
            screen.blit(select_credits, (width // 4, height * 0.45))
        else:
            screen.blit(menu_credits, (width // 4, height * 0.45))

        if selected == 2:
            screen.blit(select_settings, (width // 4, height * 0.55))
        else:
            screen.blit(menu_settings, (width // 4, height * 0.55))

        if selected == 3:
            screen.blit(select_music_off if not music_on else select_music, (width // 4, height * 0.65))
        else:
            screen.blit(menu_music_off if not music_on else menu_music, (width // 4, height * 0.65))

        if selected == 4:
            screen.blit(select_quit, (width // 4, height * 0.75))
        else:
            screen.blit(menu_quit, (width // 4, height * 0.75))

        if show_fps:
            draw_fps()

        pygame.display.update()
        fps_clock.tick(60)


def main():
    global ball_list
    global blue_list
    global shots
    global enemy_shots
    global drops
    global show_fps
    global escape_pressed
    global f3_pressed

    p = Player()
    gameover = False
    paused = False
    to_main_menu = False
    spawn = "true"
    laserspeed = -10
    escape_pressed = False
    f3_pressed = False

    lives = 3
    has_extra_life = False
    invincible_until = 0
    shake_until = 0
    rapidfire_until = 0
    enemy_timer = Time()

    ball_list = []
    blue_list = []
    shots = []
    enemy_shots = []
    drops = []

    score = 0
    flip = ""  # For flipping the ship

    current_playership = playership.copy()
    is_flipped = False

    running = True
    while running:
        fps_clock.tick(fps)  # Limit frame rate
        screen.blit(main_bg, (0, 0))  # Draw background
        scoretext = font.render("Score: {}".format(score), True, Yellow)
        keys = pygame.key.get_pressed()

        # F3 toggle in game (single press only)
        if keys[pygame.K_F3]:
            if not f3_pressed:
                show_fps = not show_fps
                f3_pressed = True
        else:
            f3_pressed = False

        # Pause with ESC / exit to menu from pause (single press only)
        was_paused = paused
        if keys[pygame.K_ESCAPE]:
            if not escape_pressed:
                if not was_paused:
                    paused = True
                else:
                    running = False
                    to_main_menu = True
                escape_pressed = True
        else:
            escape_pressed = False

        if paused:
            # Draw game state frozen
            screen.blit(scoretext, (marginal, marginal))
            screen.blit(current_playership, (p.x - 33, p.y - 40))  # Player
            for shot in shots:
                screen.blit(laserimg, (shot.x - 10, shot.y - 70))  # Laser
            for ball in ball_list:  # Enemy ships
                screen.blit(ailenimg, (ball.x - 24, ball.y - 40))
            for blue in blue_list:  # Blue enemy ships
                screen.blit(blue_ailenimg, (blue.x - 24, blue.y - 40))
            for enemy_shot in enemy_shots:
                screen.blit(laserimg, (enemy_shot.x - 10, enemy_shot.y - 10))

            # Draw pause menu
            draw_pause_menu()

            if show_fps:
                draw_fps()

            if keys[pygame.K_SPACE]:
                paused = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            pygame.display.update()
            continue

        if not gameover:

            p.updateposition(keys)
            # Cannon
            if keys[pygame.K_SPACE]:
                cooldown = 120 if pygame.time.get_ticks() < rapidfire_until else 300
                if t.peek() > cooldown:  # Reduced cooldown for better feel
                    shots.append(Shot(p.x, p.y, laserspeed))
                    laser_sound.play()
                    t.start()

            # Move all shots every frame
            for shot in shots[:]:
                shot.update()
                if shot.is_offscreen():
                    shots.remove(shot)

            # Flips the spaceship
            if keys[pygame.K_e]:
                if f.peek() > 300:  # timer
                    f.start()
                    flip = "down"
            if flip == "down":
                is_flipped = not is_flipped
                if is_flipped:
                    current_playership = pygame.transform.flip(playership, False, True)
                    laserspeed = 10
                else:
                    current_playership = playership.copy()
                    laserspeed = -10
                flip = ""

            # AI for enemies
            for ball in ball_list:
                if ball.y > 40:
                    spawn = "true"
                elif ball.y == 40:
                    spawn = "false"

            if spawn == "true":
                spawn_cooldown = max(100, 1200 - score * 18)
                if enemy_timer.peek() > spawn_cooldown:
                    blue_chance = min(0.35, 0.08 + score * 0.0015)
                    if len(blue_list) < 7 and random.random() < blue_chance:
                        blue_list.append(BlueEnemy())
                    else:
                        ball_list.append(Enemy(p.x, p.y))
                    enemy_timer.start()

            enemy_speed = min(12, 5 + score // 25)
            for ball in ball_list:
                if ball.direction1 == "höger":
                    ball.x += enemy_speed
                    if ball.x >= width - 40:
                        ball.direction1 = "ner"
                if ball.direction1 == "vänster":
                    ball.x -= enemy_speed
                    if ball.x <= 40:
                        ball.direction1 = "ner"
                if ball.direction1 == "ner" and ball.x <= 40:
                    ball.y += 80
                    ball.direction1 = "höger"
                elif ball.direction1 == "ner" and ball.x >= width - 40:
                    ball.y += 80
                    ball.direction1 = "vänster"

            # Blue enemies hover and fire aimed shots
            for blue in blue_list:
                blue.update()
                if blue.shot_timer.peek() > blue.shot_cooldown:
                    enemy_shots.append(EnemyShot(blue.x, blue.y, p.x, p.y))
                    blue.shot_timer.start()
                    blue.shot_cooldown = random.randint(1500, 3000)

            # Player movement with boundaries
            p.y += p.y_change
            p.x += p.x_change
            p.apply_boundaries()

            # Player collision with enemies (regular and blue) and enemy shots
            if pygame.time.get_ticks() >= invincible_until:
                hit = False
                for ball in ball_list:
                    if p.x + 33 >= ball.x - 24 and p.x - 33 <= ball.x + 24:
                        if p.y + 40 > ball.y - 40 and p.y - 40 < ball.y + 40:
                            hit = True
                            break
                if not hit:
                    for blue in blue_list:
                        if p.x + 33 >= blue.x - 24 and p.x - 33 <= blue.x + 24:
                            if p.y + 40 > blue.y - 40 and p.y - 40 < blue.y + 40:
                                hit = True
                                break
                if not hit:
                    for enemy_shot in enemy_shots[:]:
                        if p.x + 33 >= enemy_shot.x - 10 and p.x - 33 <= enemy_shot.x + 10:
                            if p.y + 40 > enemy_shot.y - 10 and p.y - 40 < enemy_shot.y + 10:
                                hit = True
                                enemy_shots.remove(enemy_shot)
                                break
                if hit:
                    if has_extra_life:
                        has_extra_life = False
                    elif lives > 1:
                        lives -= 1
                    else:
                        lives = 0
                        gameover = True
                        running = False
                        gameover_sound.play()
                    invincible_until = pygame.time.get_ticks() + 1500
                    shake_until = pygame.time.get_ticks() + 300

            # Shot collision with enemies
            for shot in shots[:]:
                for ball in ball_list:
                    if shot.x + 10 >= ball.x - 24 and shot.x - 10 <= ball.x + 24:
                        if shot.y + 35 > ball.y - 40 and shot.y - 35 < ball.y + 40:
                            maybe_spawn_drop(ball.x, ball.y, lives, has_extra_life, drops, ball_list)
                            ball.y = height + 100
                            ball.x = width + 100
                            ball.direction1 = ""
                            score += 1
                            if shot in shots:
                                shots.remove(shot)
                            break

            # Shot collision with blue enemies
            for shot in shots[:]:
                for blue in blue_list[:]:
                    if shot.x + 10 >= blue.x - 24 and shot.x - 10 <= blue.x + 24:
                        if shot.y + 35 > blue.y - 40 and shot.y - 35 < blue.y + 40:
                            maybe_spawn_drop(blue.x, blue.y, lives, has_extra_life, drops, ball_list)
                            blue_list.remove(blue)
                            score += 3
                            if shot in shots:
                                shots.remove(shot)
                            break

            # Move enemy shots and clear ones that leave the screen
            for enemy_shot in enemy_shots[:]:
                enemy_shot.update()
                if enemy_shot.is_offscreen():
                    enemy_shots.remove(enemy_shot)

            # Move and collect drops
            for drop in drops[:]:
                drop.update()
                if drop.is_offscreen():
                    drops.remove(drop)
                    continue
                if p.x + 33 >= drop.x - 32 and p.x - 33 <= drop.x + 32:
                    if p.y + 40 > drop.y - 32 and p.y - 40 < drop.y + 32:
                        if drop.drop_type == "life":
                            lives += 1
                        elif drop.drop_type == "golden":
                            has_extra_life = True
                        elif drop.drop_type == "rapidfire":
                            rapidfire_until = pygame.time.get_ticks() + 8000
                        drops.remove(drop)

        # Draw everything
        sx, sy = (0, 0)
        if pygame.time.get_ticks() < shake_until:
            sx, sy = (random.randint(-6, 6), random.randint(-6, 6))
        blink_visible = True
        if pygame.time.get_ticks() < invincible_until:
            blink_visible = (pygame.time.get_ticks() // 100) % 2 == 0

        screen.blit(scoretext, (marginal + sx, marginal + sy))
        for i in range(lives):
            screen.blit(heart_icon, (marginal + i * 80 + sx, marginal + 45 + sy))
        if has_extra_life:
            screen.blit(extra_life_icon, (marginal + lives * 80 + sx, marginal + 45 + sy))
        if blink_visible:
            screen.blit(current_playership, (p.x - 33 + sx, p.y - 40 + sy))  # Player
        for shot in shots:
            screen.blit(shot.image, (shot.x - 10 + sx, shot.y - 70 + sy))  # Laser
        for ball in ball_list:  # Enemy ships
            screen.blit(ailenimg, (ball.x - 24 + sx, ball.y - 40 + sy))
        for blue in blue_list:  # Blue enemy ships
            screen.blit(blue_ailenimg, (blue.x - 24 + sx, blue.y - 40 + sy))
        for enemy_shot in enemy_shots:
            screen.blit(laserimg, (enemy_shot.x - 10 + sx, enemy_shot.y - 10 + sy))
        for drop in drops:
            if drop.drop_type == "life":
                screen.blit(heart_icon, (drop.x - 32, drop.y - 32))
            elif drop.drop_type == "golden":
                screen.blit(extra_life_icon, (drop.x - 32, drop.y - 32))
            else:
                screen.blit(quickshot_icon, (drop.x - 32, drop.y - 32))

        if show_fps:
            draw_fps()

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.display.update()

    if not to_main_menu:
        death(score, p, ball_list, shots)


def death(score, p, ball_list, shots):
    # Restart screen
    waiting = True
    while waiting:
        fps_clock.tick(fps)
        screen.blit(main_bg, (0, 0))
        screen.blit(gameover_msg, (width // 2 - gameover_msg.get_width() // 2, height // 2 - 50))
        screen.blit(restart, (width // 2 - restart.get_width() // 2, height // 2 + 50))
        screen.blit(quit_msg, (width // 2 - quit_msg.get_width() // 2, height // 2 + 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            waiting = False
            main()
        if keys[pygame.K_ESCAPE]:
            waiting = False
            pygame.quit()
            quit()

        pygame.display.update()


if __name__ == '__main__':
    intro()
    pygame.quit()