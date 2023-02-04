import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import math

from math_utils import *
from vector3 import *
from ui import *

def drawOrigin():
    glBegin(GL_LINES)
    glColor(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(1000, 0, 0)
    glEnd()

    glBegin(GL_LINES)
    glColor(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0, 1000, 0)
    glEnd()

    glBegin(GL_LINES)
    glColor(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0, 0, 1000)
    glEnd()

def drawTerrain(t):
    glColor(0, 0.8, 0)
    glBegin(GL_POINTS)
    for vector in t.data:
        glVertex3f(vector.x, vector.y, vector.z)

    glEnd()

def drawShells(shells):
    glLineWidth(3)
    for s in shells:

        if s.flight_time > 0.04:
            glColor(1, 1, 0)
            glBegin(GL_LINES)
            glVertex3f(s.pos.x, s.pos.y, s.pos.z)
            glVertex3f(s.pos.x - s.vel.x * 0.05, s.pos.y - s.vel.y * 0.05, s.pos.z - s.vel.z * 0.05)
            glEnd()

        glBegin(GL_POINTS)
        glVertex3f(s.pos.x, s.pos.y, s.pos.z)
        glEnd()
        
    glLineWidth(1)

def drawPanzer(p):

    glColor(p.color[0], p.color[1], p.color[2])

    sx = p.size.x
    sy = p.size.y
    sz = p.size.z
    
    # get into panzer matrix
    glPushMatrix()
    glTranslate(p.pos.x, p.pos.y, p.pos.z)
    glRotate(p.rot, 0, 1, 0)
    glRotate(p.hull_angle, -1, 0, 0)
    
    glBegin(GL_LINES)
    glVertex3f(0, 0, sz)
    glVertex3f(0, 0, -sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(sx, 0, sz)
    glVertex3f(sx, 0, -sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-sx, 0, sz)
    glVertex3f(-sx, 0, -sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-sx, 0, sz)
    glVertex3f(sx, 0, sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-sx, 0, -sz)
    glVertex3f(sx, 0, -sz)
    glEnd()

    ## up 1
    glBegin(GL_LINES)
    glVertex3f(0, sy, sz)
    glVertex3f(0, sy, -sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(sx, sy, sz)
    glVertex3f(sx, sy, -sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-sx, sy, sz)
    glVertex3f(-sx, sy, -sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-sx, sy, sz)
    glVertex3f(sx, sy, sz)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-sx, sy, -sz)
    glVertex3f(sx, sy, -sz)
    glEnd()

    # turret
    local_x, local_y, local_z = p.local_x, p.local_y, p.local_z
    turret_x, turret_z = p.turret_x, p.turret_z
    gun_z = p.gun_z

    # get into turret matrix
    glPushMatrix()
    
    glTranslate(0, sy, 0)
    glRotate(p.turret_rot, 0, 1, 0)
    
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, sz * 0.5)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 0, sz * 0.5)
    glVertex3f(0.35 * sx, 0, -sz * 0.35)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 0, sz * 0.5)
    glVertex3f(-0.35 * sx, 0, -sz * 0.35)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-0.35 * sx, 0, -sz * 0.35)
    glVertex3f(0.35 * sx, 0, -sz * 0.35)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, sy * 0.3, 0)
    glVertex3f(0, 0, sz * 0.5)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, sy * 0.3, 0)
    glVertex3f(0.35 * sx, 0, -sz * 0.35)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, sy * 0.3, 0)
    glVertex3f(-0.35 * sx, 0, -sz * 0.35)
    glEnd()

    # get into gun matrix
    glPushMatrix()

    glRotate(p.gun_rot, -1, 0, 0)

    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, sz * 0.8)
    glEnd()

    # get out of gun matrix
    glPopMatrix()

    # get out of turret matrix
    glPopMatrix()

    # get out of panzer matrix
    glPopMatrix()

def drawScene(ground, cam, p1, p2, shells):
    #drawOrigin()
    drawTerrain(ground)
    drawPanzer(p1)
    drawPanzer(p2)
    drawShells(shells)
