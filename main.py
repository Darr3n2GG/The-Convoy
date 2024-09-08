import pygame, sys, time, random, math

pygame.init()

# Constants
FONT_PATH = './font/AtkinsonHyperlegible-Regular.ttf'
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
FRAME_SIZE_X = 500
FRAME_SIZE_Y = 500
PIXEL_SIZE = 10
FPS_CONTROLLER = pygame.time.Clock()

# Constants for sound
pygame.mixer.init(44100, -16, 2, 512)
SONAR = pygame.mixer.Sound('./soundpack/sonar.mp3')
HIT = pygame.mixer.Sound('./soundpack/explode.mp3')
SUPPLIED = pygame.mixer.Sound('./soundpack/repair.mp3')

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = 10

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

#  ------------------------------------------------------------------------- Functions -------------------------------------------------------------------------  #

# Game over screen and auto-close
def game_over():
    HIT.play()
    time.sleep(3)
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
    checkpoint_surface = checkpoint_font.render('Checkpoints : ' + str(checkpoints_reached), True, WHITE)
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

def detect_collision(cx, cy, sonar_radius, px, py):
    # Calculate the distance between the circle center and the point
    distance = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
    # Check if the distance is less than or equal to the sonar_radius
    return distance <= sonar_radius

def set_convoy_body(x, y):
    i = 0
    start_pos = []
    while i < convoy_start_size:
        start_pos.insert(i - 1, [x - 10*i, y])
        i += 1
    return start_pos

# Generates a random position
def random_pos(x, y):
    return [random.randrange(1, (x//10)) * 10, random.randrange(1, (y//10)) * 10]

# Returns a new list of random positions based on frame size
def change_pos_depend_overlappping_body(overlapping_body):
    pos = random_pos(FRAME_SIZE_X, FRAME_SIZE_Y)
    while pos in convoy_body: #repeats generating the random position when it is occupied by player or another body
        pos = random_pos(FRAME_SIZE_X, FRAME_SIZE_Y)
    if overlapping_body != None:
        while pos in overlapping_body:
            pos = random_pos(FRAME_SIZE_X,FRAME_SIZE_Y)
    return pos

#  ------------------------------------------------------------------------- Variables -------------------------------------------------------------------------  #

# Speed settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = 10

# Convoy
convoy_start_size = 3
convoy_pos = [FRAME_SIZE_X/2, FRAME_SIZE_Y/2]
convoy_body = set_convoy_body(convoy_pos[0], convoy_pos[1])
last_convoy_pos = [0,0]
direction = 'RIGHT'
change_to = direction

# checkpoints
checkpoints_pos = [convoy_pos[0] + 100, convoy_pos[1]]
checkpoints_spawn = True
checkpoints_reached = 0

# Submarines
submarines = []
submarine_limit = 2000

# Sonar
sonar_start_ticks = pygame.time.get_ticks()
sonar_emit_duration = 3000
sonar_pulse_done = True
sonar_time_passed = 0
sonar_alive_duration = 1
sonar_radius = 0

#  -------------------------------------------------------------------------------------------------------------------------------------------------------------  #


#  ------------------------------------------------------------------------- Main Logic -------------------------------------------------------------------------  #

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

    # Grid
    for i in range(0, FRAME_SIZE_X + 1, 50):
        pygame.draw.line(game_window, GREEN, (0, i), (FRAME_SIZE_X, i))
    for i in range(0, FRAME_SIZE_Y + 1, 50):
        pygame.draw.line(game_window, GREEN, (i, 0), (i, FRAME_SIZE_Y))

    # Convoy movements
    if direction == 'UP':
        convoy_pos[1] -= PIXEL_SIZE
    if direction == 'DOWN':
        convoy_pos[1] += PIXEL_SIZE
    if direction == 'LEFT':
        convoy_pos[0] -= PIXEL_SIZE
    if direction == 'RIGHT':
        convoy_pos[0] += PIXEL_SIZE
        
    # # Teleportation logic
    # if convoy_pos[0] < 0:
    #     convoy_pos[0] = FRAME_SIZE_X - PIXEL_SIZE
    # if convoy_pos[0] >= FRAME_SIZE_X:
    #     convoy_pos[0] = 0
    # if convoy_pos[1] < 0:
    #     convoy_pos[1] = FRAME_SIZE_Y - PIXEL_SIZE
    # if convoy_pos[1] >= FRAME_SIZE_Y:
    #     convoy_pos[1] = 0

    # Convoy body growing mechanism
    convoy_body.insert(0, list(convoy_pos))
    if convoy_pos[0] == checkpoints_pos[0] and convoy_pos[1] == checkpoints_pos[1]:
        checkpoints_reached += 1
        checkpoints_spawn = False
        SUPPLIED.play()
    else:
        convoy_body.pop()

    # Draw convoy body (Code must be located here in oder to avoid visual bug when drawing body)
    for pos in convoy_body:
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], PIXEL_SIZE, PIXEL_SIZE))
        
    # After reaching checkpoints
    if not checkpoints_spawn:
        if len(submarines) <= submarine_limit:
            submarines.insert(0,change_pos_depend_overlappping_body(None)) # Spawn Submarine
        for submarine_pos in submarines:
            checkpoints_pos = change_pos_depend_overlappping_body(submarine_pos) # Change checkpoint position
    checkpoints_spawn = True

    # Checkpoints
    pygame.draw.rect(game_window, WHITE, pygame.Rect(checkpoints_pos[0], checkpoints_pos[1], PIXEL_SIZE, PIXEL_SIZE))
    
    # Emit sonar
    current_ticks = pygame.time.get_ticks()
    if current_ticks - sonar_start_ticks >= sonar_emit_duration:
        for i in range(len(submarines)):
            submarines[i] = change_pos_depend_overlappping_body(checkpoints_pos)
        # Ready for next sonar cycle
        sonar_start_ticks = current_ticks
        last_convoy_pos = list(convoy_pos)
        SONAR.play()
        sonar_pulse_done = False

    # Sonar animation
    if not sonar_pulse_done:    
        sonar_time_passed = (current_ticks - sonar_start_ticks) / 2000
        sonar_radius = int(FRAME_SIZE_X * sonar_time_passed)
        pygame.draw.circle(game_window, GREEN, last_convoy_pos, sonar_radius, 3)
        if sonar_time_passed > sonar_alive_duration: # Reset sonar
            sonar_pulse_done = True

        for submarine_pos in list(submarines):
            if detect_collision(last_convoy_pos[0], last_convoy_pos[1], sonar_radius, submarine_pos[0], submarine_pos[1]):
                pygame.draw.rect(game_window, RED, pygame.Rect(submarine_pos[0], submarine_pos[1], PIXEL_SIZE, PIXEL_SIZE))

#  -------------------------------------------------------------------------------------------------------------------------------------------------------------  #

        
#  -------------------------------------------------------------------- Game Over Conditions -------------------------------------------------------------------  #

    # Getting out of bounds
    if convoy_pos[0] < 0 or convoy_pos[0] > FRAME_SIZE_X - PIXEL_SIZE or convoy_pos[1] < 0 or convoy_pos[1] > FRAME_SIZE_Y - PIXEL_SIZE:
        game_over()

    # Touching the Convoy body
    for block in convoy_body[1:]:
        if convoy_pos[0] == block[0] and convoy_pos[1] == block[1]:
            game_over()

    # Touching Submarine
    for submarine_pos in submarines:
        if convoy_pos[0] == submarine_pos[0] and convoy_pos[1] == submarine_pos[1]:
            game_over()
            # convoy_body.pop()
            # HIT.play()
            # if convoy_body == []:
            #     game_over()

#  -------------------------------------------------------------------------------------------------------------------------------------------------------------  #

    # Show checkpoints and speed value
    show_checkpoints()
    show_speed()
    
    # Refresh game screen
    pygame.display.update()

    # Refresh rate
    FPS_CONTROLLER.tick(speed)