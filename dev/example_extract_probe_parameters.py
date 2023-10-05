# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:58:50 2023

@author: mepdw
"""

import mfmc

fname = 'Example MFMC files/AS example.mfmc'

MFMC = mfmc.fn_open_file(fname)

probe_list = mfmc.fn_get_probe_list(MFMC)

for p in probe_list:
    probe_details = mfmc.fn_analyse_probe(MFMC[p])
    mfmc.fn_pretty_print_dictionary(probe_details)

mfmc.fn_close_file(MFMC)