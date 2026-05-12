import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import ctypes


# =====================
# Вектор
# =====================

class Vec3:
    def __init__(self,x=0,y=0,z=0):
        self.x,self.y,self.z=x,y,z

    def __add__(self,v):
        return Vec3(self.x+v.x,self.y+v.y,self.z+v.z)

    def __sub__(self,v):
        return Vec3(self.x-v.x,self.y-v.y,self.z-v.z)

    def __mul__(self,s):
        return Vec3(self.x*s,self.y*s,self.z*s)

    def dot(self,v):
        return self.x*v.x+self.y*v.y+self.z*v.z

    def normalize(self):
        l=math.sqrt(self.dot(self))
        if l==0:return Vec3()
        return Vec3(self.x/l,self.y/l,self.z/l)


# =====================
# Сфера
# =====================

def create_sphere(r,slices,stacks):
    v,n,i=[],[],[]

    for s in range(stacks+1):
        lat=math.pi*s/stacks
        for t in range(slices+1):
            lon=2*math.pi*t/slices
            x=r*math.sin(lat)*math.cos(lon)
            y=r*math.cos(lat)
            z=r*math.sin(lat)*math.sin(lon)
            v.append([x,y,z])
            nn=Vec3(x,y,z).normalize()
            n.append([nn.x,nn.y,nn.z])

    for s in range(stacks):
        for t in range(slices):
            a=s*(slices+1)+t
            b=a+slices+1
            i+= [a,b,a+1,b,b+1,a+1]

    return v,n,i


# =====================
# Phong
# =====================

def phong(normal,pos,lights,eye,color):
    n=Vec3(*normal).normalize()
    p=Vec3(*pos)

    result=Vec3(color[0]*0.2,color[1]*0.2,color[2]*0.2)

    for lp,lc in lights:
        l=(lp-p).normalize()
        v=(eye-p).normalize()
        diff=max(n.dot(l),0)

        r=(n*(2*n.dot(l))-l).normalize()
        spec=max(v.dot(r),0)**16

        result+=Vec3(*color)*diff
        result+=Vec3(*lc)*(spec*0.5)

    return [min(result.x,1),
            min(result.y,1),
            min(result.z,1)]


def draw_mesh(v,n,i,lights,eye,color):
    glBegin(GL_TRIANGLES)
    for idx in i:
        c=phong(n[idx],v[idx],lights,eye,color)
        glColor3f(*c)
        glVertex3f(*v[idx])
    glEnd()


def draw_shadow(v,i):
    glBegin(GL_TRIANGLES)
    for idx in i:
        glVertex3f(*v[idx])
    glEnd()


# =====================
# Shadow Matrix (100% корректная)
# =====================

def shadow_matrix(light, ground_y):

    A,B,C,D = 0,1,0,-ground_y

    lx,ly,lz,lw = light.x,light.y,light.z,1.0

    dot = A*lx+B*ly+C*lz+D*lw

    m = [
        dot-lx*A, -lx*B, -lx*C, -lx*D,
        -ly*A, dot-ly*B, -ly*C, -ly*D,
        -lz*A, -lz*B, dot-lz*C, -lz*D,
        -lw*A, -lw*B, -lw*C, dot-lw*D
    ]

    return (ctypes.c_float*16)(*m)


# =====================
# MAIN
# =====================

def main():

    pygame.init()
    display=(900,700)
    pygame.display.set_mode(display,DOUBLEBUF|OPENGL)

    gluPerspective(45,display[0]/display[1],0.1,100)
    glEnable(GL_DEPTH_TEST)

    v,n,i=create_sphere(1,30,30)

    ground_y=-1.5
    clock=pygame.time.Clock()
    t=0

    while True:

        for e in pygame.event.get():
            if e.type==QUIT:
                pygame.quit()
                return

        t+=0.01

        glClearColor(0.1,0.1,0.15,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        gluLookAt(0,4,10, 0,0,0, 0,1,0)

        light1=Vec3(4*math.cos(t),4,4*math.sin(t))
        light2=Vec3(-4*math.cos(t*0.7),3,-4*math.sin(t*0.7))

        lights=[(light1,[1,0.3,0.3]),
                (light2,[0.3,0.3,1])]

        eye=Vec3(0,4,10)

        # Земля
        glColor3f(0.3,0.3,0.3)
        glBegin(GL_QUADS)
        glVertex3f(-10,ground_y,-10)
        glVertex3f(10,ground_y,-10)
        glVertex3f(10,ground_y,10)
        glVertex3f(-10,ground_y,10)
        glEnd()

        obj_pos=(0,ground_y+1,0)

        # ---------- ТЕНИ ----------
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0,0,0,0.5)

        for light in [light1,light2]:

            mat=shadow_matrix(light,ground_y)

            glPushMatrix()
            glMultMatrixf(mat)

            glPushMatrix()
            glTranslatef(*obj_pos)
            draw_shadow(v,i)
            glPopMatrix()

            glPopMatrix()

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        # ---------- ОБЪЕКТ ----------
        glPushMatrix()
        glTranslatef(*obj_pos)
        draw_mesh(v,n,i,lights,eye,[0.3,0.6,1])
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)


if __name__=="__main__":
    main()