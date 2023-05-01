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
TYPE_TO_PREFIX = {'SEQUENCE': '/{sequence}/', 'PROBE': '/{probe}/', 'LAW': '/{law}/'}

@dataclass
class cl_loc_details:
    ref: str
    name: str
    location: str 

def fn_check_sequence(MFMC, h5_obj, size_table = {}, err_str = ''):
    #Check it is a sequence first
    if 'TYPE' not in list(h5_obj.attrs) or h5_obj.attrs["TYPE"] != "SEQUENCE":
        err_str = 'Object is not MFMC sequence'
        return (size_table, err_str)
    #First check all entries in sequence
    (size_table, err_str) = fn_check_obj(MFMC, h5_obj, size_table, err_str)
    
    #Next check all probes in probe list
    #TODO
    #Finally check all focal laws - all probes referenced must be in probe list
    #TODO
    
    
    return (size_table, err_str)

def fn_check_obj(MFMC, h5_obj, size_table = {}, err_str = ''):
    if 'TYPE' not in list(h5_obj.attrs) or h5_obj.attrs["TYPE"] not in TYPE_TO_PREFIX.keys():
        err_str += 'Referenced object missing MFMC TYPE attribute'
        return (False, size_table, err_str)
    prefix = TYPE_TO_PREFIX[h5_obj.attrs["TYPE"]]
    dsets_in_obj = fn_get_dataset_keys(h5_obj)
    #Extract relevant part of spec
    spec = SPEC.loc[SPEC.index[:].str.startswith(prefix),:]
    spec.index = spec.index.str.replace(prefix, '', regex = False)
    for name in list(spec.index):
        if spec.loc[name, 'D or A'] == 'D':
            #check the datasets first
            if name in dsets_in_obj:
                item = h5_obj[name]
            else:
                item = None    
        else:
            if name in list(h5_obj.attrs):
                item = h5_obj.attrs[name]
            else:
                item = None
        if item is not(None):
            #check type
            #Case for arrays of HDF5 refs - check they are refs to right thing
            if hasattr(item, 'dtype') and item.dtype == np.dtype('O'):
                #print('object ref:', name)
                #get list of unique ones to check
                unique_items = list(set([h5.h5r.get_name(i, MFMC.id) for i in item]))
                for i in unique_items:
                    if 'TYPE' not in list(MFMC[i].attrs) or MFMC[i].attrs['TYPE'] not in spec.loc[name, 'Reference to']:
                        err_str += 'Objects referenced in ' + name + ' should be type ' + spec.loc[name, 'Reference to']
            #check dimensions
            if hasattr(item, 'shape'):
                shape_tuple = tuple(reversed(item.shape))
                shape_str = spec.loc[name, 'Size or content']
                (size_table, e) = fn_compare_shapes_with_spec_str(shape_tuple, shape_str, size_table)
                if e:
                    err_str += name + ': ' + e + '\n'
        else:
            if spec.loc[name, 'M or O'] == 'M':
                err_str += 'Mandatory item ' + name + ' missing\n'
    return (size_table, err_str)    
                
def fn_compare_shapes_with_spec_str(shape_tuple, shape_str, size_table):
    shape_str = shape_str.replace('[', '')
    shape_str = shape_str.replace(']', '')
    shape_str = shape_str.split(',')
    if len(shape_str) != len(shape_tuple):
        err_str = 'number of dimension mismatch'
        return (size_table, err_str)
    for (ss, s, i) in zip(shape_str, shape_tuple, range(len(shape_str))):
        if ss.isnumeric():
            if int(ss) != s:
                err_str = 'dimension inconsistency (dim ' + str(i + 1) + ' should be ' + int(ss) + ')'
                return (size_table, err_str)
        else:
            if ss in size_table.keys():
                if size_table[ss] != s:
                    err_str = 'dimension inconsistency (dim ' + str(i + 1) + ' should be ' + ss + ')'
                    return (False, size_table, err_str)
            else:
                size_table[ss] = s
    return (size_table, '')

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
    sequence_list = fn_hdf5_group_refs_by_type(MFMC, 'SEQUENCE')
    return sequence_list

def fn_get_probe_list(MFMC):
    probe_list = fn_hdf5_group_refs_by_type(MFMC, 'PROBE')
    return probe_list
      
def fn_get_law_list(MFMC):
    law_list = fn_hdf5_group_refs_by_type(MFMC, 'LAW')
    return law_list
       
def fn_hdf5_group_refs_by_type(MFMC, TYPE):
    names = []
    def fn_dummy(name):
        if 'TYPE' in MFMC[name].attrs:
            if TYPE == MFMC[name].attrs['TYPE']:
                names.append(cl_loc_details(ref = MFMC[name].ref, name = name.split('/')[-1], location = MFMC[name].parent.name))
        return None
    MFMC.visit(fn_dummy)
    return names

# def fn_MFMC_check_file(MFMC):
#     #work through all sequences in file
#     sequence_list = fn_get_sequence_list(MFMC)
#     for s in sequence_list:
#         #check the attributes are OK
#         for a in SEQUENCE_ATTRS:
#             if a.name in MFMC[s.ref].attrs:
#                 print('Attribute', a.name, 'found in sequence', s.name)
#                 a2 = MFMC[s.ref].attrs[a.name]
#                 if fn_compare_shapes(a2.shape, a.shape):
#                     pass
#                     #print('Attribute', a.name, 'Shape match (found', list(a2.shape), '; should be', a.shape,')')    
#                 else:
#                     print('Attribute', a.name, 'Shape mismatch (found', list(a2.shape), '; should be', a.shape,')')    
#                 #should check type too
#             else:
#                 if a.mandatory:
#                     print('Attribute', a.name, 'missing in sequence', s.name)
#         #check the datasets are OK
#         dsets = fn_get_dataset_keys(MFMC[s.ref])
#         for d in SEQUENCE_DSETS:
#             if d.name in dsets:
#                 print('Dataset', d.name, 'found in sequence', s.name)
#                 d2 = MFMC[s.ref][d.name]
#                 if fn_compare_shapes(d2.shape, d.shape):
#                     pass
#                     #print('Attribute', a.name, 'Shape match (found', list(a2.shape), '; should be', a.shape,')')    
#                 else:
#                     print('Dataset', d.name, 'Shape mismatch (found', list(d2.shape), '; should be', d.shape,')')    
#                 #should check type too
#             else:
#                 if d.mandatory:
#                     print('Dataset', d.name, 'missing in sequence', s.name)
    
#     return            
        