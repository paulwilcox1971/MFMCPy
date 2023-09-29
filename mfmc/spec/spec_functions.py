# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 17:55:49 2023

@author: mepdw
"""

import pandas as pd
import numpy as np

#Only import specific functions used here
from ..utils.defaults import default_spec_fname
from ..strs import h5_keys, eng_keys

#Following functions are exported when from spec_functions import * is used:
__all__ = ['fn_load_specification',
           'fn_get_relevant_part_of_spec',
           'fn_parse_shape_string_in_spec',
           'default_spec',
           'spec_type_prefix',
           'spec_type_counter']

spec_type_prefix = {
    h5_keys.SEQUENCE: '{sequence}' + h5_keys.PATH_SEPARATOR, 
    h5_keys.PROBE: '{probe}' + h5_keys.PATH_SEPARATOR, 
    h5_keys.LAW: '{law}' + h5_keys.PATH_SEPARATOR}

spec_type_counter = {
    h5_keys.SEQUENCE: '<m>', 
    h5_keys.PROBE: '<p>', 
    h5_keys.LAW: '<k>'}

def fn_load_specification(spec_fname):
    spec = pd.read_excel(spec_fname, index_col = 'Name')
    spec.replace(np.nan, None, inplace = True)
    return spec

def fn_get_relevant_part_of_spec(spec, MFMC_type):
    prefix = spec_type_prefix[MFMC_type]
    subspec = spec.loc[spec.index[:].str.startswith(prefix),:]
    subspec.index = subspec.index.str.replace(prefix, '', regex = False)
    return subspec

def fn_parse_shape_string_in_spec(shape_str):
    #Parse and reverse shape_str
    shape_str = shape_str.replace(' ', '')
    shape_str = shape_str.replace('[', '')
    shape_str = shape_str.replace(']', '')
    shape_str = shape_str.split(',')
    #It needs to be reverse because spec gives shape in col-major order but 
    #shapes in Numpy are in row-major order
    shape_str = tuple(reversed(shape_str)) 
    return shape_str

default_spec = fn_load_specification(default_spec_fname)