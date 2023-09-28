# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 17:53:16 2023

@author: mepdw
"""

import unittest
import numpy as np

import os
import sys

#sys.path.append('..') #So mfmc can be found in parent directory

#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))

import mfmc as m

sys.exit()

#import mfmc.write as m
# from m.strs.string_table import *
# from m.strs.mfmc_fieldnames import *



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
    for p in input_params.keys():
        if hasattr(input_params[p], '__iter__') or input_params[p] is str:
            tmp1 = input_params[p]
            tmp2 = probe_details[p]
        else:
            tmp1 = [input_params[p]]
            tmp2 = [probe_details[p]]
        for (t1, t2) in zip(tmp1, tmp2):
            if p == m.eng_keys.PITCH and probe['ELEMENT_POSITION'].shape[0] == 1:
                pass #Pitch has no meaning for single element probe so input parameter cannot be recovered
            else:
                if isinstance(t1, float):
                    obj.assertAlmostEqual(t1, t2, places = 4, msg = 'Incorrect' + p + s)
                else:
                    obj.assertEqual(t1, t2, msg = 'Incorrect' + p + s)
    return True

class cl_test_probe_testers(unittest.TestCase):
    def test_linear(self):
        #linear probe
        for i in range(1, no_trials):
            rnd = np.random.default_rng(i)
            input_params = {}
            input_params[m.eng_keys.TYPE] = m.eng_keys.PROBE_TYPE_1D_LINEAR
            input_params[m.eng_keys.PITCH] =         rnd.random() * 5e-3 + 0.1e-3
            input_params[m.eng_keys.ELEMENT_WIDTH] =      (rnd.random() * 0.8 + 0.1) * input_params['Pitch (m)'];
            input_params[m.eng_keys.ELEMENT_LENGTH] =     rnd.random() * 20e-3 + 1e-3;
            input_params[m.eng_keys.NUMBER_OF_ELEMENTS] =   rnd.integers(1, 129)
            input_params[m.eng_keys.MID_POINT_POSITION] =    rnd.random(3) - 0.5
            #create_param_keys = ('Pitch (m)', 'Element width (m)', 'Element length (m)', 'Number of elements', 'Probe mid-point (m)')
            msg_str = ' [Seed = %i]' % i
            #Test it
            if not fn_probe_test(m.fn_linear_array, m.read.fn_test_for_1D_linear_probe, input_params, msg_str, self):
                print(msg_str)
        

unittest.main()

