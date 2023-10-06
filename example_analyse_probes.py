# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 17:28:37 2023

@author: mepdw
"""

import os
import glob

import mfmc as m

#Following line will check all probes in all example files
#fnames = glob.glob(os.sep.join(['Example MFMC files', '*.mfmc']))

#Following MFMC file just contains a load of different probe descriptions
fnames = glob.glob(os.sep.join(['Example MFMC files', 'some probes2.mfmc'])) 

suppress_law_details = True

probe_test_functions = [m.read.fn_test_for_1D_linear_probe, m.read.fn_test_for_2D_matrix_probe, m.read.fn_test_for_2D_other_probe]

probe_dict = {}

for fname in fnames:
    print('FILE: '+ fname)
    print()
    MFMC = m.read.fn_open_file_for_reading(fname)
    probe_list = m.check.fn_get_probe_list(MFMC)
    for p in probe_list:
        print('  PROBE: ' + p)
        probe_dict[p] = m.read.fn_read_probe(MFMC, p)
        for t in probe_test_functions:
            details = t(probe_dict[p])
            if details['Match (%)'] > 90: #only print the ones if match is better than 90%
                m.read.fn_pretty_print_dictionary(details)
                print()
                break #don't bother testing any more
    m.check.fn_close_file(MFMC)
    print()
    print()
    
