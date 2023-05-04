# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:49:17 2023

@author: mepdw
"""

import h5py as h5
import numpy as np
import pandas as pd

from dataclasses import dataclass

spec_fname = 'MFMC Specification 2.0.0.xlsx'

SPEC = pd.read_excel(spec_fname, index_col = 'Name')
SPEC.replace(np.nan, None, inplace = True)

SEQUENCE_TYPE = 'SEQUENCE'
PROBE_TYPE = 'PROBE'
LAW_TYPE = 'LAW'

TYPE_PREFIX = {
    SEQUENCE_TYPE: '{sequence}/', 
    PROBE_TYPE: '{probe}/', 
    LAW_TYPE: '{law}/'}

TYPE_COUNTER = {
    SEQUENCE_TYPE: '<m>', 
    PROBE_TYPE: '<p>', 
    LAW_TYPE: '<k>'}

NUMPY_EQUIV_DTYPE = {
    'H5T_STRING': np.string_,
    'H5T_FLOAT': np.floating,
    'H5T_INTEGER': np.integer,
    'H5T_STD_REF_OBJ': np.dtype('O')}



@dataclass
class cl_loc_details:
    ref: str
    name: str
    location: str 

def fn_check_sequence(MFMC, h5_obj):
    size_table = {}
    err_list = []
    #Check it is a sequence first
    if 'TYPE' not in list(h5_obj.attrs) or h5_obj.attrs["TYPE"] != SEQUENCE_TYPE:
        err_list.append('Object is not MFMC sequence')
        return (size_table, err_list)
    #First check sequence has necessary attributes and datasets with consistent sizes
    (size_table, err_list, law_list, probe_list) = fn_check_obj(MFMC, h5_obj, size_table, err_list)
    law_list = fn_unique_h5_ref_list(MFMC, law_list)
    probe_list = fn_unique_h5_ref_list(MFMC, probe_list)
    
    #Check all unique probes in probe list have necessary attributes and datasets with consistent sizes
    for probe in probe_list:
        (size_table, err_list, _, _) = fn_check_obj(MFMC, MFMC[probe], size_table, err_list)
    
    #Check all unique focal laws referenced have necessary attributes and datasets with consistent sizes and
    #get a list of unique probes referenced by laws
    probes_referenced_by_laws = []
    for law in law_list:
        (size_table, err_list, _, tmp) = fn_check_obj(MFMC, MFMC[law], size_table, err_list)
        probes_referenced_by_laws.extend(tmp)
    
    probes_referenced_by_laws = fn_unique_h5_ref_list(MFMC, probes_referenced_by_laws)
    
    #Check all probes referenced by laws are in sequence probe list
    probe_name_list = [MFMC[p].name for p in probe_list]
    for r in probes_referenced_by_laws:
        if MFMC[r].name not in probe_name_list:
            err_list.append(err_list + ': Probe ' + MFMC[r].name + ' not in probe list')
  
    #Final thing - check element indexing in laws is range
    for law in law_list:
        probes = [MFMC[i].name for i in MFMC[law]['PROBE']]
        max_vals = [size_table['N_E<' + p + '>'] for p in probes]
        vals = np.atleast_1d(MFMC[law]['ELEMENT'])
        for (p, v, m, i) in zip(probes, vals, max_vals, range(len(probes))):
            if v < 1 or v > m:
                err_list.append('ELEMENT[' + str(i + 1) + '] in law ' + fn_name_from_path(MFMC[law].name) + ': refers to elements outside range of probe ' + fn_name_from_path(p))
    
    
    return (size_table, err_list, law_list, probe_list, probes_referenced_by_laws)

def fn_unique_h5_ref_list(MFMC, ref_list):
    return [MFMC[r].ref for r in list(set([MFMC[i].name for i in ref_list]))]

def fn_name_from_path(path):
    return path.split('/')[-1]
    

def fn_check_obj(MFMC, h5_obj, size_table = {}, err_list = []):
    if 'TYPE' not in list(h5_obj.attrs):
        err_list.append(h5_obj.name + ': missing TYPE attribute')
        return (False, size_table, err_list)
    if h5_obj.attrs["TYPE"] not in TYPE_PREFIX.keys():    
        err_list.append(h5_obj.name + ': TYPE attribute not a recognised MFMC type')
        return (False, size_table, err_list)
    #strip out prefix in spec spreadsheet (would be neater to do this first in seperate function)
    prefix = TYPE_PREFIX[h5_obj.attrs['TYPE']]
    spec = SPEC.loc[SPEC.index[:].str.startswith(prefix),:]
    spec.index = spec.index.str.replace(prefix, '', regex = False)
    
    dsets_in_obj = fn_get_dataset_keys(h5_obj)
    attrs_in_obj = list(h5_obj.attrs)
    law_list = []
    probe_list = []
    for name in list(spec.index):
        #see if specified item is either a dataset of attribute in obj
        if spec.loc[name, 'D or A'] == 'D':
            #check the datasets first
            if name in dsets_in_obj:
                item = h5_obj[name]
            else:
                item = None    
        else:
            #then try the attributes
            if name in attrs_in_obj:
                item = h5_obj.attrs[name]
            else:
                item = None
        
        if item is None:
            #if item = None it is not part of spec and ignored (e.g. user-defined things)
            if spec.loc[name, 'M or O'] == 'M':
                err_list.append(name + ' in ' + h5_obj.name + ': Mandatory item missing\n')
            continue
        
        #Check the object matches specification
        
        #1. Check type of object
        spec_h5_dtype = spec.loc[name, 'Class']
        spec_numpy_types = [NUMPY_EQUIV_DTYPE[x] for x in spec_h5_dtype.replace(' ', '').split('/')]
        if hasattr(item, 'dtype'):
            item_dtype = item.dtype
        elif isinstance(item, str):
            item_dtype = np.string_
        else:
            item_dtype = None    
        if not any([np.issubdtype(item_dtype, q) for q in spec_numpy_types]):
            err_list.append(name + ' in ' + h5_obj.name + ': class should be ' + spec_h5_dtype)
                
        #2. In case for arrays of HDF5 refs - check they are refs to right thing
        if item_dtype == np.dtype('O'):
            #get list of unique ones to check
            unique_items = list(set([MFMC[i].name for i in item]))
            for i in unique_items:
                if 'TYPE' not in list(MFMC[i].attrs) or MFMC[i].attrs['TYPE'] not in spec.loc[name, 'Reference to']:
                    err_list.append(name + ' in ' + h5_obj.name + ': Objects referenced should be type ' + spec.loc[name, 'Reference to'])
                if MFMC[i].attrs['TYPE'] == LAW_TYPE:
                    law_list.append(MFMC[i].ref)
                if MFMC[i].attrs['TYPE'] == PROBE_TYPE:
                    probe_list.append(MFMC[i].ref)

        #3. Check dimensions of object
        if hasattr(item, 'shape'):
            shape_tuple = tuple(reversed(item.shape))
            if not len(shape_tuple):
                #for scalars
                shape_tuple = (1, )
            shape_str = spec.loc[name, 'Size or content']
            if h5_obj.attrs['TYPE'] in TYPE_COUNTER.keys():
                shape_str = shape_str.replace(TYPE_COUNTER[h5_obj.attrs['TYPE']], '<' + h5_obj.name + '>')
            (size_table, err) = fn_compare_shapes_with_spec_str(shape_tuple, shape_str, size_table)
            if err:
                err_list.append(name + ' in ' + h5_obj.name + ': ' + err)
    
    #Special size check if sequence
    if h5_obj.attrs["TYPE"] == SEQUENCE_TYPE:
        #loop needs to be repeated here as can't guarantee order entries are processed in first pass
        for name in list(spec.index):
            if spec.loc[name, 'Maximum']:
                max_val_str = spec.loc[name, 'Maximum']
                max_val_str = max_val_str.replace(TYPE_COUNTER[SEQUENCE_TYPE], '<' + h5_obj.name + '>')
                max_allowed_val = size_table[max_val_str]
                print()
                max_val = np.max(h5_obj[name])
                min_val = np.min(h5_obj[name])
                if min_val < 1 or max_val > max_allowed_val:
                    err_list.append(name + ' in ' + h5_obj.name + ': contains indices outside range [1, ' + str(max_allowed_val) + ']')

    return (size_table, err_list, law_list, probe_list)    
                
def fn_compare_shapes_with_spec_str(shape_tuple, shape_str, size_table):
    shape_str = shape_str.replace(' ', '')
    shape_str = shape_str.replace('[', '')
    shape_str = shape_str.replace(']', '')
    shape_str = shape_str.split(',')
    if len(shape_str) != len(shape_tuple):
        err = 'number of dimension mismatch ('+ str(len(shape_str)) + ' should be ' + str(len(shape_tuple)) + ')'
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
                    return (False, size_table, err)
            else:
                size_table[ss] = s
    return (size_table, None)

def fn_get_dataset_keys(group):
    keys = []
    for k in group.keys(): 
        if isinstance(group[k], h5.Dataset):
            keys.append(k)
    return keys

def fn_open_file(fname, root_path = '/'):
    MFMC = h5.File(fname, 'r')
    return MFMC

def fn_get_sequence_list(MFMC):
    sequence_list = fn_hdf5_group_refs_by_type(MFMC, SEQUENCE_TYPE)
    return sequence_list

def fn_get_probe_list(MFMC):
    probe_list = fn_hdf5_group_refs_by_type(MFMC, PROBE_TYPE)
    return probe_list
      
def fn_get_law_list(MFMC):
    law_list = fn_hdf5_group_refs_by_type(MFMC, LAW_TYPE)
    return law_list
       
def fn_hdf5_group_refs_by_type(MFMC, TYPE):
    names = []
    def fn_dummy(name):
        if 'TYPE' in MFMC[name].attrs:
            if TYPE == MFMC[name].attrs['TYPE']:
                names.append(cl_loc_details(ref = MFMC[name].ref, name = fn_name_from_path(name), location = MFMC[name].parent.name))
        return None
    MFMC.visit(fn_dummy)
    return names