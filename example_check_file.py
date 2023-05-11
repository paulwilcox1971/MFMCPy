# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:58:50 2023

@author: mepdw
"""

import MFMC_Py as mfmc

spec_fname = 'MFMC Specification 2.0.0.xlsx'

fname = "example mfmc file from brain.mfmc"
fname = "example mfmc file from brain 2.mfmc"
#fname = 'new_brain_example.mfmc'

MFMC = mfmc.fn_open_file(fname)

sequence_list = mfmc.fn_get_sequence_list(MFMC)

suppress_law_details = True

SPEC = mfmc.fn_load_specification(spec_fname)

for s in sequence_list:
    print('SEQUENCE', s)
    (check_log, size_table, err_list) = mfmc.fn_check_sequence(MFMC, SPEC, MFMC[s])
    print('  SIZE TABLE')
    for k in size_table.keys():
        if not(k.startswith('N_C') and suppress_law_details):
            print('    ' + k + ': ' + str(size_table[k]))
    if err_list:
        print('  ERRORS')
        for err in err_list:
            print('    ' + err)


mfmc.fn_close_file(MFMC)