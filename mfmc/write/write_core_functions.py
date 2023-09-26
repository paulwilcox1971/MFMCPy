# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 20:48:54 2023

@author: mepdw
"""
import os

import numpy as np
import h5py as h5

from ..utils import * #all functions in utils are accessible without prefix
from ..spec import *
from ..strs.mfmc_fieldnames import *
from ..strs.string_table import *

NUMPY_EQUIV_DTYPE_FOR_WRITE = {
    'H5T_STRING': np.string_,
    'H5T_FLOAT': np.floating,
    'H5T_INTEGER': np.integer,
    'H5T_STD_REF_OBJ': h5.ref_dtype}

def fn_open_file_for_writing(fname):
    """Open MFMC file if it exists, create if it does not"""
    MFMC = h5.File(fname, 'a')
    return MFMC

def fn_create_group(MFMC, group):
    """Creates a group in MFMC file if it does not already exist"""
    if group in MFMC.keys():
        grp = MFMC[group]
    else:
        grp = MFMC.create_group(group)
    return grp

def fn_create_file_for_writing(fname, warn_if_file_exists = True):
    """Open new MFMC file for writing. If it already exists, overwrite"""
    if os.path.isfile(fname) and warn_if_file_exists:
        if input('File exists: overwrite (y/n)? ').upper() != 'Y':
            MFMC = []
            return
    MFMC = h5.File(fname, 'w')
    return MFMC

def fn_add_probe(MFMC, probe, name = None, warn_if_probe_exists = True, spec = default_spec):
    """Writes probe to MFMC file.
    
    MFMC can be just the HDF5 file object or a group within it
    If no name specified, next free default name will be used.
    If name specified exists already, it will be overwritten"""
    if name == None:
        name = fn_next_free_name(MFMC, H5_PROBE)
    if name in MFMC.keys():
        if warn_if_probe_exists and input('Probe exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del MFMC[name]
    grp = MFMC.create_group(name)
    if fn_write_structure(MFMC, name, probe, fn_get_relevant_part_of_spec(spec, H5_PROBE)):
        return grp
    else:
        return []

def fn_add_law(MFMC, law, name = None, warn_if_law_exists = True, spec = default_spec):
    """Writes law to MFMC file.
    
    MFMC can be just the HDF5 file object or a group within it
    If no name specified, next free default name will be used.
    If name specified exists already, it will be overwritten"""
    if name == None:
        name = fn_next_free_name(MFMC, H5_LAW)
    if name in MFMC.keys():
        if warn_if_law_exists and input('Law exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del MFMC[name]
    grp = MFMC.create_group(name)
    if fn_write_structure(MFMC, name, law, fn_get_relevant_part_of_spec(spec, H5_LAW)):
        return grp
    else:
        return []
    
def fn_add_sequence(MFMC, seq, name = None, warn_if_seq_exists = True, spec = default_spec):
    """Adds new sequence to FMC file.
    
    probes referenced in sequence probe_list of sequence musy be already in file
    laws referenced by sequence tx/rx laws must be already in file
    """
    if name == None:
        name = fn_next_free_name(MFMC, H5_SEQUENCE)
    if name in MFMC.keys():
        if warn_if_seq_exists and input('Sequence exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del MFMC[name]
    grp = MFMC.create_group(name)
    if fn_write_structure(MFMC, name, seq, fn_get_relevant_part_of_spec(spec, H5_SEQUENCE)):
        return grp
    else:
        return []
    
def fn_add_frame(MFMC, seq_name, frame, spec = default_spec):
    #Need to use dset.resize to increment first (expandable) dim by 1 then set last layer to new frame
    #Note that this function also needs to handle new probe positions - all indexed probe positions must be within dims of existing data or new data provided
    
    #Need a list of expandable dims so these are picked up automatically when dsets created
    return
#------------------------------------------------------------------------------

def fn_write_structure(MFMC, group, var, spec):
    """Writes structure to file using dictionary key names in var as MFMC field
    names, based on spec"""
    success = True
    for i in spec.index:
        if i in var.keys():
            #Write to file according to spec
            if spec.loc[i, 'D or A'] == 'D':
                #Dataset
                if i == H5_MFMC_DATA or i == H5_MFMC_DATA_IM:
                    dtype = var[i].dtype #Special case for the actual data which will be stored in whatever form it comes in
                    chunks = (1, var[i].shape[1], var[i].shape[2])
                    maxshape = (None, var[i].shape[1], var[i].shape[2])
                else:
                    dtype = NUMPY_EQUIV_DTYPE_FOR_WRITE[spec.loc[i, 'Class']]
                    chunks = None
                    maxshape = None
                #print(i, '>>>', dtype)
                MFMC[group].create_dataset(i, data = var[i], dtype = dtype, chunks = chunks, maxshape = maxshape)
            else:
                #Attribute
                MFMC[group].attrs[i] = var[i]
        else:
            if spec.loc[i, 'M or O'] == 'M':
                print('Warning: mandatory field', i, 'missing')
                success = False
    return success

def fn_next_free_name(MFMC, type):
    """Returns next free name for MFMC group of type specified"""
    prefix = H5_DEFAULT_PREFIX[type]
    tmp = fn_hdf5_group_refs_by_type(MFMC, type)
    i = 1
    while prefix + '%i' % i in tmp:
        i += 1
    return prefix + '%i' % i