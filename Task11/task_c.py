import pygame
import math
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    weight: float = 1.0
    selected: bool = False


class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial):
        self.x = x
        self.y = y
        self.width = width
        self.height = 10
        self.min_val = min_val
        self.max_val = max_val
        self.current = initial
        self.dragging = False
        self.handle_width = 15
        self.handle_height = 20

    def get_handle_x(self):
        t = (self.current - self.min_val) / (self.max_val - self.min_val)
        return self.x + t * self.width

    def handle_mouse_press(self, x, y):
        hx = self.get_handle_x()
        if abs(x - hx) < self.handle_width and abs(y - self.y) < self.handle_height:
            self.dragging = True
            return True
        return False

    def handle_mouse_release(self):
        self.dragging = False

    def handle_mouse_move(self, x):
        if self.dragging:
            x = max(self.x, min(self.x + self.width, x))
            t = (x - self.x) / self.width
            self.current = self.min_val + t * (self.max_val - self.min_val)

    def set_value(self, val):
        self.current = max(self.min_val, min(self.max_val, val))

    def draw(self, surface):
        pygame.draw.rect(surface, (80, 80, 80), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height), 1)

        hx = self.get_handle_x()
        pygame.draw.rect(
            surface,
            (255, 255, 0),
            (hx - self.handle_width // 2,
             self.y - self.handle_height // 2 + self.height // 2,
             self.handle_width,
             self.handle_height)
        )
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (hx - self.handle_width // 2,
             self.y - self.handle_height // 2 + self.height // 2,
             self.handle_width,
             self.handle_height),
            2
        )


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
    x = y = 0.0
    n = len(points) - 1
    for i, p in enumerate(points):
        b = bernstein(i, n, t)
        x += b * p.x
        y += b * p.y
    return (x, y)


def rational_bezier_point(points, t):
    numerator_x = numerator_y = denominator = 0.0
    n = len(points) - 1

    for i, p in enumerate(points):
        b = bernstein(i, n, t) * p.weight
        numerator_x += b * p.x
        numerator_y += b * p.y
        denominator += b

    if denominator != 0:
        return (numerator_x / denominator, numerator_y / denominator)
    return (0, 0)


def draw_curve(surface, points, curve_func, color=(0, 255, 0), steps=400):
    if len(points) < 2:
        return

    curve = []
    for i in range(steps + 1):
        t = i / steps
        x, y = curve_func(points, t)
        curve.append((int(x), int(y)))

    if len(curve) > 1:
        pygame.draw.lines(surface, color, False, curve, 2)  # ✅ FIX


def draw_polygon(surface, points, color=(100, 100, 100)):
    if len(points) < 2:
        return

    poly = [(int(p.x), int(p.y)) for p in points]
    pygame.draw.lines(surface, color, False, poly, 1)  # ✅ FIX


def draw_points(surface, points):
    for p in points:
        color = (255, 255, 0) if p.selected else (255, 0, 0)
        pygame.draw.circle(surface, color, (int(p.x), int(p.y)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(p.x), int(p.y)), 6, 2)


def get_point_at(points, x, y):
    for i, p in enumerate(points):
        if math.hypot(p.x - x, p.y - y) < 10:
            return i
    return -1


def task_c():
    pygame.init()
    WIDTH, HEIGHT = 800, 850
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task C - Rational Bezier (NURBS)")
    clock = pygame.time.Clock()

    points = [
        Point(200, 600, 1.0),
        Point(200, 200, 1.0),
        Point(600, 200, 1.0),
        Point(600, 600, 1.0)
    ]

    font = pygame.font.Font(None, 20)
    weight_slider = Slider(50, 780, 700, 0.1, 5.0, 1.0)

    dragged = -1
    selected = -1
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if weight_slider.handle_mouse_press(*event.pos):
                    pass
                else:
                    clicked = get_point_at(points, *event.pos)
                    if clicked != -1:
                        dragged = clicked
                        selected = clicked
                        for p in points:
                            p.selected = False
                        points[selected].selected = True
                        weight_slider.set_value(points[selected].weight)

            elif event.type == pygame.MOUSEBUTTONUP:
                dragged = -1
                weight_slider.handle_mouse_release()

            elif event.type == pygame.MOUSEMOTION:
                if dragged != -1:
                    points[dragged].x = event.pos[0]
                    points[dragged].y = event.pos[1]

                weight_slider.handle_mouse_move(event.pos[0])

                if selected != -1 and weight_slider.dragging:
                    points[selected].weight = weight_slider.current

        screen.fill((30, 30, 40))

        draw_polygon(screen, points)
        draw_curve(screen, points, bezier_point, (100, 100, 100))
        draw_curve(screen, points, rational_bezier_point, (0, 255, 0))
        draw_points(screen, points)
        weight_slider.draw(screen)

        label = f"Weight: {weight_slider.current:.2f}" if selected != -1 else "Select a point"
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (50, 750))

        text2 = font.render("Green: Rational Bezier | Gray: Regular Bezier", True, (200, 200, 200))
        screen.blit(text2, (50, 820))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    task_c()