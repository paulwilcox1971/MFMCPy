# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:47:21 2023

@author: mepdw
"""
import os
import h5py as h5
import numpy as np


from ..utils import fn_str_to_utf, fn_get_probe_list, fn_get_law_list, fn_get_sequence_list, fn_close_file
from ..spec import default_spec, fn_get_relevant_part_of_spec

from ..strs import h5_keys
from ..strs import eng_keys


def fn_open_file_for_reading(fname):
    """Open MFMC file for reading
    
    :param fname: name of MFMC file to open.
    :type fname: string
    :type root_path: string
    :return: MFMC file or group in file.
    :rtype: HDF5 object
    """
    if os.path.isfile(fname):
        MFMC = h5.File(fname, 'r')
    else:
        print('Error: file not found')
        MFMC = []
    return MFMC

def fn_read_probe(mfmc_group, spec = default_spec):
    """Read probe details from MFMC file
    
    :param mfmc_group: a MFMC probe group within an open MFMC file.
    :type mfmc_group: HDF5 group object.
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to read the probe details from the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :return: MFMC probe data.
    :rtype: dictionary
    """
    probe = _fn_read_structure(mfmc_group, fn_get_relevant_part_of_spec(spec, h5_keys.PROBE))
    if not probe:
        return []
    if h5_keys.TYPE not in probe.keys() or probe[h5_keys.TYPE] != h5_keys.PROBE:
        print('Error: not a probe')
        return []
    else:
        return probe
    
def fn_read_law(mfmc_group, spec = default_spec):
    """Read focal law details from MFMC file
    
    :param mfmc_group: an MFMC law group within an open MFMC file.
    :type mfmc_group: HDF5 group object
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to read the law details from the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :returns: 
        - law (:py:class:`dict`) - MFMC law
    """
    law = _fn_read_structure(mfmc_group, fn_get_relevant_part_of_spec(spec, h5_keys.LAW))
    if not law:
        return []
    if h5_keys.TYPE not in law.keys() or law[h5_keys.TYPE] != h5_keys.LAW:
        print('Error: not a law')
        return []
    else:
        return law
    
def fn_read_sequence_data(mfmc_group, spec = default_spec):
    """Read sequence data (but no frames) from MFMC file
    
    :param mfmc_group: an MFMC sequence group within an open MFMC file.
    :type mfmc_group: HDF5 group object
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to read the sequence details from the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :return: MFMC sequence data.
    :rtype: dictionary
    """
    seq = _fn_read_structure(mfmc_group, 
                            fn_get_relevant_part_of_spec(spec, h5_keys.SEQUENCE), 
                            skip_fields = h5_keys.FRAME_KEYS)
    if not seq:
        return []
    if h5_keys.TYPE not in seq.keys() or seq[h5_keys.TYPE] != h5_keys.SEQUENCE:
        print('Error: not a sequence')
        return []
    else:
        #See how many frames there as this cannot be deduced from the sequence 
        #data - this is not a field that is explicitly in the MFMC spec
        if h5_keys.MFMC_DATA in mfmc_group.keys():
            seq[h5_keys.NUMBER_OF_FRAMES] = np.array(mfmc_group[h5_keys.MFMC_DATA].shape[0])
        else:
            seq[h5_keys.NUMBER_OF_FRAMES] = np.array(0)
        return seq

def fn_read_frame(mfmc_group, i = -1):
    """Read frame from sequence from MFMC file
    
    Args:
        mfmc_group (HDF5 group object): an MFMC sequence group within an open MFMC file.
        i (int): index of the frame to read
    
    Returns:
        frame (np.complex): 2D Numpy array of numerical values in the frame
    """
    if h5_keys.MFMC_DATA in mfmc_group.keys():
        frame_re = mfmc_group[h5_keys.MFMC_DATA][i, :, :]
    else:
        frame_re = 0
    if h5_keys.MFMC_DATA_IM in mfmc_group.keys():
        frame_im = mfmc_group[h5_keys.MFMC_DATA_IM][i, :, :]
    else:
        frame_im = 0
    return frame_re + 1j * frame_im
#------------------------------------------------------------------------------

def _fn_read_structure(mfmc_group, spec, skip_fields = []):
    var = {}
    success = True
    for i in spec.index:
        if i in skip_fields:
            continue
        if spec.loc[i, 'D or A'] == 'D':
            if i in mfmc_group.keys():
                #Dataset
                var[i] = mfmc_group[i][()]
        else:
            if i in mfmc_group.attrs:
                #Attribute
                var[i] = mfmc_group.attrs[i]
                if spec.loc[i, 'Class'] == 'H5T_STRING':
                    var[i] = fn_str_to_utf(var[i])
        #Convert HDF5 object refs to HDF5 object names for use in Python 
        #dictionaries
        if spec.loc[i, 'Class'] == 'H5T_STD_REF_OBJ':
            if type(var[i]) is np.ndarray:
                var[i][:] = [mfmc_group.file[j].name for j in var[i]]
            else:
                var[i] = mfmc_group.file[var[i]].name

        if spec.loc[i, 'M or O'] == 'M' and i not in var.keys():
            #Occurs if neither attribute or dataset found
            print('Error: mandatory field', i, 'missing')
            success = False
    if success:
        return var
    else:
        return []