########################################################################
from OpenGL import GL
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import math, stroke_generalize, parameters

class stroke:
    """
    this is the formal class of stroke, containing all its attributes and methods
    """
    
    #__radius = 0
    #__control_points = []
    #__thickness = 7
    #__color = (255, 255, 255)
    #----------------------------------------------------------------------
    def __init__(self, radius, start_point, color, thickness = -1):
        """Constructor"""
        self.__radius = radius
        self.__control_points = []
        self.add_control_point(start_point)
        self.__thickness = thickness
        # using reverse color is an expedient solution to the unfunctional glBlendFunc()
        R, G, B = color
        self.__true_color = color
        self.__luminosity = R * 0.299 + G * 0.587 + B * 0.114
        self.__color = 255 - R, 255 - G, 255 - B
        self.__draw_once = False
        self.__texture_img = None
        self.__curve = []
        self.__length = -1
        self.__thickness = thickness
        if not 0 <= self.__thickness <= 8:
            self.__thickness = int(round(4*(1/self.__radius + self.__luminosity/255)))
    def get_luminosity(self):
        return self.__luminosity
    def get_thickness(self):
        return self.__thickness
    def add_control_point(self, point):
        '''
        parameter 'point' should be in the pattern of (x,y)
        '''
        self.__control_points.append(point)
    
    def print_info(self):
        print "radius: ", self.__radius
        print "color: ", self.__color
        print "thickness: ", self.__thickness
        print "control points: ", 
        for point in self.__control_points:
            print point, 
        print
        
    def __get_bspline(self, control_points, iteration = 3):
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
        
        curve = control_points    
        for i in range(iteration):
            curve = get_bspline_appr(curve)
        return curve 
        
    def get_curve(self, texture=False):
        if self.__draw_once:
            return self.__curve
        else:
            curve = self.__get_bspline(self.__control_points, parameters.b_spline_iteration)
            if texture:
            #modify control points in order to fit texture context
                last_point, point= curve[:2]
                theta_former = math.atan2(last_point[1]-point[1], point[0]-last_point[0])
                dx, dy=  self.__radius * math.cos(theta_former), self.__radius * math.sin(theta_former)
                new_head = (last_point[0] - dx, last_point[1] + dy)
                curve[0] = new_head
                
                last_point, point= curve[-2:]
                theta_former = math.atan2(last_point[1]-point[1], point[0]-last_point[0])
                dx, dy=  self.__radius * math.cos(theta_former), self.__radius * math.sin(theta_former)
                new_tail = (point[0] + dx, point[1] - dy)
                curve[-1] = new_tail
            self.__curve = curve
            return self.__curve
                
    def draw(self, texture = False):
        def draw_hat(point, radius, theta, split = 8):
            vertexes = []    
            dx, dy=  radius * math.sin(theta), radius * math.cos(theta)
            vertex_1 = (point[0] - dx, point[1] - dy)
            vertex_2 = (point[0] + dx, point[1] + dy)
            vertexes.append(vertex_1)
            delta = math.pi / split
            for i in range(1, split):
                deltheta = theta+delta*i
                dx, dy=  radius * math.sin(deltheta), radius * math.cos(deltheta)
                vertex = (point[0] - dx, point[1] - dy)
                vertexes.append(vertex)
            vertexes.append(vertex_2)
            GL.glBegin(GL.GL_POLYGON)
            for vertex in vertexes:
                GL.glVertex2fv(vertex)
            GL.glEnd()
            return
        
        r, g, b = self.__color        
        curve = self.get_curve(texture)
        radius = self.__radius        


        if texture:
            #compute the length
            total_length = 0.0
            last_point = curve[0]
            for point in curve[1:]:
                dx = last_point[0] - point[0]
                dy = last_point[1] - point[1]
                total_length += math.sqrt(dx*dx+dy*dy)
                last_point = point
            #get the stroke texture based on stroke attributes
            
            #im = Image.open("../res/strokes/paint_stroke_revised_2_template.png")
            if self.__draw_once == False:
                im = stroke_generalize.get_stroke((r, g, b), self.__radius, int(total_length))
                im = im.transpose(Image.ROTATE_90)
                self.__texture_img = im
            else:
                im = self.__texture_img
            ix, iy = im.size                
            try:
                image = im.tostring("raw", "RGBA", 0, -1)
            except SystemError:
                image = im.tostring("raw", "RGBX", 0, -1)
            #implement the stroke
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL.GL_RGBA, 
                           GL.GL_UNSIGNED_BYTE, image)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_BLEND)
            GL.glEnable(GL.GL_TEXTURE_2D)
            #r = r / 256.0
            #g = g / 256.0
            #b = b / 256.0
            #GL.glColor3fv((r, g, b))            
            
        else:
            r = r / 256.0
            g = g / 256.0
            b = b / 256.0
            GL.glColor3fv((r, g, b))
        last_point, point= curve[:2]
        theta_former = math.atan2(last_point[1]-point[1], point[0]-last_point[0])
        dx, dy=  radius * math.sin(theta_former), radius * math.cos(theta_former)
        vertex_1 = (last_point[0] - dx, last_point[1] - dy)
        vertex_2 = (last_point[0] + dx, last_point[1] + dy)
        if not texture:
            draw_hat(last_point, radius, theta_former)
        GL.glBegin(GL.GL_QUAD_STRIP)
        if texture:
            GL.glTexCoord2f(0.0, 0.0)
        GL.glVertex2fv(vertex_1)
        if texture: 
            GL.glTexCoord2f(0.0, 1.0)    
            cur_length = 0.0
        GL.glVertex2fv(vertex_2)
        for next_point in curve[2:] :
            theta_later = math.atan2(point[1]-next_point[1], next_point[0]-point[0])
            beta = 0.5 * (theta_former + theta_later)
            dx, dy=  radius * math.sin(beta), radius * math.cos(beta)
            vertex_1 = (point[0] - dx, point[1] - dy)
            vertex_2 = (point[0] + dx, point[1] + dy)        
            dx = last_point[0] - point[0]
            dy = last_point[1] - point[1]
            if texture:
                cur_length += math.sqrt(dx*dx+dy*dy)
                GL.glTexCoord2f(cur_length/total_length, 0.0)
            GL.glVertex2fv(vertex_1)
            if texture: 
                GL.glTexCoord2f(cur_length/total_length, 1.0)         
            GL.glVertex2fv(vertex_2)
            last_point, point = point, next_point
            theta_former = theta_later
        dx, dy=  radius * math.sin(theta_former), radius * math.cos(theta_former)
        vertex_1 = (point[0] - dx, point[1] - dy)
        vertex_2 = (point[0] + dx, point[1] + dy)
        if texture: 
            GL.glTexCoord2f(1.0, 0.0)
        GL.glVertex2fv(vertex_1)
        if texture: 
            GL.glTexCoord2f(1.0, 1.0)    
        GL.glVertex2fv(vertex_2)
        GL.glEnd()
        if not texture:
            draw_hat(point, radius, theta_former+math.pi)
            
        #GL.glColor3fv((1 - r, 1 - g, 1 - b))
        #GL.glBegin(GL.GL_POINTS)
        #for point in self.__control_points:
            #GL.glVertex2fv(point)
        #GL.glEnd()
        self.__draw_once = True
        return 
    
    def get_point_list(self):
        return self.__control_points[:]
def get_stroke(start_point, radius, color, ref_img, canvas):
    new_stroke = stroke(radius, start_point, color)
    
    
    return new_stroke
    