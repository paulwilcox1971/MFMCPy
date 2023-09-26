# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:54:24 2023

@author: mepdw
"""

import mfmc.read as m

fname = 'write_example8.mfmc'

#fname = 'Example MFMC files\AS example.mfmc'

#Open file
MFMC = m.fn_open_file_for_reading(fname)

#Read in probes
probe_list = m.fn_get_probe_list(MFMC)
probes = []
for p in probe_list:
    probes.append(m.fn_read_probe(MFMC, p))

#Read in laws - note order is random if you just read them in!
law_list = m.fn_get_law_list(MFMC)
laws = []
for i in law_list:
    laws.append(m.fn_read_law(MFMC, i))

seq_list = m.fn_get_sequence_list(MFMC)
seq_data = m.fn_read_sequence_data(MFMC, seq_list[0])

#read last frame in seq
frames = m.fn_read_frame(MFMC, seq_list[0])

#Close file
m.fn_close_file(MFMC)