# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 17:55:49 2023

@author: mepdw
"""

import pandas as pd
import numpy as np
from .. import utils

SPEC_TYPE_PREFIX = {
    utils.SEQUENCE_TYPE: '{sequence}' + utils.H5_PATH_SEPARATOR, 
    utils.PROBE_TYPE: '{probe}' + utils.H5_PATH_SEPARATOR, 
    utils.LAW_TYPE: '{law}' + utils.H5_PATH_SEPARATOR}

SPEC_TYPE_COUNTER = {
    utils.SEQUENCE_TYPE: '<m>', 
    utils.PROBE_TYPE: '<p>', 
    utils.LAW_TYPE: '<k>'}

def fn_load_specification(spec_fname):
    spec = pd.read_excel(spec_fname, index_col = 'Name')
    spec.replace(np.nan, None, inplace = True)
    return spec

def fn_get_relevant_part_of_spec(spec, MFMC_type):
    prefix = SPEC_TYPE_PREFIX[MFMC_type]
    subspec = spec.loc[spec.index[:].str.startswith(prefix),:]
    subspec.index = subspec.index.str.replace(prefix, '', regex = False)
    return subspec

SPEC = fn_load_specification(utils.default_spec_fname)