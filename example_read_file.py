# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:58:50 2023

@author: mepdw
"""

import MFMCPy as mfmc
import numpy as np

fname = "example mfmc file from brain.mfmc"

MFMC = mfmc.fn_MFMC_open_file(fname)

#tmp = mfmc.fn_hdf5_group_refs_by_type(m, 'LAW')

sequence_list = mfmc.fn_get_sequence_list(MFMC)
probe_list = mfmc.fn_get_probe_list(MFMC)
law_list = mfmc.fn_get_law_list(MFMC)

print('File contains', len(probe_list), 'probes,', len(sequence_list), 'sequences, and', len(law_list), 'laws')
print('  Probes:')
for p in probe_list:
    print('    ', p.name)
print('  Sequences:')
for s in sequence_list:
    print('    ', s.name)
    
#mfmc.fn_MFMC_check_file(MFMC)
(size_table, err_str) = mfmc.fn_check_sequence(MFMC, MFMC[sequence_list[0].ref])
print('ERRORS')
print(err_str)
print('SIZE TABLE')
for k in size_table.keys():
    print(k + ': ' + str(size_table[k]))