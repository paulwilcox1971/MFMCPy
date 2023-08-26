# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 12:08:35 2023

@author: mepdw
"""

import numpy as np

import sys
sys.path.append('..') #So mfmc can be found in parent directory
import mfmc


def fn_linear_array(input_params):
    default_params = {mfmc.MID_POINT_POSITION_KEY:  (0.0, 0.0, 0.0), 
                      mfmc.NORMAL_VECTOR_KEY:       (0.0, 0.0, 1.0),
                      mfmc.ACTIVE_VECTOR_KEY:       (1.0, 0.0, 0.0)}
    for d in default_params.keys():
        if d not in input_params.keys():
            input_params[d] = default_params[d]
    tmp = (np.array(range(input_params[mfmc.NUMBER_OF_ELEMENTS_KEY])) - (input_params[mfmc.NUMBER_OF_ELEMENTS_KEY] - 1) / 2) * input_params[mfmc.PITCH_KEY]
    p = np.array(input_params[mfmc.MID_POINT_POSITION_KEY]).reshape(1, 3) + tmp.reshape(input_params[mfmc.NUMBER_OF_ELEMENTS_KEY], 1) * np.array(input_params[mfmc.ACTIVE_VECTOR_KEY]).reshape(1, 3)
    passive_direction = np.cross(input_params[mfmc.NORMAL_VECTOR_KEY], input_params[mfmc.ACTIVE_VECTOR_KEY])
    e1 = np.tile(passive_direction, (input_params[mfmc.NUMBER_OF_ELEMENTS_KEY], 1)) * input_params[mfmc.ELEMENT_LENGTH_KEY] / 2
    e2 = np.tile(input_params[mfmc.ACTIVE_VECTOR_KEY], (input_params[mfmc.NUMBER_OF_ELEMENTS_KEY], 1))* input_params[mfmc.ELEMENT_WIDTH_KEY] / 2
    return {'ELEMENT_POSITION': p, 'ELEMENT_MAJOR': e1, 'ELEMENT_MINOR': e2}

def fn_matrix_array(input_params):
    default_params = {mfmc.MID_POINT_POSITION_KEY:  (0.0, 0.0, 0.0), 
                      mfmc.NORMAL_VECTOR_KEY:       (0.0, 0.0, 1.0),
                      mfmc.FIRST_VECTOR_KEY:       (1.0, 0.0, 0.0)}
    for d in default_params.keys():
        if d not in input_params.keys():
            input_params[d] = default_params[d]
    p = fn_expand_if_nesc(input_params[mfmc.PITCH_KEY])
    s = fn_expand_if_nesc(input_params[mfmc.ELEMENT_SIZE_KEY])
    n = fn_expand_if_nesc(input_params[mfmc.NUMBER_OF_ELEMENTS_KEY])
    nt = n[0] * n[1]
    input_params[mfmc.SECOND_VECTOR_KEY] = np.cross(input_params[mfmc.NORMAL_VECTOR_KEY], input_params[mfmc.FIRST_VECTOR_KEY])
    (t1, t2) = np.meshgrid((np.array(range(n[0])) - (n[0] - 1) / 2) * p[0],  (np.array(range(n[1])) - (n[1] - 1) / 2) * p[1])
    p = np.array(input_params[mfmc.MID_POINT_POSITION_KEY]).reshape(1, 3) + \
        t1.reshape(nt, 1) * np.array(input_params[mfmc.FIRST_VECTOR_KEY]).reshape(1, 3) + \
        t2.reshape(nt, 1) * np.array(input_params[mfmc.SECOND_VECTOR_KEY]).reshape(1, 3)
    e1 = np.tile(input_params[mfmc.FIRST_VECTOR_KEY], (nt, 1)) * s[0] / 2
    e2 = np.tile(input_params[mfmc.SECOND_VECTOR_KEY], (nt, 1))* s[1] / 2
    return {'ELEMENT_POSITION': p, 'ELEMENT_MAJOR': e1, 'ELEMENT_MINOR': e2}

def fn_expand_if_nesc(x):
    if np.isscalar(x):
        x = (x, x)
    return x
    