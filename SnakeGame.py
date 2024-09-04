import pygame, sys, time, random, math

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

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = 10

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
pygame.display.set_caption('The Convoy')
game_window = pygame.display.set_mode((FRAME_SIZE_X + 1, FRAME_SIZE_Y + 1))

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()
emit_start_ticks = pygame.time.get_ticks()
radar_start_ticks = None

# SFX
pygame.mixer.init()
SONAR = pygame.mixer.Sound('./soundpack/sonar.mp3')
DETECTED = pygame.mixer.Sound('./soundpack/enemy_sensed.mp3')

# Returns a new list of random positions based on frame size
def random_pos():
    return [random.randrange(1, (FRAME_SIZE_X//PIXEL_SIZE)) * PIXEL_SIZE, random.randrange(1, (FRAME_SIZE_Y//PIXEL_SIZE)) * PIXEL_SIZE]

def game_over():
    game_over_font = pygame.font.Font(FONT_PATH, 100)
    game_over_surface = game_over_font.render('YOU DIED', True, RED)
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

def detect_collision(cx, cy, radius, px, py):
    # Calculate the distance between the circle center and the point
    distance = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
    # Check if the distance is less than or equal to the radius
    return distance <= radius


#   Variables  #
# Snake
snake_pos = [FRAME_SIZE_X / 5, FRAME_SIZE_Y / 2]
snake_body = [[snake_pos[0] - 10, snake_pos[1]], [snake_pos[0] - 20, snake_pos[1]], [snake_pos[0] - 30, snake_pos[1]]]
last_snake_pos = [0,0]
direction = 'RIGHT'
change_to = direction

# checkpoints
checkpoints_pos = [400, snake_pos[1]]
checkpoints_spawn = True
checkpoints = 0

# Submarine
submarines = []
emit_duration = 3000

# Radar
radar_pulsed = False
pulse_done = True
time_passed = 0
radius = 0


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
            if event.key == pygame.K_COMMA:
                speed = max(10, speed - 10)
            
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

    # Draw Grid
    for i in range(0, FRAME_SIZE_X + 1, 50):
        pygame.draw.line(game_window, GREEN, (0, i), (FRAME_SIZE_X, i))
    for i in range(0, FRAME_SIZE_Y + 1, 50):
        pygame.draw.line(game_window, GREEN, (i, 0), (i, FRAME_SIZE_Y))
        
    # Snake body
    for pos in snake_body:
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], PIXEL_SIZE, PIXEL_SIZE))

        
    # Snake movements
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


    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == checkpoints_pos[0] and snake_pos[1] == checkpoints_pos[1]:
        checkpoints += 1
        checkpoints_spawn = False
    else:
        snake_body.pop()

        
    # Spawning checkpoints on the screen
    if not checkpoints_spawn:
        checkpoints_pos = random_pos()
        submarines.insert(0,random_pos()) # Spawn landmine
    checkpoints_spawn = True

    
    # Snake checkpoints
    pygame.draw.rect(game_window, WHITE, pygame.Rect(checkpoints_pos[0], checkpoints_pos[1], 10, 10))

    
    # Emit sonar every 3 seconds
    current_ticks = pygame.time.get_ticks()
    if current_ticks - emit_start_ticks >= emit_duration:
        pulse_done = False
        last_snake_pos = list(snake_pos)
        radar_start_ticks = pygame.time.get_ticks()
        SONAR.play()
        emit_start_ticks = current_ticks

            
    # Sonar animation
    if not pulse_done:
        time_passed = (current_ticks - radar_start_ticks) / 2000
        radius = FRAME_SIZE_X * time_passed
        if time_passed > 1:
            radius = 0
            time_passed = 0
            radar_start_ticks = current_ticks
            for i in range(len(submarines)):
                submarines[i] = random_pos()
            pulse_done = True
        pygame.draw.circle(game_window,(0, 255, 0), last_snake_pos, int(radius), 3)
        
        for submarine_pos in submarines:
            if detect_collision(last_snake_pos[0], last_snake_pos[1], radius, submarine_pos[0], submarine_pos[1]):
                pygame.draw.rect(game_window, RED, pygame.Rect(submarine_pos[0], submarine_pos[1], 10, 10))
    
    
    # Game Over conditions
    # Touching the snake body
    for body in snake_body[1:]:
        if snake_pos[0] == body[0] and snake_pos[1] == body[1]:
            game_over()

    # Touching landmine
    for landmine_pos in submarines:
        if snake_pos[0] == landmine_pos[0] and snake_pos[1] == landmine_pos[1]:
            snake_body.pop()
            if snake_body == []:
                game_over()

    # Show checkpoints and speed value
    show_checkpoints()
    show_speed()
    

    # Refresh game screen
    pygame.display.update()

    # Refresh rate
    FPS_CONTROLLER.tick(speed)