# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 17:53:16 2023

@author: mepdw
"""

import unittest
import numpy as np

import sys
sys.path.append('..') #So mfmc can be found in parent directory
import mfmc

no_trials = 35

def fn_probe_test(create_fn, input_params, s, obj):
    #Create a probe from the input parameters
    try:
        #probe = create_fn(*[input_params[k] for k in create_param_keys])
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
        probe_details = mfmc.fn_analyse_probe(probe)
        #print(probe_details)
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
        #print(tmp1)
        #print(tmp2)
        for (t1, t2) in zip(tmp1, tmp2):
          #  print(type(t1))
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
            input_params[mfmc.TYPE_KEY] = mfmc.ARRAY_TYPE_1D_LINEAR
            input_params[mfmc.PITCH_KEY] =         rnd.random() * 5e-3 + 0.1e-3
            input_params[mfmc.ELEMENT_WIDTH_KEY] =      (rnd.random() * 0.8 + 0.1) * input_params['Pitch (m)'];
            input_params[mfmc.ELEMENT_LENGTH_KEY] =     rnd.random() * 20e-3 + 1e-3;
            input_params[mfmc.NUMBER_OF_ELEMENTS_KEY] =   rnd.integers(1, 129)
            input_params[mfmc.MID_POINT_POSITION_KEY] =    rnd.random(3) - 0.5
            #create_param_keys = ('Pitch (m)', 'Element width (m)', 'Element length (m)', 'Number of elements', 'Probe mid-point (m)')
            msg_str = ' [Seed = %i]' % i
            #Test it
            if not fn_probe_test(mfmc.fn_linear_array, input_params, msg_str, self):
                print(msg_str)
        

unittest.main()

