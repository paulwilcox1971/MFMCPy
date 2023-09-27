# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:58:50 2023

@author: mepdw
"""

import mfmc.check as m

fname = 'Example MFMC files/AS example.mfmc'
fname = 'write_example1.mfmc'

MFMC = m.fn_open_file_for_reading(fname)

probe_list = m.fn_get_probe_list(MFMC)

sequence_list = m.fn_get_sequence_list(MFMC)
suppress_law_details = True

for s in sequence_list:
    print('SEQUENCE', s)
    (check_log, size_table, err_list) = m.fn_check_sequence(MFMC, MFMC[s])
    print('  SIZE TABLE')
    for k in size_table.keys():
        if not(k.startswith('N_C') and suppress_law_details):
            print('    ' + k + ': ' + str(size_table[k]))
    if err_list:
        print('  ERRORS')
        for err in err_list:
            print('    ' + err)

m.fn_close_file(MFMC)