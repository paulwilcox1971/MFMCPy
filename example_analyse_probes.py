# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 17:28:37 2023

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
    MFMC = m.read.fn_open_file_for_reading(fname)
    probe_list = m.check.fn_get_probe_list(MFMC)
    for p in probe_list:
        print('  PROBE: ' + p)
        probe = m.read.fn_read_probe(MFMC, p)
        details = m.read.fn_test_for_1D_linear_probe(probe)
        m.read.fn_pretty_print_dictionary(details)
        print()
    m.check.fn_close_file(MFMC)
    print()
    print()