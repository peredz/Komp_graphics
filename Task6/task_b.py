import pygame
import math


WIDTH, HEIGHT = 900, 700
CENTER = (WIDTH // 2, HEIGHT // 2)
SCALE = 120
DISTANCE = 4  # расстояние камеры

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def rotate_x(point, angle):
    x, y, z = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    y_new = y * cos_a - z * sin_a
    z_new = y * sin_a + z * cos_a
    return (x, y_new, z_new)

def rotate_y(point, angle):
    x, y, z = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    x_new = x * cos_a + z * sin_a
    z_new = -x * sin_a + z * cos_a
    return (x_new, y, z_new)

# Перспективная проекция
def project(point):
    x, y, z = point
    factor = DISTANCE / (z + DISTANCE)
    x_proj = x * factor
    y_proj = y * factor

    x_screen = int(x_proj * SCALE + CENTER[0])
    y_screen = int(-y_proj * SCALE + CENTER[1])
    return (x_screen, y_screen)


def create_cylinder(radius=1, height=2, segments=20):
    vertices = []
    edges = []

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        vertices.append((x, -height/2, z))  # нижний круг
        vertices.append((x, height/2, z))   # верхний круг

    for i in range(segments):
        next_i = (i + 1) % segments
        edges.append((2*i, 2*next_i))         # нижний круг
        edges.append((2*i+1, 2*next_i+1))     # верхний круг
        edges.append((2*i, 2*i+1))            # боковые рёбра

    return vertices, edges

def create_cone(radius=1, height=2, segments=20):
    vertices = []
    edges = []

    # основание
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        vertices.append((x, -height/2, z))

    apex = (0, height/2, 0)
    vertices.append(apex)
    apex_index = len(vertices) - 1

    for i in range(segments):
        next_i = (i + 1) % segments
        edges.append((i, next_i))         # основание
        edges.append((i, apex_index))     # боковые рёбра

    return vertices, edges

def create_pyramid(size=1.5, height=2):
    vertices = [
        (-size, -height/2, -size),
        ( size, -height/2, -size),
        ( size, -height/2,  size),
        (-size, -height/2,  size),
        (0, height/2, 0)
    ]

    edges = [
        (0,1),(1,2),(2,3),(3,0),  # основание
        (0,4),(1,4),(2,4),(3,4)   # боковые
    ]

    return vertices, edges


cyl_v, cyl_e = create_cylinder()
cone_v, cone_e = create_cone()
pyr_v, pyr_e = create_pyramid()

shapes = [
    ("Cylinder", cyl_v, cyl_e, (0,0,255)),
    ("Cone", cone_v, cone_e, (200,0,0)),
    ("Pyramid", pyr_v, pyr_e, (0,150,0))
]

shape_index = 0

angle_x = 0
angle_y = 0


running = True
while running:
    clock.tick(60)

    angle_x += 0.01
    angle_y += 0.013

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shape_index = (shape_index + 1) % len(shapes)

    screen.fill((255,255,255))

    name, vertices, edges, color = shapes[shape_index]

    transformed = []
    for v in vertices:
        r = rotate_x(v, angle_x)
        r = rotate_y(r, angle_y)
        transformed.append(r)

    projected = [project(v) for v in transformed]

    for edge in edges:
        pygame.draw.line(screen, color,
                         projected[edge[0]],
                         projected[edge[1]], 2)

    pygame.display.flip()

pygame.quit()