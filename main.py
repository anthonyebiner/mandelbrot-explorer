from tkinter import Tk, Canvas
import tkinter.simpledialog
import numpy as np
import math
from numba import jit
from PIL import Image, ImageTk

xmin, xmax, ymin, ymax = -0.7459, -0.746, -0.105, -0.1051
xcord1, ycord1, xcord2, ycord2 = 0, 0, 0, 0
root = Tk()
w = Canvas(root, width=1000, height=1000)

@jit
def hsv_to_rgb(h, s, v):
    if s == 0.0: v *= 255; return (v, v, v)
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
    v *= 255
    i %= 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


@jit
def color(num, maxiters = 200):
    sep = 300

    scale = (math.cos(2*(sep-num)/(sep*2)*math.pi)+1)/2

    if num < sep:
        return hsv_to_rgb(scale, 1.0, scale)
    else:
        return hsv_to_rgb(scale, 1.0, 1.0)


@jit(nopython=True)
def mandelbrot(c, maxiters):
    z = c
    for n in range(maxiters):
        x2 = z.real * z.real
        y2 = z.imag * z.imag
        if x2 + y2 > 4:
            return n
        z = z * z + c
    return 0


@jit
def mandelbrot_set(xmins, xmaxs, ymins, ymaxs, width, height, maxiters):
    xs = np.linspace(xmins, xmaxs, width)
    ys = np.linspace(ymins, ymaxs, height)
    pixels = np.zeros((width, height, 3), dtype=np.uint8)
    for i in range(width):
        for j in range(height):
            n = mandelbrot(complex(xs[i], ys[j]), maxiters)
            pixels[j, i] = color(n)
    return pixels


def mandelbrot_save(xmins, xmaxs, ymins, ymaxs, width, height, maxiters):
    global xmin, xmax, ymin, ymax
    xmin, xmax, ymin, ymax = xmins, xmaxs, ymins, ymaxs
    pixs = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, maxiters)
    file = Image.fromarray(pixs)
    file.save('image.png')


def scale_maxiters(x1, x2):
    return -45.96*math.log(x1-x2) + 175


def getclick2(eventorigin):
    global x0, y0, xcord2, ycord2
    global img

    x0 = eventorigin.x
    y0 = eventorigin.y

    xcord2 = x0/800 * (xmax-xmin) + xmin
    ycord2 = y0/800 * (ymax-ymin) + ymin

    if xcord1 < xcord2 and ycord1 < ycord2:
        print(xcord2-xcord1)
        print(scale_maxiters(xcord2, xcord1))
        mandelbrot_save(xcord1, xcord2, ycord1, ycord2, 800, 800, scale_maxiters(xcord2, xcord1))
    elif xcord1 < xcord2 and ycord1 > ycord2:
        print(xcord2 - xcord1)
        print(scale_maxiters(xcord2, xcord1))
        mandelbrot_save(xcord1, xcord2, ycord2, ycord1, 800, 800, scale_maxiters(xcord2, xcord1))
    elif xcord1 > xcord2 and ycord1 < ycord2:
        print(xcord2 - xcord1)
        print(scale_maxiters(xcord1, xcord2))
        mandelbrot_save(xcord2, xcord1, ycord1, ycord2, 800, 800, scale_maxiters(xcord1, xcord2))
    elif xcord1 > xcord2 and ycord1 > ycord2:
        print(xcord1 - xcord2)
        print(scale_maxiters(xcord1, xcord2))
        mandelbrot_save(xcord2, xcord1, ycord2, ycord1, 800, 800, scale_maxiters(xcord1, xcord2))

    file = "image.png"
    original = Image.open(file)
    img = ImageTk.PhotoImage(original)

    w.create_image(0, 0, image=img, anchor="nw")

    w.bind("<Button 1>", getclick1)


def getclick1(eventorigin):
    global x0, y0, xcord1, ycord1
    x0 = eventorigin.x
    y0 = eventorigin.y

    xcord1 = x0/800 * (xmax-xmin) + xmin
    ycord1 = y0/800 * (ymax-ymin) + ymin

    print(xcord1, ycord1)

    w.bind("<Button 1>", getclick2)


def init_tk():
    # setting up a tkinter canvas
    w.pack()

    # adding the image
    file = "image.png"
    original = Image.open(file)
    img = ImageTk.PhotoImage(original)
    w.create_image(0, 0, image=img, anchor="nw")

    w.bind("<Button 1>", getclick1)

    root.mainloop()


def main():
    mandelbrot_save(-2.0, 0.5, -1.25, 1.25, 800, 800, 300)
    init_tk()


if __name__ == '__main__':
    main()
