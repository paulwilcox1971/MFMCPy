# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:25:04 2023

@author: mepdw
"""
import h5py as h5
import pandas as pd
import numpy as np

from ..strs import h5_keys
from ..strs import eng_keys

def fn_close_file(MFMC):
    MFMC.close()
    return

def fn_get_sequence_list(MFMC):
    sequence_list = fn_hdf5_group_refs_by_type(MFMC, h5_keys.SEQUENCE)
    return sequence_list

def fn_transmit_laws_for_sequence(MFMC, sequence):
    return [MFMC[i].name for i in MFMC[sequence]['TRANSMIT_LAW']]

def fn_receive_laws_for_sequence(MFMC, sequence):
    return [MFMC[i].name for i in MFMC[sequence]['RECEIVE_LAW']]

def fn_compare_dicts(d1, d2, places = 8, ignore_direction_for_keys_with_this_suffix = None):
    """compares entries with common keys in both dictionaries. Dictionaries must
    contain only numpy arrays or strings. d1 and d2 can also be lists of dicts"""
    d1 = fn_force_to_list(d1)
    d2 = fn_force_to_list(d2)
    err_msg = []
    success = True
    for [p1,p2] in zip(d1, d2):
        keys = list(set(p1.keys()).intersection(set(p2.keys())))
        for k in keys:
            if (hasattr(p1[k], '__iter__') and all(isinstance(item, str) for item in p1[k])) or isinstance(p1[k], str):
                if any(a != b for (a, b) in zip(p1[k], p2[k])):
                    err_msg.append('String ' + k + ' mismatch')
                    success = False
                    continue
            else:
                v1 = np.array(p1[k]).ravel()
                v2 = np.array(p2[k]).ravel()
                dp = np.dot(v1, v2) / np.sqrt(np.dot(v1, v1) * np.dot(v2, v2))
                if ignore_direction_for_keys_with_this_suffix and k.endswith(ignore_direction_for_keys_with_this_suffix):
                    dp = np.abs(dp) #special case where parameter is unit vector and sign doesn't matter as long as direciton correct
                if (dp - 1.0) > (10 ** (-places)):
                    err_msg.append('Value ' + k + ' mismatch with relative error of ' + str(dp - 1.0))
                    success = False
                    continue
    return (success, err_msg)


def fn_force_to_list(x):
    if type(x) != list:
        x = [x]
    return x

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
       
def fn_hdf5_group_refs_by_type(MFMC, type):
    names = []
    def fn_dummy(name):
        if h5_keys.TYPE in MFMC[name].attrs:
            if type == fn_str_to_utf(MFMC[name].attrs[h5_keys.TYPE]):
                #names.append(cl_loc_details(ref = MFMC[name].ref, name = fn_name_from_path(name), location = MFMC[name].parent.name))
                names.append(h5_keys.PATH_SEPARATOR + name)
        return None
    MFMC.visit(fn_dummy)
    return names

def fn_str_to_utf(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')
    else:
        return s