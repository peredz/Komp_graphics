import pygame
import math
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Fractal Skeleton")

def draw_skeleton(x, y, size, angle, depth):
    if depth == 0 or size < 2:
        return

    # Вычисляем конец ветки
    rad = math.radians(angle)
    nx = x + size * math.sin(rad)
    ny = y - size * math.cos(rad)

    # Рисуем линию (скелет)
    color = (60, 40, 20) if depth > 4 else (34, 139, 34)
    pygame.draw.line(screen, color, (x, y), (nx, ny), max(1, depth))

    # Случайные параметры для естественности
    left_angle = random.uniform(15, 45)
    right_angle = random.uniform(15, 45)
    scale = random.uniform(0.7, 0.8)

    # Рекурсия
    draw_skeleton(nx, ny, size * scale, angle - left_angle, depth - 1)
    draw_skeleton(nx, ny, size * scale, angle + right_angle, depth - 1)

# Генерация один раз или в цикле
screen.fill((240, 240, 240))
draw_skeleton(400, 550, 120, 0, 12)
pygame.display.flip()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
pygame.quit()