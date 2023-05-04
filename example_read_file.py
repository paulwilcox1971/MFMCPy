# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:58:50 2023

@author: mepdw
"""

import MFMCPy as mfmc
import numpy as np
import h5py as h5

fname = "example mfmc file from brain.mfmc"
fname = "example mfmc file from brain 2.mfmc"
fname = 'new_brain_example.mfmc'

MFMC = mfmc.fn_open_file(fname)

sequence_list = mfmc.fn_get_sequence_list(MFMC)

suppress_law_details = True

for s in sequence_list:
    print('SEQUENCE', s.name)
    (size_table, err_list, law_list, probe_list, probes_referenced_by_laws) = mfmc.fn_check_sequence(MFMC, MFMC[s.ref])
    print('  SIZE TABLE')
    for k in size_table.keys():
        if not(k.startswith('N_C') and suppress_law_details):
            print('    ' + k + ': ' + str(size_table[k]))
    if err_list:
        print('  ERRORS')
        for err in err_list:
            print('    ' + err)
