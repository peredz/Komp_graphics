import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))


def generate_star_poly(n, center, r_outer, r_inner):
    points = []
    # 2*N вершин
    for i in range(2 * n):
        angle = i * (math.pi / n)
        # чередование радиуса
        r = r_outer if i % 2 == 0 else r_inner
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points


star_points = generate_star_poly(13, (400, 300), 200, 100)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

    screen.fill((255, 255, 255))
    pygame.draw.polygon(screen, (255, 215, 0), star_points)

    pygame.display.flip()

pygame.quit()