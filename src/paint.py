import pickle, reference_image, cv2, cv, parameters
from stroke import stroke
from OpenGL import GL
from PIL import Image
from numpy import * 
debug = True
def paint(ref_img, canvas, radius, painting_area = None):
    '''
    given reference image should be in RGB pattern
    '''
    def get_gradient_field(ref_img):
        #if debug:
            #gradient_field = pickle.load(open('../data/cache/gradient_field.pickle', 'rb'))
        #else:
        gray_image = cv2.cvtColor(ref_img, cv.CV_RGB2GRAY)         
        gradient_field = reference_image.get_gradient_field(gray_image)
        return gradient_field
        
    def get_stroke(grid):
        
        grid_i, grid_j = grid
        left, top = grid_j * grid_size,  grid_i * grid_size
        grid_delta = delta[top: top+grid_size, left: left+grid_size]
        if grid_delta.max() >= parameters.delta_threshold:
            #grid_height, grid_width are the size of this grid, for those grids 
            # at the right or bottom edge their size may possibly not be grid_size (it is smaller).
            grid_height, grid_width = grid_delta.shape
            start_point = argmax(grid_delta)
            x, y = left + start_point % grid_width, top + start_point / grid_width
            start_point = (x, y)
            color = tuple(ref_img[y, x])
            new_stroke = stroke(radius, start_point, color)
            # find the second point
            grad_x, grad_y = gradient_field[y, x]
            grad_len = sqrt(grad_x**2 + grad_y**2)
            if grad_len != 0:
                v = vx, vy = grad_y / grad_len, -grad_x / grad_len
            else:
                v = vx, vy = 0, 1
            peak = x + radius * vx / cos(parameters.stroke_search_angle), \
                        y + radius * vy / cos(parameters.stroke_search_angle)
            if peak[0] < 0 or peak[0] >= width or peak[1] < 0 or peak[1] >= height:
                v = vx, vy = -vx, -vy
                peak = x + radius * vx / cos(parameters.stroke_search_angle), \
                            y + radius * vy / cos(parameters.stroke_search_angle)
            theta = arctan2(-vy, vx)
            end_1 = x + radius * cos(theta+parameters.stroke_search_angle), \
                          y - radius * sin(theta+parameters.stroke_search_angle)
            end_2 = x + radius * cos(theta-parameters.stroke_search_angle), \
                          y - radius * sin(theta-parameters.stroke_search_angle)
            search_left = max(0, int(min(peak[0], end_1[0], end_2[0])))
            search_right = min(width, int(ceil(max(peak[0], end_1[0], end_2[0]))))
            search_top = max(0, int(min(peak[1], end_1[1], end_2[1])))
            search_bottom = min(height, int(ceil(max(peak[1], end_1[1], end_2[1]))))
            next_point = (-1, -1)
            max_value = parameters.next_point_max_threhold
            for i in range(search_top, search_bottom):
                for j in range(search_left, search_right):
                    if radius - 1 < sqrt((i - y) ** 2 + (j - x) ** 2) < radius + 1:
                        value =  delta[i, j] - sqrt(sum((ref_img[i, j]-color)**2))
                        if  value > max_value:
                            max_value = value
                            next_point = (j, i)
            if next_point == (-1, -1):
                return None
            
            next_point = x + radius * vx, y + radius * vy
            if next_point[0] < 0 or next_point[0] >= width or next_point[1] < 0 or next_point[1] >= height:
                parameters.reason4end['stop at the second one'] += 1
                return None            
            new_stroke.add_control_point(next_point)
            g_topaint_area[next_point[1]/grid_size, next_point[0]/grid_size] = 0
            last_point, current_point = start_point, next_point
            last_vx, last_vy = vx, vy
            last_theta = arctan2(last_point[1]-current_point[1], current_point[0]-last_point[0])
            clockwise = (last_theta - theta < 0)
            # find the rest
            for k in range(1, parameters.stroke_max_length):
                x, y = current_point
                grad_x, grad_y = gradient_field[y, x]
                grad_len = sqrt(grad_x**2 + grad_y**2)
                if grad_len != 0:
                    v = vx, vy = grad_y / grad_len, -grad_x / grad_len
                else:
                    v = vx, vy = last_vx, last_vy
                if vx * last_vx + vy * last_vy < 0:
                    v = vx, vy = -vx, -vy
                theta = arctan2(-vy, vx)
                if abs(theta-last_theta) > parameters.stroke_search_angle:
                    break
                end_1 = x + radius * cos(last_theta), \
                          y - radius * sin(last_theta)
                if clockwise:
                    direction = -1
                else:
                    direction = 1
                theta_2 = theta + parameters.stroke_search_angle * direction
                end_2 = x + radius * cos(theta_2) , \
                          y - radius * sin(theta_2)
                theta_peak = (last_theta+theta_2) * 0.5
                peak = x + radius * cos(theta_peak) , \
                          y - radius * sin(theta_peak)                
                search_left = max(0, int(min(peak[0], end_1[0], end_2[0])))
                search_right = min(width, int(ceil(max(peak[0], end_1[0], end_2[0]))))
                search_top = max(0, int(min(peak[1], end_1[1], end_2[1])))
                search_bottom = min(height, int(ceil(max(peak[1], end_1[1], end_2[1]))))
                next_point = (-1, -1)
                max_value = parameters.next_point_max_threhold
                for i in range(search_top, search_bottom):
                    for j in range(search_left, search_right):
                        if radius - 1 < sqrt((i - y) ** 2 + (j - x) ** 2) < radius + 1:
                            value =  delta[i, j] - sqrt(sum((ref_img[i, j]-color)**2))
                            if  value > max_value:
                                max_value = value
                                next_point = (j, i)
                if next_point == (-1, -1):
                    break
                next_point = x + radius * vx, y + radius * vy
                if next_point[0] < 0 or next_point[0] >= width or next_point[1] < 0 or next_point[1] >= height:
                    parameters.reason4end['next one out of bound'] += 1
                    break
                if g_topaint_area[next_point[1]/grid_size, next_point[0]/grid_size] == 0:
                    parameters.reason4end['next one drew already'] += 1
                    break
                new_stroke.add_control_point(next_point)
                g_topaint_area[next_point[1]/grid_size, next_point[0]/grid_size] = 0
                last_point, current_point = current_point, next_point
                last_vx, last_vy = vx, vy
                last_theta = arctan2(last_point[1]-current_point[1], current_point[0]-last_point[0])          
            return new_stroke
        else:
            return None
    
    height, width, band = ref_img.shape
    stroke_list = []
    #delta is the difference between current canvas and reference image
    delta = int32(ref_img) - canvas
    delta = delta ** 2
    delta = delta.dot(ones(band))
    delta = sqrt(delta)
    gradient_field = get_gradient_field(ref_img)
    #reference_image.draw_gradient_direction(gradient_field)
    if painting_area != None:
        delta = delta * painting_area
    grid_size = radius
    #g_x_num, g_height stand for the numbers of grid on x and y axis
    g_x_num = int(ceil(float(width) / grid_size))
    g_y_num = int(ceil(float(height) / grid_size))
    
    g_topaint_area = ones((g_y_num, g_x_num), dtype='int8')
    for i in range(g_y_num):
        for j in range(g_x_num):
            left = j * grid_size
            top = i * grid_size
            if (delta[top:top+grid_size, left:left+grid_size].max()) <= parameters.delta_threshold:
                g_topaint_area[i, j] = 0
    for i in range(g_y_num):
        for j in range(g_x_num):
            if g_topaint_area[i, j] == 1:
                new_stroke =  get_stroke((i, j))
                if new_stroke != None:
                    stroke_list.append(new_stroke)
                    #if len(stroke_list) > 2:
                        #return stroke_list
            print "done with ", i * g_x_num + j, '/', g_x_num * g_y_num
    print len(stroke_list)
    print parameters.reason4end
    return stroke_list


def get_current_canvas(width, height):
    data = GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)
    canvas = Image.fromstring('RGB', (width, height), data)
    canvas = canvas.transpose( Image.FLIP_TOP_BOTTOM)
    canvas = array(canvas)
    return canvas

def get_empty_canvas(width, height):
    canvas = zeros(width*height*3)
    #canvas.fill(255)
    return canvas.reshape((height, width, 3))
    
def sort_stroke(stroke_list):
    stroke_list.sort(key = lambda strk: strk.get_luminosity())
    return stroke_list

def pave_the_canvas(width, height):
    GL.glBegin(GL.GL_QUADS)
    #GL.glColor3fv((0.0, 0.0, 0.0))
    GL.glColor3fv((1.0, 1.0, 1.0))
    GL.glVertex2f(0.0, 0.0)
    GL.glVertex2f(0.0, float(height))
    GL.glVertex2f(float(width), float(height))
    GL.glVertex2f(float(width), 0.0)
    GL.glEnd()                    
    return

def main():
    source_image_path = "../data/input_photos/ladygaga_small.jpg"
    ref_img = cv2.imread(source_image_path)
    reference_image.show_image(ref_img)
    height, width, band = ref_img.shape
    stroke_list = paint(ref_img, get_empty_canvas(width, height), 20)
    
    
    print "paint.py: end of main"
    return

if __name__ == '__main__':
    main()