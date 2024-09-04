import pygame, sys, time, random

pygame.init()

# Constants
FONT = pygame.font.Font('./Atkinson_Hyperlegible/AtkinsonHyperlegible-Regular.ttf', 20)
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
FRAME_SIZE_X = 500
FRAME_SIZE_Y = 500
SNAKE_SIZE = 10
FPS_CONTROLLER = pygame.time.Clock()

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = 20


# Variables
snake_pos = [FRAME_SIZE_X/2, FRAME_SIZE_Y/2]
snake_body = [[100, 50], [90, 50], [80, 50]]
food_pos = [random.randrange(0, FRAME_SIZE_X // SNAKE_SIZE) * SNAKE_SIZE,
            random.randrange(0, FRAME_SIZE_Y // SNAKE_SIZE) * SNAKE_SIZE]
food_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0

landmines = []
blink_duration = 2000
fade_duration = 1000
show_landmines = False


# Sound effect
pygame.mixer.init(44100, -16, 2, 512)
background = pygame.mixer.Sound('./soundpack/sonar.mp3')
detected = pygame.mixer.Sound('./soundpack/enemy_sensed.mp3')
ended = False


# Checks for errors encounteREDf
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print('[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Initialise game window
pygame.display.set_caption('Worm')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

# Returns a new list of random positions based on frame size
def random_pos():
    return [random.randrange(1, (FRAME_SIZE_X//10)) * 10, random.randrange(1, (FRAME_SIZE_Y//10)) * 10]


# Game Over
def game_over():
    font = pygame.font.SysFont(FONT, 90)
    game_over_surface = font.render('YOU DIED', True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/4)
    game_window.fill(BLACK)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, RED, FONT, 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

# Score
# Text aligned to top left of window
def show_score(color, FONT, size):
    score_surface = FONT.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    score_rect.topleft = (10, 15)
    game_window.blit(score_surface, score_rect)

# Speed
def show_speed(color, FONT, size):
    speed_surface = FONT.render('Speed : ' + str(speed), True, color)
    speed_rect = speed_surface.get_rect()
    speed_rect.topleft = (10, 50)
    game_window.blit(speed_surface, speed_rect)


def generate_food_position():
    while True:
        new_food_pos = [random.randrange(0, FRAME_SIZE_X // SNAKE_SIZE) * SNAKE_SIZE,
                        random.randrange(0, FRAME_SIZE_Y // SNAKE_SIZE) * SNAKE_SIZE]
        if new_food_pos not in snake_body:
            return new_food_pos


# Main logic
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Whenever a key is pressed down
        elif event.type == pygame.KEYDOWN:
            # W -> Up; S -> Down; A -> Left; D -> Right
            if event.key == pygame.K_UP or event.key == ord('w'):
                change_to = 'UP'
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                change_to = 'RIGHT'

            # Speed
            if event.key == pygame.K_PERIOD:
                speed += 10
                print(speed)
            if event.key == pygame.K_COMMA:
                speed = max(10, speed - 10)
                print(speed)
            
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # instantaneous manoeuvre prevention
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # GFX
    game_window.fill(BLACK)
    for i in range(0, FRAME_SIZE_X, 50):
        pygame.draw.line(game_window, GREEN, (0, i), (FRAME_SIZE_X, i))
    for i in range(0, FRAME_SIZE_Y , 50):
        pygame.draw.line(game_window, GREEN, (i, 0), (i, FRAME_SIZE_Y))
    for pos in snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Sound
    if not ended:
        background.play(-1)
    #detected only plays when enemy is hit

    # Snake movements
    if direction == 'UP':
        snake_pos[1] -= SNAKE_SIZE
    if direction == 'DOWN':
        snake_pos[1] += SNAKE_SIZE
    if direction == 'LEFT':
        snake_pos[0] -= SNAKE_SIZE
    if direction == 'RIGHT':
        snake_pos[0] += SNAKE_SIZE

    # Teleportation logic
    if snake_pos[0] < 0:
        snake_pos[0] = FRAME_SIZE_X - SNAKE_SIZE
    if snake_pos[0] >= FRAME_SIZE_X:
        snake_pos[0] = 0
    if snake_pos[1] < 0:
        snake_pos[1] = FRAME_SIZE_Y - SNAKE_SIZE
    if snake_pos[1] >= FRAME_SIZE_Y:
        snake_pos[1] = 0


    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    # Spawning food on the screen
    if not food_spawn:
        food_pos = generate_food_position()
        landmines.insert(0,random_pos()) # Spawn landmine
    food_spawn = True

    pygame.draw.rect(game_window, WHITE, pygame.Rect(food_pos[0], food_pos[1], SNAKE_SIZE, SNAKE_SIZE))

    # Landmine blinking
    current_ticks = pygame.time.get_ticks()
    if not show_landmines and current_ticks - start_ticks >= blink_duration:
        show_landmines = True
        for i in range(len(landmines)):
            landmines[i] = random_pos()
        start_ticks = current_ticks
    elif show_landmines and current_ticks - start_ticks >= fade_duration:
        show_landmines = False
        start_ticks = current_ticks
    if show_landmines:
        for landmine_pos in landmines:
            pygame.draw.rect(game_window, RED, pygame.Rect(landmine_pos[0], landmine_pos[1], 10, 10))   

    
    # Game Over conditions
    # Touching the snake body
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()


    # landmine
    for landmine_pos in landmines:
        if snake_pos[0] == landmine_pos[0] and snake_pos[1] == landmine_pos[1]:
            snake_body.pop()
            if snake_body == []:
                game_over()

    show_score(WHITE, FONT, 20)

    show_speed(WHITE, FONT, 20)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    FPS_CONTROLLER.tick(speed)