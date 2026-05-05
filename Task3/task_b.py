import pygame
import math
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))

def draw_fract(x, y, size, angle, depth):
    screen.fill((240, 240, 240))
    draw_skeleton(x, y, size, angle, depth)

def draw_skeleton(x, y, size, angle, depth):
    if depth == 0 or size < 2:
        return

    # конец ветки
    rad = math.radians(angle)
    nx = x + size * math.sin(rad)
    ny = y - size * math.cos(rad)

    color = (60, 40, 20) if depth > 4 else (34, 139, 34)
    pygame.draw.line(screen, color, (x, y), (nx, ny), 1)

    # случайные параметры
    left_angle = random.uniform(15, 45)
    right_angle = random.uniform(15, 45)
    scale = random.uniform(0.7, 0.8)

    draw_skeleton(nx, ny, size * scale, angle - left_angle, depth - 1)
    draw_skeleton(nx, ny, size * scale, angle + right_angle, depth - 1)

draw_fract(400, 550, 120, 0, 12)
pygame.display.flip()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                draw_fract(400, 550, 120, 0, 12)
                pygame.display.flip()

pygame.quit()