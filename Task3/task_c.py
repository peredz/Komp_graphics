import pygame
import math

pygame.init()
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

# Настройки грамматик: (аксиома, правила, угол, длина, итерации)
SYSTEMS = {
    "bush": ("VZFFF", {"V": "[+++W][---W]W", "W": "FVP", "P": "F[-F]V"}, 25, 5, 6),
    "fern": ("X", {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}, 25, 3, 6),
}


def generate_l_system(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        next_str = "".join(rules.get(c, c) for c in current)
        current = next_str
    return current


def draw_l_system(instructions, angle_step, distance):
    screen.fill((255, 255, 255))
    stack = []
    x, y = 500, 650
    angle = -90  # Вверх

    for char in instructions:
        if char == "F":
            nx = x + distance * math.cos(math.radians(angle))
            ny = y + distance * math.sin(math.radians(angle))
            pygame.draw.line(screen, (60, 40, 20), (x, y), (nx, ny), 1)
            x, y = nx, ny
        elif char == "+":
            angle += angle_step
        elif char == "-":
            angle -= angle_step
        elif char == "[":
            stack.append((x, y, angle))
        elif char == "]":
            # Перед возвратом рисуем листву
            pygame.draw.circle(screen, (34, 139, 34), (int(x), int(y)), 3)
            x, y, angle = stack.pop()


# Выбор системы и отрисовка
axiom, rules, angle, dist, iters = SYSTEMS["bush"]
model_str = generate_l_system(axiom, rules, iters)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

    draw_l_system(model_str, angle, dist)
    pygame.display.flip()
    clock.tick(1)

pygame.quit()