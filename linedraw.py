import pygame
pygame.init()

win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Draw Line Function in Pygame")

run = True
while run:
    pygame.time.delay(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
    mouse_pos = pygame.mouse.get_pos()
    win.fill((0,0,0))
    pygame.draw.line(win, (0,255,0), (250, 250), mouse_pos, 3)
    pygame.display.update()
pygame.quit()