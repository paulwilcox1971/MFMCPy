# -*- coding: utf-8 -*-
"""
This creates a simple MFMC file, checks contents, reads file back, and
checks against original data
"""

import unittest
import numpy as np

import os
import sys
import copy

#Set working directory one level up from where this file is
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-1]))


import mfmc as m

fname = 'test2.mfmc'

#------------------------------------------------------------------------------
def fn_write(obj):
        #Open file for writing and load spec
        MFMC = m.write.fn_create_file_for_writing(fname, False)

        #Write probes to file
        m.write.fn_create_group(MFMC, obj.probe_group)
        probe_objs = []
        for (p, n) in zip(obj.probes, obj.probe_names):
            probe_objs.append(m.write.fn_add_probe(MFMC[obj.probe_group], p, n))
        
        #Write laws to file
        m.write.fn_create_group(MFMC, obj.law_group)
        law_objs = []
        for (l, n) in zip(obj.laws, obj.law_names):
            law = copy.copy(l) #copy needed to so that the reference can be converted to H5 ref for writing to file
            law[m.write.h5_keys.PROBE] = [MFMC[law[m.write.h5_keys.PROBE][0]].ref]
            law_objs.append(m.write.fn_add_law(MFMC[obj.law_group], law, n))
        
        #Write sequence header to file
        
        # laws = []
        # sequences = []
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
    probes = []
    for p in obj.probe_names:
        probes.append(m.read.fn_read_probe(MFMC, obj.probe_group + m.strs.h5_keys.PATH_SEPARATOR + p))

    #Compare read probes with what they should be!
    [success, err_msg]= m.utils.fn_compare_dicts(obj.probes, probes)
    obj.assertTrue(success, err_msg)

    #Compare laws with what they should be
    laws = []
    for l in obj.law_names:
        law = m.read.fn_read_law(MFMC, obj.law_group + m.strs.h5_keys.PATH_SEPARATOR + l)
        law[m.write.h5_keys.PROBE] = []
        for ll in law[m.write.h5_keys.PROBE]:
            law[m.write.h5_keys.PROBE].append(MFMC[ll].name)
        laws.append(law)
        
    [success, err_msg]= m.utils.fn_compare_dicts(obj.laws, laws)
    obj.assertTrue(success, err_msg)

    # #Close file
    m.read.fn_close_file(MFMC)
    
                                               
    return success

def fn_setup(obj):
    #
    obj.probe_prefix = 'TEST PROBE'
    obj.probe_group = '/TEST PROBE GROUP'
    obj.law_prefix = 'TEST LAW'
    obj.law_group = '/TEST LAW GROUP'
    #define all the correct parameters here 
    no_elements = 4
    input_params1 = {}
    input_params1[m.write.eng_keys.PITCH] = 1e-3
    input_params1[m.write.eng_keys.ELEMENT_WIDTH] = 0.9e-3
    input_params1[m.write.eng_keys.ELEMENT_LENGTH] = 10e-3
    input_params1[m.write.eng_keys.NUMBER_OF_ELEMENTS] = no_elements
    
    obj.probes = [];
    obj.probe_names = []
    for i in [1,2]:
        obj.probes.append(m.write.fn_1D_linear_probe(input_params1))
        obj.probe_names.append(obj.probe_prefix + str(i))
#    print(obj.probe_names[-1])

    obj.laws = []
    obj.law_names = []
    for i in range(no_elements):
        law = {m.write.h5_keys.TYPE: m.write.h5_keys.LAW}
        law[m.write.h5_keys.PROBE] = [obj.probe_group + m.strs.h5_keys.PATH_SEPARATOR + obj.probe_names[0]]
        law[m.write.h5_keys.ELEMENT] = [i + 1]
        obj.laws.append(law)
        obj.law_names.append(obj.law_prefix + str(i + 1))
    #print(obj.laws[-1])
    #print(obj.law_names[-1])


    return

class cl_test_probe_testers(unittest.TestCase):
    def setUp(self):
        fn_setup(self)
        fn_write(self)
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

