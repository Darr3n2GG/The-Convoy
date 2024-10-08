import pygame, sys, time, random, math, json
import rand_pos

pygame.init()

with open('data.json') as f:
    data = json.load(f)
    FRAME_SIZE = data['frame_size']
    PIXEL_SIZE = data['pixel_size']
    DEFAULT_SPEED = data['default_speed']
    WINDOW_CAPTION = data['window_caption']

# Constants
FONT_PATH = './font/AtkinsonHyperlegible-Regular.ttf'
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
FRAME_SIZE_X = FRAME_SIZE['x']
FRAME_SIZE_Y = FRAME_SIZE['y']
FPS_CONTROLLER = pygame.time.Clock()

# Constants for sound
pygame.mixer.init(44100, -16, 2, 512)
SONAR = pygame.mixer.Sound('./soundpack/sonar.mp3')
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
pygame.display.set_caption(WINDOW_CAPTION)
game_window = pygame.display.set_mode((FRAME_SIZE_X + 1, FRAME_SIZE_Y + 1))
window_area = rand_pos.Area(FRAME_SIZE_X, FRAME_SIZE_Y, PIXEL_SIZE)

#  ------------------------------------------------------------------------- Functions -------------------------------------------------------------------------  #

# Helper function to render text
def render_text(text, font_path, font_size, color, position, position_type='midtop'):
    font = pygame.font.Font(font_path, font_size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    # Set the position type dynamically
    setattr(rect, position_type, position)

    game_window.blit(surface, rect)

# Game over screen with defeat message and checkpoints
def game_over():
    HIT.play() # add a toggle for enabling game logic to stop game

    # Render the "Defeat" message using render_text()
    game_window.fill(BLACK)
    render_text('Defeat', './font/Jacquard24-Regular.ttf', 100, RED, (FRAME_SIZE_X / 2, FRAME_SIZE_Y / 4))

    # Fill the screen and show checkpoints
    show_checkpoints()

    # Update the display
    pygame.display.flip()
    time.sleep(3)
    
    # Stop game
    global running
    running = False

# Show checkpoints reached by the convoy
def show_checkpoints():
    # Use the render_text() function for checkpoints display
    render_text(f'Checkpoints: {checkpoints_reached}', FONT_PATH, 20, WHITE, (10, 15), 'topleft')

# Show convoy's speed
def show_speed():
    # Use the render_text() function for speed display
    render_text(f'Speed: {speed}', FONT_PATH, 12, WHITE, (game_window.get_width() - 10, game_window.get_height() - 10), 'bottomright')

def detect_collision(cx, cy, sonar_radius, px, py):
    # Calculate the distance between the circle center and the point
    distance = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
    # Check if the distance is less than or equal to the sonar_radius
    return distance <= sonar_radius

def set_convoy_body(x, y):
    i = 0
    start_pos = []
    while i < convoy_start_size:
        start_pos.insert(i - 1, [x - PIXEL_SIZE*i, y])
        i += 1
    return start_pos

def add_submarine():
    if len(submarines) <= submarine_limit:
        submarines.insert(0,Submarine()) # Spawn Submarine

#  ------------------------------------------------------------------------- Variables -------------------------------------------------------------------------  #

# Speed settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
speed = DEFAULT_SPEED

class Entity():
    def __init__(self, pos: list[int], color: pygame.Color) -> None:
        self.pos = pos
        self.color = color
    def draw(self):
        pygame.draw.rect(game_window, self.color, pygame.Rect(self.pos[0], self.pos[1], PIXEL_SIZE, PIXEL_SIZE))

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
class Submarine(Entity):
    def __init__(self) -> None:
        random_pos = rand_pos.get_non_overlapping_pos(window_area, convoy_body)
        super().__init__(random_pos, RED)
        
    def reset_pos(self):
        overlapping_bodies = convoy_body.copy()
        overlapping_bodies.append(checkpoints_pos)
        random_pos = rand_pos.get_non_overlapping_pos(window_area, overlapping_bodies)
        self.pos = random_pos

    def show(self):
        self.draw()

submarines = []
submarine_limit = 2000
submarines_scanned = []

# Sonar        
sonar_emit_duration = 3000
sonar_pulse_done = True
sonar_alive_duration = 1
sonar_radius = 0
is_emit = pygame.USEREVENT + 1
sonar_timer = pygame.time.set_timer(is_emit, sonar_emit_duration, 0)

#  -------------------------------------------------------------------------------------------------------------------------------------------------------------  #


#  ------------------------------------------------------------------------- Main Logic -------------------------------------------------------------------------  #
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
        
        if event.type == is_emit:
            for i in range(len(submarines)):
                submarines[i].reset_pos()
            last_convoy_pos = convoy_pos.copy()
            submarines_scanned = submarines.copy()
            SONAR.play()
            sonar_start_ticks = pygame.time.get_ticks()
            sonar_pulse_done = False


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
    for i in range(0, FRAME_SIZE_Y + 1, 5*PIXEL_SIZE):
        # Draws a horizontal line every 50px towards height of window
        # .draw.line(play_surface, color, start_point, end_point)
        pygame.draw.line(game_window, GREEN, (0, i), (FRAME_SIZE_X, i))
    for i in range(0, FRAME_SIZE_X + 1, 5*PIXEL_SIZE):
        # Draws a vertical line every 50px towards width of window
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
    convoy_body.insert(0, convoy_pos.copy())
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
        add_submarine()
        overlapping_bodies = convoy_body.copy()
        for submarine in submarines:
            overlapping_bodies.append(submarine.pos)
        checkpoints_pos = rand_pos.get_non_overlapping_pos(window_area, overlapping_bodies) # Change checkpoint position
    checkpoints_spawn = True

    # Checkpoints
    pygame.draw.rect(game_window, WHITE, pygame.Rect(checkpoints_pos[0], checkpoints_pos[1], PIXEL_SIZE, PIXEL_SIZE))

    # Sonar animation
    current_ticks = pygame.time.get_ticks()
    if not sonar_pulse_done:
        sonar_time_passed = (current_ticks - sonar_start_ticks) / 2000
        sonar_radius = int(FRAME_SIZE_X * sonar_time_passed)
        pygame.draw.circle(game_window, GREEN, last_convoy_pos, sonar_radius, 3)
        if sonar_time_passed > sonar_alive_duration: # Reset sonar
            sonar_pulse_done = True

        for submarine in submarines_scanned:
            if detect_collision(last_convoy_pos[0], last_convoy_pos[1], sonar_radius, submarine.pos[0], submarine.pos[1]):
                submarine.show()

#  -------------------------------------------------------------------------------------------------------------------------------------------------------------  #

        
#  -------------------------------------------------------------------- Game Over Conditions -------------------------------------------------------------------  #

    # Getting out of bounds
    if convoy_pos[0] < 0 or convoy_pos[0] > FRAME_SIZE_X - PIXEL_SIZE or convoy_pos[1] < 0 or convoy_pos[1] > FRAME_SIZE_Y - PIXEL_SIZE:
        game_over()

    # Touching the Convoy body
    for body in convoy_body[1:]:
        if convoy_pos[0] == body[0] and convoy_pos[1] == body[1]:
            game_over()

    # Touching Submarine
    for submarine in submarines:
        if convoy_pos[0] == submarine.pos[0] and convoy_pos[1] == submarine.pos[1]:
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

# Close game
pygame.quit()
sys.exit()