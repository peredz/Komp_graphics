import pygame
import math

# --- Инициализация Pygame ---
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


def is_point_in_triangle(p, a, b, c):
    """Проверка, лежит ли точка p внутри треугольника abc (барицентрический метод)"""

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
    # Векторное произведение (направление поворота)
    val = (curr[0] - prev[0]) * (next_p[1] - curr[1]) - (curr[1] - prev[1]) * (next_p[0] - curr[0])
    return val > 0  # True, если поворот левый (для обхода против часовой)


def get_triangles_ear_clipping(polygon):
    """Алгоритм Ear Clipping"""
    vertices = list(polygon)
    triangles = []

    # Пока в полигоне больше 3 вершин
    while len(vertices) > 3:
        ear_found = False
        for i in range(len(vertices)):
            prev = vertices[i - 1]
            curr = vertices[i]
            next_p = vertices[(i + 1) % len(vertices)]

            # 1. Вершина должна быть выпуклой
            if is_convex(prev, curr, next_p):
                # 2. Внутри треугольника не должно быть других вершин
                is_ear = True
                for j in range(len(vertices)):
                    p = vertices[j]
                    if p in (prev, curr, next_p):
                        continue
                    if is_point_in_triangle(p, prev, curr, next_p):
                        is_ear = False
                        break

                if is_ear:
                    # Нашли ухо! Отрезаем.
                    triangles.append((prev, curr, next_p))
                    vertices.pop(i)
                    ear_found = True
                    break

        if not ear_found:
            # Если ухо не найдено (может быть в самопересекающихся полигонах)
            break

    # Добавляем последний оставшийся треугольник
    if len(vertices) == 3:
        triangles.append(tuple(vertices))

    return triangles


# --- Создание тестового монотонного полигона ---
# Рисуем "зубчатую" фигуру, которая монотона по X
polygon = [
    (100, 300), (200, 100), (300, 250), (400, 100),
    (500, 250), (600, 100), (700, 300), (600, 500),
    (400, 350), (200, 500)
]

# Выполняем триангуляцию один раз
triangulated_mesh = get_triangles_ear_clipping(polygon)

# --- Главный цикл ---
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill((255, 255, 255))

    # Рисуем треугольники
    for tri in triangulated_mesh:
        # Рисуем закрашенные треугольники для наглядности
        # pygame.draw.polygon(screen, (230, 240, 255), tri)
        # Рисуем границы треугольников (ребра триангуляции)
        pygame.draw.polygon(screen, (150, 150, 150), tri, 1)

    # Рисуем контур полигона
    pygame.draw.polygon(screen, (50, 120, 200), polygon, 3)

    # Рисуем вершины
    for p in polygon:
        pygame.draw.circle(screen, (200, 50, 50), (int(p[0]), int(p[1])), 5)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()