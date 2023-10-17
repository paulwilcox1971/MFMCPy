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


def fn_open_file_for_reading(fname, root_path = '/'):
    """Open MFMC file for reading
    
    :param fname: name of MFMC file to open.
    :type fname: string
    :param root_path: Optional. HDF5 path within file. All subsequent reads
        will be relative to this. Default = '/' (i.e. the root)
    :type root_path: string
    :return: MFMC file or group in file.
    :rtype: HDF5 object
    
    NOTE: root_path not implemented yet
    """
    if os.path.isfile(fname):
        MFMC = h5.File(fname, 'r')
    else:
        print('Error: file not found')
        MFMC = []
    return MFMC

def fn_read_probe(MFMC, group, spec = default_spec):
    """Read probe details from MFMC file
    
    :param MFMC: an open MFMC file or group within an open MFMC file.
    :type MFMC: HDF5 file or HDF5 group object
    :param group: name of an MFMC probe group in the HDF5 file (which include a path
        through the HDF5 file hierarchy).
    :type group: string
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to read the probe details from the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :return: MFMC probe data.
    :rtype: dictionary
    """
    probe = _fn_read_structure(MFMC, group, fn_get_relevant_part_of_spec(spec, h5_keys.PROBE))
    if not probe:
        return []
    if h5_keys.TYPE not in probe.keys() or probe[h5_keys.TYPE] != h5_keys.PROBE:
        print('Error: not a probe')
        return []
    else:
        return probe
    
def fn_read_law(MFMC, group, spec = default_spec):
    """Read focal law details from MFMC file
    
    :param MFMC: an open MFMC file or group within an open MFMC file.
    :type MFMC: HDF5 file or HDF5 group object
    :param group: name of an MFMC law group in the HDF5 file (which include a path
        through the HDF5 file hierarchy).
    :type group: string
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to read the law details from the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :return: MFMC law data.
    :rtype: dictionary
    """
    law = _fn_read_structure(MFMC, group, fn_get_relevant_part_of_spec(spec, h5_keys.LAW))
    if not law:
        return []
    if h5_keys.TYPE not in law.keys() or law[h5_keys.TYPE] != h5_keys.LAW:
        print('Error: not a law')
        return []
    else:
        return law
    
def fn_read_sequence_data(MFMC, group, spec = default_spec):
    """Read sequence data (but no frames) from MFMC file
    
    :param MFMC: an open MFMC file or group within an open MFMC file.
    :type MFMC: HDF5 file or HDF5 group object
    :param group: name of an MFMC sequence group in the HDF5 file (which include a path
        through the HDF5 file hierarchy).
    :type group: string
    :param spec: Optional. Python dictionary containing the MFMC specification
        used to read the sequence details from the file. Default is to use the
        default MFMC specification loaded from spreadsheet in /mfmc/spec.
    :type spec: dictionary
    :return: MFMC sequence data.
    :rtype: dictionary
    """
    seq = _fn_read_structure(MFMC, group, 
                            fn_get_relevant_part_of_spec(spec, h5_keys.SEQUENCE), 
                            skip_fields = h5_keys.FRAME_KEYS)
    if not seq:
        return []
    if h5_keys.TYPE not in seq.keys() or seq[h5_keys.TYPE] != h5_keys.SEQUENCE:
        print('Error: not a sequence')
        return []
    else:
        return seq

def fn_read_frame(MFMC, group, i = -1):
    """Read frame from sequence from MFMC file
    
    :param MFMC: an open MFMC file or group within an open MFMC file.
    :type MFMC: HDF5 file or HDF5 group object
    :param group: name of an MFMC sequence group in the HDF5 file (which include a path
        through the HDF5 file hierarchy).
    :type group: string
    :param i: index of frame. Optional. Default = -1 (last frame in sequence)
    :type i: int
    :return: MFMC frame data.
    :rtype: dictionary
    """
    if h5_keys.MFMC_DATA in MFMC[group].keys():
        frame_re = MFMC[group][h5_keys.MFMC_DATA][i, :, :]
    else:
        frame_re = 0
    if h5_keys.MFMC_DATA_IM in MFMC[group].keys():
        frame_im = MFMC[group][h5_keys.MFMC_DATA_IM][i, :, :]
    else:
        frame_im = 0
    return frame_re + 1j * frame_im
#------------------------------------------------------------------------------

def _fn_read_structure(MFMC, group, spec, skip_fields = []):
    var = {}
    success = True
    for i in spec.index:
        if i in skip_fields:
            continue
        if spec.loc[i, 'D or A'] == 'D':
            if i in MFMC[group].keys():
                #Dataset
                var[i] = MFMC[group][i][()]
        else:
            if i in MFMC[group].attrs:
                #Attribute
                var[i] = MFMC[group].attrs[i]
                if spec.loc[i, 'Class'] == 'H5T_STRING':
                    var[i] = fn_str_to_utf(var[i])
        #Convert HDF5 object refs to HDF5 object names for use in Python 
        #dictionaries
        if spec.loc[i, 'Class'] == 'H5T_STD_REF_OBJ':
            if type(var[i]) is np.ndarray:
                var[i][:] = [MFMC[j].name for j in var[i]]
            else:
                var[i] = MFMC[var[i]].name

        if spec.loc[i, 'M or O'] == 'M' and i not in var.keys():
            #Occurs if neither attribute or dataset found
            print('Error: mandatory field', i, 'missing')
            success = False
    if success:
        return var
    else:
        return []