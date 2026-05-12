import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

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

def create_torus(major_r, minor_r, major_segs, minor_segs):
    vertices = []
    normals = []
    indices = []
    
    for i in range(major_segs):
        theta = 2 * math.pi * i / major_segs
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        
        for j in range(minor_segs):
            phi = 2 * math.pi * j / minor_segs
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)
            
            x = (major_r + minor_r * cos_phi) * cos_theta
            y = minor_r * sin_phi
            z = (major_r + minor_r * cos_phi) * sin_theta
            
            nx = cos_phi * cos_theta
            ny = sin_phi
            nz = cos_phi * sin_theta
            
            vertices.append([x, y, z])
            normals.append([nx, ny, nz])
    
    for i in range(major_segs):
        for j in range(minor_segs):
            a = i * minor_segs + j
            b = a + minor_segs
            c = ((i + 1) % major_segs) * minor_segs + j
            d = c + minor_segs
            
            indices.extend([a, b % (major_segs * minor_segs), c])
            indices.extend([c, b % (major_segs * minor_segs), d % (major_segs * minor_segs)])
    
    return vertices, normals, indices

def gouraud_lighting(normal, pos, light_pos, mat_diffuse, ambient):
    normal = Vec3(normal[0], normal[1], normal[2])
    pos = Vec3(pos[0], pos[1], pos[2])
    light = (light_pos - pos).normalize()
    
    diff = max(0, normal.dot(light))
    diffuse = Vec3(mat_diffuse[0], mat_diffuse[1], mat_diffuse[2]) * diff
    ambient_color = Vec3(mat_diffuse[0], mat_diffuse[1], mat_diffuse[2]) * ambient
    color = ambient_color + diffuse
    
    return [min(1.0, color.x), min(1.0, color.y), min(1.0, color.z)]

def phong_lighting(normal, pos, light_pos, eye_pos, mat_diffuse, ambient):
    normal = Vec3(normal[0], normal[1], normal[2])
    pos = Vec3(pos[0], pos[1], pos[2])
    
    light = (light_pos - pos).normalize()
    view = (eye_pos - pos).normalize()
    reflect = (normal * (2 * normal.dot(light))) - light
    
    diff = max(0, normal.dot(light))
    spec = max(0, view.dot(reflect)) ** 16
    
    diffuse = Vec3(mat_diffuse[0], mat_diffuse[1], mat_diffuse[2]) * diff
    specular = Vec3(1.0, 1.0, 1.0) * spec * 0.5
    ambient_color = Vec3(mat_diffuse[0], mat_diffuse[1], mat_diffuse[2]) * ambient
    
    color = ambient_color + diffuse + specular
    return [min(1.0, color.x), min(1.0, color.y), min(1.0, color.z)]

def draw_mesh(vertices, normals, indices, light_pos, eye_pos, mat_diffuse, ambient, shading_mode):
    colors = []
    
    if shading_mode == "gouraud":
        for i, normal in enumerate(normals):
            color = gouraud_lighting(normal, vertices[i], light_pos, mat_diffuse, ambient)
            colors.append(color)
    else:
        for i, normal in enumerate(normals):
            color = phong_lighting(normal, vertices[i], light_pos, eye_pos, mat_diffuse, ambient)
            colors.append(color)
    
    glBegin(GL_TRIANGLES)
    for idx in indices:
        glColor3f(colors[idx][0], colors[idx][1], colors[idx][2])
        glVertex3f(vertices[idx][0], vertices[idx][1], vertices[idx][2])
    glEnd()

def draw_light_indicator(position, color):
    glPushMatrix()
    glTranslatef(position.x, position.y, position.z)
    glColor3f(color.x, color.y, color.z)
    quad = gluNewQuadric()
    gluSphere(quad, 0.15, 8, 8)
    glPopMatrix()

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)

def main():
    pygame.init()
    display = (800, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Task B - Gouraud vs Phong (SPACE to toggle)")
    
    glViewport(0, 0, 800, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 1.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    init_opengl()
    
    sphere_verts, sphere_norms, sphere_inds = create_sphere(0.8, 15, 15)
    torus_verts, torus_norms, torus_inds = create_torus(0.6, 0.3, 20, 15)
    
    shading_mode = "gouraud"
    clock = pygame.time.Clock()
    time = 0.0
    
    print("Current mode: Gouraud (SPACE to toggle)")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shading_mode = "phong" if shading_mode == "gouraud" else "gouraud"
                    print(f"Switched to: {shading_mode.upper()}")
        
        time += 0.02
        light_pos = Vec3(3.5 * math.cos(time * 0.5), 1.5, 3.5 * math.sin(time * 0.5))
        eye_pos = Vec3(0.0, 0.0, 5.0)
        ambient = 0.3
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.12, 0.12, 0.16, 1.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        glRotatef(20.0, 1.0, 0.0, 0.0)
        glRotatef(time * 10.0, 0.0, 1.0, 0.0)
        
        glPushMatrix()
        glTranslatef(-1.5, 0.0, 0.0)
        draw_mesh(sphere_verts, sphere_norms, sphere_inds, light_pos, eye_pos, [0.4, 0.4, 1.0], ambient, shading_mode)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(1.5, 0.0, 0.0)
        draw_mesh(torus_verts, torus_norms, torus_inds, light_pos, eye_pos, [1.0, 0.4, 0.4], ambient, shading_mode)
        glPopMatrix()
        
        draw_light_indicator(light_pos, Vec3(1.0, 1.0, 0.8))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

