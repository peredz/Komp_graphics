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


class Fireworks:
    PALETTES = [
        [(255, 80, 60), (255, 200, 80), (255, 255, 180)],
        [(60, 120, 255), (130, 200, 255), (220, 240, 255)],
        [(80, 255, 80), (180, 255, 160), (230, 255, 220)],
        [(255, 80, 220), (255, 160, 200), (255, 220, 230)],
        [(255, 220, 50), (255, 240, 160), (255, 255, 210)],
    ]

    def __init__(self, x, y):
        self.origin_x = x
        self.origin_y = y
        self.particles = []
        self.timer = 0
        self.interval = 1.4

    def launch(self):
        n = random.randint(120, 220)
        ep_x = self.origin_x + random.uniform(-60, 60)
        ep_y = self.origin_y + random.uniform(-220, -80)

        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 220)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            life = random.uniform(1.0, 2.6)
            size = random.uniform(2, 5)
            frame = random.randint(0, len(self.PALETTES) - 1)
            
            p = Particle(ep_x, ep_y, vx, vy, 0, 140, life, size, (255, 255, 255))
            p.frame = frame
            self.particles.append(p)

    def lerp_color(self, c1, c2, t):
        t = max(0, min(t, 1))
        return (
            int(c1[0] + t * (c2[0] - c1[0])),
            int(c1[1] + t * (c2[1] - c1[1])),
            int(c1[2] + t * (c2[2] - c1[2]))
        )

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.launch()
            self.timer = 0

        for p in self.particles:
            if not p.alive:
                continue
            p.update(dt)
            t = 1 - p.ratio()
            pal = self.PALETTES[p.frame % len(self.PALETTES)]
            
            if t < 0.5:
                p.color = self.lerp_color(pal[0], pal[1], t * 2)
            else:
                p.color = self.lerp_color(pal[1], pal[2], (t - 0.5) * 2)

        self.particles = [p for p in self.particles if p.alive]

    def draw(self, screen):
        for p in self.particles:
            if not p.alive:
                continue
            pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), int(p.size))


def task_a():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task A - Fireworks")
    clock = pygame.time.Clock()

    fireworks = Fireworks(WIDTH // 2, HEIGHT - 100)
    
    print("==================== УПРАВЛЕНИЕ =================")
    print("SPACE - запуск фейерверка | ESC - выход")
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
                if event.key == pygame.K_SPACE:
                    fireworks.launch()

        fireworks.update(dt)

        screen.fill((8, 8, 25))
        fireworks.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    task_a()
