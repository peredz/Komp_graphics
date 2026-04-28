import pygame
import math

WIDTH, HEIGHT = 900, 700
CENTER = (WIDTH // 2, HEIGHT // 2)

FOCAL_LENGTH = 600
SCALE = 250

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# -------------------------------------------------
# Вращения
# -------------------------------------------------
def rotate_x(p, angle):
    x, y, z = p
    c = math.cos(angle)
    s = math.sin(angle)
    return (x,
            y * c - z * s,
            y * s + z * c)

def rotate_y(p, angle):
    x, y, z = p
    c = math.cos(angle)
    s = math.sin(angle)
    return (x * c + z * s,
            y,
            -x * s + z * c)

# -------------------------------------------------
# Перспективная проекция
# -------------------------------------------------
def project(p):
    x, y, z = p
    z += 3  # отодвигаем объект от камеры

    factor = FOCAL_LENGTH / z
    x_proj = x * factor + CENTER[0]
    y_proj = -y * factor + CENTER[1]
    return (int(x_proj), int(y_proj))

# -------------------------------------------------
# Сфера
# -------------------------------------------------
def create_sphere(radius=1, lat_steps=20, lon_steps=20):
    vertices = []
    faces = []

    for i in range(lat_steps + 1):
        theta = math.pi * i / lat_steps
        for j in range(lon_steps):
            phi = 2 * math.pi * j / lon_steps

            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.cos(theta)
            z = radius * math.sin(theta) * math.sin(phi)

            vertices.append((x, y, z))

    for i in range(lat_steps):
        for j in range(lon_steps):
            next_j = (j + 1) % lon_steps

            p1 = i * lon_steps + j
            p2 = i * lon_steps + next_j
            p3 = (i + 1) * lon_steps + j
            p4 = (i + 1) * lon_steps + next_j

            faces.append((p1, p2, p3))
            faces.append((p2, p4, p3))

    return vertices, faces

vertices, faces = create_sphere()

angle_x = 0
angle_y = 0

# -------------------------------------------------
# Главный цикл
# -------------------------------------------------
running = True
while running:
    clock.tick(60)

    angle_x += 0.01
    angle_y += 0.013

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:
                FOCAL_LENGTH += 50
            if event.key == pygame.K_MINUS:
                FOCAL_LENGTH -= 50
                if FOCAL_LENGTH < 100:
                    FOCAL_LENGTH = 100

    screen.fill((255, 255, 255))

    # Трансформация вершин
    transformed = []
    for v in vertices:
        r = rotate_x(v, angle_x)
        r = rotate_y(r, angle_y)
        transformed.append(r)

    # Painter's algorithm (сортировка по глубине)
    face_list = []
    for face in faces:
        pts = [transformed[i] for i in face]
        avg_z = sum(p[2] for p in pts) / 3
        face_list.append((avg_z, face))

    # сортируем от дальних к ближним
    face_list.sort(reverse=True)

    for avg_z, face in face_list:
        pts_3d = [transformed[i] for i in face]

        # Back-face culling
        v1 = pts_3d[1]
        v0 = pts_3d[0]
        v2 = pts_3d[2]

        normal_z = (
            (v1[0] - v0[0]) * (v2[1] - v0[1]) -
            (v1[1] - v0[1]) * (v2[0] - v0[0])
        )

        if normal_z > 0:
            continue  # задняя грань

        pts_2d = [project(p) for p in pts_3d]

        color = (120, 170, 255)
        pygame.draw.polygon(screen, color, pts_2d)
        pygame.draw.polygon(screen, (50, 50, 100), pts_2d, 1)

    pygame.display.flip()

pygame.quit()