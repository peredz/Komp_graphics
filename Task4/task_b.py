import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))


def generate_star_poly(n, center, r_outer, r_inner):
    points = []
    # Всего будет 2*N вершин (N внешних и N внутренних)
    for i in range(2 * n):
        angle = i * (math.pi / n)
        # Чередуем радиус: для четных i — внешний, для нечетных — внутренний
        r = r_outer if i % 2 == 0 else r_inner
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points


# N=13 (лучей), внешний радиус 200, внутренний 100
star_points = generate_star_poly(13, (400, 300), 200, 100)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

    screen.fill((255, 255, 255))
    pygame.draw.polygon(screen, (255, 215, 0), star_points)  # Золотой цвет
    pygame.draw.polygon(screen, (0, 0, 0), star_points, 2)  # Контур

    pygame.display.flip()

pygame.quit()