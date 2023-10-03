# -*- coding: utf-8 -*-
"""
This creates a simple MFMC file, checks contents, reads file back, and
checks against original data
"""

import unittest
import numpy as np

import os
import sys

#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))


import mfmc as m

fname = 'test.mfmc'

#------------------------------------------------------------------------------
def fn_write(probes):
    # try:
        #Probe
    
        #Open file for writing and load spec
        MFMC = m.write.fn_create_file_for_writing(fname, False)

        #Write a couple of probes to the file
        m.write.fn_create_group(MFMC, 'PROBES')
        probe_objs = []
        for p in probes:
            probe_objs.append(m.write.fn_add_probe(MFMC['PROBES'], p))
        
        laws = []
        sequences = []
        #add some laws (FMC-like)
        # law_refs = []
        # law = {m.write.h5_keys.TYPE: m.write.h5_keys.LAW}
        # m.write.fn_create_group(MFMC, 'LAWS')
        # for i in range(no_elements):
        #     law[m.write.h5_keys.PROBE] = [probe_obj1.ref]
        #     law[m.write.h5_keys.ELEMENT] = [i + 1]
        #     law_refs.append(m.write.fn_add_law(MFMC['LAWS'], law).ref)
    
        # #Add a sequence
        # seq = {m.write.h5_keys.TYPE: m.write.h5_keys.SEQUENCE}
    
    
        # seq[m.write.h5_keys.TRANSMIT_LAW] =       np.array([law_refs[i] for i in range(no_elements) for j in range(no_elements)])
        # seq[m.write.h5_keys.RECEIVE_LAW] =        np.array([law_refs[i] for i in range(no_elements) for j in range(no_elements)])
        # seq[m.write.h5_keys.PROBE_LIST] =         np.array([probe_obj1.ref, probe_obj2.ref])
        # seq[m.write.h5_keys.TIME_STEP] =          np.array(1e-9)
        # seq[m.write.h5_keys.START_TIME] =         np.array(0.0)
        # seq[m.write.h5_keys.SPECIMEN_VELOCITY] =  np.array([3000.0, 6000.0])
        # seq[m.write.h5_keys.MFMC_DATA] = np.random.write.randn(1, seq[m.write.h5_keys.TRANSMIT_LAW].shape[0], 100)
        # seq[m.write.h5_keys.MFMC_DATA_IM] = np.random.write.randn(1, seq[m.write.h5_keys.TRANSMIT_LAW].shape[0], 100)
        # seq_name = m.write.fn_add_sequence(MFMC, seq).name 
    
        # #add 3 frames
        # for i in range(5):
        #     frame = {}
        #     frame[m.write.h5_keys.MFMC_DATA] = np.random.randn(1, seq[m.write.h5_keys.TRANSMIT_LAW].shape[0], 100) + 5 * i
        #     frame[m.write.h5_keys.PROBE_POSITION] = np.array([[[i / 10, 0.0, 0.0],[i / 10 + 3, 0.0, 0.0]]])
        #     m.write.fn_add_frame(MFMC, seq_name, frame)
    
        m.write.fn_close_file(MFMC)
        return True
    # except:
    #     return (False, [], [], [])

def fn_check():
    MFMC = m.read.fn_open_file_for_reading(fname)

    probe_list = m.read.fn_get_probe_list(MFMC)

    sequence_list = m.read.fn_get_sequence_list(MFMC)
    suppress_law_details = True

    success = True
    for s in sequence_list:
        print('SEQUENCE', s)
        (check_log, size_table, err_list) = m.read.fn_check_sequence(MFMC, MFMC[s])
        print('  SIZE TABLE')
        for k in size_table.keys():
            if not(k.startswith('N_C') and suppress_law_details):
                print('    ' + k + ': ' + str(size_table[k]))
        if err_list:
            print('  ERRORS')
            for err in err_list:
                print('    ' + err)
            success = False

    m.read.fn_close_file(MFMC)
    
    return success

def fn_read(obj):
    success = True
    #Open file
    MFMC = m.read.fn_open_file_for_reading(fname)

    #Read in probes
    probe_list = m.read.fn_get_probe_list(MFMC)
    probes = []
    for p in probe_list:
        probes.append(m.read.fn_read_probe(MFMC, p))

    # #Read in laws - note order is random if you just read them in!
    # law_list = m.read.fn_get_law_list(MFMC)
    # laws = []
    # for i in law_list:
    #     laws.append(m.read.fn_read_law(MFMC, i))

    # seq_list = m.read.fn_get_sequence_list(MFMC)
    # seq_data = m.read.fn_read_sequence_data(MFMC, seq_list[0])

    # #read last frame in seq
    # frames = m.read.fn_read_frame(MFMC, seq_list[0])

    # #Close file
    m.read.fn_close_file(MFMC)
    
    #need to compare them item by item!
    for [p1,p2] in zip(obj.probes, probes):
        for k in p1.keys():
            if type(p1[k]) is str:
                obj.assertEqual(p1[k], p2[k], msg = 'Incorrect' + k)
            else:
                v1 = np.array(p1[k]).ravel()
                v2 = np.array(p2[k]).ravel()
                dp = np.dot(v1, v2) / np.sqrt(np.dot(v1, v1) * np.dot(v2, v2))
                obj.assertAlmostEqual(dp, 1.0, places = 8, msg = 'Incorrect ' + k)
    return success

def fn_setup():
    no_elements = 4
    input_params1 = {}
    input_params1[m.write.eng_keys.PITCH] = 1e-3
    input_params1[m.write.eng_keys.ELEMENT_WIDTH] = 0.9e-3
    input_params1[m.write.eng_keys.ELEMENT_LENGTH] = 10e-3
    input_params1[m.write.eng_keys.NUMBER_OF_ELEMENTS] = no_elements
    
    probes = [];
    probes.append(m.write.fn_1D_linear_probe(input_params1))
    return probes

class cl_test_probe_testers(unittest.TestCase):
    def setUp(self):
        self.probes = fn_setup()
        fn_write(self.probes)
    # def test_write(self):
    #     self.assertTrue()
    #     print('Write test')
    def test_check(self):
        self.assertTrue(fn_check())
        print('Check test')
    def test_read(self):
        self.assertTrue(fn_read(self))
        print('Read test')

unittest.main()

