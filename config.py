import pygame as pg
from math import pi, sin, cos
from random import randint

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


win_width = 1000
win_height = 700

poly_borderwidth = 5
pol_borderclarity = 6

background = pg.Color(26, 26, 26)
mirror_color = pg.Color(171, 196, 170)
pointer_color = pg.Color(0, 0, 0)

white = pg.Color(255, 255, 255)
black = pg.Color(0, 0, 0)

laser_width = 3
shader_steps = 6
shader_spread = 1.4
laser_offset = 1.2
laser_max_pow = 30

mirror_width = 5

button_img = (get_asset(('texture', 'nine_slice'), 'gold_button', 'png'), (5,)*4)

widget_button_width = 80
widget_button_padding = 5
widget_button_height = 50


