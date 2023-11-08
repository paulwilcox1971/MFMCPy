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
    """Open MFMC file if it exists, create if it does not
    
    :param fname: name of MFMC file to open / create.
    :type fname: string
    :return: MFMC file.
    :rtype: HDF5 object
    """
    MFMC = h5.File(fname, 'a')
    return MFMC

def fn_create_group(MFMC, group):
    """Creates a group in MFMC file if it does not already exist
    
    :param MFMC: an open MFMC file or existing group within an open MFMC file.
    :type MFMC: HDF5 file or HDF5 group object
    :param group: name of group to create, which should can include path to a 
        group, which will be interpreted relative to MFMC, so if MFMC is the
        object `group1` and `group = group2/new_group` then the group created 
        will be at `group1/group2/new_group`
    :type group: string
    :return: name of group
    :rtype: string
    """
    if group in MFMC.keys():
        grp = MFMC[group]
    else:
        grp = MFMC.create_group(group)
    return grp.name

def fn_create_file_for_writing(fname, warn_if_file_exists = True):
    """Open new MFMC file for writing. If it already exists, overwrite
    
    :param fname: name of MFMC file to open / create.
    :type fname: string
    :param warn_if_file_exists: Optional. If `True` will ask for confirmation if file 
        exists for it to be overwritten; if `False`, existing file will just be
        overwritten. Default is `True`.
    :type warn_if_file_exists: bool
    :return: MFMC file object.
    :rtype: HDF5 object
    """
    if os.path.isfile(fname) and warn_if_file_exists:
        if input('File exists: overwrite (y/n)? ').upper() != 'Y':
            MFMC = []
            return
    MFMC = h5.File(fname, 'w')
    return MFMC

def fn_add_probe(mfmc_file_or_group, probe, name = None, warn_if_probe_exists = True, spec = default_spec):
    """Writes probe to MFMC file.
    
    :param mfmc_file_or_group: an open MFMC file or existing group within an 
        open MFMC file.
    :type mfmc_file_or_group: HDF5 file or HDF5 group object.
    :param probe: dictionary with key-value pairs that match the MFMC 
        specifications for probe parameters. Only keys in probe which match 
        keys in specification will be written to file, others will be ignored.
        If a mandatory key is missing, an error will be thrown.
    :type probe: Python dictionary
    :param name: Optional. Name of group to write the probe details to in the 
        file. Default is to use the next available name based on the default
        name prefix specified in `h5_keys.DEFAULT_PREFIX[h5_keys.PROBE]`.
    :type name: string
    :param warn_if_probe_exists: Optional. If `True` will ask for confirmation
        if `name` specified already exists in file before it is overwritten.
    :type warn_if_probe_exists: bool
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to write the probe details to the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :return: Name of probe group.
    :rtype: string
    """
    probe[h5_keys.TYPE] = h5_keys.PROBE
    if name == None:
        name = _fn_next_free_name(mfmc_file_or_group, h5_keys.PROBE)
    if name in mfmc_file_or_group.keys():
        if warn_if_probe_exists and input('Probe exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del mfmc_file_or_group[name]
    grp = mfmc_file_or_group.create_group(name)
    if _fn_write_structure(mfmc_file_or_group[name], probe, fn_get_relevant_part_of_spec(spec, h5_keys.PROBE)):
        return grp.name
    else:
        return []

def fn_add_law(mfmc_file_or_group, law, name = None, warn_if_law_exists = True, spec = default_spec):
    """Writes law to MFMC file.
    
    :param mfmc_file_or_group: an open MFMC file or existing group within an 
        open MFMC file.
    :type mfmc_file_or_group: HDF5 file or HDF5 group object.
    :param law: dictionary with key-value pairs that match the MFMC 
        specifications for law parameters. Only keys in law which match 
        keys in specification will be written to file, others will be ignored.
        If a mandatory key is missing, an error will be thrown.
    :type law: Python dictionary
    :param name: Optional. Name of group to write the law details to in the 
        file. Default is to use the next available name based on the default
        name prefix specified in `h5_keys.DEFAULT_PREFIX[h5_keys.LAW]`.
    :type name: string
    :param warn_if_law_exists: Optional. If `True` will ask for confirmation
        if `name` specified already exists in file before it is overwritten.
    :type warn_if_law_exists: bool
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to write the law details to the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :return: Name of law group.
    :rtype: string
    """
    law[h5_keys.TYPE] = h5_keys.LAW
    if name == None:
        name = _fn_next_free_name(mfmc_file_or_group, h5_keys.LAW)
    if name in mfmc_file_or_group.keys():
        if warn_if_law_exists and input('Law exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del mfmc_file_or_group[name]
    grp = mfmc_file_or_group.create_group(name)
    if _fn_write_structure(mfmc_file_or_group[name], law, fn_get_relevant_part_of_spec(spec, h5_keys.LAW)):
        return grp.name
    else:
        return []
    
def fn_add_sequence(mfmc_file_or_group, seq, name = None, warn_if_seq_exists = True, spec = default_spec):
    """Writes sequence details and frames if present to MFMC file.
    
    :param mfmc_file_or_group: an open MFMC file or existing group within an 
        open MFMC file.
    :type mfmc_file_or_group: HDF5 file or HDF5 group object.
    :param seq: dictionary with key-value pairs that match the MFMC 
        specifications for sequence parameters. Only keys in sequence which match 
        keys in specification will be written to file, others will be ignored.
        If a mandatory key is missing, an error will be thrown.
    :type seq: Python dictionary
    :param name: Optional. Name of group to write the sequence details to in the 
        file. Default is to use the next available name based on the default
        name prefix specified in `h5_keys.DEFAULT_PREFIX[h5_keys.SEQUENCE]`.
    :type name: string
    :param warn_if_seq_exists: Optional. If `True` will ask for confirmation
        if `name` specified already exists in file before it is overwritten.
    :type warn_if_seq_exists: bool
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to write the sequence details to the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :return: Name of sequence group.
    :rtype: string
    """
    seq[h5_keys.TYPE] = h5_keys.SEQUENCE
    if name == None:
        name = _fn_next_free_name(mfmc_file_or_group, h5_keys.SEQUENCE)
    if name in mfmc_file_or_group.keys():
        if warn_if_seq_exists and input('Sequence exists: overwrite (y/n)? ').upper() != 'Y':
            return []
        del mfmc_file_or_group[name]
    grp = mfmc_file_or_group.create_group(name)
    if not _fn_write_structure(
            mfmc_file_or_group[name], seq, 
            fn_get_relevant_part_of_spec(spec, h5_keys.SEQUENCE), 
            skip_fields = h5_keys.FRAME_KEYS):
        return []
    #If no frames of data included in seq return here, otherwise add the frames
    if h5_keys.MFMC_DATA not in seq.keys():
        return grp.name
        #seq[h5_keys.MFMC_DATA] = np.zeros((0, len(seq[h5_keys.TRANSMIT_LAW]), len(seq[h5_keys.TIME])))
    #Add frame
    frame = {}
    for k in h5_keys.FRAME_KEYS:
        if k in seq.keys():
            frame[k] = seq[k]
            
    if not fn_add_frame(mfmc_file_or_group[name], frame):
        return []

    return grp.name
    
def fn_add_frame(mfmc_seq, frame, spec = default_spec):
    """Adds frame(s) to existing sequence.
    
    :param mfmc_seq: an existing MFMC sequence group within an open MFMC file.
    :type mfmc_seq: HDF5 file or HDF5 group object.
    :param frame: dictionary with key-value pairs that match the MFMC 
        specification. See below. Only keys in specification will be written to file, 
        others will be ignored.
    :type frame: Python dictionary
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to write the sequence details to the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :return: Success or not.
    :rtype: bool
    
    Mandatory frame keys:
        * for h5_keys.MFMC_DATA
    Optional frame keys (if omitted the default in brackets is used):
        * h5_keys.PROBE_POSITION (default = [0.0, 0.0, 0.0])*
        * h5_keys.PROBE_X_DIRECTION (default = [1.0, 0.0, 0.0])*
        * h5_keys.PROBE_Y_DIRECTION (default = [0.0, 1.0, 0.0])*
        * h5_keys.PROBE_PLACEMENT_INDEX (default = [1, 1, ...., 1] of length frame[h5_keys.MFMC_DATA].shape[0])
        * h5_keys.MFMC_DATA_IM (default = None)
    Note that h5_keys.PROBE_PLACEMENT_INDEX here should be an index (first 
    row is index 1) into rows of the arrays marked * as supplied to this 
    function. When written to file, the arrays marked * are appended to 
    those already in the file and the indices in h5_keys.PROBE_PLACEMENT_INDEX
    will be updated accordingly. 
    """
    
    if h5_keys.MFMC_DATA not in frame.keys():
        print('Error: MFMC_DATA data missing from frame')
        return False
    if h5_keys.PROBE_PLACEMENT_INDEX in mfmc_seq.keys():
        current_max_placement_index = np.max(mfmc_seq[h5_keys.PROBE_PLACEMENT_INDEX][()])
    else:
        current_max_placement_index = 0
    #print(current_max_placement_index)
    no_frames = frame[h5_keys.MFMC_DATA].shape[0]
    no_ascans = mfmc_seq[h5_keys.TRANSMIT_LAW].shape[0]
    no_probes = mfmc_seq[h5_keys.PROBE_LIST].shape[0]
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
        _fn_append_or_create_dataset(mfmc_seq, i, frame[i], spec)
    
    return True
#------------------------------------------------------------------------------

def _fn_append_or_create_dataset(mfmc_group, name, data, spec):
    if name not in spec.index:
        print('Not in spec!')
        return
    shape_str = fn_parse_shape_string_in_spec(spec.loc[name, 'Size or content'])
    #Add leading singleton dimensions of insufficent dims in data to match spec
    if len(data.shape) < len(shape_str):
        data = np.expand_dims(data, tuple(np.arange(len(shape_str) - len(data.shape))))
    #Append or create the dataset
    if name in mfmc_group.keys():
        #If dataset already exists, append  
        size = list(mfmc_group[name].shape)
        # print('Current size', size)
        size[0] += data.shape[0]
        # print('New size', size)
        # print('New data size', data.shape)
        mfmc_group[name].resize(size)
        mfmc_group[name][-data.shape[0]:] = data
        pass
    else:
        #Otherwise, create new dataset with expandable dimension
        if name == h5_keys.MFMC_DATA or name == h5_keys.MFMC_DATA_IM:
            dtype = data.dtype #Special case for the actual data which will be stored in whatever form it comes in
        else:
            dtype = NUMPY_EQUIV_DTYPE_FOR_WRITE[spec.loc[name, 'Class']]
        chunks = list(data.shape)
        chunks[0] = 1
        maxshape = list(data.shape)
        maxshape[0] = None
        mfmc_group.create_dataset(name, data = data, dtype = dtype, chunks = tuple(chunks), maxshape = tuple(maxshape))

def _fn_write_structure(mfmc_group, var, spec, skip_fields = []):
    """Writes structure to file using dictionary key names in var as MFMC field
    names, based on spec"""
    success = True
    for i in spec.index:
        if i in skip_fields:
            continue
        if i in var.keys():
            #Convert Python dictionary keys to HDF5 object references - need to 
            #create new variable otherwise entries in original list in calling
            #script will be overwitten as well
            if spec.loc[i, 'Class'] == 'H5T_STD_REF_OBJ':
                if type(var[i]) is list or type(var[i]) is np.ndarray:
                    var_to_write = [mfmc_group.file[j].ref for j in var[i]]
                else:
                    var_to_write = mfmc_group.file[var[i]].ref
            else:
                var_to_write = var[i]
            #Write to file according to spec
            if spec.loc[i, 'D or A'] == 'D':
                mfmc_group.create_dataset(i, data = var_to_write, dtype = NUMPY_EQUIV_DTYPE_FOR_WRITE[spec.loc[i, 'Class']])
            else:
                #Attribute
                mfmc_group.attrs[i] = var_to_write
        else:
            if spec.loc[i, 'M or O'] == 'M':
                print('Warning: mandatory field', i, 'missing')
                success = False
    return success

def _fn_next_free_name(MFMC, type):
    """Returns next free name for MFMC group of type specified"""
    prefix = h5_keys.DEFAULT_PREFIX[type]
    tmp = fn_hdf5_group_refs_by_type(MFMC, type)
    i = 1
    while prefix + '%i' % i in tmp:
        i += 1
    return prefix + '%i' % i