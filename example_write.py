# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 21:14:14 2023

@author: mepdw
"""
import mfmc.write as m
import numpy as np

fname = 'write_example1.mfmc'

spec_fname = 'docs/MFMC Specification 2.0.0.xlsx'

#Create a 1D linear probe
no_elements = 4
input_params1 = {}
input_params1[m.PITCH_KEY] = 1e-3
input_params1[m.ELEMENT_WIDTH_KEY] = 0.9e-3
input_params1[m.ELEMENT_LENGTH_KEY] = 10e-3
input_params1[m.NUMBER_OF_ELEMENTS_KEY] = no_elements
probe1 = m.fn_linear_array(input_params1)

#Open file for writing and load spec
#MFMC = m.fn_open_file_for_writing(fname)
MFMC = m.fn_create_file_for_writing(fname, False)

#Write a couple of probes to the file
m.fn_create_group(MFMC, 'PROBES')
probe_obj1 = m.fn_add_probe(MFMC['PROBES'], probe1)
probe_obj2 = m.fn_add_probe(MFMC['PROBES'], probe1)

#add some laws (FMC-like)
law_refs = []
law = {m.H5_TYPE: m.H5_LAW}
m.fn_create_group(MFMC, 'LAWS')
for i in range(no_elements):
    law[m.H5_PROBE] = [probe_obj1.ref]
    law[m.H5_ELEMENT] = [i + 1]
    law_refs.append(m.fn_add_law(MFMC['LAWS'], law).ref)

#Add a sequence
seq = {m.H5_TYPE: m.H5_SEQUENCE}


seq[m.H5_TRANSMIT_LAW] =       np.array([law_refs[i] for i in range(no_elements) for j in range(no_elements)])
seq[m.H5_RECEIVE_LAW] =        np.array([law_refs[i] for i in range(no_elements) for j in range(no_elements)])
seq[m.H5_PROBE_LIST] =         np.array([probe_obj1.ref, probe_obj2.ref])
seq[m.H5_TIME_STEP] =          np.array(1e-9)
seq[m.H5_START_TIME] =         np.array(0.0)
seq[m.H5_SPECIMEN_VELOCITY] =  np.array([3000.0, 6000.0])
seq[m.H5_MFMC_DATA] = np.random.randn(1, seq[m.H5_TRANSMIT_LAW].shape[0], 100)
seq[m.H5_MFMC_DATA_IM] = np.random.randn(1, seq[m.H5_TRANSMIT_LAW].shape[0], 100)
seq_name = m.fn_add_sequence(MFMC, seq).name 

#add 3 frames
for i in range(5):
    frame = {}
    frame[m.H5_MFMC_DATA] = np.random.randn(1, seq[m.H5_TRANSMIT_LAW].shape[0], 100) + 5 * i
    frame[m.H5_PROBE_POSITION] = np.array([[[i / 10, 0.0, 0.0],[i / 10 + 3, 0.0, 0.0]]])
    m.fn_add_frame(MFMC, seq_name, frame)

m.fn_close_file(MFMC)
