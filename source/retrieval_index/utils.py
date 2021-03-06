#-*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, sys
import pandas as pd
import numpy as np
from io import BytesIO
import PIL.Image
import IPython.display
import shutil
from math import sqrt

import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt


def build_rainbow(n, curve=None):
    rgb = []
    width = 2 * np.pi
    for i in range(3):
        offset = -i * width / 3
        cur = np.cos(np.linspace(offset, offset + width, n))
        rgb.append(cur)
    rainbow = (1 + np.vstack(rgb)) / 2
    if curve:
        rainbow = curve(rainbow)
    rainbow = np.minimum(rainbow * 256, 255).astype(int)
    return rainbow.T

def map_range(x, in_min, in_max, out_min, out_max):
    return out_min + (out_max - out_min) * (x - in_min) / (in_max - in_min)

def plot_origin_images(xy, label, num_classes, file_name=""):
    for idx in range(num_classes):
        part_res = xy[label==idx]
        plt.scatter(part_res[:, 0], part_res[:, 1])
    plt.grid(True)
    plt.savefig(file_name)

def plot_images(images, xy, blend=np.maximum, canvas_shape=(1024, 1024), fill=0):
    h, w = images.shape[1:3]
    if images.ndim == 4:
        canvas_shape = (canvas_shape[0], canvas_shape[1], images.shape[3])
    
    min_xy = np.amin(xy, 0)
    max_xy = np.amax(xy, 0)
    
    min_canvas = np.array((0, 0))
    max_canvas = np.array((canvas_shape[0] - h, canvas_shape[1] - w))
    
    canvas = np.full(canvas_shape, fill)
    for image, pos in zip(images, xy):
        x_off, y_off = map_range(pos, min_xy, max_xy, min_canvas, max_canvas).astype(int)
        sub_canvas = canvas[y_off:y_off+h, x_off:x_off+w]
        sub_image = image[:h, :w]
        canvas[y_off:y_off+h, x_off:x_off+w] = blend(sub_canvas, sub_image)

    return canvas

def show_array(a, fmt='png', filename=None, retina=False, zoom=None):
    if len(a.shape) == 1:
        n = len(a)
        side = int(sqrt(n))
        if (side * side) == n:
            a = a.reshape(side, side)
        else:
            raise ValueError('input is one-dimensional', a.shape)
    a = np.uint8(np.clip(a, 0, 255))
    image_data = BytesIO()
    PIL.Image.fromarray(a).save(image_data, fmt)
    if filename is None:
        height, width = a.shape[:2]
        if zoom is not None:
            width *= zoom
            height *= zoom
        # disp_image = PIL.Image.fromarray(a)
        # disp_image.show()
        IPython.display.display(IPython.display.Image(data=image_data.getvalue(),
                                                      width=width,
                                                      height=height,
                                                      retina=retina))
    else:
        with open(filename, 'wb') as f:
            image_data.seek(0)
            shutil.copyfileobj(image_data, f)


def show_loss_function(margin_value=10):
    pn_distance = range(-20, 21)
    y = list()
    for t_val in pn_distance:
        print(t_val)
        if t_val > margin_value:
            # t_y = np.log(margin_value + np.exp(t_val))
            t_y = np.square(t_val)
            # t_y = max(t_y, margin_value + t_val)
        elif t_val > -1.0 * margin_value:
            t_y = 5 * (margin_value + t_val)
        else:
            t_y = 0.0
        y.append(t_y)
    plt.plot(pn_distance, y)
    plt.show()
