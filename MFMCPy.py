# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:49:17 2023

@author: mepdw
"""

import h5py as h5
import numpy as np
from dataclasses import dataclass

@dataclass
class cl_loc_details:
    ref: str
    name: str
    location: str 
    
@dataclass
class cl_attr_details:
    name: str
    mandatory: bool
    dtype: np.dtype
    shape: list[int]


#Sequence attribute specifications
SEQUENCE_ATTRS = []
SEQUENCE_ATTRS.append(cl_attr_details(name = 'START_TIME', mandatory = True, dtype = float, shape = [1]))
SEQUENCE_ATTRS.append(cl_attr_details(name = 'TIME_STEP', mandatory = True, dtype = float, shape = [1]))
SEQUENCE_ATTRS.append(cl_attr_details(name = 'SPECIMEN_VELOCITY', mandatory = True, dtype = float, shape = [2]))
SEQUENCE_ATTRS.append(cl_attr_details(name = 'WEDGE_VELOCITY', mandatory = False, dtype = float, shape = [2]))
SEQUENCE_ATTRS.append(cl_attr_details(name = 'TAG', mandatory = False, dtype = str, shape = [1]))
SEQUENCE_ATTRS.append(cl_attr_details(name = 'DAC_CURVE', mandatory = False, dtype = str, shape = [np.NaN]))

SEQUENCE_DSETS = []
SEQUENCE_DSETS.append(cl_attr_details(name = 'PROBE_POSITION', mandatory = True, dtype = float, shape = [3, np.NaN, np.NaN]))
#dimension order from h5py seems to be reverse of expected - check of row or column major

def fn_compare_shapes(a, b):
    #compares shapes ignoring NaNs
    return np.all(np.ma.masked_where(np.isnan(a), a) == np.ma.masked_where(np.isnan(b), b))

def fn_get_dataset_keys(group):
    keys = []
    for k in group.keys(): 
        if isinstance(group[k], h5.Dataset):
            keys.append(k)
    return keys


def fn_MFMC_open_file(fname, root_path = '/'):
    MFMC = h5.File(fname, 'r')
    return MFMC

def fn_get_sequence_list(MFMC):
    sequence_list = fn_hdf5_group_refs_by_type(MFMC, 'SEQUENCE')
    return sequence_list

def fn_get_probe_list(MFMC):
    probe_list = fn_hdf5_group_refs_by_type(MFMC, 'PROBE')
    return probe_list
      
def fn_get_law_list(MFMC):
    law_list = fn_hdf5_group_refs_by_type(MFMC, 'LAW')
    return law_list
       
def fn_hdf5_group_refs_by_type(MFMC, TYPE):
    names = []
    def fn_dummy(name):
        if 'TYPE' in MFMC[name].attrs:
            if TYPE == MFMC[name].attrs['TYPE']:
                names.append(cl_loc_details(ref = MFMC[name].ref, name = name.split('/')[-1], location = MFMC[name].parent.name))
        return None
    MFMC.visit(fn_dummy)
    return names

def fn_MFMC_check_file(MFMC):
    #work through all sequences in file
    sequence_list = fn_get_sequence_list(MFMC)
    for s in sequence_list:
        #check the attributes are OK
        for a in SEQUENCE_ATTRS:
            if a.name in MFMC[s.ref].attrs:
                print('Attribute', a.name, 'found in sequence', s.name)
                a2 = MFMC[s.ref].attrs[a.name]
                if fn_compare_shapes(a2.shape, a.shape):
                    pass
                    #print('Attribute', a.name, 'Shape match (found', list(a2.shape), '; should be', a.shape,')')    
                else:
                    print('Attribute', a.name, 'Shape mismatch (found', list(a2.shape), '; should be', a.shape,')')    
                #should check type too
            else:
                if a.mandatory:
                    print('Attribute', a.name, 'missing in sequence', s.name)
        #check the datasets are OK
        dsets = fn_get_dataset_keys(MFMC[s.ref])
        for d in SEQUENCE_DSETS:
            if d.name in dsets:
                print('Dataset', d.name, 'found in sequence', s.name)
                d2 = MFMC[s.ref][d.name]
                if fn_compare_shapes(d2.shape, d.shape):
                    pass
                    #print('Attribute', a.name, 'Shape match (found', list(a2.shape), '; should be', a.shape,')')    
                else:
                    print('Dataset', d.name, 'Shape mismatch (found', list(d2.shape), '; should be', d.shape,')')    
                #should check type too
            else:
                if d.mandatory:
                    print('Dataset', d.name, 'missing in sequence', s.name)
    
    return            
        