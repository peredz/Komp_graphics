import pygame
import math
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


def generate_oval_poly(n, center_x, center_y, a, b):
    angles = [i * (2 * math.pi / n) for i in range(n)]
    points = []
    for angle in angles:
        x = center_x + a * math.cos(angle)
        y = center_y + b * math.sin(angle)
        points.append((x, y))
    return points


def draw_triangulation(surface, points, color):
    if len(points) < 3:
        return

    v0 = points[0]

    # Рисуем треугольники: (v0, v_i, v_{i+1})
    for i in range(1, len(points) - 1):
        v1 = points[i]
        v2 = points[i + 1]

        pygame.draw.line(surface, color, v0, v2, 1)

        pygame.draw.polygon(
            surface,
            (random.randint(0,255),random.randint(0,255),random.randint(0,255)),
            [v0, v1, v2]
        )


polygon = generate_oval_poly(13, 400, 300, 250, 150)

screen.fill((255, 255, 255))

draw_triangulation(screen, polygon, (200, 200, 200))

pygame.draw.polygon(screen, (50, 120, 200), polygon, 3)

pygame.draw.circle(screen, (0, 200, 0), (int(polygon[0][0]), int(polygon[0][1])), 7)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    pygame.display.flip()
    clock.tick(30)

pygame.quit()