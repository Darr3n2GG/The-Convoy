import pygame, sys, time, random

pygame.init()

# Constants
FONT_PATH = './font/AtkinsonHyperlegible-Regular.ttf'
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
# BLUE = pygame.Color(0, 0, 255)
FRAME_SIZE_X = 500
FRAME_SIZE_Y = 500
PIXEL_SIZE = 10
FPS_CONTROLLER = pygame.time.Clock()


# Sound effects
pygame.mixer.init(44100, -16, 2, 512)
SONAR = pygame.mixer.Sound('./soundpack/sonar.mp3')
# DETECTED = pygame.mixer.Sound('./soundpack/enemy_sensed.mp3')
HIT = pygame.mixer.Sound('./soundpack/explode.mp3')
SUPPLIED = pygame.mixer.Sound('./soundpack/repair.mp3')


# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print('[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Initialise game window
pygame.display.set_caption('The Convoy')
game_window = pygame.display.set_mode((FRAME_SIZE_X + 1, FRAME_SIZE_Y + 1))

# FPS controller
fps_controller = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()
radar_start_ticks = pygame.time.get_ticks()


# Functions #
# Returns a new list of random positions based on frame size
def random_pos():
    return [random.randrange(1, (FRAME_SIZE_X//PIXEL_SIZE)) * PIXEL_SIZE, random.randrange(1, (FRAME_SIZE_Y//PIXEL_SIZE)) * PIXEL_SIZE]

def game_over():
    game_over_font = pygame.font.Font('./fonts/Jacquard24-Regular.ttf', 100)
    game_over_surface = game_over_font.render('Defeat', True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/4)
    game_window.fill(BLACK)
    game_window.blit(game_over_surface, game_over_rect)
    show_checkpoints()
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

def show_checkpoints():
    checkpoint_font = pygame.font.Font(FONT_PATH, 20)
    checkpoint_surface = checkpoint_font.render('Checkpoints : ' + str(checkpoints), True, WHITE)
    checkpoint_rect = checkpoint_surface.get_rect()
    checkpoint_rect.topleft = (10, 15)
    game_window.blit(checkpoint_surface, checkpoint_rect)

def show_speed():
    speed_font = pygame.font.Font(FONT_PATH, 12)
    speed_surface = speed_font.render('Speed : ' + str(speed), True, WHITE)
    speed_rect = speed_surface.get_rect()
    speed_rect.bottomright = (game_window.get_width() - 10, game_window.get_height() - 10)
    game_window.blit(speed_surface, speed_rect)



#   Variables  #
# Convoy
snake_pos = [FRAME_SIZE_X/2, FRAME_SIZE_Y/2]
snake_body = [[snake_pos[0] - 10, snake_pos[1]], [snake_pos[0] - 20, snake_pos[1]], [snake_pos[0] - 30, snake_pos[1]]]
last_snake_pos = [0,0]
direction = 'RIGHT'
change_to = direction

# Speed settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = 10

# checkpoints
checkpoints_pos = random_pos()
checkpoints_spawn = True
checkpoints = 0

# Submarines
submarines = []
blink_duration = 2000
fade_duration = 1000
show_submarines = False

# Radar
pulse_done = True
time_passed = 0
radius = 0



#-------------------------------------------------------------------------------------------------------------------------------------------------


# Main logic #
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
                # print(speed)
            if event.key == pygame.K_COMMA:
                speed = max(10, speed - 10)
                # print(speed)
            
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

    # Grid
    for i in range(0, FRAME_SIZE_X + 1, 50):
        pygame.draw.line(game_window, GREEN, (0, i), (FRAME_SIZE_X, i))
    for i in range(0, FRAME_SIZE_Y + 1, 50):
        pygame.draw.line(game_window, GREEN, (i, 0), (i, FRAME_SIZE_Y))
        

    # Convoy body
    for pos in snake_body:
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], PIXEL_SIZE, PIXEL_SIZE))
        
    # Convoy movements
    if direction == 'UP':
        snake_pos[1] -= PIXEL_SIZE
    if direction == 'DOWN':
        snake_pos[1] += PIXEL_SIZE
    if direction == 'LEFT':
        snake_pos[0] -= PIXEL_SIZE
    if direction == 'RIGHT':
        snake_pos[0] += PIXEL_SIZE
        
    # Teleportation logic
    if snake_pos[0] < 0:
        snake_pos[0] = FRAME_SIZE_X - PIXEL_SIZE
    if snake_pos[0] >= FRAME_SIZE_X:
        snake_pos[0] = 0
    if snake_pos[1] < 0:
        snake_pos[1] = FRAME_SIZE_Y - PIXEL_SIZE
    if snake_pos[1] >= FRAME_SIZE_Y:
        snake_pos[1] = 0

    # Convoy growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == checkpoints_pos[0] and snake_pos[1] == checkpoints_pos[1]:
        checkpoints += 1
        checkpoints_spawn = False
        SUPPLIED.play()
    else:
        snake_body.pop()

        
    # Spawning checkpoints
    if not checkpoints_spawn:
        checkpoints_pos = random_pos()
        submarines.insert(0,random_pos()) # Spawn landmine
    checkpoints_spawn = True

    # Checkpoints
    pygame.draw.rect(game_window, WHITE, pygame.Rect(checkpoints_pos[0], checkpoints_pos[1], 10, 10))

    
    # Submarine blinking
    current_ticks = pygame.time.get_ticks()
    if not show_submarines and current_ticks - start_ticks >= blink_duration:
        show_submarines = True
        pulse_done = False
        last_snake_pos = list(snake_pos)
        for i in range(len(submarines)):
            submarines[i] = random_pos()
        SONAR.play()
        start_ticks = current_ticks
    elif show_submarines and current_ticks - start_ticks >= fade_duration:
        show_submarines = False
        start_ticks = current_ticks
    if show_submarines:
        for landmine_pos in submarines:
            pygame.draw.rect(game_window, RED, pygame.Rect(landmine_pos[0], landmine_pos[1], 10, 10))

            
    # Sonar animation
    if not pulse_done:
        time_passed += (current_ticks - radar_start_ticks) / 50000
        radius = FRAME_SIZE_X * time_passed
        if radius > FRAME_SIZE_X * 1.1:
            radius = 0
            time_passed = 0
            radar_start_ticks = current_ticks
            pulse_done = True
        pygame.draw.circle(game_window,(0, 255, 0), last_snake_pos, int(radius), 3)
    
    
    # Game Over conditions
    # Touching the snake body
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    # Touching landmine
    for landmine_pos in submarines:
        if snake_pos[0] == landmine_pos[0] and snake_pos[1] == landmine_pos[1]:
            snake_body.pop()
            HIT.play()
            if snake_body == []:
                game_over()



    # Show checkpoints and speed value
    show_checkpoints()
    show_speed()
    

    # Refresh game screen
    pygame.display.update()

    # Refresh rate
    FPS_CONTROLLER.tick(speed)