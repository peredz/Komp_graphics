#!/usr/bin/env python3
"""
Task 1A: Билинейное преобразование по 4 углам - фиксированное искажение

Быстрая реализация через сетку квадратов с локальными аффинными преобразованиями
"""

import numpy as np
from PIL import Image
import os


def bilinear_warp_trapezoid(image):
    r"""
    Трапеция: две верхние точки ближе друг к другу, чем нижние
    
    Источник (нормализовано [0,1]):
      (0, 0) --- (1, 0)
      |           |
      (0, 1) --- (1, 1)
    
    Мишень (трапеция):
      (0.2, 0) --- (0.8, 0)      верхняя сторона узкая
      |              |
      (0, 1) --- (1, 1)           нижняя сторона широкая
    """
    img_array = np.array(image)
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=2)
    
    height, width = img_array.shape[:2]
    
    # Углы источника (нормализованные)
    src_corners = np.array([
        [0, 0],      # top-left
        [1, 0],      # top-right
        [0, 1],      # bottom-left
        [1, 1]       # bottom-right
    ], dtype=np.float32)
    
    # Углы мишени (трапеция)
    dst_corners = np.array([
        [0.2 * width, 0.1 * height],        # top-left (сужена)
        [0.8 * width, 0.1 * height],        # top-right (сужена)
        [0.05 * width, 0.9 * height],       # bottom-left (расширена)
        [0.95 * width, 0.9 * height]        # bottom-right (расширена)
    ], dtype=np.float32)
    
    return apply_bilinear_warp(img_array, src_corners, dst_corners, width, height)


def bilinear_warp_rhombus(image):
    r"""
    Ромб: центр приподнят, углы по сторонам
    
    Мишень:
           (0.5, 0.1)
          /         \
      (0.1, 0.5)   (0.9, 0.5)
          \         /
           (0.5, 0.9)
    """
    img_array = np.array(image)
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=2)
    
    height, width = img_array.shape[:2]
    
    # Углы источника
    src_corners = np.array([
        [0, 0],      # top-left
        [1, 0],      # top-right
        [0, 1],      # bottom-left
        [1, 1]       # bottom-right
    ], dtype=np.float32)
    
    # Углы мишени (ромб)
    dst_corners = np.array([
        [0.5 * width, 0.1 * height],        # top
        [0.9 * width, 0.5 * height],        # right
        [0.1 * width, 0.5 * height],        # left
        [0.5 * width, 0.9 * height]         # bottom
    ], dtype=np.float32)
    
    # Переорганизуем: top-left, top-right, bottom-left, bottom-right
    dst_corners_reord = np.array([
        dst_corners[2],  # left -> top-left
        dst_corners[0],  # top -> top-right
        dst_corners[3],  # bottom -> bottom-left
        dst_corners[1]   # right -> bottom-right
    ], dtype=np.float32)
    
    return apply_bilinear_warp(img_array, src_corners, dst_corners_reord, width, height)


def apply_bilinear_warp(img_array, src_corners, dst_corners, width, height):
    """
    Быстрое преобразование квадрилатерала через сетку с локальными аффинными преобразованиями
    """
    result = np.zeros_like(img_array)
    
    # Параметры сетки
    grid_size = 15  # Размер сетки (15x15 ячеек)
    
    print(f"Обработка сетки {grid_size}x{grid_size}...")
    
    # Создаем координаты сетки параметров (u, v)
    u_vals = np.linspace(0, 1, grid_size + 1)
    v_vals = np.linspace(0, 1, grid_size + 1)
    
    # Для каждой ячейки сетки
    for i in range(grid_size):
        if i % 3 == 0:
            print(f"  Строка {i}/{grid_size}")
        
        for j in range(grid_size):
            # Параметры ячейки
            u0, u1 = u_vals[j], u_vals[j + 1]
            v0, v1 = v_vals[i], v_vals[i + 1]
            
            # Четыре угла ячейки в мишени
            c0, c1, c2, c3 = dst_corners
            dst_pix = np.array([
                (1-u0)*(1-v0)*c0 + u0*(1-v0)*c1 + (1-u0)*v0*c2 + u0*v0*c3,
                (1-u1)*(1-v0)*c0 + u1*(1-v0)*c1 + (1-u1)*v0*c2 + u1*v0*c3,
                (1-u0)*(1-v1)*c0 + u0*(1-v1)*c1 + (1-u0)*v1*c2 + u0*v1*c3,
                (1-u1)*(1-v1)*c0 + u1*(1-v1)*c1 + (1-u1)*v1*c2 + u1*v1*c3
            ], dtype=np.float32)
            
            # Четыре угла ячейки в источнике
            c0, c1, c2, c3 = src_corners
            src_pix = np.array([
                (1-u0)*(1-v0)*c0 + u0*(1-v0)*c1 + (1-u0)*v0*c2 + u0*v0*c3,
                (1-u1)*(1-v0)*c0 + u1*(1-v0)*c1 + (1-u1)*v0*c2 + u1*v0*c3,
                (1-u0)*(1-v1)*c0 + u0*(1-v1)*c1 + (1-u0)*v1*c2 + u0*v1*c3,
                (1-u1)*(1-v1)*c0 + u1*(1-v1)*c1 + (1-u1)*v1*c2 + u1*v1*c3
            ], dtype=np.float32)
            
            # Применяем аффинное преобразование для этой ячейки
            warp_cell(result, img_array, src_pix, dst_pix, width, height)
    
    return Image.fromarray(np.uint8(result))


def warp_cell(result, source, src_quad, dst_quad, width, height):
    """
    Применяет аффинное преобразование для одной ячейки сетки
    """
    # Вычисляем аффинную матрицу для преобразования dst -> src
    try:
        # Используем первые 3 точки для вычисления аффинного преобразования
        # dst_pts = M @ src_pts, где M - (2, 2) матрица и вектор смещения (2,)
        src_pts = src_quad[:3]  # (3, 2)
        dst_pts = dst_quad[:3]  # (3, 2)
        
        # Составляем систему в однородных координатах
        # [src_x1 src_y1 1]   [m11 m12 b1]   [dst_x1]
        # [src_x2 src_y2 1] @ [m21 m22 b2] = [dst_x2]
        # [src_x3 src_y3 1]                   [dst_x3]
        
        # Для x координат
        A = np.hstack([src_pts, np.ones((3, 1))])  # (3, 3)
        bx = dst_pts[:, 0]  # (3,)
        by = dst_pts[:, 1]  # (3,)
        
        coeffs_x = np.linalg.solve(A, bx)  # [m11, m21, b1]
        coeffs_y = np.linalg.solve(A, by)  # [m12, m22, b2]
        
        M = np.array([[coeffs_x[0], coeffs_y[0]],
                      [coeffs_x[1], coeffs_y[1]]])
        b = np.array([coeffs_x[2], coeffs_y[2]])
        
        # Обратное преобразование
        M_inv = np.linalg.inv(M)
        
    except np.linalg.LinAlgError:
        return
    
    # Bounding box в мишени
    min_x = int(max(0, np.min(dst_quad[:, 0])))
    max_x = int(min(width - 1, np.max(dst_quad[:, 0])))
    min_y = int(max(0, np.min(dst_quad[:, 1])))
    max_y = int(min(height - 1, np.max(dst_quad[:, 1])))
    
    # Для каждого пикселя в bbox
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            # Вычисляем координаты в источнике
            dst_pt = np.array([x, y], dtype=np.float32)
            src_pt = M_inv @ (dst_pt - b)
            
            sx, sy = src_pt
            
            # Проверяем границы
            if 0 <= sx < source.shape[1] - 1 and 0 <= sy < source.shape[0] - 1:
                # Билинейная интерполяция
                color = bilinear_interpolate(source, sx, sy)
                result[y, x] = color


def bilinear_interpolate(image, x, y):
    """
    Билинейная интерполяция цвета в точке (x, y)
    """
    x0 = int(np.floor(x))
    x1 = x0 + 1
    y0 = int(np.floor(y))
    y1 = y0 + 1
    
    # Границы
    x0 = max(0, min(x0, image.shape[1] - 1))
    x1 = max(0, min(x1, image.shape[1] - 1))
    y0 = max(0, min(y0, image.shape[0] - 1))
    y1 = max(0, min(y1, image.shape[0] - 1))
    
    # Веса
    wx = x - np.floor(x)
    wy = y - np.floor(y)
    
    # Четыре соседних пикселя
    c00 = image[y0, x0].astype(np.float32)
    c10 = image[y0, x1].astype(np.float32)
    c01 = image[y1, x0].astype(np.float32)
    c11 = image[y1, x1].astype(np.float32)
    
    # Интерполяция
    c0 = c00 * (1 - wx) + c10 * wx
    c1 = c01 * (1 - wx) + c11 * wx
    c = c0 * (1 - wy) + c1 * wy
    
    return c


if __name__ == "__main__":
    # Пытаемся найти изображение
    image_path = None
    if os.path.exists("pic.png"):
        image_path = "pic.png"
    elif os.path.exists("../pic.png"):
        image_path = "../pic.png"
    elif os.path.exists("../../pic.png"):
        image_path = "../../pic.png"
    
    if not image_path:
        print("Ошибка: не найдено изображение pic.png")
        print("Пожалуйста, поместите pic.png в папку Task9 или на уровень выше")
        exit(1)
    
    print(f"Загружаю изображение: {image_path}")
    img = Image.open(image_path)
    
    # Создаем выходную папку
    os.makedirs("task1_pics", exist_ok=True)
    
    print("Применяю трапецию...")
    warp_trapezoid = bilinear_warp_trapezoid(img)
    warp_trapezoid.save("task1_pics/trapezoid.png")
    print("Сохранено: task1_pics/trapezoid.png")
    
    print("Применяю ромб...")
    warp_rhombus = bilinear_warp_rhombus(img)
    warp_rhombus.save("task1_pics/rhombus.png")
    print("Сохранено: task1_pics/rhombus.png")
    
    print("Готово!")
