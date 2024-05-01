# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 10:52:45 2023

@author: mepdw
"""
import mfmc

fname = '../Example MFMC files/AS example.mfmc'

MFMC = mfmc.read.fn_open_file_for_reading(fname)

probe_list = mfmc.read.fn_get_probe_list(MFMC)

for pl in probe_list:
    p = mfmc.read.fn_read_probe(MFMC[pl])
    probe_details = mfmc.read.fn_analyse_probe(p)
    mfmc.read.fn_pretty_print_dictionary(probe_details)

mfmc.read.fn_close_file(MFMC)