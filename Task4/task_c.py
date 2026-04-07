import pygame
import math

def generate_spiral(n, center, max_r):
    points = []
    for i in range(n):
        angle = i * (math.pi * 4 / n)  # 2 полных оборота (4*pi)
        r = (i / n) * max_r            # Радиус растет от 0 до max_r
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_butterfly(n, center, scale):
    points = []
    for i in range(n):
        t = i * (2 * math.pi / n)
        # Классическая параметризация для самопересечений
        x = center[0] + scale * math.sin(t)
        y = center[1] + scale * math.sin(t) * math.cos(t)
        points.append((x, y))
    return points

# Отрисовка (основной цикл аналогичен предыдущим)
pygame.init()
screen = pygame.display.set_mode((800, 600))
poly_points = generate_butterfly(100, (400, 300), 250)
# poly_points = generate_spiral(100, (400, 300), 250)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
    screen.fill((255, 255, 255))
    # Соединяем точки в порядке их генерации
    pygame.draw.lines(screen, (150, 50, 200), True, poly_points, 2)
    pygame.display.flip()
pygame.quit()