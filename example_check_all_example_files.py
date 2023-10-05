# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 17:18:58 2023

@author: mepdw
"""

import os
import glob

import mfmc as m

fnames = glob.glob(os.sep.join(['Example MFMC files', '*.mfmc']))

suppress_law_details = True

for fname in fnames:
    print('FILE: '+fname)
    print()
    MFMC = m.check.fn_open_file_for_reading(fname)
    sequence_list = m.check.fn_get_sequence_list(MFMC)
    for s in sequence_list:
        print('  SEQUENCE: ' + s)
        (check_log, size_table, err_list) = m.check.fn_check_sequence(MFMC, MFMC[s])
        print('    SIZE TABLE')
        for k in size_table.keys():
            if not(k.startswith('N_C') and suppress_law_details):
                print('    ' + k + ': ' + str(size_table[k]))
        if err_list:
            print('    ERRORS')
            for err in err_list:
                print('    ' + err)

    m.check.fn_close_file(MFMC)
    print()
    print()