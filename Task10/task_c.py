#!/usr/bin/env python3
"""
Task 10C: Морфинг с автоматическим построением соответствия

Задача: Реализовать морфинг с автоматическим построением соответствия
на основе контуров объектов.

Особенности:
- Пользователь выделяет контур на первом изображении (интерактивная рисовка)
- Программа автоматически сегментирует объект (находит границы)
- Пользователь выделяет контур на втором изображении
- Программа автоматически строит сетку соответствия между контурами
- Генерируется морфинг анимация

Управление на этапе выделения контура:
- Левая кнопка мыши: рисование контура
- SPACE: завершить контур
- ПКМ: отменить последнюю точку
- ESC: выход
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pygame
import cv2
from scipy.spatial import Delaunay
from typing import List, Tuple
import os


class ContourDrawer:
    """Интерактивное выделение контура на изображении"""
    
    def __init__(self, image_path: str, width: int = 900, height: int = 700):
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
        
        self.contour_points = []
        self.running = True
        self.completed = False
    
    def run(self) -> List[Tuple[int, int]]:
        """Запускает интерактивное выделение контура"""
        pygame.display.set_caption("Нарисуйте контур объекта (ЛКМ рисовать, SPACE завершить, ПКМ отменить)")
        
        font = pygame.font.Font(None, 20)
        
        # Создаем поверхность для рисования
        drawing_surf = pygame.Surface((self.display_image.width, self.display_image.height))
        
        while self.running:
            self.screen.fill((240, 240, 240))
            
            # Рисуем исходное изображение
            image_surf = pygame.image.fromstring(
                self.display_image.tobytes(),
                self.display_image.size,
                self.display_image.mode
            )
            self.screen.blit(image_surf, (0, 0))
            
            # Рисуем контур
            if len(self.contour_points) > 1:
                pygame.draw.lines(self.screen, (0, 255, 0), self.contour_points, 2)
            
            # Рисуем точки контура
            for i, (x, y) in enumerate(self.contour_points):
                pygame.draw.circle(self.screen, (255, 0, 0), (x, y), 3)
            
            # Информация
            info_text = f"Точек в контуре: {len(self.contour_points)} | ЛКМ рисовать | SPACE завершить | ПКМ отменить | ESC выход"
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
                        self.contour_points.append(event.pos)
                    elif event.button == 3:  # ПКМ
                        if self.contour_points:
                            self.contour_points.pop()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if len(self.contour_points) >= 3:
                            self.completed = True
                            self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
            
            self.clock.tick(60)
        
        if self.completed and self.contour_points:
            # Конвертируем в координаты исходного изображения
            return [(int(x * self.scale_x), int(y * self.scale_y)) for x, y in self.contour_points]
        
        return None


def resample_contour(contour: List[Tuple[int, int]], num_points: int) -> List[Tuple[int, int]]:
    """
    Переискажает контур заданным количеством точек
    Используется для получения одинакового количества точек на обоих контурах
    """
    contour = np.array(contour, dtype=np.float32)
    
    # Вычисляем накопленную длину
    segments = np.diff(contour, axis=0)
    distances = np.sqrt(np.sum(segments**2, axis=1))
    cumsum = np.insert(np.cumsum(distances), 0, 0)
    total_length = cumsum[-1]
    
    # Равномерно распределяем новые точки
    new_positions = np.linspace(0, total_length, num_points)
    new_contour = []
    
    for pos in new_positions:
        # Находим сегмент, где находится позиция
        idx = np.searchsorted(cumsum, pos) - 1
        idx = np.clip(idx, 0, len(contour) - 2)
        
        # Интерполируем
        if cumsum[idx + 1] - cumsum[idx] > 1e-6:
            t = (pos - cumsum[idx]) / (cumsum[idx + 1] - cumsum[idx])
            point = contour[idx] * (1 - t) + contour[idx + 1] * t
            new_contour.append(tuple(point))
    
    return new_contour


def build_correspondence_grid(contour1: List[Tuple[int, int]], 
                             contour2: List[Tuple[int, int]],
                             num_inner_points: int = 5) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Строит сетку соответствия между двумя контурами
    
    Алгоритм:
    1. Переискажаем оба контура на одинаковое количество точек
    2. Добавляем внутренние точки на основе центроида
    3. Возвращаем соответствующие наборы точек
    """
    
    # Выравниваем контуры по количеству точек
    num_points = max(len(contour1), len(contour2))
    contour1_resampled = resample_contour(contour1, num_points)
    contour2_resampled = resample_contour(contour2, num_points)
    
    points1 = list(contour1_resampled)
    points2 = list(contour2_resampled)
    
    # Вычисляем центроиды
    center1 = np.mean(contour1_resampled, axis=0)
    center2 = np.mean(contour2_resampled, axis=0)
    
    # Добавляем концентрические точки внутри контура
    for i in range(1, num_inner_points + 1):
        alpha = 1 - i / (num_inner_points + 1)
        
        # Для каждой точки контура добавляем точку ближе к центру
        for j in range(num_points):
            p1 = np.array(contour1_resampled[j])
            p2 = np.array(contour2_resampled[j])
            
            inner1 = center1 * alpha + p1 * (1 - alpha)
            inner2 = center2 * alpha + p2 * (1 - alpha)
            
            points1.append(tuple(inner1))
            points2.append(tuple(inner2))
    
    return points1, points2


def get_morphing_frames_auto(img1: Image.Image, img2: Image.Image,
                            points1: List[Tuple[int, int]],
                            points2: List[Tuple[int, int]],
                            num_frames: int = 20) -> List[Image.Image]:
    """
    Создает кадры морфинга с автоматически построенной сеткой
    """
    
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    
    width, height = img1.size
    
    # Добавляем углы
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
        
        # Заполняем оставшиеся пиксели
        mask = np.sum(morphed, axis=2) == 0
        morphed[mask] = img1_array[mask]
        
        # Crossdissolve
        result = (morphed * (1 - t) + img2_array * t).astype(np.uint8)
        frames.append(Image.fromarray(result))
    
    return frames


def barycentric_coords(p: np.ndarray, triangle: np.ndarray) -> np.ndarray:
    """Вычисляет барицентрические координаты"""
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
    
    img1_path = "image1.jpg"
    img2_path = "image2.jpg"
    
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print("Ошибка: Необходимо подготовить два изображения (image1.jpg и image2.jpg)")
        return
    
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    
    # Убеждаемся, что изображения одинакового размера
    if img1.size != img2.size:
        print(f"Масштабирование второго изображения с {img2.size} на {img1.size}...")
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    if img1.mode != 'RGB':
        img1 = img1.convert('RGB')
    if img2.mode != 'RGB':
        img2 = img2.convert('RGB')
    
    print("=== Выделение контура на первом изображении ===")
    drawer1 = ContourDrawer(img1_path)
    contour1 = drawer1.run()
    
    if contour1 is None:
        print("Отменено")
        return
    
    print(f"Получен контур с {len(contour1)} точками")
    
    print("\n=== Выделение контура на втором изображении ===")
    drawer2 = ContourDrawer(img2_path)
    contour2 = drawer2.run()
    
    if contour2 is None:
        print("Отменено")
        return
    
    print(f"Получен контур с {len(contour2)} точками")
    
    # Строим сетку соответствия
    print("\nПостроение сетки соответствия...")
    points1, points2 = build_correspondence_grid(contour1, contour2, num_inner_points=3)
    
    print(f"Построена сетка с {len(points1)} соответствующих точек")
    
    # Генерируем кадры морфинга
    print("Генерирование кадров морфинга...")
    frames_forward = get_morphing_frames_auto(img1, img2, points1, points2, num_frames=20)
    
    # Добавляем обратный проход
    frames_animation = frames_forward + frames_forward[-2:0:-1]
    
    # Сохраняем
    os.makedirs("output", exist_ok=True)
    
    # Сохраняем промежуточные кадры
    for i, frame in enumerate(frames_forward):
        frame.save(f"output/morph_auto_frame_{i:02d}.png")
    
    # Сохраняем GIF
    frames_animation[0].save(
        "output/morph_auto_animation.gif",
        save_all=True,
        duration=100,
        loop=0
    )
    print("Сохранено: output/morph_auto_animation.gif")


if __name__ == "__main__":
    main()
