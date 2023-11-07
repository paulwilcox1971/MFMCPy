# -*- coding: utf-8 -*-
"""
This creates a simple MFMC file, checks contents, reads file back, and
checks against original data
"""

import unittest
import numpy as np

import os

#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))


import mfmc as m

fname = os.sep.join(['Example MFMC files', 'unit-test test file.mfmc'])

#------------------------------------------------------------------------------
def fn_write(obj):
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
    obj.probe_dict_write = {}
    obj.probe_dict_write[m.write.fn_add_probe(MFMC, probe1)] = probe1
    obj.probe_dict_write[m.write.fn_add_probe(MFMC, probe1)] = probe1

    #add some laws (each using one element from each probe)
    obj.law_dict_write = {}
    for i in range(no_elements):
        law = {}
        law[m.strs.h5_keys.PROBE] = [list(obj.probe_dict_write.keys())[0], list(obj.probe_dict_write.keys())[1]]
        law[m.strs.h5_keys.ELEMENT] = [i % no_elements + 1, (i + 1) % no_elements + 1]
        obj.law_dict_write[m.write.fn_add_law(MFMC, law)] = law

    #Create a sequence
    seq_write = {}
    seq_write[m.strs.h5_keys.TRANSMIT_LAW] =       [list(obj.law_dict_write.keys())[i] for i in range(no_elements) for j in range(no_elements)]
    seq_write[m.strs.h5_keys.RECEIVE_LAW] =        [list(obj.law_dict_write.keys())[j] for i in range(no_elements) for j in range(no_elements)]
    seq_write[m.strs.h5_keys.PROBE_LIST] =         [list(obj.probe_dict_write.keys())[0], list(obj.probe_dict_write.keys())[1]]
    seq_write[m.strs.h5_keys.TIME_STEP] =          1e-9
    seq_write[m.strs.h5_keys.START_TIME] =         0.0
    seq_write[m.strs.h5_keys.SPECIMEN_VELOCITY] =  [3000.0, 6000.0]
    seq_write[m.strs.h5_keys.MFMC_DATA] =          np.random.randn(3, len(seq_write[m.strs.h5_keys.TRANSMIT_LAW]), 20)

    #Add two sequences, one with an initial frame, one without
    obj.seq_dict_write = {}
    obj.seq_dict_write[m.write.fn_add_sequence(MFMC, seq_write)] = seq_write
    seq_write.pop(m.strs.h5_keys.MFMC_DATA)
    obj.seq_dict_write[m.write.fn_add_sequence(MFMC, seq_write)] = seq_write

    #add 3 frames to first sequence
    for i in range(5):
        frame = {}
        frame[m.strs.h5_keys.MFMC_DATA] = np.random.randn(1, len(seq_write[m.strs.h5_keys.TRANSMIT_LAW]), 20) + 5 * i
        frame[m.strs.h5_keys.PROBE_POSITION] = np.array([[i / 10, 0.0, 0.0],[i / 10 + 3, 0.0, 0.0]])
        m.write.fn_add_frame(MFMC, list(obj.seq_dict_write.keys())[0], frame)

    m.write.fn_close_file(MFMC)
    return True

def fn_read(obj):
    #Open file
    MFMC = m.read.fn_open_file_for_reading(fname)

    #Read in probes
    obj.probe_dict_read = {}
    for p in m.read.fn_get_probe_list(MFMC):
        obj.probe_dict_read[p] = m.read.fn_read_probe(MFMC, p)

    #Read in laws
    law_list = m.read.fn_get_law_list(MFMC)
    obj.law_dict_read = {}
    for i in m.read.fn_get_law_list(MFMC):
        obj.law_dict_read[i] = m.read.fn_read_law(MFMC, i)

    #Read in sequences
    obj.seq_dict_read = {}
    for s in m.read.fn_get_sequence_list(MFMC):
        obj.seq_dict_read[s] = m.read.fn_read_sequence_data(MFMC, s)
        obj.seq_dict_read[s][m.strs.h5_keys.MFMC_DATA] = m.read.fn_read_frame(MFMC, s)

    #Close file
    m.read.fn_close_file(MFMC)
    return True

def fn_check():
    MFMC = m.check.fn_open_file_for_reading(fname)

    probe_list = m.check.fn_get_probe_list(MFMC)

    sequence_list = m.check.fn_get_sequence_list(MFMC)
    suppress_law_details = True

    success = True
    for s in sequence_list:
        (check_log, size_table, err_list) = m.check.fn_check_sequence(MFMC, MFMC[s])
        if err_list:
            success = False

    m.check.fn_close_file(MFMC)
    
    return success

def fn_compare_read_write_data(obj):
    success = True
    #Check probes
    for i in obj.probe_dict_write.keys():
        print('Checking ' + i)
        (success, err_msg) = m.utils.fn_compare_dicts(obj.probe_dict_write[i], obj.probe_dict_read[i], ignore_direction_for_keys_with_this_suffix = None)
        if err_msg:
            print(err_msg)
    #Check laws
    for i in obj.law_dict_write.keys():
        print('Checking ' + i)
        (success, err_msg) = m.utils.fn_compare_dicts(obj.law_dict_write[i], obj.law_dict_read[i], ignore_direction_for_keys_with_this_suffix = None)
        if err_msg:
            print(err_msg)
    #Check sequences
    for i in obj.seq_dict_write.keys():
        print('Checking ' + i)
        (success, err_msg) = m.utils.fn_compare_dicts(obj.seq_dict_write[i], obj.seq_dict_read[i], ignore_direction_for_keys_with_this_suffix = None)
        if err_msg:
            print(err_msg)
    return success
    

class cl_test_probe_testers(unittest.TestCase):
    def test_write_and_read(self):
        self.assertTrue(fn_write(self))
        self.assertTrue(fn_read(self))
        self.assertTrue(fn_compare_read_write_data(self))
        self.assertTrue(fn_check())
        print('Write-read-check test')

unittest.main()

