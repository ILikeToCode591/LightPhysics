import pygame as pg
from math import pi, sin, cos
from random import randint, random

pg.init()


def get_asset(typ, name, ext):
    return f'assets/{"s/".join(typ)}s/{name}.{ext}'


def get_unique_key():
    return ''.join([str(randint(0, 9)) for i in range(7)])


def get_vector_angle(vector: pg.Vector2):
    a = vector.as_polar()[1]
    if a < 0:
        a += 360
    return a

#window clarity

win_width = 1000
win_height = 700

# polygons

poly_borderwidth = 5
pol_borderclarity = 6

# constants

background = pg.Color(26, 26, 26)
mirror_color = pg.Color(171, 196, 170)
pointer_color = pg.Color(0, 0, 0)

white = pg.Color(255, 255, 255)
black = pg.Color(0, 0, 0)
transparent = pg.Color(0, 0, 0, 0)

unit = pg.Vector2(1, 1)

# general

laser_width = 3
shader_steps = 6
shader_spread = 1.4
laser_offset = 1.2
laser_max_pow = 30

mirror_width = 5

# nine_slices

button_img = (get_asset(('texture', 'nine_slice'), 'gold_button', 'png'), (5,)*4)
button_p_img = (get_asset(('texture', 'nine_slice'), 'gold_button_pressed', 'png'), (5,)*4)
text_box_img = (get_asset(('texture', 'nine_slice'), 'text_box', 'png'), (5,)*4)

# build screen

widget_button_width = 80
widget_button_padding = 5
widget_button_height = 50

# saves screen

paddingh, paddingv = 15, 20
button_s = 80
