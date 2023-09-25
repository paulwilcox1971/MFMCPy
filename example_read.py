# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:54:24 2023

@author: mepdw
"""

import mfmc.read as m

fname = 'write_example5.mfmc'

#fname = 'Example MFMC files\AS example.mfmc'

#Open file
MFMC = m.fn_open_file_for_reading(fname)

pl = m.fn_get_probe_list(MFMC)

probe = m.fn_read_probe(MFMC, pl[0], m.SPEC)

#Close file
m.fn_close_file(MFMC)