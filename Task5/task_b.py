import pygame
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

def is_point_in_triangle(p, a, b, c):
    """Проверка, лежит ли точка p внутри треугольника abc"""

    def cross_product(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = cross_product(p, a, b)
    d2 = cross_product(p, b, c)
    d3 = cross_product(p, c, a)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


def is_convex(prev, curr, next_p):
    """Проверка, является ли вершина curr выпуклой"""

    val = (curr[0] - prev[0]) * (next_p[1] - curr[1]) - (curr[1] - prev[1]) * (next_p[0] - curr[0])
    return val > 0


def get_triangles_ear_clipping(polygon):
    """Алгоритм Ear Clipping"""

    vertices = list(polygon)
    triangles = []

    while len(vertices) > 3:
        ear_found = False
        for i in range(len(vertices)):
            prev = vertices[i - 1]
            curr = vertices[i]
            next_p = vertices[(i + 1) % len(vertices)]

            if is_convex(prev, curr, next_p):
                # внутри треугольника не должно быть других вершин
                is_ear = True
                for j in range(len(vertices)):
                    p = vertices[j]
                    if p in (prev, curr, next_p):
                        continue
                    if is_point_in_triangle(p, prev, curr, next_p):
                        is_ear = False
                        break

                if is_ear:
                    # нашли ухо - отрезаем
                    triangles.append((prev, curr, next_p))
                    vertices.pop(i)
                    ear_found = True
                    break

        if not ear_found:
            break

    # последний оставшийся треугольник
    if len(vertices) == 3:
        triangles.append(tuple(vertices))

    return triangles


polygon = [
    (100, 300), (200, 100), (300, 250), (400, 100),
    (500, 250), (600, 100), (700, 300), (600, 500),
    (400, 350), (200, 500)
]

triangulated_mesh = get_triangles_ear_clipping(polygon)

screen.fill((255, 255, 255))

for tri in triangulated_mesh:
    pygame.draw.polygon(
        screen,
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        tri,
        0)

# контур
pygame.draw.polygon(screen, (50, 120, 200), polygon, 3)

for p in polygon:
    pygame.draw.circle(screen, (200, 50, 50), (int(p[0]), int(p[1])), 5)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    pygame.display.flip()
    clock.tick(30)

pygame.quit()