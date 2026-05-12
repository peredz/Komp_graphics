#!/usr/bin/env python3
"""
Task 1C: Билинейный варпинг с обратным отображением и билинейной интерполяцией

Этот вариант более качественный, чем 1A:
- Использует обратное отображение (для каждого пикселя выхода ищем прообраз)
- Применяет билинейную интерполяцию цвета
- Избегает дырок в изображении (в отличие от прямого отображения)

Математика:
- Для каждого пикселя (x, y) выходного изображения
- Находим параметры (u, v) через обратное преобразование
- Получаем координаты (sx, sy) в источнике через билинейную интерполяцию
- Интерполируем цвет в точке (sx, sy)
"""

import numpy as np
from PIL import Image
import os
import time


def load_image_safe():
    """Находит и загружает pic.png"""
    paths = ["pic.png", "../pic.png", "../../pic.png"]
    for path in paths:
        if os.path.exists(path):
            return Image.open(path), path
    raise FileNotFoundError("pic.png не найдено")


class BilinearWarpInverse:
    """Билинейный варпинг с обратным отображением"""
    
    def __init__(self, image):
        self.source_image = image
        self.src_width, self.src_height = image.size
        self.img_array = np.array(image)
        
        # Обеспечиваем RGB
        if len(self.img_array.shape) == 2:
            self.img_array = np.stack([self.img_array] * 3, axis=2)
    
    def warp_trapezoid(self, output_width, output_height):
        """
        Трапеция: верхняя сторона узкая, нижняя широкая
        Использует обратное отображение и билинейную интерполяцию
        """
        # Углы источника (нормализованные)
        src_corners = np.array([
            [0, 0],
            [1, 0],
            [0, 1],
            [1, 1]
        ], dtype=np.float32)
        
        # Углы мишени (трапеция)
        dst_corners = np.array([
            [0.2 * output_width, 0.1 * output_height],
            [0.8 * output_width, 0.1 * output_height],
            [0.05 * output_width, 0.9 * output_height],
            [0.95 * output_width, 0.9 * output_height]
        ], dtype=np.float32)
        
        return self.apply_warp_inverse(src_corners, dst_corners, output_width, output_height)
    
    def warp_rhombus(self, output_width, output_height):
        """Ромб: центр приподнят"""
        src_corners = np.array([
            [0, 0],
            [1, 0],
            [0, 1],
            [1, 1]
        ], dtype=np.float32)
        
        # Углы мишени (ромб)
        dst_corners = np.array([
            [0.1 * output_width, 0.5 * output_height],  # left
            [0.5 * output_width, 0.1 * output_height],  # top
            [0.5 * output_width, 0.9 * output_height],  # bottom
            [0.9 * output_width, 0.5 * output_height]   # right
        ], dtype=np.float32)
        
        # Переорганизуем в TL, TR, BL, BR
        dst_corners_reord = np.array([
            dst_corners[1],  # top -> TL
            dst_corners[1],  # top -> TR (будет переопределено)
            dst_corners[2],  # bottom -> BL
            dst_corners[2]   # bottom -> BR
        ], dtype=np.float32)
        
        dst_corners_reord[0] = dst_corners[0]  # left -> TL
        dst_corners_reord[1] = dst_corners[3]  # right -> TR
        
        return self.apply_warp_inverse(src_corners, dst_corners_reord, output_width, output_height)
    
    def warp_barrel(self, output_width, output_height):
        """Бочка: выпуклое расширение"""
        src_corners = np.array([
            [0, 0],
            [1, 0],
            [0, 1],
            [1, 1]
        ], dtype=np.float32)
        
        # Углы мишени (бочка)
        dst_corners = np.array([
            [0.15 * output_width, 0.15 * output_height],
            [0.85 * output_width, 0.15 * output_height],
            [0.15 * output_width, 0.85 * output_height],
            [0.85 * output_width, 0.85 * output_height]
        ], dtype=np.float32)
        
        return self.apply_warp_inverse(src_corners, dst_corners, output_width, output_height)
    
    def apply_warp_inverse(self, src_corners, dst_corners, output_width, output_height):
        """
        Применяет билинейный варпинг с обратным отображением
        
        Алгоритм:
        1. Для каждого пикселя выхода (x, y)
        2. Находим параметры (u, v) в системе мишени
        3. Вычисляем координаты в источнике через билинейную интерполяцию
        4. Интерполируем цвет
        """
        result = np.zeros((output_height, output_width, self.img_array.shape[2]), dtype=np.uint8)
        
        print(f"Применяю варпинг ({output_width}x{output_height})...")
        
        for y in range(output_height):
            if y % 50 == 0:
                print(f"  Обработано {y}/{output_height} строк...")
            
            for x in range(output_width):
                # Находим параметры (u, v) для точки выхода (x, y)
                u, v = self.find_uv_for_point(x, y, dst_corners)
                
                if 0 <= u <= 1 and 0 <= v <= 1:
                    # Вычисляем координаты в источнике
                    src_point = self.bilinear_interpolate_point(src_corners, u, v)
                    sx, sy = src_point
                    
                    # Масштабируем до размера изображения
                    sx = sx * (self.src_width - 1)
                    sy = sy * (self.src_height - 1)
                    
                    if 0 <= sx < self.src_width - 1 and 0 <= sy < self.src_height - 1:
                        # Интерполируем цвет
                        color = self.bilinear_interpolate_color(sx, sy)
                        result[y, x] = color
        
        return Image.fromarray(result)
    
    def find_uv_for_point(self, x, y, dst_corners):
        """
        Находит параметры (u, v) для точки (x, y) в системе мишени
        
        Решаем систему:
        (x, y) = (1-u)(1-v)*d00 + u(1-v)*d10 + (1-u)v*d01 + uv*d11
        
        Используется метод Newton-Raphson для решения нелинейной системы
        """
        # Начальное приближение
        u, v = 0.5, 0.5
        
        for iteration in range(10):
            # Текущая позиция
            p = self.bilinear_interpolate_point(dst_corners, u, v)
            
            # Ошибка
            error = p - np.array([x, y], dtype=np.float32)
            error_norm = np.linalg.norm(error)
            
            if error_norm < 1e-2:  # Достаточно точно
                break
            
            # Якобиан (производные)
            dp_du = self.compute_derivative_u(dst_corners, u, v)
            dp_dv = self.compute_derivative_v(dst_corners, u, v)
            
            # Матрица якобиана
            J = np.column_stack([dp_du, dp_dv])
            
            try:
                # Решаем систему J @ delta = error
                delta = np.linalg.solve(J, error)
                
                # Newton шаг с демпфированием
                u -= delta[0] * 0.5
                v -= delta[1] * 0.5
                
            except np.linalg.LinAlgError:
                # Сингулярная матрица
                break
            
            # Ограничиваем значения
            u = np.clip(u, 0, 1)
            v = np.clip(v, 0, 1)
        
        return u, v
    
    def bilinear_interpolate_point(self, corners, u, v):
        """
        Билинейная интерполяция точки
        p(u, v) = (1-u)(1-v)*c00 + u(1-v)*c10 + (1-u)v*c01 + uv*c11
        """
        c00 = corners[0]
        c10 = corners[1]
        c01 = corners[2]
        c11 = corners[3]
        
        p = ((1-u)*(1-v) * c00 +
             u*(1-v) * c10 +
             (1-u)*v * c01 +
             u*v * c11)
        
        return p
    
    def compute_derivative_u(self, corners, u, v):
        """dp/du"""
        c00 = corners[0]
        c10 = corners[1]
        c01 = corners[2]
        c11 = corners[3]
        
        dp_du = (-(1-v) * c00 +
                 (1-v) * c10 -
                 v * c01 +
                 v * c11)
        
        return dp_du
    
    def compute_derivative_v(self, corners, u, v):
        """dp/dv"""
        c00 = corners[0]
        c10 = corners[1]
        c01 = corners[2]
        c11 = corners[3]
        
        dp_dv = (-(1-u) * c00 -
                 u * c10 +
                 (1-u) * c01 +
                 u * c11)
        
        return dp_dv
    
    def bilinear_interpolate_color(self, x, y):
        """
        Билинейная интерполяция цвета в точке (x, y)
        в координатах исходного изображения
        """
        x0 = int(np.floor(x))
        x1 = min(x0 + 1, self.src_width - 1)
        y0 = int(np.floor(y))
        y1 = min(y0 + 1, self.src_height - 1)
        
        # Нормализуем координаты
        x0 = max(0, min(x0, self.src_width - 1))
        x1 = max(0, min(x1, self.src_width - 1))
        y0 = max(0, min(y0, self.src_height - 1))
        y1 = max(0, min(y1, self.src_height - 1))
        
        # Веса
        wx = x - np.floor(x)
        wy = y - np.floor(y)
        
        # Четыре соседних пикселя
        c00 = self.img_array[y0, x0].astype(np.float32)
        c10 = self.img_array[y0, x1].astype(np.float32)
        c01 = self.img_array[y1, x0].astype(np.float32)
        c11 = self.img_array[y1, x1].astype(np.float32)
        
        # Билинейная интерполяция
        c0 = c00 * (1 - wx) + c10 * wx
        c1 = c01 * (1 - wx) + c11 * wx
        c = c0 * (1 - wy) + c1 * wy
        
        return np.uint8(c)


if __name__ == "__main__":
    image_path, _ = load_image_safe()
    print(f"Загружаю изображение: {image_path}")
    img = Image.open(image_path)
    
    # Создаем выходную папку
    os.makedirs("task1_pics", exist_ok=True)
    
    warp = BilinearWarpInverse(img)
    
    # Размер выходного изображения
    output_width, output_height = 800, 600
    
    # Трапеция
    print("\n--- Трапеция (обратное отображение) ---")
    start = time.time()
    trapezoid = warp.warp_trapezoid(output_width, output_height)
    trapezoid.save("task1_pics/trapezoid_inverse.png")
    print(f"Сохранено: task1_pics/trapezoid_inverse.png ({time.time() - start:.2f}s)")
    
    # Ромб
    print("\n--- Ромб (обратное отображение) ---")
    start = time.time()
    rhombus = warp.warp_rhombus(output_width, output_height)
    rhombus.save("task1_pics/rhombus_inverse.png")
    print(f"Сохранено: task1_pics/rhombus_inverse.png ({time.time() - start:.2f}s)")
    
    # Бочка
    print("\n--- Бочка (обратное отображение) ---")
    start = time.time()
    barrel = warp.warp_barrel(output_width, output_height)
    barrel.save("task1_pics/barrel_inverse.png")
    print(f"Сохранено: task1_pics/barrel_inverse.png ({time.time() - start:.2f}s)")
    
    print("\nГотово!")
