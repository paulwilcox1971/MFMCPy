# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:30:12 2023

@author: mepdw
"""

import MFMC_Py as mfmc

import MFMC_probe_type_testers

from inspect import getmembers, isfunction

PROBE_TEST_FUNCTION_PREFIX = 'fn_test_for'

def fn_analyse_probe(probe):
    details = {'type': 'Unknown'}
    match = 0
    #get a list of the probe tester functions in file
    names = dir(MFMC_probe_type_testers)
    for n in names:
        fn_test_function = getattr(MFMC_probe_type_testers, n)
        if isfunction(fn_test_function) and n.startswith(PROBE_TEST_FUNCTION_PREFIX):
            (d, m) = fn_test_function(probe)
            if m > match:
                match = m
                details = d
    
    
    
    return (match, details)