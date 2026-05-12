#!/usr/bin/env python3
"""
Task 10B: Морфинг двух растровых изображений по заданным ключевым точкам

Задача: Реализовать морфинг между двумя растровыми изображениями
(например, лицами) с использованием 8-12 ручно выбранных ключевых точек.

Особенности:
- Поддержка интерактивного выбора точек с помощью мыши
- Триангуляция Делоне для кусочно-аффинного преобразования
- Сохранение анимации в GIF
- Двусторонний морфинг (туда и обратно)

Управление:
- Левая кнопка мыши: добавление опорной точки
- Правая кнопка мыши: удаление последней точки
- SPACE: начать морфинг с текущими точками
- ESC: выход
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pygame
import os
from scipy.spatial import Delaunay
from typing import List, Tuple


class MorphingUI:
    """Интерактивный интерфейс для выбора соответствующих точек"""
    
    def __init__(self, image_path: str, width: int = 800, height: int = 600):
        pygame.init()
        
        # Загружаем изображение
        self.image = Image.open(image_path)
        self.image_width, self.image_height = self.image.size
        
        # Масштабируем для отображения
        scale = min(width / self.image_width, height / self.image_height)
        new_size = (int(self.image_width * scale), int(self.image_height * scale))
        self.display_image = self.image.resize(new_size, Image.Resampling.LANCZOS)
        
        self.display_width = width
        self.display_height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        self.scale_x = self.image_width / self.display_image.width
        self.scale_y = self.image_height / self.display_image.height
        
        self.points = []
        self.running = True
        self.ready = False
    
    def run(self) -> List[Tuple[int, int]]:
        """Запускает интерактивный выбор точек"""
        pygame.display.set_caption("Выберите соответствующие точки (ЛКМ для добавления, ПКМ для удаления, SPACE для готовности)")
        
        font = pygame.font.Font(None, 24)
        
        while self.running:
            self.screen.fill((240, 240, 240))
            
            # Рисуем изображение
            image_surf = pygame.image.fromstring(
                self.display_image.tobytes(),
                self.display_image.size,
                self.display_image.mode
            )
            self.screen.blit(image_surf, (0, 0))
            
            # Рисуем точки
            for i, (x, y) in enumerate(self.points):
                pygame.draw.circle(self.screen, (0, 255, 0), (x, y), 5)
                text = font.render(str(i + 1), True, (0, 0, 0))
                self.screen.blit(text, (x + 10, y))
            
            # Информация
            info_text = f"Точек: {len(self.points)}/12 | ЛКМ добавить | ПКМ удалить | SPACE готово | ESC выход"
            info_surf = font.render(info_text, True, (0, 0, 0))
            self.screen.blit(info_surf, (10, self.display_height - 30))
            
            pygame.display.flip()
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # ЛКМ
                        if len(self.points) < 12:
                            self.points.append(event.pos)
                    elif event.button == 3:  # ПКМ
                        if self.points:
                            self.points.pop()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if len(self.points) >= 4:
                            self.ready = True
                            self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
            
            self.clock.tick(60)
        
        if self.ready:
            # Конвертируем в координаты исходного изображения
            return [(int(x * self.scale_x), int(y * self.scale_y)) for x, y in self.points]
        
        return None


def get_morphing_frames(img1: Image.Image, img2: Image.Image, 
                       points1: List[Tuple[int, int]], 
                       points2: List[Tuple[int, int]], 
                       num_frames: int = 20) -> List[Image.Image]:
    """
    Создает кадры морфинга между двумя изображениями
    
    Алгоритм:
    1. Треугулируем точки первого изображения (Делоне)
    2. Применяем те же треугольники ко второму
    3. Для каждого кадра интерполируем точки и применяем warping + crossdissolve
    """
    
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    
    width, height = img1.size
    
    # Добавляем углы как дополнительные точки для триангуляции
    corners = np.array([[0, 0], [width, 0], [0, height], [width, height]], dtype=np.float32)
    
    pts1_extended = np.array(points1 + list(corners), dtype=np.float32)
    pts2_extended = np.array(points2 + list(corners), dtype=np.float32)
    
    # Триангуляция
    tri = Delaunay(pts1_extended)
    
    frames = []
    
    for frame_idx in range(num_frames):
        t = frame_idx / (num_frames - 1)
        
        # Интерполируем точки
        interp_pts = pts1_extended * (1 - t) + pts2_extended * t
        
        # Создаем промежуточный кадр
        morphed = np.zeros_like(img1_array)
        
        # Применяем трансформацию для каждого треугольника
        for tri_idx, simplex in enumerate(tri.simplices):
            # Вершины треугольника в исходном изображении
            tri_src = pts1_extended[simplex]
            # Вершины в промежуточном положении
            tri_interp = interp_pts[simplex]
            
            # Минимальный bounding box
            min_x = max(0, int(np.floor(np.min(tri_interp[:, 0]))))
            max_x = min(width, int(np.ceil(np.max(tri_interp[:, 0]))))
            min_y = max(0, int(np.floor(np.min(tri_interp[:, 1]))))
            max_y = min(height, int(np.ceil(np.max(tri_interp[:, 1]))))
            
            # Для каждого пикселя в bbox
            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    point = np.array([x, y], dtype=np.float32)
                    
                    # Проверяем, находится ли точка внутри треугольника
                    bary = barycentric_coords(point, tri_interp)
                    
                    if bary is not None and np.all(bary >= -1e-6):
                        # Преобразуем в координаты исходного изображения
                        src_point = bary @ tri_src
                        sx, sy = src_point
                        
                        # Интерполируем цвет из первого изображения
                        color = bilinear_interpolate(img1_array, sx, sy)
                        morphed[y, x] = color
        
        # Смешиваем с вторым изображением (crossdissolve)
        # Заполняем оставшиеся пиксели
        mask = np.sum(morphed, axis=2) == 0
        morphed[mask] = img1_array[mask]
        
        # Crossdissolve
        result = (morphed * (1 - t) + img2_array * t).astype(np.uint8)
        frames.append(Image.fromarray(result))
    
    return frames


def barycentric_coords(p: np.ndarray, triangle: np.ndarray) -> np.ndarray:
    """Вычисляет барицентрические координаты точки относительно треугольника"""
    v0 = triangle[1] - triangle[0]
    v1 = triangle[2] - triangle[0]
    v2 = p - triangle[0]
    
    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)
    
    denom = dot00 * dot11 - dot01 * dot01
    if abs(denom) < 1e-10:
        return None
    
    inv_denom = 1 / denom
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    w = 1 - u - v
    
    return np.array([w, u, v])


def bilinear_interpolate(img: np.ndarray, x: float, y: float) -> np.ndarray:
    """Билинейная интерполяция цвета"""
    h, w = img.shape[:2]
    
    x = np.clip(x, 0, w - 1)
    y = np.clip(y, 0, h - 1)
    
    x0, y0 = int(x), int(y)
    x1 = min(x0 + 1, w - 1)
    y1 = min(y0 + 1, h - 1)
    
    dx = x - x0
    dy = y - y0
    
    c00 = img[y0, x0].astype(float)
    c10 = img[y0, x1].astype(float)
    c01 = img[y1, x0].astype(float)
    c11 = img[y1, x1].astype(float)
    
    c0 = c00 * (1 - dx) + c10 * dx
    c1 = c01 * (1 - dx) + c11 * dx
    c = c0 * (1 - dy) + c1 * dy
    
    return np.uint8(np.clip(c, 0, 255))


def main():
    """Основная функция"""
    
    # Предположим, что у нас есть два изображения
    img1_path = "image1.jpg"  # Первое изображение
    img2_path = "image2.jpg"  # Второе изображение
    
    # Проверяем, существуют ли файлы
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print("Ошибка: Необходимо подготовить два изображения (image1.jpg и image2.jpg)")
        print("Используемые изображения должны быть похожего размера")
        return
    
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    
    # Убеждаемся, что изображения одинакового размера
    if img1.size != img2.size:
        print(f"Масштабирование второго изображения с {img2.size} на {img1.size}...")
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    # Конвертируем в RGB если нужно
    if img1.mode != 'RGB':
        img1 = img1.convert('RGB')
    if img2.mode != 'RGB':
        img2 = img2.convert('RGB')
    
    print("=== Выбор ключевых точек на первом изображении ===")
    ui1 = MorphingUI(img1_path)
    points1 = ui1.run()
    
    if points1 is None:
        print("Отменено")
        return
    
    print(f"Выбрано {len(points1)} точек на первом изображении")
    
    print("\n=== Выбор соответствующих точек на втором изображении ===")
    ui2 = MorphingUI(img2_path)
    points2 = ui2.run()
    
    if points2 is None:
        print("Отменено")
        return
    
    print(f"Выбрано {len(points2)} точек на втором изображении")
    
    # Генерируем кадры морфинга
    print("\nГенерирование кадров морфинга...")
    frames_forward = get_morphing_frames(img1, img2, points1, points2, num_frames=20)
    
    # Добавляем обратный проход для плавной анимации
    frames_animation = frames_forward + frames_forward[-2:0:-1]
    
    # Сохраняем
    os.makedirs("output", exist_ok=True)
    
    # Сохраняем промежуточные кадры
    for i, frame in enumerate(frames_forward):
        frame.save(f"output/morph_frame_{i:02d}.png")
    
    # Сохраняем GIF
    frames_animation[0].save(
        "output/morph_animation.gif",
        save_all=True,
        duration=100,
        loop=0
    )
    print("Сохранено: output/morph_animation.gif")


if __name__ == "__main__":
    main()
