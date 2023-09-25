# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:47:21 2023

@author: mepdw
"""
import h5py as h5

from ..utils import *
from ..spec import *
from ..strs.mfmc_fieldnames import *
from ..strs.string_table import *


def fn_open_file_for_reading(fname, root_path = '/'):
    MFMC = h5.File(fname, 'r')
    return MFMC

def fn_read_probe(MFMC, group, spec):
    probe = fn_read_structure(MFMC, group, fn_get_relevant_part_of_spec(spec, H5_PROBE))
    if H5_TYPE not in probe.keys() or probe[H5_TYPE] != H5_PROBE:
        print('Error: not a probe')
    return probe

def fn_read_structure(MFMC, group, spec):
    var = {}
    for i in spec.index:
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
    
    return var