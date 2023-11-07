# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 17:28:12 2023

@author: mepdw
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 21:14:14 2023

@author: mepdw
"""

import sys
import os

import numpy as np


fname = os.sep.join(['Example MFMC files', 'read-write-check test file.mfmc'])

#------------------------------------------------------------------------------
# WRITE
#------------------------------------------------------------------------------

import mfmc as m

#Create a 1D linear probe
no_elements = 4
input_params1 = {}
input_params1[m.strs.eng_keys.PITCH] = 1e-3
input_params1[m.strs.eng_keys.ELEMENT_WIDTH] = 0.9e-3
input_params1[m.strs.eng_keys.ELEMENT_LENGTH] = 10e-3
input_params1[m.strs.eng_keys.NUMBER_OF_ELEMENTS] = no_elements
probe1 = m.write.fn_1D_linear_probe(input_params1)

#Open file for writing and load spec
#MFMC = m.writefn_open_file_for_writing(fname)
MFMC = m.write.fn_create_file_for_writing(fname, False)

#Write a couple of probes to the file
#m.fn_create_group(MFMC, 'PROBES')
probe_dict_write = {}
probe_dict_write[m.write.fn_add_probe(MFMC, probe1)] = probe1
probe_dict_write[m.write.fn_add_probe(MFMC, probe1)] = probe1

#add some laws (each using one element from each probe)
law_dict_write = {}
for i in range(no_elements):
    law = {}
    law[m.strs.h5_keys.PROBE] = [list(probe_dict_write.keys())[0], list(probe_dict_write.keys())[1]]
    law[m.strs.h5_keys.ELEMENT] = [i % no_elements + 1, (i + 1) % no_elements + 1]
    law_dict_write[m.write.fn_add_law(MFMC, law)] = law

#Create a sequence
seq_write = {}
seq_write[m.strs.h5_keys.TRANSMIT_LAW] =       [list(law_dict_write.keys())[i] for i in range(no_elements) for j in range(no_elements)]
seq_write[m.strs.h5_keys.RECEIVE_LAW] =        [list(law_dict_write.keys())[j] for i in range(no_elements) for j in range(no_elements)]
seq_write[m.strs.h5_keys.PROBE_LIST] =         [list(probe_dict_write.keys())[0], list(probe_dict_write.keys())[1]]
seq_write[m.strs.h5_keys.TIME_STEP] =          1e-9
seq_write[m.strs.h5_keys.START_TIME] =         0.0
seq_write[m.strs.h5_keys.SPECIMEN_VELOCITY] =  [3000.0, 6000.0]
seq_write[m.strs.h5_keys.MFMC_DATA] =          np.random.randn(3, len(seq_write[m.strs.h5_keys.TRANSMIT_LAW]), 100)

#Add two sequences, one with an initial frame, one without
seq_dict_write = {}
seq_dict_write[m.write.fn_add_sequence(MFMC, seq_write)] = seq_write
seq_write.pop(m.strs.h5_keys.MFMC_DATA)
seq_dict_write[m.write.fn_add_sequence(MFMC, seq_write)] = seq_write

#add 3 frames to first sequence
for i in range(5):
    frame = {}
    frame[m.strs.h5_keys.MFMC_DATA] = np.random.randn(1, len(seq_write[m.strs.h5_keys.TRANSMIT_LAW]), 100) + 5 * i
    frame[m.strs.h5_keys.PROBE_POSITION] = np.array([[i / 10, 0.0, 0.0],[i / 10 + 3, 0.0, 0.0]])
    m.write.fn_add_frame(MFMC, list(seq_dict_write.keys())[0], frame)

m.write.fn_close_file(MFMC)

#------------------------------------------------------------------------------
# READ
#------------------------------------------------------------------------------

#Open file
MFMC = m.read.fn_open_file_for_reading(fname)

#Read in probes
probe_dict_read = {}
for p in m.read.fn_get_probe_list(MFMC):
    probe_dict_read[p] = m.read.fn_read_probe(MFMC, p)

#Read in laws
law_list = m.read.fn_get_law_list(MFMC)
law_dict_read = {}
for i in m.read.fn_get_law_list(MFMC):
    law_dict_read[i] = m.read.fn_read_law(MFMC, i)

#Read in sequences
seq_dict_read = {}
for s in m.read.fn_get_sequence_list(MFMC):
    seq_dict_read[s] = m.read.fn_read_sequence_data(MFMC, s)
    seq_dict_read[s][m.strs.h5_keys.MFMC_DATA] = m.read.fn_read_frame(MFMC, s)

#Close file
m.read.fn_close_file(MFMC)

#------------------------------------------------------------------------------
# CHECK
#------------------------------------------------------------------------------


MFMC = m.check.fn_open_file_for_reading(fname)

probe_list = m.check.fn_get_probe_list(MFMC)

sequence_list = m.check.fn_get_sequence_list(MFMC)
suppress_law_details = True

for s in sequence_list:
    print('SEQUENCE', s)
    (check_log, size_table, err_list) = m.check.fn_check_sequence(MFMC, MFMC[s])
    print('  SIZE TABLE')
    for k in size_table.keys():
        if not(k.startswith('N_C') and suppress_law_details):
            print('    ' + k + ': ' + str(size_table[k]))
    if err_list:
        print('  ERRORS')
        for err in err_list:
            print('    ' + err)

m.check.fn_close_file(MFMC)
