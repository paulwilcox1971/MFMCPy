# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 12:08:35 2023

@author: mepdw
"""

import numpy as np
from ..utils import fn_close_file 
from ..strs import h5_keys
from ..strs import eng_keys

def fn_1D_linear_probe(input_params):
    """Create dictionary of MFMC data to describe 1D linear array probe.
    
    :param input_params: Dictionary of engineering input parameters. See
        below
    :type input_params: dictionary
    :return: MFMC dictionary
    :rtype: dictionary
    
    Input parameter dictionary (defaults for optional params):
        * eng_keys.NUMBER_OF_ELEMENTS (int)
        * eng_keys.PITCH (float)
        * eng_keys.ELEMENT_LENGTH (float)
        * eng_keys.ELEMENT_WIDTH (float)
        * eng_keys.MID_POINT_POSITION ((float, float, float)) = (0.0, 0.0, 0.0)
        * eng_keys.NORMAL_VECTOR ((float, float, float)) = (0.0, 0.0, 1.0)
        * eng_keys.ACTIVE_VECTOR ((float, float, float)) = (1.0, 0.0, 0.0)
        * eng_keys.CENTRE_FREQUENCY (float) = 1.0e6
    """
    default_params = {eng_keys.MID_POINT_POSITION:  (0.0, 0.0, 0.0), 
                      eng_keys.NORMAL_VECTOR:       (0.0, 0.0, 1.0),
                      eng_keys.ACTIVE_VECTOR:       (1.0, 0.0, 0.0),
                      eng_keys.CENTRE_FREQUENCY:    1.0e6}
    for d in default_params.keys():
        if d not in input_params.keys():
            input_params[d] = default_params[d]
    tmp = (np.array(range(input_params[eng_keys.NUMBER_OF_ELEMENTS])) - (input_params[eng_keys.NUMBER_OF_ELEMENTS] - 1) / 2) * input_params[eng_keys.PITCH]
    p = np.array(input_params[eng_keys.MID_POINT_POSITION]).reshape(1, 3) + tmp.reshape(input_params[eng_keys.NUMBER_OF_ELEMENTS], 1) * np.array(input_params[eng_keys.ACTIVE_VECTOR]).reshape(1, 3)
    passive_direction = np.cross(input_params[eng_keys.NORMAL_VECTOR], input_params[eng_keys.ACTIVE_VECTOR])
    e1 = np.tile(passive_direction, (input_params[eng_keys.NUMBER_OF_ELEMENTS], 1)) * input_params[eng_keys.ELEMENT_LENGTH] / 2
    e2 = np.tile(input_params[eng_keys.ACTIVE_VECTOR], (input_params[eng_keys.NUMBER_OF_ELEMENTS], 1))* input_params[eng_keys.ELEMENT_WIDTH] / 2
    return {h5_keys.TYPE: h5_keys.PROBE, 
            h5_keys.ELEMENT_POSITION: p, 
            h5_keys.ELEMENT_MAJOR: e1, 
            h5_keys.ELEMENT_MINOR: e2, 
            h5_keys.CENTRE_FREQUENCY: input_params[eng_keys.CENTRE_FREQUENCY], 
            h5_keys.ELEMENT_SHAPE: np.ones(input_params[eng_keys.NUMBER_OF_ELEMENTS])}

def fn_2D_matrix_probe(input_params):
    """Create dictionary of MFMC data to describe 2D matrix array probe.
    
    :param input_params: Dictionary of engineering input parameters. See
        below
    :type input_params: dictionary
    :return: MFMC dictionary
    :rtype: dictionary
    
    Input parameter dictionary (defaults for optional params):
        * eng_keys.NUMBER_OF_ELEMENTS ((int, int))
        * eng_keys.PITCH ((float, float))
        * eng_keys.ELEMENT_SIZE ((float, float))
        * eng_keys.MID_POINT_POSITION ((float, float, float)) = (0.0, 0.0, 0.0)
        * eng_keys.NORMAL_VECTOR ((float, float, float)) = (0.0, 0.0, 1.0)
        * eng_keys.ACTIVE_VECTOR ((float, float, float)) = (1.0, 0.0, 0.0)
        * eng_keys.CENTRE_FREQUENCY (float) = 1.0e6
    """
    default_params = {eng_keys.MID_POINT_POSITION:  (0.0, 0.0, 0.0), 
                      eng_keys.NORMAL_VECTOR:       (0.0, 0.0, 1.0),
                      eng_keys.FIRST_VECTOR:       (1.0, 0.0, 0.0),
                      eng_keys.CENTRE_FREQUENCY:    1.0e6}
    for d in default_params.keys():
        if d not in input_params.keys():
            input_params[d] = default_params[d]
    p = _fn_expand_if_nesc(input_params[eng_keys.PITCH])
    s = _fn_expand_if_nesc(input_params[eng_keys.ELEMENT_SIZE])
    n = _fn_expand_if_nesc(input_params[eng_keys.NUMBER_OF_ELEMENTS])
    nt = n[0] * n[1]
    input_params[eng_keys.SECOND_VECTOR] = np.cross(input_params[eng_keys.NORMAL_VECTOR], input_params[eng_keys.FIRST_VECTOR])
    (t1, t2) = np.meshgrid((np.array(range(n[0])) - (n[0] - 1) / 2) * p[0],  (np.array(range(n[1])) - (n[1] - 1) / 2) * p[1])
    p = np.array(input_params[eng_keys.MID_POINT_POSITION]).reshape(1, 3) + \
        t1.reshape(nt, 1) * np.array(input_params[eng_keys.FIRST_VECTOR]).reshape(1, 3) + \
        t2.reshape(nt, 1) * np.array(input_params[eng_keys.SECOND_VECTOR]).reshape(1, 3)
    e1 = np.tile(input_params[eng_keys.FIRST_VECTOR], (nt, 1)) * s[0] / 2
    e2 = np.tile(input_params[eng_keys.SECOND_VECTOR], (nt, 1))* s[1] / 2
    return {h5_keys.TYPE: h5_keys.PROBE, 
            h5_keys.ELEMENT_POSITION: p, 
            h5_keys.ELEMENT_MAJOR: e1, 
            h5_keys.ELEMENT_MINOR: e2, 
            h5_keys.CENTRE_FREQUENCY: input_params[eng_keys.CENTRE_FREQUENCY], 
            h5_keys.ELEMENT_SHAPE: np.ones(input_params[eng_keys.NUMBER_OF_ELEMENTS])}

#------------------------------------------------------------------------------

def _fn_expand_if_nesc(x):
    """Expands a scalar argument to a tuple of two identical values"""
    if np.isscalar(x):
        x = (x, x)
    return x
    