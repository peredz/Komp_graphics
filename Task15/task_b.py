import pygame
import math
import numpy as np
from PIL import Image

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, t):
        return Vec3(self.x * t, self.y * t, self.z * t)

def rot_x(v, a):
    c, s = math.cos(a), math.sin(a)
    return Vec3(v.x, v.y * c - v.z * s, v.y * s + v.z * c)

def rot_y(v, a):
    c, s = math.cos(a), math.sin(a)
    return Vec3(v.x * c + v.z * s, v.y, -v.x * s + v.z * c)

def project(v, fov, cx, cy):
    z = v.z + fov
    z = max(0.001, z)
    scale = fov / z
    return (cx + v.x * scale, cy + v.y * scale)

class HeightMap:
    def __init__(self):
        self.W, self.H = 0, 0
        self.data = None
    
    def get(self, x, y):
        x = max(0, min(x, self.W - 1))
        y = max(0, min(y, self.H - 1))
        return self.data[y * self.W + x]
    
    def load_from_file(self, path):
        try:
            img = Image.open(path).convert('L')
            self.W, self.H = img.size
            arr = np.array(img, dtype=np.float32) / 255.0
            self.data = arr.flatten()
            return True
        except:
            return False
    
    def generate_synthetic(self, w, h):
        self.W, self.H = w, h
        self.data = np.zeros(w * h, dtype=np.float32)
        for y in range(h):
            for x in range(w):
                fx, fy = x / w, y / h
                v = (0.5 * math.sin(fx * 2 * math.pi * 2) * math.cos(fy * 2 * math.pi * 2) +
                     0.25 * math.sin(fx * 2 * math.pi * 5 + 1) * math.sin(fy * 2 * math.pi * 4) +
                     0.15 * math.cos(fx * 2 * math.pi * 8) * math.sin(fy * 2 * math.pi * 7 + 0.5) +
                     0.1 * math.sin(fx * 2 * math.pi * 13 + fy * 2 * math.pi * 11))
                self.data[y * w + x] = (v + 1.0) * 0.5

class Mesh:
    def __init__(self):
        self.verts = []
        self.tri_idx = []
        self.colors = []
        self.grid_w, self.grid_h = 0, 0
    
    def build(self, hm, height_scale, height_exp, smoothed, use_natural_colors, cell_size=1.0):
        self.grid_w, self.grid_h = hm.W, hm.H
        self.verts = []
        self.colors = []
        
        off_x = (self.grid_w - 1) * cell_size * 0.5
        off_z = (self.grid_h - 1) * cell_size * 0.5
        
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if smoothed:
                    h = (hm.get(x, y) + hm.get(x - 1, y) + hm.get(x + 1, y) +
                         hm.get(x, y - 1) + hm.get(x, y + 1)) / 5.0
                else:
                    h = hm.get(x, y)
                
                raised = (h ** height_exp) * height_scale
                self.verts.append(Vec3(
                    x * cell_size - off_x,
                    -raised,
                    y * cell_size - off_z
                ))
                
                if use_natural_colors:
                    self.colors.append(height_color_natural(h))
                else:
                    self.colors.append((128, 128, 128))
        
        self.tri_idx = []
        for y in range(self.grid_h - 1):
            for x in range(self.grid_w - 1):
                tl = y * self.grid_w + x
                tr = tl + 1
                bl = tl + self.grid_w
                br = bl + 1
                self.tri_idx.extend([tl, tr, bl, tr, br, bl])

def height_color_natural(h):
    stops = [
        (0.00, (15, 50, 80)),
        (0.15, (25, 90, 140)),
        (0.25, (50, 130, 180)),
        (0.30, (194, 178, 128)),
        (0.35, (85, 140, 50)),
        (0.45, (70, 160, 60)),
        (0.55, (90, 130, 50)),
        (0.65, (130, 115, 70)),
        (0.75, (120, 90, 60)),
        (0.85, (100, 80, 70)),
        (0.92, (180, 180, 180)),
        (1.00, (255, 255, 255)),
    ]
    
    if h <= stops[0][0]:
        return stops[0][1]
    if h >= stops[-1][0]:
        return stops[-1][1]
    
    for i in range(1, len(stops)):
        if h <= stops[i][0]:
            t = (h - stops[i-1][0]) / (stops[i][0] - stops[i-1][0])
            a, b = stops[i-1][1], stops[i][1]
            return tuple(int(a[j] + t * (b[j] - a[j])) for j in range(3))
    
    return stops[-1][1]

def render_mesh(surface, mesh, angle_x, angle_y, zoom, fov, wire_mode):
    w, h = surface.get_size()
    cx, cy = w * 0.5, h * 0.5
    
    screen = []
    for v in mesh.verts:
        v_scaled = v * zoom
        v_rot = rot_x(v_scaled, angle_x)
        v_rot = rot_y(v_rot, angle_y)
        v_rot.z += fov * 2.5
        p = project(v_rot, fov, cx, cy)
        screen.append((int(p[0]), int(p[1])))
    
    if wire_mode:
        for t in range(len(mesh.tri_idx) // 3):
            i0, i1, i2 = mesh.tri_idx[t*3], mesh.tri_idx[t*3+1], mesh.tri_idx[t*3+2]
            
            pygame.draw.line(surface, (255, 255, 255), screen[i0], screen[i1], 1)
            pygame.draw.line(surface, (255, 255, 255), screen[i1], screen[i2], 1)
            pygame.draw.line(surface, (255, 255, 255), screen[i2], screen[i0], 1)
    else:
        for t in range(len(mesh.tri_idx) // 3):
            i0, i1, i2 = mesh.tri_idx[t*3], mesh.tri_idx[t*3+1], mesh.tri_idx[t*3+2]
            c0 = mesh.colors[i0]
            
            pts = [screen[i0], screen[i1], screen[i2]]
            pygame.draw.polygon(surface, c0, pts)

def main():
    pygame.init()
    W, H = 800, 800
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Task B — Camera control")
    clock = pygame.time.Clock()
    
    hm = HeightMap()
    if not hm.load_from_file("landscape.jpg"):
        print("Файл не найден — генерация синтетической карты 64×64")
        hm.generate_synthetic(64, 64)
    else:
        print(f"Карта загружена: {hm.W}×{hm.H} пикселей")
    
    step = max(1, min(hm.W, hm.H) // 60)
    sub_hm = HeightMap()
    sub_hm.W, sub_hm.H = hm.W // step, hm.H // step
    sub_hm.data = np.array([hm.get(x * step, y * step) 
                            for y in range(sub_hm.H) 
                            for x in range(sub_hm.W)], dtype=np.float32)
    
    mesh = Mesh()
    mesh.build(sub_hm, 20.0, 1.0, False, True, 1.0)
    
    angle_x, angle_y = 0.5, 0.3
    zoom = 8.0
    fov = 400.0
    mode = "solid"
    
    dragging = False
    last_mouse = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "wire"
                elif event.key == pygame.K_2:
                    mode = "solid"
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse:
                    cur = pygame.mouse.get_pos()
                    dx = (cur[0] - last_mouse[0]) * 0.005
                    dy = (cur[1] - last_mouse[1]) * 0.005
                    angle_y += dx
                    angle_x += dy
                    angle_x = max(-1.5, min(1.5, angle_x))
                    last_mouse = cur
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom *= 1.1
                else:
                    zoom *= 0.9
                zoom = max(0.5, min(100.0, zoom))
        
        screen.fill((20, 25, 35))
        render_mesh(screen, mesh, angle_x, angle_y, zoom, fov, mode == "wire")
        
        font = pygame.font.Font(None, 24)
        text = font.render(f"Режим: {mode} | Mouse: rotate | Wheel: zoom | 1:Wire 2:Solid ESC:Exit", True, (220, 220, 220))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
