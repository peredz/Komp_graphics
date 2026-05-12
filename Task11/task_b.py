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


def b_spline_segment(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t

    b0 = (-t3 + 3 * t2 - 3 * t + 1) / 6.0
    b1 = (3 * t3 - 6 * t2 + 4) / 6.0
    b2 = (-3 * t3 + 3 * t2 + 3 * t + 1) / 6.0
    b3 = t3 / 6.0

    x = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]
    y = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]
    return (x, y)


def extend_b_spline(points):
    extended = [points[0]]
    extended.append(points[0])
    extended.extend(points)
    extended.append(points[-1])
    extended.append(points[-1])
    return extended


def b_spline_point(points, t):
    if len(points) < 2:
        return (0, 0)

    ext = extend_b_spline([(p.x, p.y) for p in points])
    segments = len(ext) - 3

    segment = t * segments
    seg_index = min(int(segment), segments - 1)
    local_t = segment - seg_index

    p0 = ext[seg_index]
    p1 = ext[seg_index + 1]
    p2 = ext[seg_index + 2]
    p3 = ext[seg_index + 3]

    return b_spline_segment(p0, p1, p2, p3, local_t)


def catmull_rom_segment(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t

    q0 = -t3 + 2 * t2 - t
    q1 = 3 * t3 - 5 * t2 + 2
    q2 = -3 * t3 + 4 * t2 + t
    q3 = t3 - t2

    x = 0.5 * (p0[0] * q0 + p1[0] * q1 + p2[0] * q2 + p3[0] * q3)
    y = 0.5 * (p0[1] * q0 + p1[1] * q1 + p2[1] * q2 + p3[1] * q3)
    return (x, y)


def extend_catmull(points):
    extended = [points[0]]
    extended.extend(points)
    extended.append(points[-1])
    return extended


def catmull_rom_point(points, t):
    if len(points) < 2:
        return (0, 0)

    ext = extend_catmull([(p.x, p.y) for p in points])
    segments = len(ext) - 3

    segment = t * segments
    i = min(int(segment), segments - 1)
    local_t = segment - i

    p0 = ext[i]
    p1 = ext[i + 1]
    p2 = ext[i + 2]
    p3 = ext[i + 3]

    return catmull_rom_segment(p0, p1, p2, p3, local_t)


def draw_curve(surface, points, curve_func, color=(0, 255, 0), steps=400):
    if len(points) < 2:
        return

    curve = []
    for i in range(steps + 1):
        t = i / steps
        x, y = curve_func(points, t)
        curve.append((int(x), int(y)))

    if len(curve) > 1:
        pygame.draw.lines(surface, color, False, curve, 2)  # <-- исправлено


def draw_polygon(surface, points, color=(100, 100, 100)):
    if len(points) < 2:
        return

    poly = [(int(p.x), int(p.y)) for p in points]
    pygame.draw.lines(surface, color, False, poly, 1)  # <-- исправлено


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


def task_b():
    pygame.init()
    WIDTH, HEIGHT = 800, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task B - Bezier, B-Spline, Catmull-Rom")
    clock = pygame.time.Clock()

    points = [
        Point(100, 400),
        Point(200, 200),
        Point(400, 300),
        Point(600, 200),
        Point(700, 500)
    ]

    font = pygame.font.Font(None, 24)
    curve_types = ["Bezier", "B-Spline", "Catmull-Rom"]
    curve_colors = [(0, 255, 0), (0, 255, 255), (255, 0, 255)]
    curve_funcs = [bezier_point, b_spline_point, catmull_rom_point]

    current_curve = 0
    dragged = -1
    selected = -1

    print("1 - Bezier, 2 - B-Spline, 3 - Catmull-Rom")
    print("Right Click - Add point, Delete - Remove point")

    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = get_point_at(points, *event.pos)
                    if clicked != -1:
                        dragged = clicked
                        selected = clicked
                        for p in points:
                            p.selected = False
                        points[selected].selected = True
                elif event.button == 3:
                    points.append(Point(event.pos[0], event.pos[1]))
            elif event.type == pygame.MOUSEBUTTONUP:
                dragged = -1
            elif event.type == pygame.MOUSEMOTION:
                if dragged != -1:
                    points[dragged].x = event.pos[0]
                    points[dragged].y = event.pos[1]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_curve = 0
                    print(f"Switched to: {curve_types[current_curve]}")
                elif event.key == pygame.K_2:
                    current_curve = 1
                    print(f"Switched to: {curve_types[current_curve]}")
                elif event.key == pygame.K_3:
                    current_curve = 2
                    print(f"Switched to: {curve_types[current_curve]}")
                elif event.key == pygame.K_DELETE and selected != -1:
                    points.pop(selected)
                    selected = -1

        screen.fill((30, 30, 40))

        draw_polygon(screen, points)
        if len(points) >= 2:  # для всех кривых нужно минимум 2 точки
            draw_curve(screen, points, curve_funcs[current_curve], curve_colors[current_curve])
        draw_points(screen, points)

        text = font.render(f"Curve: {curve_types[current_curve]} | Points: {len(points)}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    task_b()