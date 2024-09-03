import pygame
pygame.init()

win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Draw Line Function in Pygame")

run = True
while run:
    for i in range(0, 500, 20):
        pygame.draw.line(win, (255,255,255), (0, i), (500, i), 10)
        pygame.draw.line(win, (255,255,255), (i, 0), (i, 500), 10)
    pygame.display.flip()
pygame.quit()
