from scipy import misc as misc
from scipy import ndimage as ndimage
from numpy import array as array
infilename = "../res/strokes/paint_stroke_revised.jpg"
outfilename = "../res/strokes/paint_stroke_revised_2.png"
def covRGB2HSV((r,g, b)):
    h, s, v = 0.0, 0.0, 0.0
    M = float(max(r, g, b))
    m = float(min(r, g, b))
    if M == m:
        h = 0.0
    elif r == M:
        if g >= b:
            h = 60 * float(g - b) / (M - m)
        else:
            h =  60 *float(g - b) / (M - m) + 360
    elif g == M:
        h = 60 *float(b - r) / (M - m) + 120
    elif b == M:
        h = 60 *float(r - g) / (M - m) + 240
    if h >= 360:
        print h, s, v, M, m
        print r, g, b
        print float(b - r) 
        exit()
    v = M / 256.0
    if M != 0.0:
        s = (M - m) / M
    else:
        s = 0.0
    return (h, s, v)
def covHSV2RGB((h, s, v)):
    v = int(round(v * 256))
    if s == 0.0:
        r = g = b = v
    else:
        h /= 60
        i = int(h)
        f = h - i
        a = int(round(v * (1 - s)))
        b = int(round(v * (1 - s*f)))
        c = int(round(v * (1 - s*(1-f))))
        if i == 0:r = v; g = c; b = a;
        elif i == 1:r = b; g = v; b = a;
        elif i == 2:r = a; g = v; b = c;
        elif i == 3:r = a; g = b; b = v;
        elif i == 4:r = c; g = a; b = v;
        elif i == 5:r = v; g = a; b = b
        else:print"error i", h, s, v, i
    return (r, g, b)
def main():
    image = misc.imread(infilename).astype(int)
    f = lambda (h, s, v): (h, s / 2.0, v)
    hsvimage = array([[f(covRGB2HSV(tuple(i))) for i in j] for j in image])
    rgbimage = array([[covHSV2RGB(tuple(i)) for i in j] for j in hsvimage])
    
    '''
    res1 = ndimage.gaussian_filter(rgbimage, 3)
    res2 = ndimage.gaussian_filter(res1, 1)
    alpha = 30
    res = res1 + alpha * (res1 - res2)
    '''
    lx, ly, lz= rgbimage.shape
    #res = rgbimage[lx/4:-lx/4, ly/4:-ly/4]
    misc.imsave(outfilename, rgbimage)
if __name__ == "__main__":
    main()