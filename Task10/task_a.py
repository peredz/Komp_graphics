#!/usr/bin/env python3
"""
Task 10A: Морфинг двух простых геометрических фигур (круг в квадрат)

Задача: Реализовать морфинг между кругом и квадратом с жестко заданным
соответствием 4 точек.

Теория:
- Морфинг = Warping + Интерполяция цвета
- Для геометрических фигур используем аффинные преобразования между 
  соответствующими точками
- Для каждого промежуточного кадра t ∈ [0, 1]:
  * Интерполируем координаты опорных точек
  * Применяем warping
  * Смешиваем цвета (crossdissolve)

Опорные точки (фиксированные):
- Круг: центр (200, 200), точки на окружности
- Квадрат: угловые точки и центр
"""

import numpy as np
from PIL import Image, ImageDraw
import os


def create_circle(width=400, height=400, center_x=200, center_y=200, radius=100, color=(100, 150, 255)):
    """Создает изображение круга"""
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Рисуем заполненный круг
    draw.ellipse([center_x - radius, center_y - radius, 
                  center_x + radius, center_y + radius], 
                 fill=color, outline=(50, 50, 50))
    
    return img


def create_square(width=400, height=400, center_x=200, center_y=200, size=150, color=(255, 150, 100)):
    """Создает изображение квадрата"""
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    half_size = size // 2
    # Рисуем заполненный квадрат
    draw.rectangle([center_x - half_size, center_y - half_size,
                    center_x + half_size, center_y + half_size],
                   fill=color, outline=(50, 50, 50))
    
    return img


def get_circle_control_points(center_x=200, center_y=200, radius=100):
    """
    Получает 4 опорные точки на окружности круга
    (в основных направлениях: верх, право, низ, лево)
    """
    points = np.array([
        [center_x, center_y - radius],      # верх
        [center_x + radius, center_y],      # право
        [center_x, center_y + radius],      # низ
        [center_x - radius, center_y]       # лево
    ], dtype=np.float32)
    return points


def get_square_control_points(center_x=200, center_y=200, half_size=75):
    """
    Получает 4 опорные точки на углах квадрата
    """
    points = np.array([
        [center_x, center_y - half_size],       # верх (средина верхней стороны)
        [center_x + half_size, center_y],       # право (средина правой стороны)
        [center_x, center_y + half_size],       # низ (средина нижней стороны)
        [center_x - half_size, center_y]        # лево (средина левой стороны)
    ], dtype=np.float32)
    return points


def interpolate_points(src_pts, dst_pts, t):
    """
    Интерполирует координаты опорных точек
    t: параметр от 0 до 1 (0 = исходная фигура, 1 = целевая)
    """
    return src_pts * (1 - t) + dst_pts * t


def apply_piecewise_affine_warp(img_array, src_pts, dst_pts, width, height):
    """
    Применяет кусочно-аффинное преобразование с использованием триангуляции
    
    Алгоритм:
    1. Объединяем опорные точки с углами изображения
    2. Строим триангуляцию Делоне
    3. Для каждого треугольника ищем соответствующее аффинное преобразование
    4. Применяем преобразование к каждому пикселю
    """
    from scipy.spatial import Delaunay
    
    result = np.zeros_like(img_array)
    
    # Расширяем точки с углами
    all_src_pts = np.vstack([src_pts, [[0, 0], [width, 0], [0, height], [width, height]]])
    all_dst_pts = np.vstack([dst_pts, [[0, 0], [width, 0], [0, height], [width, height]]])
    
    # Триангуляция по исходным точкам (destination)
    tri = Delaunay(all_dst_pts)
    
    # Для каждого пикселя выходного изображения
    for y in range(height):
        for x in range(width):
            point = np.array([x, y], dtype=np.float32)
            
            # Находим треугольник, содержащий точку
            simplex_idx = tri.find_simplex(point)
            
            if simplex_idx == -1:
                # Точка вне триангуляции, копируем из исходного
                result[y, x] = img_array[y, x]
                continue
            
            # Получаем вершины треугольника
            simplex = tri.simplices[simplex_idx]
            dst_tri = all_dst_pts[simplex]  # треугольник в пространстве вывода
            src_tri = all_src_pts[simplex]  # соответствующий треугольник в исходном пространстве
            
            # Вычисляем барицентрические координаты
            v0 = dst_tri[1] - dst_tri[0]
            v1 = dst_tri[2] - dst_tri[0]
            v2 = point - dst_tri[0]
            
            dot00 = np.dot(v0, v0)
            dot01 = np.dot(v0, v1)
            dot02 = np.dot(v0, v2)
            dot11 = np.dot(v1, v1)
            dot12 = np.dot(v1, v2)
            
            inv_denom = 1 / (dot00 * dot11 - dot01 * dot01 + 1e-10)
            u = (dot11 * dot02 - dot01 * dot12) * inv_denom
            v = (dot00 * dot12 - dot01 * dot02) * inv_denom
            w = 1 - u - v
            
            # Преобразуем в исходное пространство
            src_point = w * src_tri[0] + u * src_tri[1] + v * src_tri[2]
            
            # Интерполируем цвет
            sx, sy = src_point
            sx = np.clip(sx, 0, width - 1)
            sy = np.clip(sy, 0, height - 1)
            
            # Билинейная интерполяция
            x0, y0 = int(sx), int(sy)
            x1, y1 = min(x0 + 1, width - 1), min(y0 + 1, height - 1)
            
            dx = sx - x0
            dy = sy - y0
            
            c00 = img_array[y0, x0].astype(float)
            c10 = img_array[y0, x1].astype(float)
            c01 = img_array[y1, x0].astype(float)
            c11 = img_array[y1, x1].astype(float)
            
            c0 = c00 * (1 - dx) + c10 * dx
            c1 = c01 * (1 - dx) + c11 * dx
            c = c0 * (1 - dy) + c1 * dy
            
            result[y, x] = np.uint8(np.clip(c, 0, 255))
    
    return result


def morph_frame(circle_img, square_img, t):
    """
    Создает один кадр морфинга
    t: параметр от 0 до 1
    """
    circle_array = np.array(circle_img)
    square_array = np.array(square_img)
    
    width, height = circle_img.size
    
    # Опорные точки
    circle_pts = get_circle_control_points(width // 2, height // 2, 100)
    square_pts = get_square_control_points(width // 2, height // 2, 75)
    
    # Интерполируем точки
    interp_pts = interpolate_points(circle_pts, square_pts, t)
    
    # Применяем warping к кругу (приближаем его к квадрату)
    try:
        warped = apply_piecewise_affine_warp(circle_array, circle_pts, interp_pts, width, height)
    except:
        warped = circle_array
    
    # Смешиваем цвета (crossdissolve)
    morphed = (warped * (1 - t) + square_array * t).astype(np.uint8)
    
    return Image.fromarray(morphed)


def main():
    """Основная функция"""
    width, height = 400, 400
    
    # Создаем исходные изображения
    print("Создание исходных изображений...")
    circle = create_circle(width, height)
    square = create_square(width, height)
    
    # Создаем промежуточные кадры
    num_frames = 15
    frames = []
    
    print(f"Генерирование {num_frames} кадров морфинга...")
    for i in range(num_frames):
        t = i / (num_frames - 1)
        print(f"  Кадр {i+1}/{num_frames} (t={t:.2f})")
        
        frame = morph_frame(circle, square, t)
        frames.append(frame)
    
    # Сохраняем
    os.makedirs("output", exist_ok=True)
    
    # Сохраняем промежуточные кадры
    for i, frame in enumerate(frames):
        frame.save(f"output/morph_frame_{i:02d}.png")
        print(f"Сохранено: output/morph_frame_{i:02d}.png")
    
    # Сохраняем анимацию
    frames_loop = frames + frames[-2:0:-1]  # Добавляем обратный проход для плавной анимации
    frames_loop[0].save(
        "output/morph_circle_to_square.gif",
        save_all=True,
        duration=100,
        loop=0
    )
    print("Сохранено: output/morph_circle_to_square.gif")


if __name__ == "__main__":
    main()
