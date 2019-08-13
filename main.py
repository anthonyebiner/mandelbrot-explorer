import os
from tkinter import Tk, Canvas, messagebox
import math
import numpy as np
from PIL import Image, ImageTk
from numba import jit

pics = -1
xmin, xmax, ymin, ymax = [], [], [], []
xcord1, ycord1, xcord2, ycord2 = 0, 0, 0, 0
root = Tk()
w = Canvas(root, width=1000, height=1000)

@jit
def hsv_to_rgb(h, s, v):
    if s == 0.0: v *= 255; return v, v, v
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
    v *= 255
    i %= 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


@jit
def color(num):
    sep = 300

    scale = (math.cos(2*(sep-num)/(sep*2)*math.pi)+1)/2

    if num < sep:
        return hsv_to_rgb(scale/2, 1.0, scale)
    else:
        return hsv_to_rgb(scale/2, 1.0, 1.0)


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
    global xmin, xmax, ymin, ymax, pics
    pics += 1
    xmin.append(xmins)
    xmax.append(xmaxs)
    ymin.append(ymins)
    ymax.append(ymaxs)
    pixs = mandelbrot_set(xmin[pics], xmax[pics], ymin[pics], ymax[pics], width, height, maxiters)
    file = Image.fromarray(pixs)
    file.save('image' + str(pics) + '.png')


def scale_maxiters(x1, x2):
    return -45.96*math.log(x1-x2) + 175


def release(eventorigin):
    global x2, y2, xcord2, ycord2
    global img

    x2 = x0 + min(x1-x0, y1-y0)
    y2 = y0 + min(x1-x0, y1-y0)

    xcord2 = x2/800 * (xmax[pics]-xmin[pics]) + xmin[pics]
    ycord2 = y2/800 * (ymax[pics]-ymin[pics]) + ymin[pics]

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

    file = "image" + str(pics) + ".png"
    original = Image.open(file)
    img = ImageTk.PhotoImage(original)

    w.create_image(0, 0, image=img, anchor="nw")

    w.bind("<ButtonRelease-1>", click)


rect1 = w.create_rectangle(0, 0, 0, 0, outline='white')


def motion(eventorigin):
    global x0, y0, x1, y1, rect1, xcord1, ycord1
    x1 = eventorigin.x
    y1 = eventorigin.y

    w.delete(rect1)

    rect1 = w.create_rectangle(x0, y0, x0 + min(x1-x0, y1-y0), y0 + min(x1-x0, y1-y0), outline='white')
    # rect1 = w.create_rectangle(x0, y0, x1, y1, outline='white')

    w.bind("<ButtonRelease-1>", release)


def click(eventorigin):
    global x0, y0, xcord1, ycord1
    x0 = eventorigin.x
    y0 = eventorigin.y

    xcord1 = x0/800 * (xmax[pics]-xmin[pics]) + xmin[pics]
    ycord1 = y0/800 * (ymax[pics]-ymin[pics]) + ymin[pics]

    print(xcord1, ycord1)

    w.bind("<B1-Motion>", motion)


def back(eventorigin):
    global pics, img
    print(pics)
    pics -= 1
    print(pics)
    file = "image" + str(pics) + ".png"
    original = Image.open(file)
    img = ImageTk.PhotoImage(original)

    xmax.pop()
    xmin.pop()
    ymax.pop()
    ymin.pop()

    w.create_image(0, 0, image=img, anchor="nw")


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        for i in range(pics):
            os.remove('image' + str(i) + '.png')
        root.destroy()


def init_tk():
    # setting up a tkinter canvas
    w.pack()

    # adding the image
    file = "image" + str(pics) + ".png"
    original = Image.open(file)
    img = ImageTk.PhotoImage(original)
    w.create_image(0, 0, image=img, anchor="nw")

    w.bind("<Button-1>", click)
    w.bind("<Button-3>", back)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


def main():
    mandelbrot_save(-2.0, 0.5, -1.25, 1.25, 800, 800, 300)
    init_tk()


if __name__ == '__main__':
    main()
