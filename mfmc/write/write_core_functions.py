# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 20:48:54 2023

@author: mepdw
"""
import os

import numpy as np
import h5py as h5

from ..utils import fn_hdf5_group_refs_by_type  
from ..spec import default_spec, fn_get_relevant_part_of_spec, fn_parse_shape_string_in_spec

from ..strs import h5_keys
from ..strs import eng_keys

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
        name = fn_next_free_name(MFMC, h5_keys.PROBE)
    if name in MFMC.keys():
        if warn_if_probe_exists and input('Probe exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del MFMC[name]
    grp = MFMC.create_group(name)
    if fn_write_structure(MFMC, name, probe, fn_get_relevant_part_of_spec(spec, h5_keys.PROBE)):
        return grp
    else:
        return []

def fn_add_law(MFMC, law, name = None, warn_if_law_exists = True, spec = default_spec):
    """Writes law to MFMC file.
    
    MFMC can be just the HDF5 file object or a group within it
    If no name specified, next free default name will be used.
    If name specified exists already, it will be overwritten"""
    if name == None:
        name = fn_next_free_name(MFMC, h5_keys.LAW)
    if name in MFMC.keys():
        if warn_if_law_exists and input('Law exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del MFMC[name]
    grp = MFMC.create_group(name)
    if fn_write_structure(MFMC, name, law, fn_get_relevant_part_of_spec(spec, h5_keys.LAW)):
        return grp
    else:
        return []
    
def fn_add_sequence(MFMC, seq, name = None, warn_if_seq_exists = True, spec = default_spec):
    """Adds new sequence to FMC file.
    
    probes referenced in sequence probe_list of sequence musy be already in file
    laws referenced by sequence tx/rx laws must be already in file
    """
    if name == None:
        name = fn_next_free_name(MFMC, h5_keys.SEQUENCE)
    if name in MFMC.keys():
        if warn_if_seq_exists and input('Sequence exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del MFMC[name]
    grp = MFMC.create_group(name)
    if fn_write_structure(
            MFMC, name, seq, 
            fn_get_relevant_part_of_spec(spec, h5_keys.SEQUENCE), 
            skip_fields = [h5_keys.MFMC_DATA, h5_keys.MFMC_DATA_IM, h5_keys.PROBE_PLACEMENT_INDEX, h5_keys.PROBE_POSITION, h5_keys.PROBE_X_DIRECTION, h5_keys.PROBE_Y_DIRECTION]):
        return grp
    else:
        return []
    
def fn_add_frame(MFMC, seq_name, frame, spec = default_spec):
    """Adds frame(s) to existing sequence.
    
    frame must be dictionary with key MFMC_DATA at minimum. Optional keys are
    h5_keys.PROBE_POSITION - default= [0,0,0]
    h5_keys.PROBE_X_DIRECTION - default= [1,0,0]
    h5_keys.PROBE_Y_DIRECTION - default= [0,1,0]
    PROBE_PLACEMENT_INDEX - default = ones of correct shape
    PROBE_PLACEMENT_INDEX should be index into the supplied h5_keys.PROBE_POSITION 
    etc. arrays (1st row = index 1). These will be incremented when added to 
    file so that they point to corresponding rows in overall PROBE_POSITION etc. 
    arrays in file
    
    """
    if h5_keys.MFMC_DATA not in frame.keys():
        print('Error: MFMC_DATA data missing from frame')
        return False
    if h5_keys.PROBE_PLACEMENT_INDEX in MFMC[seq_name].keys():
        current_max_placement_index = np.max(MFMC[seq_name][h5_keys.PROBE_PLACEMENT_INDEX][()])
    else:
        current_max_placement_index = 0
    #print(current_max_placement_index)
    no_frames = frame[h5_keys.MFMC_DATA].shape[0]
    no_ascans = MFMC[seq_name][h5_keys.TRANSMIT_LAW].shape[0]
    no_probes = MFMC[seq_name][h5_keys.PROBE_LIST].shape[0]
    if h5_keys.PROBE_PLACEMENT_INDEX not in frame.keys():
        frame[h5_keys.PROBE_PLACEMENT_INDEX] = np.tile(np.ones((1, no_ascans)), (no_frames, 1))
    if h5_keys.PROBE_POSITION not in frame.keys():
        frame[h5_keys.PROBE_POSITION] = np.tile(np.array([0.0, 0.0, 0.0]), (1, no_probes, 1))
    if h5_keys.PROBE_X_DIRECTION not in frame.keys():
        frame[h5_keys.PROBE_X_DIRECTION] = np.tile(np.array([1.0, 0.0, 0.0]), (1, no_probes, 1))
    if h5_keys.PROBE_Y_DIRECTION not in frame.keys():
        frame[h5_keys.PROBE_Y_DIRECTION] = np.tile(np.array([0.0, 1.0, 0.0]), (1, no_probes, 1))
    spec = fn_get_relevant_part_of_spec(spec, h5_keys.SEQUENCE)
    
    #print(frame[h5_keys.PROBE_PLACEMENT_INDEX])
    frame[h5_keys.PROBE_PLACEMENT_INDEX] += current_max_placement_index
    if  frame[h5_keys.PROBE_PLACEMENT_INDEX].shape[0] != no_frames:
        print('Error: first dimensions of ' + h5_keys.MFMC_DATA +' and ' + h5_keys.PROBE_PLACEMENT_INDEX + 'are inconsistent')
        return False
    for i in frame.keys():
        fn_append_or_create_dataset(MFMC, seq_name, i, frame[i], spec)
    
    return True
#------------------------------------------------------------------------------

def fn_append_or_create_dataset(MFMC, group, name, data, spec):
    if name not in spec.index:
        print('Not in spec!')
        return
    shape_str = fn_parse_shape_string_in_spec(spec.loc[name, 'Size or content'])
    if name in MFMC[group].keys():
        size = list(MFMC[group][name].shape)
        # print('Current size', size)
        size[0] += data.shape[0]
        # print('New size', size)
        # print('New data size', data.shape)
        MFMC[group][name].resize(size)
        MFMC[group][name][-data.shape[0]:] = data
        pass
    else:
        #Create with expandable dimension
        if name == h5_keys.MFMC_DATA or name == h5_keys.MFMC_DATA_IM:
            dtype = data.dtype #Special case for the actual data which will be stored in whatever form it comes in
        else:
            dtype = NUMPY_EQUIV_DTYPE_FOR_WRITE[spec.loc[name, 'Class']]
        chunks = list(data.shape)
        chunks[0] = 1
        maxshape = list(data.shape)
        maxshape[0] = None
        MFMC[group].create_dataset(name, data = data, dtype = dtype, chunks = tuple(chunks), maxshape = tuple(maxshape))

def fn_write_structure(MFMC, group, var, spec, skip_fields = []):
    """Writes structure to file using dictionary key names in var as MFMC field
    names, based on spec"""
    success = True
    for i in spec.index:
        if i in skip_fields:
            continue
        if i in var.keys():
            #Write to file according to spec
            if spec.loc[i, 'D or A'] == 'D':
                MFMC[group].create_dataset(i, data = var[i], dtype = NUMPY_EQUIV_DTYPE_FOR_WRITE[spec.loc[i, 'Class']])
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
    prefix = h5_keys.DEFAULT_PREFIX[type]
    tmp = fn_hdf5_group_refs_by_type(MFMC, type)
    i = 1
    while prefix + '%i' % i in tmp:
        i += 1
    return prefix + '%i' % i