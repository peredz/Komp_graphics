import pygame
import math


def generate_butterfly(n, center, scale):
    points = []
    for i in range(n):
        t = i * (2 * math.pi / n)

        x = center[0] + scale * math.sin(t)
        y = center[1] + scale * math.sin(t) * math.cos(t)
        points.append((x, y))
    return points

pygame.init()
screen = pygame.display.set_mode((800, 600))
poly_points = generate_butterfly(100, (400, 300), 250)

screen.fill((255, 255, 255))

pygame.draw.lines(screen, (150, 50, 200), True, poly_points, 2)
pygame.display.flip()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

pygame.quit()