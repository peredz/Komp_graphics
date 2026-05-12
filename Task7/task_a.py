import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, v):
        return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)
    
    def __sub__(self, v):
        return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)
    
    def __mul__(self, s):
        return Vec3(self.x * s, self.y * s, self.z * s)
    
    def __truediv__(self, s):
        return Vec3(self.x / s, self.y / s, self.z / s) if s != 0 else Vec3(0, 0, 0)
    
    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z
    
    def cross(self, v):
        return Vec3(self.y * v.z - self.z * v.y, self.z * v.x - self.x * v.z, self.x * v.y - self.y * v.x)
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return Vec3(self.x / l, self.y / l, self.z / l)
        return Vec3(0, 0, 0)

def create_sphere(radius, slices, stacks):
    vertices = []
    normals = []
    indices = []
    
    for i in range(stacks + 1):
        lat = math.pi * i / stacks
        sin_lat = math.sin(lat)
        cos_lat = math.cos(lat)
        
        for j in range(slices + 1):
            lng = 2 * math.pi * j / slices
            sin_lng = math.sin(lng)
            cos_lng = math.cos(lng)
            
            x = radius * sin_lat * cos_lng
            y = radius * cos_lat
            z = radius * sin_lat * sin_lng
            
            vertices.append([x, y, z])
            normal = Vec3(x, y, z).normalize()
            normals.append([normal.x, normal.y, normal.z])
    
    for i in range(stacks):
        for j in range(slices):
            a = i * (slices + 1) + j
            b = a + slices + 1
            indices.extend([a, b, a + 1])
            indices.extend([b, b + 1, a + 1])
    
    return vertices, normals, indices

def gouraud_lighting(normal, light_pos, eye_pos, mat_diffuse):
    normal = Vec3(normal[0], normal[1], normal[2])
    eye = (eye_pos - Vec3(normal.x, normal.y, normal.z)).normalize()
    light = (light_pos - Vec3(normal.x, normal.y, normal.z)).normalize()
    
    diff = max(0, normal.dot(light))
    diffuse = Vec3(mat_diffuse[0], mat_diffuse[1], mat_diffuse[2]) * diff
    
    ambient = Vec3(0.2, 0.2, 0.2)
    color = ambient + diffuse
    
    return [min(1.0, color.x), min(1.0, color.y), min(1.0, color.z)]

def draw_sphere(radius, slices, stacks, light_pos, eye_pos, mat_diffuse):
    vertices, normals, indices = create_sphere(radius, slices, stacks)
    
    colors = []
    for normal in normals:
        color = gouraud_lighting(normal, light_pos, eye_pos, mat_diffuse)
        colors.append(color)
    
    glBegin(GL_TRIANGLES)
    for idx in indices:
        glColor3f(colors[idx][0], colors[idx][1], colors[idx][2])
        glVertex3f(vertices[idx][0], vertices[idx][1], vertices[idx][2])
    glEnd()

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)

def setup_camera(angle_x, angle_y, zoom):
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0 * zoom)
    glRotatef(angle_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)

def draw_light_indicator(position, color):
    glPushMatrix()
    glTranslatef(position.x, position.y, position.z)
    glColor3f(color.x, color.y, color.z)
    quad = gluNewQuadric()
    gluSphere(quad, 0.15, 10, 10)
    glPopMatrix()

def main():
    pygame.init()
    display = (800, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Task A - Gouraud Shading")
    
    glViewport(0, 0, 800, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 1.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    init_opengl()
    
    clock = pygame.time.Clock()
    time = 0.0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        time += 0.02
        light_pos = Vec3(3.0 * math.cos(time), 2.0, 3.0 * math.sin(time))
        eye_pos = Vec3(0.0, 0.0, 5.0)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.12, 0.12, 0.16, 1.0)
        
        glMatrixMode(GL_MODELVIEW)
        setup_camera(20.0, time * 10.0, 1.0)
        
        draw_sphere(1.0, 10, 10, light_pos, eye_pos, [0.4, 0.4, 1.0])
        draw_light_indicator(light_pos, Vec3(1.0, 1.0, 0.8))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
