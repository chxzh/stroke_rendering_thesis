from PIL import Image, ImageDraw
import random
#inner class definition
class ridge:
    #represent a pile formed because of pigment uneven distribution
    #member variables include: position, radius, height
    def __init__(self, position, height = 10, radius = 1, delta = 1):
        self.position = position
        self.height = height
        self.radius = radius
        self.delta = delta
    def print_info(self):
        #for debug only
        print "position = " + str(self.position) + "; height = " + str(self.height) + "; radius = " + str(self.width) + ";"
    def get_interfered_region(self):
        #delta = int(32*self.height/float(self.radius))
        #delta = random.randint(0, 16)
        delta = self.delta
        region = [-delta] * self.radius + [delta]* self.radius
        return region
    def delta_descend(self):
        self.delta = max(0, self.delta-1)

#pre define parameters for testing
basecolor = (128, 120, 190)
ridge_list_example = [
    ridge(50, 7, 7), 
    ridge(100, 1, 1), 
    ridge(150, 3)
]
        
def get_random_line(width):
    #generate a line of ramdom even-distributed deltas within given domain, and a tail of 100-pixel of original color for comparison
    #default domain was [-5,5]
    randlist = [random.randint(-5, 5) for i in xrange(width-100)] + [0 for i in xrange(100)]
    return randlist

def get_ridge_list(width, thickness=8):
    #generate a list of ridge within the width according the thickness
    #ridges would not be too closed to each other, and they tend to be similiar
    #the thicker the pigment is, the more possible that it was viscous, 
    # which indicates that the higher ridges could possibly be
    
    #ridge_list = ridge_list_example
    ridge_list = [ridge(i*2+1, height=1, radius=1, delta=random.randint(0, 15)) for i in xrange(width)]
    return ridge_list
def get_redged_line(width):
    ridge_list = get_ridge_list(width)
    line = [0] * width
    all_line = []
    for i in range(32):
        for j in range(len(ridge_list)):
            r = ridge_list[j]
            ridge_list[j].delta_descend()
            line[r.position-r.radius: r.position+r.radius] = r.get_interfered_region()
            
        all_line.extend(line[0:width])
    return all_line
def get_body_texture(size = (512, 512), color = (0, 0, 0, 255)):
    if len(color) == 3:
        R, G, B = color
        A = 255
        color = (R, G, B, A)
    elif len(color) == 4:
         R, G, B, A = color
    im = Image.new('RGBA', size, color)
    data = list(im.getdata())
    width, height= size
    #line = get_random_line(width)
    line = get_redged_line(width)
    data = [(R + delta, G + delta, B + delta, A) for delta in line] * (height / 32)

            
    im.putdata(data)
    return im
def main():
    im = get_body_texture(color=basecolor)
    im.show()
    
if __name__ == "__main__":
    main()