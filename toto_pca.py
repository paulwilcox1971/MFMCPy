# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 21:34:15 2023

@author: mepdw
"""
import mfmc
import numpy as np


xtheta = 0 * np.pi / 180
ytheta = 30 * np.pi / 180
ztheta = 0 * np.pi / 180
el_pos_err = 0#0.0000001e-3

#1D linear probe creation and recovery
input_params1 = {}
input_params1[mfmc.PITCH_KEY] = 1e-3
input_params1[mfmc.ELEMENT_WIDTH_KEY] = 0.9e-3
input_params1[mfmc.ELEMENT_LENGTH_KEY] = 10e-3
input_params1[mfmc.NUMBER_OF_ELEMENTS_KEY] = 11
input_params1[mfmc.NORMAL_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([0, 0, 1], xtheta, ytheta, ztheta)
input_params1[mfmc.ACTIVE_VECTOR_KEY] = mfmc.fn_rotate_about_xyz_axes([1, 0, 0], xtheta, ytheta, ztheta)
probe1 = mfmc.fn_linear_array(input_params1)

p = probe1['ELEMENT_POSITION']

(q, v, no_dims, loglikelihood) = mfmc.fn_convert_to_natural_coordinates(p)

