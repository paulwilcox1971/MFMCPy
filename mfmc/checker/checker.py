# -*- coding: utf-8 -*-
"""
Created on Wed May 10 22:23:04 2023

@author: mepdw
"""

import numpy as np
import pandas as pd
from ..utils import utils

SEPARATOR_STR = '; '

SPEC_TYPE_PREFIX = {
    utils.SEQUENCE_TYPE: '{sequence}' + utils.H5_PATH_SEPARATOR, 
    utils.PROBE_TYPE: '{probe}' + utils.H5_PATH_SEPARATOR, 
    utils.LAW_TYPE: '{law}' + utils.H5_PATH_SEPARATOR}

SPEC_TYPE_COUNTER = {
    utils.SEQUENCE_TYPE: '<m>', 
    utils.PROBE_TYPE: '<p>', 
    utils.LAW_TYPE: '<k>'}

NUMPY_EQUIV_DTYPE = {
    'H5T_STRING': np.string_,
    'H5T_FLOAT': np.floating,
    'H5T_INTEGER': np.integer,
    'H5T_STD_REF_OBJ': np.dtype('O')}


def fn_load_specification(spec_fname):
    SPEC = pd.read_excel(spec_fname, index_col = 'Name')
    SPEC.replace(np.nan, None, inplace = True)
    return SPEC

def fn_check_sequence(MFMC, SPEC, sequence_name):
    check_log = []
    size_table = {}
    err_list = []
    
    #Check it is a sequence first
    if 'TYPE' not in list(sequence_name.attrs) or utils.fn_str_to_utf(sequence_name.attrs["TYPE"]) != utils.SEQUENCE_TYPE:
        err_list.append('Object is not MFMC sequence')
        return (check_log, size_table, err_list)
    
    #First check sequence group itself
    sequence_specification = fn_get_relevant_part_of_spec(SPEC, utils.SEQUENCE_TYPE)
    #return (check_log, size_table, err_list)
    (check_log, size_table, err_list, objects_referenced_by_sequence) = fn_check_mfmc_group_against_specification(MFMC, SPEC, sequence_name, sequence_specification, check_log, size_table, err_list)

    #Second, check all probe groups in sequence's probe list
    probe_list_from_sequence = objects_referenced_by_sequence['PROBE_LIST']
    probe_spec = fn_get_relevant_part_of_spec(SPEC, utils.PROBE_TYPE)
    #print(probe_list_from_sequence)
    #print(size_table)
    for probe in probe_list_from_sequence:
        (check_log, size_table, err_list, objects_referenced) = fn_check_mfmc_group_against_specification(MFMC, SPEC, MFMC[probe], probe_spec, check_log, size_table, err_list)

    #Third, check all law groups in sequence's transmit and receive laws, and 
    #log all the probes referenced by laws
    law_list_from_sequence = list(set(objects_referenced_by_sequence['TRANSMIT_LAW'] + objects_referenced_by_sequence['RECEIVE_LAW']))
    probes_referenced_by_laws = []
    law_spec = fn_get_relevant_part_of_spec(SPEC, utils.LAW_TYPE)
    for law in law_list_from_sequence:
        (check_log, size_table, err_list, objects_referenced) = fn_check_mfmc_group_against_specification(MFMC, SPEC, MFMC[law], law_spec, check_log, size_table, err_list)
        probes_referenced_by_laws += objects_referenced['PROBE']
    probes_referenced_by_laws = list(set(probes_referenced_by_laws))
    
    #Check all probes referenced by laws are in sequence's probe list
    #probe_name_list = [MFMC[p].name for p in probe_list]
    #print(size_table)
    for r in probes_referenced_by_laws:
        if MFMC[r].name not in probe_list_from_sequence:# probe_name_list:
            err_list.append(err_list + ': Probe ' + MFMC[r].name + ' not in probe list')
    #return (check_log, size_table, err_list)
    #Final thing - check element indexing in laws is range
    for law in law_list_from_sequence:
        probes = [utils.fn_str_to_utf(MFMC[i].name) for i in MFMC[law]['PROBE']]
        #print(size_table)
        #print(probes)
        max_vals = [size_table['N_E<' + p + '>'] for p in probes]
        vals = np.atleast_1d(MFMC[law]['ELEMENT'])
        for (p, v, m, i) in zip(probes, vals, max_vals, range(len(probes))):
            if v < 1 or v > m:
                err_list.append('ELEMENT[' + str(i + 1) + '] in law ' + utils.fn_name_from_path(MFMC[law].name) + ': refers to elements outside range of probe ' + utils.fn_name_from_path(p))
    
    
    return (check_log, size_table, err_list)


def fn_get_relevant_part_of_spec(SPEC, MFMC_type):
    prefix = SPEC_TYPE_PREFIX[MFMC_type]
    spec = SPEC.loc[SPEC.index[:].str.startswith(prefix),:]
    spec.index = spec.index.str.replace(prefix, '', regex = False)
    return spec
    

def fn_check_mfmc_group_against_specification(MFMC, SPEC, mfmc_group, spec, check_log = [], size_table = {}, err_list = []):
    #This function works through spec and checks the data in mfmc_group against 
    #it for (0) its presence if mandatory, (1) its type, (2) its shape, and (3)
    #if HDF5 object reference that it points to correct type of mfmc_group
    objects_referenced = {}
    if 'TYPE' not in list(mfmc_group.attrs):
        err_list.append(mfmc_group.name + ': missing TYPE attribute')
        return (check_log, size_table, err_list, objects_referenced)
    if utils.fn_str_to_utf(mfmc_group.attrs["TYPE"]) not in SPEC_TYPE_PREFIX.keys():    
        err_list.append(mfmc_group.name + ': TYPE attribute not a recognised MFMC type')
        return (check_log, size_table, err_list, objects_referenced)
    
    
    dsets_in_obj = utils.fn_get_dataset_keys(mfmc_group)
    attrs_in_obj = list(mfmc_group.attrs)
    for name in list(spec.index):
        base_string = mfmc_group.name + utils.H5_PATH_SEPARATOR + name + ': '
        check_string = base_string
        
        #see if specified item is either a dataset of attribute in mfmc_group
        if spec.loc[name, 'D or A'] == 'D':
            #check the datasets first
            if name in dsets_in_obj:
                item = mfmc_group[name]
            else:
                item = None    
        else:
            #then try the attributes
            if name in attrs_in_obj:
                item = mfmc_group.attrs[name]
            else:
                item = None
        
        if isinstance(item, bytes):
            item = utils.fn_str_to_utf(item)
        
        #Check the object matches specification
        
        #0. If mandatory in spec, check datafield appears in group
        
        if item is None:
            #if item = None it is not part of spec and ignored (e.g. user-defined things)
            if spec.loc[name, 'M or O'] == 'M':
                err_str = base_string + 'Mandatory item missing'
                err_list.append(err_str)
                check_log.append(err_str)
            continue
        
        #1. Check type of datafield
        spec_h5_dtype = spec.loc[name, 'Class']
        spec_numpy_types = [NUMPY_EQUIV_DTYPE[x] for x in spec_h5_dtype.replace(' ', '').split('/')]
        if hasattr(item, 'dtype'):
            item_dtype = item.dtype
        elif isinstance(item, str):
            item_dtype = np.string_
        else:
            item_dtype = None    
        if not any([np.issubdtype(item_dtype, q) for q in spec_numpy_types]):
            err_str = 'Class should be ' + spec_h5_dtype
            err_list.append(base_string + err_str)
            check_string += err_str + SEPARATOR_STR
        else:
            check_string += 'Class OK' + SEPARATOR_STR
                
        #2. Check dimensions of datafield
        if hasattr(item, 'shape'):
            shape_tuple = tuple(reversed(item.shape))
            if not len(shape_tuple):
                #for scalars
                shape_tuple = (1, )
            shape_str = spec.loc[name, 'Size or content']
            if utils.fn_str_to_utf(mfmc_group.attrs['TYPE']) in SPEC_TYPE_COUNTER.keys():
                shape_str = shape_str.replace(SPEC_TYPE_COUNTER[utils.fn_str_to_utf(mfmc_group.attrs['TYPE'])], '<' + mfmc_group.name + '>')
            
            (size_table, err_str) = fn_compare_shapes_with_spec_str(shape_tuple, shape_str, size_table)
            if err_str:
                check_string += err_str + SEPARATOR_STR
                err_list.append(base_string + err_str)
            else:
                check_string += 'Size OK' + SEPARATOR_STR

        #3. In case for arrays of HDF5 refs - check they are refs to right thing and make a list of them
        if item_dtype == np.dtype('O'):
            #get list of unique ones to check
            unique_items = utils.fn_unique_h5_ref_list(MFMC, item)
            if any(['TYPE' not in list(MFMC[i].attrs) or utils.fn_str_to_utf(MFMC[i].attrs['TYPE']) not in spec.loc[name, 'Reference to'] for i in unique_items]):
                err_str = 'Objects referenced should be type ' + spec.loc[name, 'Reference to']
                err_list.append(base_string + err_str)
                check_string += err_str + SEPARATOR_STR
                objects_referenced[name] = []
            else:
                check_string += 'Referenced object types OK' + SEPARATOR_STR
                objects_referenced[name] = unique_items
        
        #Add the chec string to the log
        check_log.append(check_string)
    return (check_log, size_table, err_list, objects_referenced)    
                
def fn_compare_shapes_with_spec_str(shape_tuple, shape_str, size_table):
    #print(shape_tuple, shape_str, size_table)
    shape_str = shape_str.replace(' ', '')
    shape_str = shape_str.replace('[', '')
    shape_str = shape_str.replace(']', '')
    shape_str = shape_str.split(',')
    if len(shape_str) != len(shape_tuple):
        err = 'number of dimension mismatch ('+ str(len(shape_tuple)) + ' should be ' + str(len(shape_str)) + ')'
        return (size_table, err)
    for (ss, s, i) in zip(shape_str, shape_tuple, range(len(shape_str))):
        if ss.isnumeric():
            if int(ss) != s:
                err = 'dimension inconsistency (dim ' + str(i + 1) + ' should be ' + str(ss) + ')'
                return (size_table, err)
        else:
            if ss in size_table.keys():
                if size_table[ss] != s:
                    err = 'dimension inconsistency (dim ' + str(i + 1) + ' should be ' + ss + ')'
                    return (size_table, err)
            else:
                size_table[ss] = s
    return (size_table, None)

