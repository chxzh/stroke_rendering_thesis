import cv2, cv, copy, pickle, parameters
from PIL import Image, ImageDraw
from numpy import *

def get_gaussian_reference(src_img, radius):
    ksize = int(radius) * 2 + 1
    return cv2.GaussianBlur(src_img, (ksize, ksize), float(radius))

def get_salient_reference(src):
    hsv_img = cv2.cvtColor(src, cv.CV_BGR2HSV)
    height, width, band = hsv_img.shape
    hue_field, saturation_field, value_field = \
        float64(hsv_img.dot(array([1, 0, 0]))), hsv_img.dot(array([0, 1, 0])), hsv_img.dot(array([0, 0, 1]))
    hue_field = hue_field * pi / 90
    saturation_field = saturation_field * value_field / 256
    x_field, y_field = saturation_field * cos(hue_field), saturation_field * sin(hue_field)
    color_vector_field = x_field.reshape(x_field.size, 1) * array([1, 0]) + y_field.reshape(y_field.size, 1) * array([0, 1])
    color_vector_field = color_vector_field.reshape(height, width, 2)
    radius_list = [1, 2, 4, 8]
    feature_matrix_list = []
    value_field = uint8(value_field)
    empty = zeros((height, width))
    #for radius in radius_list:
        #blured_field = int16(get_gaussian_reference(value_field, radius))
        ## computing dG(x,y,r)/dx
        #feature_matrix_x = empty.copy()
        #feature_matrix_x[:, 1:width-1] += (blured_field[:, 2:width] - blured_field[:, 0:width-2])
        #feature_matrix_list.append(feature_matrix_x)
        ## computing dG(x,y,r)/dy
        #feature_matrix_y = empty.copy()
        #feature_matrix_y[1:height-1, :] += (blured_field[2:height, :] - blured_field[0:height-2, :])
        #feature_matrix_list.append(feature_matrix_y) 
        ## computing d^2(G(x,y,r))/d(x^2)
        #feature_matrix_x2 = empty.copy()
        #feature_matrix_x2[:, 1:width-1] += (feature_matrix_x[:, 2:width] - feature_matrix_x[:, 0:width-2])
        #feature_matrix_list.append(feature_matrix_x2)
        ## computing d^2(G(x,y,r))/d(y^2)
        #feature_matrix_y2 = empty.copy()
        #feature_matrix_y2[1:height-1, :] += (feature_matrix_y[2:height, :] - feature_matrix_y[0:height-2, :])
        #feature_matrix_list.append(feature_matrix_y2)
        ## computing d^2(G(x,y,r))/d(x*y)        
        #feature_matrix_xy = empty.copy()
        #feature_matrix_xy[1:height-1, :] += (feature_matrix_x[2:height, :] - feature_matrix_x[0:height-2, :])
        #feature_matrix_list.append(feature_matrix_xy)
    for radius in radius_list:
        blured_field = get_gaussian_reference(color_vector_field, radius)
        # computing dG(x,y,r)/dx
        feature_matrix_x = empty.copy()
        tmp = (blured_field[:, 2:width] - blured_field[:, 0:width-2])
        tmp = (tmp * tmp).dot(ones(2))
        feature_matrix_x[:, 1:width-1] += sqrt(tmp)
        feature_matrix_list.append(feature_matrix_x)
        # computing dG(x,y,r)/dy
        feature_matrix_y = empty.copy()
        tmp = blured_field[2:height, :] - blured_field[0:height-2, :]
        tmp = (tmp * tmp).dot(ones(2))
        feature_matrix_y[1:height-1, :] += sqrt(tmp)
        feature_matrix_list.append(feature_matrix_y) 
        # computing d^2(G(x,y,r))/d(x^2)
        feature_matrix_x2 = empty.copy()
        tmp = feature_matrix_x[:, 2:width] - feature_matrix_x[:, 0:width-2]
        feature_matrix_x2[:, 1:width-1] += tmp
        feature_matrix_list.append(feature_matrix_x2)
        # computing d^2(G(x,y,r))/d(y^2)
        feature_matrix_y2 = empty.copy()
        tmp = feature_matrix_y[2:height, :] - feature_matrix_y[0:height-2, :]
        feature_matrix_y2[1:height-1, :] += tmp
        feature_matrix_list.append(feature_matrix_y2)
        # computing d^2(G(x,y,r))/d(x*y)        
        feature_matrix_xy = empty.copy()
        tmp = feature_matrix_x[2:height, :] - feature_matrix_x[0:height-2, :]
        feature_matrix_xy[1:height-1, :] += tmp
        feature_matrix_list.append(feature_matrix_xy)
        
    feature_len = len(feature_matrix_list)
    feature_field = array(feature_matrix_list).reshape(feature_len, width*height)
    #for i in range(feature_len):
        #feature_matrix_list[i] = feature_matrix_list[i].flatten()
    #feature_matrix_list = array(feature_matrix_list)
    SIGMA = cov(feature_field)
    SIGMA_INV = linalg.inv(SIGMA)
    # computing (x-mu)'SIGMA^(-1)(x-mu)
    mu = array([mean(feature_factor) for feature_factor in feature_field])
    delta_field = feature_field.transpose() - mu
    delta_field = delta_field.reshape(height, width, feature_len)
    tmp = delta_field.dot(SIGMA_INV)
    #tmp = array([delta.dot(SIGMA_INV) for delta in delta_list])
    salience = (tmp * delta_field).dot(ones(feature_len))
    salience = sqrt(salience)
    mu, sigma = salience.mean(), salience.std()
    
    salience = (salience - mu) / (sigma * parameters.salience_threshold)
    salience = uint8(bool8(int8(salience)))
    #salience = salience.reshape(height, width)
    
    #salience = zeros((height, width))
    #grid_size = feature_len * 2.  # + .0
    #grid_x_num = int(ceil(width/grid_size))
    #grid_y_num = int(ceil(height/grid_size))
    #feature_field = feature_matrix_list.transpose().reshape(height, width, feature_len)
    #for i in range(1, grid_y_num-1):
        #for j in range(1, grid_x_num-1):
            #outer_left, outer_right, outer_top, outer_bottom = \
                #(j - 1) * grid_size, min(width, (j + 2) * grid_size), \
                #(i - 1) * grid_size, min(height, (i + 2) * grid_size)
            #inner_left, inner_right, inner_top, inner_bottom = \
                #j * grid_size, (j + 1) * grid_size, \
                #i * grid_size, (i + 1) * grid_size
            #feature_subfield = feature_field[outer_top:outer_bottom, outer_left:outer_right]
            #feature_subfield = feature_subfield.reshape((outer_bottom-outer_top)*(outer_right-outer_left), feature_len).transpose()
            #SIGMA = cov(feature_subfield)
            #SIGMA_INV = linalg.inv(SIGMA)
            #mu = array([mean(feature_subfield_factor) for feature_subfield_factor in feature_subfield])
            #inner_feature_subfield = feature_field[inner_top:inner_bottom, inner_left:inner_right]
            #delta_field = inner_feature_subfield-mu
            #tmp = delta_field.dot(SIGMA_INV)
            #salience[inner_top:inner_bottom, inner_left:inner_right] = (tmp * delta_field).dot(ones(feature_len))
    return salience

def get_gradient_field(img):
    #img = zeros(img.size, "int").reshape(img.shape) + img
    h, w = img.shape
    gradient_field = zeros(img.size*2).reshape(h, w, 2)
    corners_field = zeros((h-2)*(w-2), "int").reshape(h-2, w-2)
    #print corners_field.dtype
    #corners_field.dtype = "int"

    corners_field =  corners_field + \
        img[2:h, 2:w] - img[0:h-2, 0:w-2] 
    x_field = \
        corners_field + img[1:h-1, 2:w] - img[1:h-1, 0:w-2]\
        + img[0:h-2, 2:w] - img[2:h, 0:w-2]
    y_field = \
        corners_field+ img[2:h, 1:w-1] - img[0:h-2, 1:w-1] \
        + img[2:h, 0:w-2] - img[0:h-2, 2:w]
    for i in xrange(h-2):
        for j in xrange(w-2):
            gradient_field[i+1, j+1] = array([x_field[i, j], y_field[i, j]])
    return gradient_field 
      
    
def show_image(img, name = "window"):
    cv2.namedWindow(name)   
    cv2.imshow(name, img)   
    cv2.waitKey(0)  
    cv2.destroyWindow(name)
    
def draw_gradient(gradient_field, source_image_path):
    im = Image.open(source_image_path)
    h, w, band = gradient_field.shape    
    draw = ImageDraw.Draw(im)    
    for i in xrange(1, h/10+1):
        for j in xrange(1, w/10+1):
            y, x = i * 10, j * 10
            grad =  gradient_field[i*10, j*10]
            dist = sqrt(sum(grad*grad))
            if dist != 0.0:
                grad = grad / dist * 5
            draw.line((x+grad[0], y-grad[1],\
                       x-grad[0], y+grad[1]), \
                      fill=(0, 0, 255), width=1)
    im.show()    
    
def draw_gradient_direction(gradient_field):
    h, w, band = gradient_field.shape
    dm = zeros(h*w*3, "uint8").reshape((h, w, 3))
    dm.fill(255)
    for i in xrange(h):
        for j in xrange(w):
            grd = gradient_field[i, j]
            dist = sqrt(sum(grd*grd)) 
            if dist == 0.0:
                dm[i, j, 0] = 0
                dm[i, j, 2] = 0
            else:
                x, y = grd
                y = -y
                theta = arctan2(y, x) * 180 / pi
                if theta < 0.0:
                    theta += 180
                dm[i, j, 0] = theta
                dm[i, j, 2] = uint8(min(255, dist))
    show_image(cv2.cvtColor(dm, cv.CV_HSV2BGR), name="window")    
    return 
    

def main():
    source_image_path = "../data/input_photos/hertzmannexample.jpg"
    #source_image_path = "e:/circle.jpg"
    source_image = cv2.imread(source_image_path)
    get_salient_reference(source_image)
    #gray_image = cv2.cvtColor(source_image, cv.CV_BGR2GRAY)
    #blur_image_10 = get_gaussian_reference(gray_image, 10)
    #draw_gradient_direction(gradient_field)
    #draw_gradient(gradient_field, source_image_path)
    #show_image(gray_image)
    #show = cv2.Sobel(gray_image, cv.CV_16S, 0, 1, ksize=3)
    #show_image(int8(show))
    #show_image(blur_image_20)
    print "end of main"
    return

if __name__ == "__main__":
    main()
    