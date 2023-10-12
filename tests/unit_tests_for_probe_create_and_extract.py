# -*- coding: utf-8 -*-
"""
Runs unit tests for checking that MFMC descriptions of probes of different 
types can be created from engineering parameters, and same engineering 
parameters can be recovered from MFMC descriptions.

Currently covers:
    1D linear
    2D matrix
"""

import unittest
import numpy as np

import os
import sys


#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))

import mfmc as m

no_trials = 100

#This is function that actually tests if probe input parameters match extracted ones
def fn_probe_test(create_fn, test_fn, input_params, s, obj):
    #Create a probe from the input parameters
    try:
        probe = create_fn(input_params)
    except:
        print('EXCEPTION in ' + create_fn.__name__ + ' during testing' + s)
        loc = locals()
        del loc['i'], loc['probe'], loc['s'], loc['rnd'], loc['self']
        for k in loc.keys():
            print('    ' + k + '=' + str(loc[k]))
        return False
            
    #Analyse probe to recover the parameters
    try:
        probe_details = test_fn(probe)
    except:
        print('EXCEPTION in fn_analyse_probe during testing' + s)
        loc = locals()
        del loc['i'], loc['probe'], loc['probe_details'], loc['s'], loc['rnd'], loc['self']
        for k in loc.keys():
            print('    ' + k + '=' + str(loc[k]))
        return False
            
    #Compare the recovered parameters to the input ones
    [success, err_msg] = m.utils.fn_compare_dicts(probe_details, input_params, 
                                                  ignore_direction_for_keys_with_this_suffix = m.strs.eng_keys.DIRECTION_ONLY_SUFFIX,
                                                  places = 12)
    obj.assertTrue(success, err_msg)
    return True

class cl_test_probe_testers(unittest.TestCase):
    def test_linear(self):
        #linear probe
        for i in range(1, no_trials):
            rnd = np.random.default_rng(i)
            input_params = {}
            input_params[m.strs.eng_keys.TYPE] =               m.strs.eng_keys.PROBE_TYPE_1D_LINEAR
            input_params[m.strs.eng_keys.PITCH] =              rnd.random() * 5e-3 + 0.1e-3
            input_params[m.strs.eng_keys.ELEMENT_WIDTH] =      (rnd.random() * 0.8 + 0.1) * input_params[m.strs.eng_keys.PITCH];
            input_params[m.strs.eng_keys.ELEMENT_LENGTH] =     rnd.random() * 20e-3 + 1e-3;
            input_params[m.strs.eng_keys.NUMBER_OF_ELEMENTS] = rnd.integers(2, 129)
            input_params[m.strs.eng_keys.MID_POINT_POSITION] = rnd.random(3) - 0.5
            #Random rotation
            tx = 2 * (rnd.random() - 1) * np.pi
            ty = 2 * (rnd.random() - 1) * np.pi
            tz = 2 * (rnd.random() - 1) * np.pi
            input_params[m.strs.eng_keys.ACTIVE_VECTOR] =       m.utils.fn_rotate_about_z_axis(
                                                                    m.utils.fn_rotate_about_y_axis(
                                                                        m.utils.fn_rotate_about_x_axis([1, 0, 0], tx),
                                                                        ty),
                                                                    tz)
            input_params[m.strs.eng_keys.PASSIVE_VECTOR] =      m.utils.fn_rotate_about_z_axis(
                                                                    m.utils.fn_rotate_about_y_axis(
                                                                        m.utils.fn_rotate_about_x_axis([0, 1, 0], tx),
                                                                        ty),
                                                                    tz)
            msg_str = ' [Seed = %i]' % i
            #Test it
            if not fn_probe_test(m.write.fn_1D_linear_probe, m.read.fn_test_for_1D_linear_probe, input_params, msg_str, self):
                print(msg_str)
    def test_matrix(self):
         #matrix probe
         for i in range(1, no_trials):
            rnd = np.random.default_rng(i)
            input_params = {}
            input_params[m.strs.eng_keys.TYPE] = m.strs.eng_keys.PROBE_TYPE_2D_MATRIX
            input_params[m.strs.eng_keys.PITCH] =         rnd.random(size = 2) * 5e-3 + 0.1e-3
            input_params[m.strs.eng_keys.ELEMENT_SIZE] =      (rnd.random(size = 2) * 0.8 + 0.1) * input_params[m.strs.eng_keys.PITCH];
            input_params[m.strs.eng_keys.NUMBER_OF_ELEMENTS] =   rnd.integers(2, 12, size = 2)
            input_params[m.strs.eng_keys.MID_POINT_POSITION] =    rnd.random(3) - 0.5
            msg_str = ' [Seed = %i]' % i
            #Random rotation
            tx = 2 * (rnd.random() - 1) * np.pi
            ty = 2 * (rnd.random() - 1) * np.pi
            tz = 2 * (rnd.random() - 1) * np.pi
            input_params[m.strs.eng_keys.FIRST_VECTOR] =       m.utils.fn_rotate_about_z_axis(
                                                                    m.utils.fn_rotate_about_y_axis(
                                                                        m.utils.fn_rotate_about_x_axis([1, 0, 0], tx),
                                                                        ty),
                                                                    tz)
            input_params[m.strs.eng_keys.SECOND_VECTOR] =      m.utils.fn_rotate_about_z_axis(
                                                                    m.utils.fn_rotate_about_y_axis(
                                                                        m.utils.fn_rotate_about_x_axis([0, 1, 0], tx),
                                                                        ty),
                                                        tz)
            #Test it
            if not fn_probe_test(m.write.fn_2D_matrix_probe, m.read.fn_test_for_2D_matrix_probe, input_params, msg_str, self):
                print(msg_str)

unittest.main()

