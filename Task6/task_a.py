import pygame
import math


WIDTH, HEIGHT = 800, 600
SCALE = 120
CENTER = (WIDTH // 2, HEIGHT // 2)


def rotate_y(point, angle):
    x, y, z = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    x_new = x * cos_a + z * sin_a
    y_new = y
    z_new = -x * sin_a + z * cos_a

    return (x_new, y_new, z_new)


def project(point):
    x, y, z = point
    x_screen = int(x * SCALE + CENTER[0])
    y_screen = int(-y * SCALE + CENTER[1])
    return (x_screen, y_screen)


cube_vertices = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1)
]

cube_edges = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7)
]


oct_vertices = [
    (1,0,0), (-1,0,0),
    (0,1,0), (0,-1,0),
    (0,0,1), (0,0,-1)
]

oct_edges = [
    (0,2),(0,3),(0,4),(0,5),
    (1,2),(1,3),(1,4),(1,5),
    (2,4),(4,3),(3,5),(5,2)
]


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

angle = 0
current_shape = "cube"

running = True
while running:
    clock.tick(60)
    angle += 0.01

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_shape = "oct" if current_shape == "cube" else "cube"

    screen.fill((255,255,255))

    if current_shape == "cube":
        vertices = cube_vertices
        edges = cube_edges
        color = (0,0,255)
    else:
        vertices = oct_vertices
        edges = oct_edges
        color = (200,0,0)

    rotated = [rotate_y(v, angle) for v in vertices]

    projected = [project(v) for v in rotated]

    for edge in edges:
        pygame.draw.line(screen, color,
                         projected[edge[0]],
                         projected[edge[1]], 2)

    pygame.display.flip()

pygame.quit()