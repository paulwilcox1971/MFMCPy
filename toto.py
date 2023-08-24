# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 10:52:45 2023

@author: mepdw
"""
import mfmc
import numpy as np

# fname = 'Example MFMC files/AS example.mfmc'

# MFMC = mfmc.fn_open_file(fname)

# probe_list = mfmc.fn_get_probe_list(MFMC)

# for p in probe_list:
#     probe_details = mfmc.fn_analyse_probe(MFMC[p])
#     mfmc.fn_pretty_print_dictionary(probe_details)

# mfmc.fn_close_file(MFMC)

#probe = mfmc.fn_matrix_array(1e-3, 0.9e-3, 32, centre_pos = (0.0, 0.0, 0.0), normal_direction = (0.0, 0.0, 1.0), first_direction = (1.0, 0.0, 0.0))
input_params = {}
input_params[mfmc.PITCH_KEY] = 1e-3
input_params[mfmc.ELEMENT_WIDTH_KEY] = 0.9e-3
input_params[mfmc.ELEMENT_LENGTH_KEY] = 10e-3
input_params[mfmc.NUMBER_OF_ELEMENTS_KEY] = 11
probe = mfmc.fn_linear_array(input_params)
p = probe['ELEMENT_POSITION']
#p = np.random.rand(128,3)

probe_details = mfmc.fn_analyse_probe(probe)
mfmc.fn_pretty_print_dictionary(probe_details)

(q, v, no_dims, loglikelihood_dim) = mfmc.fn_convert_to_natural_coordinates(p)
print(no_dims, loglikelihood_dim)

(pitch, loglikelihood_pitch) = mfmc.fn_estimate_pitch(q)
print(pitch, loglikelihood_pitch)

