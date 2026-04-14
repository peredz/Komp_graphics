import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


def draw_tree(x, y, size, angle, depth):
    if depth == 0:
        return

    # вершины нового квадрата
    rad = math.radians(angle)
    rad_up = math.radians(angle - 90)

    x1 = x + size * math.cos(rad_up)
    y1 = y + size * math.sin(rad_up)
    x2 = x1 + size * math.cos(rad)
    y2 = y1 + size * math.sin(rad)
    x3 = x + size * math.cos(rad)
    y3 = y + size * math.sin(rad)

    color = "green"
    pygame.draw.polygon(screen, color, [(x, y), (x1, y1), (x2, y2), (x3, y3)])

    new_size = size * (math.sqrt(2) / 2)

    # левое ответвление
    draw_tree(x1, y1, new_size, angle - 45, depth - 1)

    # правое ответвление
    tx = x1 + new_size * math.cos(math.radians(angle - 45))
    ty = y1 + new_size * math.sin(math.radians(angle - 45))
    draw_tree(tx, ty, new_size, angle + 45, depth - 1)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill((255, 255, 255))
    draw_tree(350, 550, 100, 0, 10)
    pygame.display.flip()
    clock.tick(1)

pygame.quit()