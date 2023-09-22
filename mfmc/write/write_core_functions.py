# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 20:48:54 2023

@author: mepdw
"""
import numpy as np
import h5py as h5

from .. import utils
from .. import spec

NUMPY_EQUIV_DTYPE = {
    'H5T_STRING': np.string_,
    'H5T_FLOAT': np.floating,
    'H5T_INTEGER': np.integer,
    'H5T_STD_REF_OBJ': np.dtype('O')}

def fn_open_file_for_writing(fname):
    """Open file if it exists, create if not and return handle"""
    MFMC = h5.File(fname, 'a')
    return MFMC

def fn_write_probe(MFMC, SPEC, probe, group = '/P'):
    """Writes probe to open MFMC file. If it exists already, it will be 
    overwritten"""
    if group in MFMC.keys():
        del MFMC[group]
    MFMC.create_group(group)
    fn_write_structure_to_file(MFMC, group, probe, spec.fn_get_relevant_part_of_spec(SPEC, 'PROBE'))

def fn_write_structure_to_file(MFMC, group, var, spec):
    for i in spec.index:
        if i in var.keys():
            #Write to file according to spec
            if spec.loc[i, 'D or A'] == 'D':
                #Dataset
                MFMC[group].create_dataset(i, data = var[i], dtype = NUMPY_EQUIV_DTYPE[spec.loc[i, 'Class']])
            else:
                #Attribute
                MFMC[group][i] = var[i]
        else:
            if spec.loc[i, 'M or O'] == 'M':
                print('Error: mandatory field', i, 'missing')

                