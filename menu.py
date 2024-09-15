import pygame, sys

pygame.init()

BLACK = pygame.Color(0, 0, 0)

FRAME_SIZE_X = 500
FRAME_SIZE_Y = 500
FPS_CONTROLLER = pygame.time.Clock()
game_window = pygame.display.set_mode((FRAME_SIZE_X + 1, FRAME_SIZE_Y + 1))

# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print('[!] Had {check_errors[1]} errors when initialising menu, exiting...')
    sys.exit(-1)
else:
    print('[+] Menu successfully initialised')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    game_window.fill(BLACK)
    pygame.display.update()
    FPS_CONTROLLER.tick(60)
