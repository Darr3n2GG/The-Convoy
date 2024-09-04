import pygame, sys, time, random

# Constants
FONT_FAMILY = "helvetica neue", "sans serif"
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
DIFFICULTY = 10
FRAME_SIZE_X = 800
FRAME_SIZE_Y = 800
SNAKE_SIZE = 10
FPS_CONTROLLER = pygame.time.Clock()


# Variables
snake_pos = [400, 400]
snake_body = [[100, 50], [90, 50], [80, 50]]
food_pos = [random.randrange(0, FRAME_SIZE_X // SNAKE_SIZE) * SNAKE_SIZE,
            random.randrange(0, FRAME_SIZE_Y // SNAKE_SIZE) * SNAKE_SIZE]
food_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0

# Sound effect
pygame.mixer.init(44100, -16, 2, 512)
background = pygame.mixer.Sound('./soundpack/sonar.mp3')
detected = pygame.mixer.Sound('./soundpack/enemy_sensed.mp3')
ended = False

# Style
font_family = "helvetica neue", "helvetica", "sans-serif"

# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
difficulty = 10

# Window size
frame_size_multiplier = 1
frame_size_x = 800 * frame_size_multiplier
frame_size_y = 800 * frame_size_multiplier

# Checks for errors encounteRED
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Initialise game window
pygame.display.set_caption('Worm')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))


# FPS (frames per second) controller
fps_controller = pygame.time.Clock()


# Game Over
def game_over():
    font = pygame.font.SysFont(FONT_FAMILY, 90)
    game_over_surface = font.render('YOU DIED', True, RED)



# Score
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x/10, 15)
    else:
        score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()


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
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Making sure the snake cannot move in the opposite direction instantaneously
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Moving the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    if direction == 'DOWN':
        snake_pos[1] += 10
    if direction == 'LEFT':
        snake_pos[0] -= 10
    if direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    # Spawning food on the screen
    if not food_spawn:
        food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True

    # GFX
    game_window.fill(BLACK)
    for i in range(0, frame_size_x, 50):
        pygame.draw.line(game_window, GREEN, (0, i), (frame_size_x, i))
    for i in range(0, frame_size_y , 50):
        pygame.draw.line(game_window, GREEN, (i, 0), (i, frame_size_y))
    for pos in snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))


    # Snake food
    pygame.draw.rect(game_window, WHITE, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    # Teleportation logic
    if snake_pos[0] < 0:
        snake_pos[0] = frame_size_x - 10
    if snake_pos[0] >= frame_size_x:
        snake_pos[0] = 0
    if snake_pos[1] < 0:
        snake_pos[1] = frame_size_y - 10
    if snake_pos[1] >= frame_size_y:
        snake_pos[1] = 0
    
    # Sound
    if not ended:
        background.play(-1)
        #detected only plays when enemy is hit
        
    # Game Over conditions
    # Getting out of bounds is removed as teleportation is added
    # Touching the snake body
    for block in snake_body[1:]:  #block is not previously called
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    show_score(1, WHITE, FONT_FAMILY, 20)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(difficulty)