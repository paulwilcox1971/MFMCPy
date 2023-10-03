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

import numpy as np

fname = 'write_example1.mfmc'

#------------------------------------------------------------------------------
# WRITE
#------------------------------------------------------------------------------

import mfmc.write as m

#Create a 1D linear probe
no_elements = 4
input_params1 = {}
input_params1[m.eng_keys.PITCH] = 1e-3
input_params1[m.eng_keys.ELEMENT_WIDTH] = 0.9e-3
input_params1[m.eng_keys.ELEMENT_LENGTH] = 10e-3
input_params1[m.eng_keys.NUMBER_OF_ELEMENTS] = no_elements
probe1 = m.fn_1D_linear_probe(input_params1)

#Open file for writing and load spec
#MFMC = m.fn_open_file_for_writing(fname)
MFMC = m.fn_create_file_for_writing(fname, False)

#Write a couple of probes to the file
m.fn_create_group(MFMC, 'PROBES')
probe_obj1 = m.fn_add_probe(MFMC['PROBES'], probe1)
probe_obj2 = m.fn_add_probe(MFMC['PROBES'], probe1)

#add some laws (FMC-like)
law_refs = []
law = {m.h5_keys.TYPE: m.h5_keys.LAW}
m.fn_create_group(MFMC, 'LAWS')
for i in range(no_elements):
    law[m.h5_keys.PROBE] = [probe_obj1.ref]
    law[m.h5_keys.ELEMENT] = [i + 1]
    law_refs.append(m.fn_add_law(MFMC['LAWS'], law).ref)

#Add a sequence
seq = {m.h5_keys.TYPE: m.h5_keys.SEQUENCE}


seq[m.h5_keys.TRANSMIT_LAW] =       np.array([law_refs[i] for i in range(no_elements) for j in range(no_elements)])
seq[m.h5_keys.RECEIVE_LAW] =        np.array([law_refs[i] for i in range(no_elements) for j in range(no_elements)])
seq[m.h5_keys.PROBE_LIST] =         np.array([probe_obj1.ref, probe_obj2.ref])
seq[m.h5_keys.TIME_STEP] =          np.array(1e-9)
seq[m.h5_keys.START_TIME] =         np.array(0.0)
seq[m.h5_keys.SPECIMEN_VELOCITY] =  np.array([3000.0, 6000.0])
seq[m.h5_keys.MFMC_DATA] = np.random.randn(1, seq[m.h5_keys.TRANSMIT_LAW].shape[0], 100)
seq[m.h5_keys.MFMC_DATA_IM] = np.random.randn(1, seq[m.h5_keys.TRANSMIT_LAW].shape[0], 100)
seq_name = m.fn_add_sequence(MFMC, seq).name 

#add 3 frames
for i in range(5):
    frame = {}
    frame[m.h5_keys.MFMC_DATA] = np.random.randn(1, seq[m.h5_keys.TRANSMIT_LAW].shape[0], 100) + 5 * i
    frame[m.h5_keys.PROBE_POSITION] = np.array([[[i / 10, 0.0, 0.0],[i / 10 + 3, 0.0, 0.0]]])
    m.fn_add_frame(MFMC, seq_name, frame)

m.fn_close_file(MFMC)

#------------------------------------------------------------------------------
# READ
#------------------------------------------------------------------------------

import mfmc.read as m

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

#------------------------------------------------------------------------------
# CHECK
#------------------------------------------------------------------------------

import mfmc.check as m

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
