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


class WeatherSys:
    def __init__(self, weather_type):
        self.particles = []
        self.weather_type = weather_type
        self.accum = 0
        self.rate = 160 if weather_type == "rain" else 90

    def toggle(self):
        self.weather_type = "snow" if self.weather_type == "rain" else "rain"
        self.rate = 160 if self.weather_type == "rain" else 90
        self.particles.clear()

    def emit(self):
        p = Particle(
            random.uniform(0, WIDTH),
            random.uniform(-60, 0),
            0, 0, 0, 0,
            12, 1, (255, 255, 255)
        )

        if self.weather_type == "rain":
            p.vx = random.uniform(-15, 15)
            p.vy = random.uniform(250, 450)
            p.ax = 0
            p.ay = 500
            p.size = random.uniform(1, 2)
            p.color = (140, 175, 255)
        else:
            p.vx = random.uniform(-25, 25)
            p.vy = random.uniform(20, 55)
            p.ax = 0
            p.ay = 45
            p.size = random.uniform(2, 4.5)
            p.color = (255, 255, 255)

        self.particles.append(p)

    def update(self, dt):
        self.accum += dt
        inv = 1.0 / self.rate

        while self.accum >= inv:
            self.emit()
            self.accum -= inv

        for p in self.particles:
            if not p.alive:
                continue
            p.update(dt)
            
            if self.weather_type == "snow":
                p.vx = math.sin(p.y * 0.012) * 35

            if p.y > HEIGHT + 40:
                p.alive = False

        self.particles = [p for p in self.particles if p.alive]

    def draw(self, screen):
        if self.weather_type == "rain":
            for p in self.particles:
                if not p.alive:
                    continue
                tail_x = p.x - p.vx * 0.04
                tail_y = p.y - p.vy * 0.04
                pygame.draw.line(screen, p.color, (p.x, p.y), (tail_x, tail_y), 1)
        else:
            for p in self.particles:
                if not p.alive:
                    continue
                pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), int(p.size))


def task_b():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Task B - Rain/Snowfall")
    clock = pygame.time.Clock()

    weather = WeatherSys("rain")
    
    print("==================== УПРАВЛЕНИЕ =================")
    print("T - переключение дождь/снег | ESC - выход")
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
                if event.key == pygame.K_t:
                    weather.toggle()

        weather.update(dt)

        if weather.weather_type == "rain":
            bg_color = (35, 45, 65)
        else:
            bg_color = (190, 200, 220)

        screen.fill(bg_color)
        weather.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    task_b()
