from numpy import *
# not stroke should have more control points than the number of stroke_max_length
stroke_max_length = 20
# the next control point would be search in the area in  the angle of stroke_search_angle
stroke_search_angle = pi / 3
# only for point with delta more than delta_threshold would be started with a new stroke
delta_threshold = 25
# parameter deciding the qualification of next point
next_point_max_threhold = 0
# salience threshold, times of std
salience_threshold = 1
# iteration number of computing approaximate b-spline
b_spline_iteration = 2


reason4end = {
    'stop at the second one': 0,
    'next one out of bound': 0,
    'next one drew already': 0
              }