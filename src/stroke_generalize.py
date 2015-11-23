from PIL import Image
import random
import math
        
def get_stroke(color, radius, length, thickness =7):
    def draw_head():
        r, g, b, a = color
        head =  Image.new("RGBA", (width, head_length), (255, 255, 255, 0))
        data = list(head.getdata())
        w, h = head.size
        start, end = head_edge
        line = [0] * (end-start)
        copy_hair_bunch_list = hair_bunch_list[start:end]
        for i in range(end-start):
             line[i-1] = (copy_hair_bunch_list[i-2]+2*copy_hair_bunch_list[i-1]+copy_hair_bunch_list[i])*0.25
        i = start
        for hair_bunch in line:
            dist = i - width * 0.5
            try:
                length = max(0, min(h,math.sqrt(radius*radius-dist*dist) * 0.5 + hair_bunch))
            except ValueError:
                print radius, dist, i
                exit()
            integer = int(length)
            decimal = length - integer
            delta = deltas[i]
            data[i*h:i*h+integer+1] = [(r + delta, g + delta, b + delta, a)] * (integer) + [(r + delta, g + delta, b + delta, int(255*decimal))]
            i += 1
        data = data[:w*h]
        head = head.transpose(Image.ROTATE_90)
        head.putdata(data)
        head = head.transpose(Image.ROTATE_90)
        data = list(head.getdata())
        data2 = []
        for j in range(h):
            line = data[j*w: j*w + w]
            new_line = [(255, 255, 255, 0)] * w
            for i in range(-2, w-2):
                try:
                    a = line[i-2][3] + line[i-1][3] * 3 + line[i][3] * 6 + line[i+1][3] * 3 + line[i+2][3]
                except IndexError:
                    print i, len(line), line[i-1]
                    exit()
                if a != 0:
                    a = a/14
                    delta = deltas[i]
                    new_line[i] = (r + delta, g + delta, b + delta, a)
            data2.extend(new_line)
        head.putdata(data2)
        im.paste(head, (0, 0))
        return 
    
    def draw_tail():
        r, g, b, a = color
        tail =  Image.new("RGBA", (width, tail_length), (255, 255, 255, 0))
        data = list(tail.getdata())
        w, h = tail.size
        start, end = tail_edge
        line = [0] * (end-start)
        i = start
        copy_hair_bunch_list = hair_bunch_list[start:end]        
        for hair_bunch in copy_hair_bunch_list:
            #length = max(0, min(h,math.sqrt(radius*radius-dist*dist) * 0.5 + hair_bunch))
            length = max(0, min(h, radius * 0.5 + hair_bunch))
            integer = int(length)
            decimal = length - integer
            delta = deltas[i]
            data[i*h: i*h+integer+1] =  [(0, 0, 0, 255)]+ [(r + delta, g + delta, b + delta, a)] * (integer - 1) + [(r + delta, g + delta, b + delta, int(255*decimal))]
            i += 1
        data = data[:w*h]
        tail = tail.transpose(Image.ROTATE_90)
        tail.putdata(data)
        tail = tail.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
        data = list(tail.getdata())
        data2 = []
        for j in range(h):
            line = data[j*w: j*w + w]
            new_line = [(255, 255, 255, 0)] * w
            for i in range(-2, w-2):
                try:
                    a = line[i-2][3] + line[i-1][3] * 3 + line[i][3] * 6 + line[i+1][3] * 3 + line[i+2][3]
                except IndexError:
                    print i, len(line), line[i-1]
                    exit()
                if a != 0:
                    a = a/14
                    delta = deltas[i]
                    new_line[i] = (r + delta, g + delta, b + delta, a)
            data2.extend(new_line)
        tail.putdata(data2)        
        im.paste(tail, (0, height-tail_length))        
        return
    
    def draw_wing():
        wing =  Image.new("RGBA", (wing_width, height - head_length - tail_length), (255, 255, 255, 0))
        w, h = wing.size        
        left_wing = list(wing.getdata())
        for i in range(h):
            left_wing[i*w+wing_width/2:i*w+w] = [color] * (w - wing_width / 2)
        wing.putdata(left_wing)
        im.paste(wing, (0, head_length))
        im.paste(wing.rotate(180), (width-wing_width, head_length))
        return head_edge, tail_edge    

    def draw_body():
        #color = (127, 127, 127, 255)  
        body =  Image.new("RGBA", (width-wing_width*2, height - head_length - tail_length), color)
        data = list(body.getdata())
        w, h = body.size
        r, g, b, a = color
        line = []
        data2 = []
        #band = 16
        #data2.extend(line*50)
        #deltas = [int(round(i)) for i in hair_bunch_list[wing_width/2:wing_width/2+w]]
        #for i in range(w):
            #delta = int(round(random.normalvariate(0, band/2)))
            #deltas[i] = delta
        #for i in range(w):
            #delta = deltas[i]
            #line[i] = (r+delta, g+delta, b+delta, a)
        #data2.extend(line*50)
        #for i in range(-1, w-1):
            #delta = int( 0.6 * deltas[i] + 0.2 * deltas[i-1] + 0.2 * deltas[i+1])
            #line[i] = (r+delta, g+delta, b+delta, a)            
        #data2.extend(line*50)
        for delta in deltas[wing_width:wing_width+w]:
            #delta = int(round( 0.6 * deltas[i+1] - 0.6 * deltas[i-1]+ 0.2 * deltas[i+2] - 0.2 * deltas[i-2]))
            line.append((r+delta, g+delta, b+delta, a))
        #data2.extend(line*(50))
        
        #data2.extend([color]*w*(h-200))
        data2.extend(line*h)
        #for i in range(h):
            #for j in range(w):
                #pos = i * w + j
                #data[pos] = line[j]
        body.putdata(data2)
        im.paste(body, (wing_width, head_length))
        
        return
    
    def settle_parameters(thickness):
        #settle parameters including: 
        # head_edge, tail_edge, head_length, tail_length, wing_width 
        # according to the given parameters including: 
        # thickness, width,
        # and more importantly, the hair-bunches
        
        wing_width = radius / 4
        head_length = radius
        tail_length = radius
        head_edge = (wing_width / 2, width - wing_width / 2)
        tail_edge = (wing_width / 2, width - wing_width / 2)
        sigma = radius * 0.25 * thickness / 8
        hair_bunch_list.extend([random.normalvariate(0, sigma) for i in range(width)])
        hblist_length = width
        deltas.extend([0]*hblist_length)
        for i in range(-2, hblist_length-2):
                    deltas[i] = int(round( 0.6 * hair_bunch_list[i+1] - 0.6 * hair_bunch_list[i-1]
                                           + 0.2 * hair_bunch_list[i+2] - 0.2 * hair_bunch_list[i-2]))     
        return wing_width, head_length, head_edge, tail_length, tail_edge
    
    if len(color) == 3:
        r, g, b = color
        a = 255
        color = r, g, b, a
    elif len(color) == 4:
        r, g, b, a = color
    else:
        #wrong format of the color
        return null    
    if length <radius * 2:
        #wrong size
        return null
    im = Image.new("RGBA", (radius * 2, length), color)
    data = im.getdata()
    width = radius * 2
    height = length
    head_edge = (0, width - 1)
    tail_edge = (0, width - 1)
    wing_width = 0
    head_length = 0
    tail_length = 0
    hair_bunch_list = []
    deltas = []
    wing_width, head_length, head_edge, tail_length, tail_edge = settle_parameters(thickness)

    draw_body()
    head_edge, tail_edge = draw_wing()
    draw_head()
    draw_tail()
    
    return im

def main():
    color = (0, 192, 128)
    radius, length = 31, 200
    thickness = 7
    im = get_stroke(color, radius, length, thickness)
    im.save("result.png")
    im.show()

if __name__ == "__main__":
    main()