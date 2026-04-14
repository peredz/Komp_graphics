import pygame
import math



def is_convex(prev, curr, next_p):
    # Векторное произведение для проверки выпуклости (обход против часовой)
    val = (curr[0] - prev[0]) * (next_p[1] - curr[1]) - (curr[1] - prev[1]) * (next_p[0] - curr[0])
    return val > 0


def is_point_in_triangle(p, a, b, c):
    def cross_product(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = cross_product(p, a, b)
    d2 = cross_product(p, b, c)
    d3 = cross_product(p, c, a)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


# --- Алгоритм объединения контуров ---

def merge_holes(outer, holes):
    """
    Соединяет отверстия с внешним контуром.
    Упрощенная версия: соединяет ближайшие точки.
    """
    combined = list(outer)
    for hole in holes:
        # Для простоты найдем ближайшие точки между внешним контуром и дырой
        min_dist = float('inf')
        bridge = (0, 0)  # индексы (outer_idx, hole_idx)

        for i, p_out in enumerate(combined):
            for j, p_hole in enumerate(hole):
                d = math.hypot(p_out[0] - p_hole[0], p_out[1] - p_hole[1])
                if d < min_dist:
                    min_dist = d
                    bridge = (i, j)

        i, j = bridge
        # Перестраиваем контур: идем по внешнему до моста -> входим в дыру
        # -> обходим дыру целиком -> выходим по мосту обратно в ту же точку внешнего
        hole_part = hole[j:] + hole[:j]
        combined = combined[:i + 1] + hole_part + [hole_part[0], combined[i]] + combined[i + 1:]

    return combined


# --- Основной Ear Clipping ---

def triangulate(polygon):
    vertices = list(polygon)
    triangles = []

    # Ограничитель итераций на случай ошибок геометрии
    limit = len(vertices) * len(vertices)
    iters = 0

    while len(vertices) > 2 and iters < limit:
        iters += 1
        for i in range(len(vertices)):
            prev = vertices[i - 1]
            curr = vertices[i]
            nxt = vertices[(i + 1) % len(vertices)]

            if is_convex(prev, curr, nxt):
                is_ear = True
                for j in range(len(vertices)):
                    p = vertices[j]
                    if p in (prev, curr, nxt): continue
                    if is_point_in_triangle(p, prev, curr, nxt):
                        is_ear = False
                        break

                if is_ear:
                    triangles.append((prev, curr, nxt))
                    vertices.pop(i)
                    break
    return triangles


# --- Визуализация Pygame ---

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.tick.Clock() if hasattr(pygame, 'tick') else pygame.time.Clock()

# 1. Внешний контур (против часовой стрелки)
outer_poly = [(100, 100), (100, 500), (700, 500), (700, 100)]
# 2. Отверстие (по часовой стрелке - важно для корректной математики "пустоты")
hole1 = [(200, 200), (500, 200), (500, 400), (200, 400)]

# Объединяем в один контур
merged_contour = merge_holes(outer_poly, [hole1])
# Триангулируем
mesh = triangulate(merged_contour)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

    screen.fill((255, 255, 255))

    # Рисуем результат триангуляции
    for tri in mesh:
        pygame.draw.polygon(screen, (200, 220, 255), tri)
        pygame.draw.polygon(screen, (100, 100, 100), tri, 1)

    # Рисуем оригинальные контуры для четкости
    pygame.draw.polygon(screen, (255, 0, 0), outer_poly, 3)
    pygame.draw.polygon(screen, (0, 0, 255), hole1, 3)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()