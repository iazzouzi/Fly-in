import pygame

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Fly-in")

r = True
while r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            r = False
    screen.fill('white')
    pygame.draw.circle(screen, 'red', pygame.Vector2(1920/2, 1080/2), 30)
    pygame.display.flip()


pygame.quit()