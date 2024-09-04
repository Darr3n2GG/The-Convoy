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

# Constants for sound
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
emit_start_ticks = pygame.time.get_ticks()
radar_start_ticks = None


# Functions #
# Returns a new list of random positions based on frame size
def random_pos():
    xpos = random.randrange(1, (FRAME_SIZE_X//10)) * 10
    ypos = random.randrange(1, (FRAME_SIZE_Y//10)) * 10
    while [xpos, ypos] in convoy_body: #repeats generating the random position when it is occupied by player
        xpos = random.randrange(1, (FRAME_SIZE_X//10)) * 10
        ypos = random.randrange(1, (FRAME_SIZE_Y//10)) * 10
    return [xpos, ypos]
    
# Game over screen and auto-close
def game_over():
    game_over_font = pygame.font.Font('./font/Jacquard24-Regular.ttf', 100)
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

# Show checkpoints reached by the Convoy
def show_checkpoints():
    checkpoint_font = pygame.font.Font(FONT_PATH, 20)
    checkpoint_surface = checkpoint_font.render('Checkpoints : ' + str(checkpoints), True, WHITE)
    checkpoint_rect = checkpoint_surface.get_rect()
    checkpoint_rect.topleft = (10, 15)
    game_window.blit(checkpoint_surface, checkpoint_rect)

# Show convoy's speed
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

# Speed settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = 10

# Convoy
convoy_pos = [FRAME_SIZE_X/2, FRAME_SIZE_Y/2]
convoy_body = [[convoy_pos[0] - 10, convoy_pos[1]], [convoy_pos[0] - 20, convoy_pos[1]], [convoy_pos[0] - 30, convoy_pos[1]]]
last_convoy_pos = [0,0]
direction = 'RIGHT'
change_to = direction

# checkpoints
checkpoints_pos = [400, convoy_pos[1]]
checkpoints_spawn = True
checkpoints = 0

# Submarines
submarines = []
emit_duration = 3000

# Radar
radar_pulsed = False
pulse_done = True
time_passed = 0
radius = 0


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

    # instantaneous manoeuvre prevention -- avoid head-tail switch
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
        
    # Convoy body
    for pos in convoy_body:
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], PIXEL_SIZE, PIXEL_SIZE))
        
    # Convoy movements
    if direction == 'UP':
        convoy_pos[1] -= PIXEL_SIZE
    if direction == 'DOWN':
        convoy_pos[1] += PIXEL_SIZE
    if direction == 'LEFT':
        convoy_pos[0] -= PIXEL_SIZE
    if direction == 'RIGHT':
        convoy_pos[0] += PIXEL_SIZE

        
    # Teleportation logic
    if convoy_pos[0] < 0:
        convoy_pos[0] = FRAME_SIZE_X - PIXEL_SIZE
    if convoy_pos[0] >= FRAME_SIZE_X:
        convoy_pos[0] = 0
    if convoy_pos[1] < 0:
        convoy_pos[1] = FRAME_SIZE_Y - PIXEL_SIZE
    if convoy_pos[1] >= FRAME_SIZE_Y:
        convoy_pos[1] = 0


    # Convoy body growing mechanism
    convoy_body.insert(0, list(convoy_pos))
    if convoy_pos[0] == checkpoints_pos[0] and convoy_pos[1] == checkpoints_pos[1]:
        checkpoints += 1
        checkpoints_spawn = False
        SUPPLIED.play()
    else:
        convoy_body.pop()

        
    # Spawning checkpoints
    if not checkpoints_spawn:
        checkpoints_pos = random_pos()
        submarines.insert(0,random_pos()) # Spawn Submarine
    checkpoints_spawn = True

    # Checkpoints
    pygame.draw.rect(game_window, WHITE, pygame.Rect(checkpoints_pos[0], checkpoints_pos[1], PIXEL_SIZE, PIXEL_SIZE))

    
    # Emit sonar every 3 seconds
    current_ticks = pygame.time.get_ticks()
    if current_ticks - emit_start_ticks >= emit_duration:
        pulse_done = False
        last_convoy_pos = list(convoy_pos)
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
        pygame.draw.circle(game_window,(0, 255, 0), last_convoy_pos, int(radius), 3)

        for submarine_pos in submarines:
            if detect_collision(last_convoy_pos[0], last_convoy_pos[1], radius, submarine_pos[0], submarine_pos[1]):
                pygame.draw.rect(game_window, RED, pygame.Rect(submarine_pos[0], submarine_pos[1], PIXEL_SIZE, PIXEL_SIZE))
        
    # Game Over conditions
    # Touching the Convoy body
    for block in convoy_body[1:]:
        if convoy_pos[0] == block[0] and convoy_pos[1] == block[1]:
            game_over()


    # Touching Submarine
    for submarine_pos in submarines:
        if convoy_pos[0] == submarine_pos[0] and convoy_pos[1] == submarine_pos[1]:
            # convoy_body.pop()
            HIT.play()
            game_over()
            # if convoy_body == []:
            #     game_over()



    # Show checkpoints and speed value
    show_checkpoints()
    show_speed()
    

    # Refresh game screen
    pygame.display.update()

    # Refresh rate
    FPS_CONTROLLER.tick(speed)