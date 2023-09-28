# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:47:21 2023

@author: mepdw
"""
import os
import h5py as h5

from ..utils import *
from ..spec import default_spec, fn_get_relevant_part_of_spec
from ..strs import h5_keys
from ..strs import eng_keys

def fn_open_file_for_reading(fname, root_path = '/'):
    if os.path.isfile(fname):
        MFMC = h5.File(fname, 'r')
    else:
        print('Error: file not found')
        MFMC = []
    return MFMC

def fn_read_probe(MFMC, group, spec = default_spec):
    probe = fn_read_structure(MFMC, group, fn_get_relevant_part_of_spec(spec, h5_keys.PROBE))
    if not probe:
        return []
    if h5_keys.TYPE not in probe.keys() or probe[h5_keys.TYPE] != h5_keys.PROBE:
        print('Error: not a probe')
        return []
    else:
        return probe
    
def fn_read_law(MFMC, group, spec = default_spec):
    law = fn_read_structure(MFMC, group, fn_get_relevant_part_of_spec(spec, h5_keys.LAW))
    if not law:
        return []
    if h5_keys.TYPE not in law.keys() or law[h5_keys.TYPE] != h5_keys.LAW:
        print('Error: not a law')
        return []
    else:
        return law
    
def fn_read_sequence_data(MFMC, group, spec = default_spec):
    seq = fn_read_structure(MFMC, group, fn_get_relevant_part_of_spec(spec, h5_keys.SEQUENCE), skip_fields = [h5_keys.MFMC_DATA, h5_keys.MFMC_DATA_IM])
    if not seq:
        return []
    if h5_keys.TYPE not in seq.keys() or seq[h5_keys.TYPE] != h5_keys.SEQUENCE:
        print('Error: not a sequence')
        return []
    else:
        return seq

def fn_read_frame(MFMC, group, i = -1):
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

def fn_read_structure(MFMC, group, spec, skip_fields = []):
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
        if spec.loc[i, 'M or O'] == 'M' and i not in var.keys():
            #Occurs if neither attribute or dataset found
            print('Error: mandatory field', i, 'missing')
            success = False
    if success:
        return var
    else:
        return []