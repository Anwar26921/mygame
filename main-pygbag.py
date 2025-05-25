import pygame
import random

pygame.init()

# Use fixed screen size (fullscreen causes issues in Pygbag)
screen = pygame.display.set_mode((640, 480))
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("LayerEdge Token Dash")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TOKEN_COLOR = (255, 215, 0)
SHIELD_COLOR = (0, 255, 0)
PAUSE_COLOR = (200, 200, 200)

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Load assets
try:
    logo = pygame.image.load("layeredge_logo.jpg")
    logo = pygame.transform.scale(logo, (60, 60))
except:
    logo = None

# Disable sound for browser
pickup_sound = None
# try:
#     pygame.mixer.init()
#     pickup_sound = pygame.mixer.Sound("coin_pickup.ogg")
# except:
#     pickup_sound = None

clock = pygame.time.Clock()

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def intro_screen():
    running_intro = True
    frame = 0
    while running_intro:
        screen.fill(BLACK)
        frame += 1

        if logo:
            scale_pulse = 1 + 0.05 * (1 + abs((frame // 10) % 20 - 10))
            scaled_logo = pygame.transform.rotozoom(logo, 0, scale_pulse)
            rect = scaled_logo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(scaled_logo, rect)

        draw_text("LayerEdge Token Dash", big_font, WHITE, WIDTH // 2 - 250, HEIGHT // 2 + 100)
        draw_text("Tap anywhere to start", font, WHITE, WIDTH // 2 - 160, HEIGHT // 2 + 160)

        for event in pygame.event.get():
            if hasattr(event, "type"):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running_intro = False

        pygame.display.flip()
        clock.tick(60)

def pause_screen():
    paused = True
    while paused:
        screen.fill(BLACK)
        draw_text("PAUSED", big_font, PAUSE_COLOR, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("Tap anywhere to resume", font, PAUSE_COLOR, WIDTH // 2 - 140, HEIGHT // 2 + 20)
        pygame.display.flip()

        for event in pygame.event.get():
            if hasattr(event, "type"):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    paused = False

        clock.tick(15)

def main_game():
    player = pygame.Rect(WIDTH // 2 - 30, HEIGHT - 80, 60, 60)
    player_speed = 10
    has_shield = True
    move_left = False
    move_right = False

    def random_x_obstacle():
        return random.randint(WIDTH // 4, WIDTH * 3 // 4 - 60)

    def random_x_token():
        return random.randint(WIDTH // 4, WIDTH * 3 // 4 - 30)

    obstacles = [pygame.Rect(random_x_obstacle(), random.randint(-600, -60), 60, 60) for _ in range(5)]
    tokens = [pygame.Rect(random_x_token(), random.randint(-600, -60), 30, 30) for _ in range(3)]

    score = 0
    tokens_collected = 0
    frame_count = 0

    total_time = 60 * 1000
    start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        elapsed_time = pygame.time.get_ticks() - start_ticks
        remaining_time = max(0, total_time - elapsed_time)
        seconds_left = remaining_time // 1000

        screen.fill(BLACK)
        frame_count += 1

        for event in pygame.event.get():
            if hasattr(event, "type"):
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if x < WIDTH // 2:
                        move_left = True
                    else:
                        move_right = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    move_left = False
                    move_right = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pause_screen()

        if move_left and player.x > WIDTH // 4:
            player.x -= player_speed
        if move_right and player.x < WIDTH * 3 // 4 - player.width:
            player.x += player_speed

        if logo:
            screen.blit(logo, (player.x, player.y))
        else:
            pygame.draw.rect(screen, (0, 150, 255), player)

        for obs in obstacles:
            obs.y += 5
            pygame.draw.rect(screen, WHITE, obs)
            if obs.colliderect(player):
                if has_shield:
                    has_shield = False
                    obs.y = -100
                    obs.x = random_x_obstacle()
                else:
                    running = False
            if obs.y > HEIGHT:
                obs.y = random.randint(-100, -40)
                obs.x = random_x_obstacle()
                score += 1

        for token in tokens:
            token.y += 3
            pulse = 5 * (1 + abs((frame_count // 5) % 10 - 5))
            pygame.draw.ellipse(screen, TOKEN_COLOR, token.inflate(pulse, pulse))
            if token.colliderect(player):
                if pickup_sound:
                    pickup_sound.play()
                token.y = random.randint(-300, -60)
                token.x = random_x_token()
                tokens_collected += 1
                has_shield = True

        if has_shield:
            pygame.draw.circle(screen, SHIELD_COLOR, (player.centerx, player.centery), 40, 2)

        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"EDGEN: {tokens_collected}", font, TOKEN_COLOR, 10, 40)
        if has_shield:
            draw_text("Shield ON", font, SHIELD_COLOR, 10, 70)
        draw_text(f"Time Left: {seconds_left}s", font, WHITE, WIDTH - 180, 10)
        draw_text("Press 'P' to pause", font, WHITE, WIDTH - 220, 40)

        pygame.display.flip()
        clock.tick(60)

        if remaining_time <= 0:
            running = False

    # Removed file writing for web
    # with open("leaderboard.txt", "a") as f:
    #     f.write(f"Score: {score} | EDGEN: {tokens_collected}\n")

    return score, tokens_collected

def game_over_screen(score, tokens):
    running_over = True
    while running_over:
        screen.fill(BLACK)
        draw_text("GAME OVER", big_font, WHITE, WIDTH // 2 - 150, HEIGHT // 2 - 100)
        draw_text(f"Final Score: {score}", font, WHITE, WIDTH // 2 - 90, HEIGHT // 2)
        draw_text(f"EDGEN Collected: {tokens}", font, TOKEN_COLOR, WIDTH // 2 - 110, HEIGHT // 2 + 40)
        draw_text("Tap anywhere to play again", font, WHITE, WIDTH // 2 - 150, HEIGHT // 2 + 100)

        for event in pygame.event.get():
            if hasattr(event, "type"):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running_over = False

        pygame.display.flip()
        clock.tick(30)

# Run the game
while True:
    intro_screen()
    score, tokens = main_game()
    game_over_screen(score, tokens)
