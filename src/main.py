import reference_image, pickle, paint, cv2, cv, stroke
from OpenGL import GL
from OpenGL.GLU import *
from OpenGL.GLUT import *
stroke_list = []
def get_painting(image_path, display_in_window = True):
    '''
    1. open source image
    2. generate different reference images
    3. generate strokes of different layers according to reference images
    4. render strokes based on layers and other stroke parameters
    '''
    
    def init_opengl(width, height):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA|GLUT_SINGLE)
        glutInitWindowSize(width, height)
        glutCreateWindow("SBR")
        #the place function "paint_the_paint()" was referred
        glutDisplayFunc(paint_the_painting)
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        gluOrtho2D(0.0, float(width), float(height), 0.0)
        #anti-aliasing codes
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)  
        
        
        #GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)  
        GL.glEnable(GL.GL_BLEND)
        GL.glHint(GL.GL_POINT_SMOOTH_HINT, GL.GL_NICEST)
        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        #GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)
        #GL.glEnable(GL.GL_POLYGON_SMOOTH)
    
    def single_stroke_test(texture = False):
        paint.pave_the_canvas(width, height)
        strk = stroke.stroke(30, (30, 30), (0, 255, 0))
        strk.add_control_point((100, 100))
        strk.add_control_point((200, 100))
        stroke_list.append(strk)
    
    def paint_the_painting():
        for strk in stroke_list:      
            strk.draw(True)
            #strk.draw()

        GL.glFlush()
        #ref_img = reference_image.get_gaussian_reference(src_img, 5)
        #stroke_list = paint.paint(ref_img, paint.get_current_canvas(width, height), radius=5)
        #stroke_list = paint.sort_stroke(stroke_list)
        #for strk in stroke_list:      
            ##strk.draw(True)
            #strk.draw()

        #GL.glFlush()                        
        return 
    
    def get_stroke_list(R, use_salience=False):
        paint.pave_the_canvas(width, height)
        canvas = paint.get_current_canvas(width, height)
        if use_salience:
            salience = reference_image.get_salient_reference(src_img)
            ref = src_img
        else:
            salience = None
            ref = reference_image.get_gaussian_reference(src_img, R)
            
        stroke_list_tmp = paint.paint(ref, canvas, radius=R, painting_area=salience)
        #stroke_list_tmp = paint.sort_stroke(stroke_list_tmp)
        stroke_list.extend(stroke_list_tmp)
        glutPostRedisplay()
        #stroke_list = paint.sort_stroke(stroke_list)
        #for strk in stroke_list:      
            ##strk.draw(True)
            #strk.draw()

        #GL.glFlush()
        ##return 
        #ref_img = reference_image.get_gaussian_reference(src_img, 10)
        #stroke_list = paint.paint(ref_img, paint.get_current_canvas(width, height), radius=10)
        #stroke_list = paint.sort_stroke(stroke_list)

        
    src_img = cv2.imread(image_path)
    src_img = cv2.cvtColor(src_img, cv.CV_BGR2RGB)
    height, width, band = src_img.shape
    init_opengl(width, height)
    #single_stroke_test()
    #get_stroke_list(40)
    get_stroke_list(32)
    get_stroke_list(16)
    get_stroke_list(8)
    get_stroke_list(4, use_salience=True)
    get_stroke_list(2, use_salience=True)
    if display_in_window:
        glutMainLoop()        
    
    return 
    
def main():
    image_path = "../data/input_photos/fishergirl.jpg"
    #image_path = "../data/input_photos/ladygaga.jpg"
    #image_path = "../data/input_photos/ladygaga_small_g20.png"
    get_painting(image_path)
    #src_img = cv2.imread(image_path)
    #gsn_img = reference_image.get_gaussian_reference(src_img, 20)
    #cv2.imwrite('../data/input_photos/ladygaga_small_g20.png', gsn_img)
    #test_list = range(9)
    
    return
if __name__ == "__main__":
    main()
    