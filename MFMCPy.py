# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:49:17 2023

@author: mepdw
"""

import h5py as h5
import numpy as np

def fn_MFMC_open_file(fname, root_path = '/'):
    MFMC = h5.File(fname, 'r')
    return MFMC

def fn_find_SEQ(name):
    if 'LAW' in name:
         print(name)
    # else:
    return (None, name)
    #return fn_find_by_type(name, 'SEQ')

def fn_find_by_type(name, TYPE):
    if 'TYPE' in name.attrs:
        if name.attrs['TYPE'] is TYPE:
            return (name)
    return None

def fn_print_attrs(name, obj):
    print(name)
    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))
        
        
def fn_find_groups(MFMC, TYPE):
    names = []
    def fn_dummy(name):
        if 'TYPE' in MFMC[name].attrs:
            if TYPE == MFMC[name].attrs['TYPE']:
                names.append(name)
        return None
    MFMC.visit(fn_dummy)
    return names