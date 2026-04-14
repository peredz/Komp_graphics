import pygame
import math

pygame.init()
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

SYSTEMS = {
    "1": ("F", {"F": "FF+[+F-F-F]-[-F+F+F]"}, 25, 4, 4),  # куст
    "2": ("X", {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}, 25, 3, 6),  # папоротник
}


def generate_l_system(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        current = "".join(rules.get(c, c) for c in current)
    return current


def draw_l_system(instructions, angle_step, distance):
    screen.fill((255, 255, 255))
    stack = []
    x, y = 500, 650
    angle = -90

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
            pygame.draw.circle(screen, (34, 139, 34), (int(x), int(y)), 2)
            x, y, angle = stack.pop()


current_key = "1"
axiom, rules, angle_step, dist, iters = SYSTEMS[current_key]
model_str = generate_l_system(axiom, rules, iters)
needs_update = True

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_key = "1"
                needs_update = True
            elif event.key == pygame.K_2:
                current_key = "2"
                needs_update = True

    if needs_update:
        axiom, rules, angle_step, dist, iters = SYSTEMS[current_key]
        model_str = generate_l_system(axiom, rules, iters)
        draw_l_system(model_str, angle_step, dist)
        pygame.display.flip()
        needs_update = False

    clock.tick(30)

pygame.quit()