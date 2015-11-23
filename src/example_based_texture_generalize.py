from PIL import Image
basecolor = (218, 218, 227)
def convert(color, avg):
    r, g, b, a = color
    R, G, B = basecolor
    band = 128
    if a != 0:
        gray = get_gray(r, g, b)
        r = R + max(-band, min(band, gray - avg))
        g = G + max(-band, min(band, gray - avg))
        b = B + max(-band, min(band, gray - avg))
    return (r, g, b, a)

def get_intensity(r, g, b):
    M = max(r, g, b)
    intensity = float(M) / 255
    return int(intensity)
    
def get_gray(r, g, b):
    return (r * 299 + g * 587 + b * 114) / 1000

def get_convert_template(src, avg):
    band = 128
    templt = []
    for point in src:
        r, g, b, a = point
        if a != 0:
            gray = get_gray(r, g, b)
            level = max(0, min(band, (gray - avg)/2)+band)
            r = level
            g = level
            b = level
        templt.append((r, g, b, a))
    return templt   
    
def get_template(filename):    
    im = Image.open(filename)
    data = list(im.getdata())
    data2 = []
    for point in data:
        r, g, b, a = point
        if a != 0:
            value = get_gray(r, g, b)
            #value = get_intensity(r, g, b)
            data2.append(value)
    avg = int(sum(data2)/float(len(data2)))
    #stat = [0] * 256
    #for point in data2:
        #stat[point] += 1
    #print avg
    #i = 0
    #for st in stat:
        #print i - avg, ":", st
        #i += 1
    #exit()
    data2 = []
    data2 = get_convert_template(data, avg)
    #for point in data:
        #data2.append(convert(point, avg))
    im.putdata(data2)
    return im

def main():
    filename = "../res/strokes/paint_stroke_revised_2.png"
    im = get_template(filename)
    im.show()
    #im.save("../res/strokes/paint_stroke_revised_2_template.png")
    
if __name__ == "__main__":
    main()