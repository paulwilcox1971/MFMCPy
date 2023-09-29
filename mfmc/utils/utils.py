# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:25:04 2023

@author: mepdw
"""
import h5py as h5
import pandas as pd
import numpy as np

from ..strs import h5_keys, eng_keys

__all__ = ['fn_hdf5_group_refs_by_type',
           'fn_close_file',
           'fn_get_sequence_list',
           'fn_transmit_laws_for_sequence',
           'fn_receive_laws_for_sequence',
           'fn_unique_h5_ref_list',
           'fn_name_from_path',
           'fn_get_dataset_keys',
           'fn_get_probe_list',
           'fn_get_law_list',
           'fn_str_to_utf']

#Various MFMC utility functions

def fn_close_file(MFMC):
    MFMC.close()
    return

def fn_get_sequence_list(MFMC):
    sequence_list = fn_hdf5_group_refs_by_type(MFMC, h5_keys.SEQUENCE)
    return sequence_list

def fn_transmit_laws_for_sequence(MFMC, sequence):
    return [MFMC[i].name for i in MFMC[sequence][h5_keys.TRANSMIT_LAW]]

def fn_receive_laws_for_sequence(MFMC, sequence):
    return [MFMC[i].name for i in MFMC[sequence][h5_keys.RECEIVE_LAW]]

def fn_unique_h5_ref_list(MFMC, ref_list):
    # if type(ref_list) is not list:
    #     return MFMC[ref_list]
    # else:
    return [MFMC[r].name for r in list(set([MFMC[i].name for i in ref_list]))]

def fn_name_from_path(path):
    return path.split('/')[-1]

def fn_get_dataset_keys(group):
    keys = []
    for k in group.keys(): 
        if isinstance(group[k], h5.Dataset):
            keys.append(k)
    return keys

def fn_get_probe_list(MFMC):
    probe_list = fn_hdf5_group_refs_by_type(MFMC, h5_keys.PROBE)
    return probe_list
      
def fn_get_law_list(MFMC):
    law_list = fn_hdf5_group_refs_by_type(MFMC, h5_keys.LAW)
    return law_list
       
def fn_hdf5_group_refs_by_type(MFMC, TYPE):
    names = []
    def fn_dummy(name):
        if 'TYPE' in MFMC[name].attrs:
            if TYPE == fn_str_to_utf(MFMC[name].attrs[h5_keys.TYPE]):
                #names.append(cl_loc_details(ref = MFMC[name].ref, name = fn_name_from_path(name), location = MFMC[name].parent.name))
                names.append(name)
        return None
    MFMC.visit(fn_dummy)
    return names

def fn_str_to_utf(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')
    else:
        return s