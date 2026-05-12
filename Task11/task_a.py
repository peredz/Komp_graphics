import pygame
import math
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    weight: float = 1.0
    selected: bool = False


def binomial(n, k):
    if k == 0 or k == n:
        return 1
    result = 1
    for i in range(1, k + 1):
        result = result * (n - i + 1) // i
    return result


def bernstein(i, n, t):
    return binomial(n, i) * (t ** i) * ((1 - t) ** (n - i))


def bezier_point(points, t):
    x = y = 0
    n = len(points) - 1
    for i, p in enumerate(points):
        b = bernstein(i, n, t)
        x += b * p.x
        y += b * p.y
    return (x, y)


def draw_curve(surface, points, color=(0, 255, 0), steps=400):
    if len(points) < 2:
        return

    curve = []
    for i in range(steps + 1):
        t = i / steps
        x, y = bezier_point(points, t)
        curve.append((int(x), int(y)))

    if len(curve) > 1:
        pygame.draw.lines(surface, color, False, curve, 2)  # исправлено


def draw_polygon(surface, points, color=(100, 100, 100)):
    if len(points) < 2:
        return

    poly = [(int(p.x), int(p.y)) for p in points]
    pygame.draw.lines(surface, color, False, poly, 1)  # исправлено


def draw_points(surface, points):
    for p in points:
        color = (255, 255, 0) if p.selected else (255, 0, 0)
        pygame.draw.circle(surface, color, (int(p.x), int(p.y)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(p.x), int(p.y)), 6, 2)


def get_point_at(points, x, y):
    for i, p in enumerate(points):
        dx, dy = p.x - x, p.y - y
        if math.sqrt(dx * dx + dy * dy) < 10:
            return i
    return -1


def task_a():
    pygame.init()
    WIDTH, HEIGHT = 800, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task A - Bezier Curve")
    clock = pygame.time.Clock()

    points = [
        Point(200, 600),
        Point(200, 200),
        Point(600, 200),
        Point(600, 600)
    ]

    dragged = -1
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragged = get_point_at(points, *event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                dragged = -1
            elif event.type == pygame.MOUSEMOTION:
                if dragged != -1:
                    points[dragged].x = event.pos[0]
                    points[dragged].y = event.pos[1]

        screen.fill((30, 30, 40))

        draw_polygon(screen, points)
        draw_curve(screen, points)
        draw_points(screen, points)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    task_a()