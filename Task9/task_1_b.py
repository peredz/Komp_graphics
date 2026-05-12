#!/usr/bin/env python3
"""
Task 1B: Билинейное преобразование с интерактивным управлением углами мышью

Используется pygame для интерактивного управления:
- Левая кнопка мыши: перемещение угла четырехугольника
- Правая кнопка мыши: сброс на исходное положение
- ESC: выход
"""

import numpy as np
from PIL import Image
import pygame
import os
import math


def load_image_safe():
    """Находит и загружает pic.png"""
    paths = ["pic.png", "../pic.png", "../../pic.png"]
    for path in paths:
        if os.path.exists(path):
            return Image.open(path), path
    raise FileNotFoundError("pic.png не найдено")


class BilinearWarpEditor:
    def __init__(self, image_path, display_width=800, display_height=600):
        pygame.init()
        
        # Загружаем изображение
        self.source_image = Image.open(image_path)
        
        # Размер исходного изображения
        self.src_width, self.src_height = self.source_image.size
        
        # Размер окна
        self.display_width = display_width
        self.display_height = display_height
        self.screen = pygame.display.set_mode((display_width, display_height))
        pygame.display.set_caption("Bilinear Warp Editor - перемещайте углы мышью")
        
        self.clock = pygame.time.Clock()
        
        # Начальные углы мишени (исходное положение)
        self.dst_corners_init = np.array([
            [50, 50],
            [display_width - 50, 50],
            [50, display_height - 50],
            [display_width - 50, display_height - 50]
        ], dtype=np.float32)
        
        # Текущие углы мишени
        self.dst_corners = self.dst_corners_init.copy()
        
        # Выбранный угол (-1 если не выбран)
        self.selected_corner = -1
        
        # Радиус для выделения угла мышью
        self.corner_radius = 10
        
    def find_corner_at_mouse(self, mouse_pos):
        """Находит угол рядом с позицией мыши"""
        for i, corner in enumerate(self.dst_corners):
            dist = math.sqrt((mouse_pos[0] - corner[0])**2 + (mouse_pos[1] - corner[1])**2)
            if dist <= self.corner_radius:
                return i
        return -1
    
    def compute_bilinear_mesh(self, src_corners, dst_corners, grid_size=50):
        """
        Вычисляет координаты для преобразования в виде сетки
        Для эффективности используем сетку вместо пиксель-за-пикселем
        """
        # Создаем сетку параметров (u, v)
        u_vals = np.linspace(0, 1, grid_size)
        v_vals = np.linspace(0, 1, grid_size)
        
        mesh_src = []
        mesh_dst = []
        
        for v in v_vals:
            for u in u_vals:
                # Билинейная интерполяция в источнике
                src = ((1-u)*(1-v) * src_corners[0] +
                       u*(1-v) * src_corners[1] +
                       (1-u)*v * src_corners[2] +
                       u*v * src_corners[3])
                
                # Билинейная интерполяция в мишени
                dst = ((1-u)*(1-v) * dst_corners[0] +
                       u*(1-v) * dst_corners[1] +
                       (1-u)*v * dst_corners[2] +
                       u*v * dst_corners[3])
                
                mesh_src.append(src)
                mesh_dst.append(dst)
        
        return np.array(mesh_src), np.array(mesh_dst)
    
    def bilinear_warp_image(self):
        """Применяет билинейный варпинг к изображению"""
        img_array = np.array(self.source_image)
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=2)
        
        # Углы источника (нормализованные в размер изображения)
        src_corners = np.array([
            [0, 0],
            [self.src_width - 1, 0],
            [0, self.src_height - 1],
            [self.src_width - 1, self.src_height - 1]
        ], dtype=np.float32)
        
        # Выходное изображение
        result = np.zeros((self.display_height, self.display_width, img_array.shape[2]), dtype=np.uint8)
        
        # Используем обратное отображение
        for y in range(self.display_height):
            for x in range(self.display_width):
                # Вычисляем параметры (u, v) для точки (x, y)
                u, v = self.find_uv_for_point(x, y, self.dst_corners)
                
                # Вычисляем координаты в источнике
                sx = u * (self.src_width - 1)
                sy = v * (self.src_height - 1)
                
                if 0 <= sx < self.src_width - 1 and 0 <= sy < self.src_height - 1:
                    # Билинейная интерполяция
                    color = self.bilinear_interpolate(img_array, sx, sy)
                    result[y, x] = color
        
        return result
    
    def find_uv_for_point(self, x, y, dst_corners):
        """
        Находит параметры (u, v) для точки (x, y) в системе мишени
        Используется итерационный метод (Newton-Raphson)
        """
        # Начальное приближение
        u, v = 0.5, 0.5
        point = np.array([x, y], dtype=np.float32)
        
        for iteration in range(10):
            # Текущая позиция
            p = ((1-u)*(1-v) * dst_corners[0] +
                 u*(1-v) * dst_corners[1] +
                 (1-u)*v * dst_corners[2] +
                 u*v * dst_corners[3])
            
            # Якобиан (производные по u и v)
            dp_du = (-(1-v) * dst_corners[0] +
                     (1-v) * dst_corners[1] -
                     v * dst_corners[2] +
                     v * dst_corners[3])
            
            dp_dv = (-(1-u) * dst_corners[0] -
                     u * dst_corners[1] +
                     (1-u) * dst_corners[2] +
                     u * dst_corners[3])
            
            # Ошибка
            error = p - point
            error_norm = np.linalg.norm(error)
            
            if error_norm < 0.01:
                break
            
            # Матрица якобиана
            J = np.array([dp_du, dp_dv]).T
            
            try:
                delta = np.linalg.solve(J, error)
                u -= delta[0] * 0.5
                v -= delta[1] * 0.5
            except np.linalg.LinAlgError:
                break
            
            # Ограничиваем значения
            u = np.clip(u, 0, 1)
            v = np.clip(v, 0, 1)
        
        return u, v
    
    def bilinear_interpolate(self, image, x, y):
        """Билинейная интерполяция цвета"""
        x0 = int(np.floor(x))
        x1 = min(x0 + 1, image.shape[1] - 1)
        y0 = int(np.floor(y))
        y1 = min(y0 + 1, image.shape[0] - 1)
        
        wx = x - np.floor(x)
        wy = y - np.floor(y)
        
        c00 = image[y0, x0].astype(np.float32)
        c10 = image[y0, x1].astype(np.float32)
        c01 = image[y1, x0].astype(np.float32)
        c11 = image[y1, x1].astype(np.float32)
        
        c0 = c00 * (1 - wx) + c10 * wx
        c1 = c01 * (1 - wx) + c11 * wx
        c = c0 * (1 - wy) + c1 * wy
        
        return c.astype(np.uint8)
    
    def render(self):
        """Отрисовывает сцену"""
        self.screen.fill((255, 255, 255))
        
        # Применяем варпинг
        warped = self.bilinear_warp_image()
        
        # Конвертируем в pygame surface
        surface = pygame.surfarray.make_surface(warped.swapaxes(0, 1))
        self.screen.blit(surface, (0, 0))
        
        # Рисуем четырехугольник
        corners_int = tuple((int(c[0]), int(c[1])) for c in self.dst_corners)
        pygame.draw.polygon(self.screen, (0, 255, 0), corners_int, 3)
        
        # Рисуем углы
        for i, corner in enumerate(self.dst_corners):
            color = (255, 0, 0) if i == self.selected_corner else (0, 0, 255)
            pygame.draw.circle(self.screen, color, (int(corner[0]), int(corner[1])), self.corner_radius)
            
            # Номер угла
            font = pygame.font.Font(None, 24)
            text = font.render(str(i), True, (255, 255, 255))
            self.screen.blit(text, (int(corner[0]) - 5, int(corner[1]) - 5))
        
        # Инструкция
        font = pygame.font.Font(None, 20)
        text = font.render("Левая кнопка: перемещение | Правая: сброс | ESC: выход", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))
        
        pygame.display.flip()
    
    def run(self):
        """Главный цикл"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка
                        self.selected_corner = self.find_corner_at_mouse(event.pos)
                    elif event.button == 3:  # Правая кнопка
                        self.dst_corners = self.dst_corners_init.copy()
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.selected_corner = -1
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.selected_corner >= 0:
                        self.dst_corners[self.selected_corner] = np.array(event.pos, dtype=np.float32)
            
            self.render()
            self.clock.tick(30)
        
        pygame.quit()


if __name__ == "__main__":
    image_path, _ = load_image_safe()
    editor = BilinearWarpEditor(image_path)
    editor.run()
