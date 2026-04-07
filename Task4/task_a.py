import pygame
import math
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


def generate_convex_poly(n, center_x, center_y, a, b):
    # Генерируем N случайных углов и сортируем для выпуклости
    # angles = sorted([random.uniform(0, 2 * math.pi) for _ in range(n)])
    angles = [i * (2 * math.pi / n) for i in range(n)]

    
    points = []
    for angle in angles:
        # Уравнение эллипса: x = a*cos(t), y = b*sin(t)
        x = center_x + a * math.cos(angle)
        y = center_y + b * math.sin(angle)
        points.append((x, y))
    return points


# Параметры: N=13, центр (400,300), радиусы 250 и 150
polygon = generate_convex_poly(13, 400, 300, 250, 150)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill((255, 255, 255))

    # Рисуем сам полигон
    pygame.draw.polygon(screen, (50, 120, 200), polygon, 2)

    # Рисуем вершины (точки)
    for p in polygon:
        pygame.draw.circle(screen, (200, 50, 50), (int(p[0]), int(p[1])), 4)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()