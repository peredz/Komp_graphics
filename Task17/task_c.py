import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 800
FPS = 60


class Particle:
    def __init__(self, x, y, vx, vy, ax, ay, life, size, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.alive = True
        self.frame = 0
        self.alpha = 255

    def update(self, dt):
        if not self.alive:
            return
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def ratio(self):
        return max(0, min(self.life / self.max_life, 1))


class FireSys:
    FRAME_SIZE = 32
    FRAMES = 4

    def __init__(self, x, y):
        self.emitter_x = x
        self.emitter_y = y
        self.particles = []
        self.rate = 55
        self.accum = 0
        self.atlas = self._build_atlas()

    def _build_atlas(self):
        atlas = pygame.Surface((self.FRAME_SIZE * self.FRAMES, self.FRAME_SIZE), pygame.SRCALPHA)
        
        for frame in range(self.FRAMES):
            for y in range(self.FRAME_SIZE):
                for x in range(self.FRAME_SIZE):
                    dx = x - self.FRAME_SIZE / 2
                    dy = y - self.FRAME_SIZE / 2
                    d = math.sqrt(dx*dx + dy*dy) / (self.FRAME_SIZE / 2)
                    intensity = max(0, 1 - d)
                    intensity *= 1 - frame * 0.12
                    
                    n = 0.8 + 0.2 * math.sin(x * 0.4 + frame) * math.cos(y * 0.4 - frame)
                    intensity *= n
                    
                    alpha = int(intensity * 255)
                    
                    if intensity > 0.7:
                        color = (255, 255, 210, alpha)
                    elif intensity > 0.4:
                        color = (255, 190, 20, alpha)
                    else:
                        color = (255, 100, 0, alpha)
                    
                    atlas.set_at((frame * self.FRAME_SIZE + x, y), color)
        
        return atlas

    def update(self, dt):
        self.accum += dt
        inv = 1.0 / self.rate

        while self.accum >= inv:
            p = Particle(
                self.emitter_x + random.uniform(-18, 18),
                self.emitter_y + random.uniform(-5, 5),
                random.uniform(-22, 22),
                random.uniform(-130, -55),
                0,
                -25,
                random.uniform(0.9, 2.1),
                random.uniform(16, 32),
                (255, 255, 255)
            )
            self.particles.append(p)
            self.accum -= inv

        for p in self.particles:
            if not p.alive:
                continue
            p.update(dt)
            prog = 1 - p.ratio()
            p.frame = min(int(prog * self.FRAMES), self.FRAMES - 1)
            p.alpha = int(p.ratio() * 255)

        self.particles = [p for p in self.particles if p.alive]

    def draw(self, screen):
        for p in self.particles:
            if not p.alive:
                continue
            
            frame_rect = pygame.Rect(p.frame * self.FRAME_SIZE, 0, self.FRAME_SIZE, self.FRAME_SIZE)
            frame_surf = self.atlas.subsurface(frame_rect).copy()
            frame_surf.set_alpha(p.alpha)
            
            scale = p.size / self.FRAME_SIZE
            scaled_size = int(self.FRAME_SIZE * scale)
            scaled_surf = pygame.transform.scale(frame_surf, (scaled_size, scaled_size))
            
            rect = scaled_surf.get_rect(center=(int(p.x), int(p.y)))
            screen.blit(scaled_surf, rect, special_flags=pygame.BLEND_ADD)


def task_c():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task C - Fire")
    clock = pygame.time.Clock()

    fire = FireSys(WIDTH // 2, HEIGHT - 100)
    
    print("==================== УПРАВЛЕНИЕ =================")
    print("Наблюдайте за огнём | ESC - выход")
    print("=================================================\n")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        fire.update(dt)

        screen.fill((10, 5, 5))
        fire.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    task_c()
