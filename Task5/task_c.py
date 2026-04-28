import pygame
import math


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

def polygon_area(poly):
    area = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    return area / 2

def is_point_in_triangle(p, a, b, c):
    d1 = cross(p, a, b)
    d2 = cross(p, b, c)
    d3 = cross(p, c, a)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)

def is_convex(prev, curr, nxt):
    return cross(prev, curr, nxt) > 0

def merge_holes(outer, holes):

    if polygon_area(outer) < 0:
        outer.reverse()

    combined = outer[:]

    for hole in holes:

        if polygon_area(hole) > 0:
            hole.reverse()

        # 1️⃣ самая правая точка отверстия
        rightmost = max(hole, key=lambda p: p[0])
        hole_index = hole.index(rightmost)

        # ближайшая точка внешнего контура справа
        min_dist = float("inf")
        outer_index = 0

        for i, p in enumerate(combined):
            if p[0] > rightmost[0]:
                dist = (p[0] - rightmost[0]) ** 2 + (p[1] - rightmost[1]) ** 2
                if dist < min_dist:
                    min_dist = dist
                    outer_index = i

        # если справа нет точек - берём просто ближайшую
        if min_dist == float("inf"):
            for i, p in enumerate(combined):
                dist = (p[0] - rightmost[0]) ** 2 + (p[1] - rightmost[1]) ** 2
                if dist < min_dist:
                    min_dist = dist
                    outer_index = i

        new_poly = []

        # до точки моста
        for i in range(outer_index + 1):
            new_poly.append(combined[i])

        # мост в отверстие
        new_poly.append(rightmost)

        # обход отверстия
        hole_cycle = hole[hole_index:] + hole[:hole_index]
        for p in hole_cycle[1:]:
            new_poly.append(p)

        new_poly.append(rightmost)

        for i in range(outer_index, len(combined)):
            new_poly.append(combined[i])

        combined = new_poly

    return combined

def triangulate(polygon):

    vertices = polygon[:]
    triangles = []

    limit = len(vertices) ** 2
    counter = 0

    while len(vertices) > 2 and counter < limit:
        counter += 1

        for i in range(len(vertices)):

            prev = vertices[i - 1]
            curr = vertices[i]
            nxt = vertices[(i + 1) % len(vertices)]

            if not is_convex(prev, curr, nxt):
                continue

            ear = True
            for p in vertices:
                if p in (prev, curr, nxt):
                    continue
                if is_point_in_triangle(p, prev, curr, nxt):
                    ear = False
                    break

            if ear:
                triangles.append((prev, curr, nxt))
                vertices.pop(i)
                break

    return triangles

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

outer_poly = [(100, 100), (100, 500), (700, 500), (700, 100)]
hole1 = [(200, 200), (500, 200), (500, 400), (200, 400)]

merged = merge_holes(outer_poly, [hole1])
mesh = triangulate(merged)

print("Количество треугольников:", len(mesh))

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    for tri in mesh:
        pygame.draw.polygon(screen, (200, 220, 255), tri)
        pygame.draw.polygon(screen, (100, 100, 100), tri, 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()