from OpenGL import GL
from OpenGL.GLU import *
from OpenGL.GLUT import *

import os
import math
from PIL import Image
imagesize = (500, 400)

def init():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA|GLUT_SINGLE)
    width, height = imagesize
    glutInitWindowSize(width, height)
    glutCreateWindow("Sencond")
    glutDisplayFunc(drawFunc)
    GL.glClearColor(0.5, 0.5, 0.5, 1.0)
    gluOrtho2D(0.0, float(width), float(height), 0.0)
    #anti-aliasing codes
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)  
    GL.glEnable(GL.GL_BLEND)
    GL.glHint(GL.GL_POINT_SMOOTH_HINT, GL.GL_NICEST)
    GL.glEnable(GL.GL_POINT_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    #GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)
    #GL.glEnable(GL.GL_POLYGON_SMOOTH)
 
def drawFunc():
    control_points = [
        (50.0, 50.0),
        (200.0, 100.0),
        (250.0, 200.0),
        (200.0, 350.0)
                      ]
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    generate_texture()     
    curve =  get_bspline(control_points, 3)
    
    #draw_points(curve, (0.0, 0.0, 1.0), 2)
    draw_untextured_stroke(curve, (0.0, 0.75, 0.5), 60)
    curve2 = [tuple(x+75 for x in point) for point in curve]
    draw_untextured_stroke(curve2, (0.25, 0.70, 0.5), 40)
    #draw_points(curve, (1.0, 1.0, 0.0), 7)
    #draw_line_strip(curve, (0.0, 1.0, 0.0), 1)

    
    GL.glFlush()
def draw_untextured_stroke(curve, color, radius) :
    #decaying the texture of a complete stroke
    GL.glBegin(GL.GL_QUAD_STRIP)
    #GL.glBegin(GL.GL_LINES)
    GL.glColor3fv(color)
    total_length = 0.0
    last_point = curve[0]
    for point in curve[1:]:
        dx = last_point[0] - point[0]
        dy = last_point[1] - point[1]
        total_length += math.sqrt(dx*dx+dy*dy)
        last_point = point
    last_point, point= curve[:2]
    theta_former = math.atan2(last_point[1]-point[1], point[0]-last_point[0])
    dx, dy=  radius * math.sin(theta_former), radius * math.cos(theta_former)
    vertex_1 = (last_point[0] - dx, last_point[1] - dy)
    vertex_2 = (last_point[0] + dx, last_point[1] + dy)    
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex2fv(vertex_1)
    GL.glTexCoord2f(0.0, 0.0)    
    GL.glVertex2fv(vertex_2)
    cur_length = 0.0
    for next_point in curve[2:] :
        theta_later = math.atan2(point[1]-next_point[1], next_point[0]-point[0])
        beta = 0.5 * (theta_former + theta_later)
        dx, dy=  radius * math.sin(beta), radius * math.cos(beta)
        vertex_1 = (point[0] - dx, point[1] - dy)
        vertex_2 = (point[0] + dx, point[1] + dy)        
        dx = last_point[0] - point[0]
        dy = last_point[1] - point[1]
        cur_length += math.sqrt(dx*dx+dy*dy)
        GL.glTexCoord2f(cur_length/total_length, 1.0)
        GL.glVertex2fv(vertex_1)
        GL.glTexCoord2f(cur_length/total_length, 0.0)         
        GL.glVertex2fv(vertex_2)        
        last_point, point = point, next_point
        theta_former = theta_later
    dx, dy=  radius * math.sin(theta_later), radius * math.cos(theta_later)
    vertex_1 = (next_point[0] - dx, next_point[1] - dy)
    vertex_2 = (next_point[0] + dx, next_point[1] + dy)
    GL.glTexCoord2f(1.0, 1.0)
    GL.glVertex2fv(vertex_1)
    GL.glTexCoord2f(1.0, 0.0)    
    GL.glVertex2fv(vertex_2)
    GL.glEnd()
    
def draw_textured_stroke(curve, color, radius) :
    #apply stroke matrix
    GL.glBegin(GL.GL_QUAD_STRIP)
    #GL.glBegin(GL.GL_LINES)
    GL.glColor3fv(color)
    #total_length = 0.0
    #last_point = curve[0]
    #for point in curve[1:]:
        #dx = last_point[0] - point[0]
        #dy = last_point[1] - point[1]
        #total_length += math.sqrt(dx*dx+dy*dy)
        #last_point = point
    last_point, point= curve[:2]
    theta_former = math.atan2(last_point[1]-point[1], point[0]-last_point[0])
    dx, dy=  radius * math.sin(theta_former), radius * math.cos(theta_former)
    vertex_1 = (last_point[0] - dx, last_point[1] - dy)
    vertex_2 = (last_point[0] + dx, last_point[1] + dy)    
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex2fv(vertex_1)
    GL.glTexCoord2f(0.0, 0.0)    
    GL.glVertex2fv(vertex_2)
    cur_length = 0.0
    for next_point in curve[2:] :
        theta_later = math.atan2(point[1]-next_point[1], next_point[0]-point[0])
        beta = 0.5 * (theta_former + theta_later)
        dx, dy=  radius * math.sin(beta), radius * math.cos(beta)
        vertex_1 = (point[0] - dx, point[1] - dy)
        vertex_2 = (point[0] + dx, point[1] + dy)        
        #dx = last_point[0] - point[0]
        #dy = last_point[1] - point[1]
        #cur_length += math.sqrt(dx*dx+dy*dy)
        GL.glTexCoord2f(0.0, 1.0)
        GL.glVertex2fv(vertex_1)
        GL.glTexCoord2f(0.0, 0.0)         
        GL.glVertex2fv(vertex_2)        
        last_point, point = point, next_point
        theta_former = theta_later
    dx, dy=  radius * math.sin(theta_later), radius * math.cos(theta_later)
    vertex_1 = (next_point[0] - dx, next_point[1] - dy)
    vertex_2 = (next_point[0] + dx, next_point[1] + dy)
    GL.glTexCoord2f(0.0, 1.0)
    GL.glVertex2fv(vertex_1)
    GL.glTexCoord2f(0.0, 0.0)    
    GL.glVertex2fv(vertex_2)
    GL.glEnd()     
def generate_texture():
    #im = Image.open("res/strokes/stroke_matrix.png")
    im = Image.open("res/strokes/paint_stroke_revised_2_template.png")
    #im = im.point(lambda i: 255-i)
    ix, iy = im.size
    try:
        image = im.tostring("raw", "RGBA", 0, -1)
    except SystemError:
        image = im.tostring("raw", "RGBX", 0, -1)    
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL.GL_RGBA, 
                   GL.GL_UNSIGNED_BYTE, image)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
    GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_BLEND)
    #GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_DECAL)
    GL.glEnable(GL.GL_TEXTURE_2D)
    
def draw_line_strip(points, color, size = 1):
    GL.glLineWidth(size)
    GL.glBegin(GL.GL_LINE_STRIP)
    GL.glColor3fv(color)
    for point in points:
        GL.glVertex2fv(point)
    GL.glEnd() 
    
def draw_points(points, color, size = 1):
    GL.glPointSize(size)
    GL.glBegin(GL.GL_POINTS)
    GL.glColor3fv(color)
    for point in points:
        GL.glVertex2fv(point)
    GL.glEnd() 
    
def get_bspline(control_points, iteration):
    curve = control_points    
    for i in range(iteration):
        curve = get_bspline_appr(curve)
    return curve        

def get_bspline_appr(control_points):
    curve = []
    length = len(control_points)
    if length <= 2:
        return control_points[:]
    last_point = control_points[0]
    point =  control_points[1]
    curve.append(last_point)
    for next_point in control_points[2:]:
        mid_point = ((last_point[0] + point[0]) / 2.0, (last_point[1] + point[1]) / 2.0)
        curve.append(mid_point)
        fix_point = (
            (last_point[0] + 6 * point[0] + next_point[0]) / 8.0, (last_point[1] + 6 * point[1] + next_point[1]) / 8.0
        )
        curve.append(fix_point)
        last_point = point
        point = next_point
    mid_point = ((last_point[0] + point[0]) / 2, (last_point[1] + point[1]) / 2)    
    curve.append(mid_point)
    curve.append(point)
    return curve
    
def main():    
    os.chdir("..")
    #print os.listdir(os.curdir)
    #return 
    init()
    glutMainLoop()
    
if __name__ == '__main__':
    main()