# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 17:55:49 2023

@author: mepdw
"""

import pandas as pd
import numpy as np
from .. import utils
from ..strs import h5_keys
from ..strs import eng_keys


SPEC_TYPE_PREFIX = {
    h5_keys.SEQUENCE: '{sequence}' + h5_keys.PATH_SEPARATOR, 
    h5_keys.PROBE: '{probe}' + h5_keys.PATH_SEPARATOR, 
    h5_keys.LAW: '{law}' + h5_keys.PATH_SEPARATOR}

SPEC_TYPE_COUNTER = {
    h5_keys.SEQUENCE: '<m>', 
    h5_keys.PROBE: '<p>', 
    h5_keys.LAW: '<k>'}

def fn_load_specification(spec_fname):
    spec = pd.read_excel(spec_fname, index_col = 'Name')
    spec.replace(np.nan, None, inplace = True)
    return spec

def fn_get_relevant_part_of_spec(spec, MFMC_type):
    prefix = SPEC_TYPE_PREFIX[MFMC_type]
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

try:
    default_spec = fn_load_specification(utils.default_spec_fname)
except:
    default_spec = None

expandable_dims = ['N_M', 'N_F<m>', 'N_B<m>']