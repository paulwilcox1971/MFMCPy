# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:30:12 2023

@author: mepdw
"""

#import MFMC_Py as mfmc
import numpy as np
import re
from inspect import isfunction

import sys
sys.path.append('..') #So mfmc can be found in parent directory

from ..strs import h5_keys
from ..strs import eng_keys
from .probe_type_testers import fn_test_for_1D_linear_probe, fn_test_for_2D_matrix_probe, fn_test_for_2D_other_probe


PROBE_TEST_FUNCTION_PREFIX = 'fn_test_for'


#Following hardcoded- would be better to search for them using abve prefix
#probe_test_functions = [m.read.fn_test_for_1D_linear_probe, m.read.fn_test_for_2D_matrix_probe, m.read.fn_test_for_2D_other_probe]
probe_test_functions = [fn_test_for_1D_linear_probe, fn_test_for_2D_matrix_probe, fn_test_for_2D_other_probe]



def fn_analyse_probe(probe, relative_tolerance = 0.000001):
    """Try all available probe test functions on MFMC probe data and return
    details from one that gives best match
    
    :param probe: MFMC probe data read from MFMC file.
    :type probe: dictionary
    :param relative_tolerance: Relative tolerance for matches expressed as a 
        decimal (e.g. 0.01 = 1% tolerance).
    :type relative_tolerance: float
    """
    best_match = 0
    best_match_details = None
    for t in probe_test_functions:
        details = t(probe)
        # fn_pretty_print_dictionary(details)
        if details['Match (%)'] > best_match:
            best_match = details['Match (%)']
            best_match_details = details
    
    
    # match = 0
    # details = {}
    # #get a list of the probe tester functions in file
    # names = dir(m.read.probe_type_testers)
    # for n in names:
    #     fn_test_function = getattr(m, n)
    #     if isfunction(fn_test_function) and n.startswith(PROBE_TEST_FUNCTION_PREFIX):
    #         d = fn_test_function(probe, relative_tolerance)
    #         if d[m.MATCH_KEY] > match:
    #             match = d[m.MATCH_KEY]
    #             details = d
           
    return best_match_details

UNITS = {'m': ['mm', 1e3],
         'rads': ['degs', 180 / np.pi],
         'Hz': ['MHz', 1e-6]}

#Following should go in utilities
def fn_pretty_print_dictionary(d, decimal_places = 3, units = UNITS, print_to_string = False):
    """Print contents of dictionary nicely.
    
    :param d: Dictionary to print
    :type d: dictionary
    :param decimal_places: Number of decimal places to use for output.
    :type decimal_places: int
    :return: probe details.
    :rtype: dictionary
    """
    output = ''
    
    k_max = np.max([len(k) for k in list(d.keys())])
    for k in d.keys():
        v = d[k]
        units_to_print = ''
        #For numerical data
        if np.asarray(v).dtype.kind in set('buifc'): #force to be numpy array if numeric
            v = np.atleast_1d(v)
            #look for units '(*)' in key and take appropriate action
            u = re.search('\((.*?)\)', k)
            if u:
                u = u.group(1)
                if u in units.keys():
                    v_print = v * units[u][1]
                    units_to_print = units[u][0]
                else:
                    v_print = v
                    units_to_print = u
                k = k[:len(k) - len(u) - 3]
            else:
                v_print = v
            if np.asarray(v_print).dtype.kind in set('i'):
                fmt_str = '%i'
            else:
                fmt_str = ('%.' + str(decimal_places) + 'f')
            if len(v_print) > 1:
                s = '(' + ', '.join([fmt_str % vv for vv in v_print]) + ') ' + units_to_print
            else:
                s = fmt_str % v_print +' ' + units_to_print
        else:
            s = str(v)
        output += ' ' * (k_max - len(k)) + k + ': ' + s + '\n'
        
    if print_to_string:
        return output
    else:
        print(output)
            
            
# def fn_print_to_string(*args, **kwargs):
#     output = io.StringIO()
#     print(*args, file = output, **kwargs)
#     contents = output.getvalue()
#     output.close()
#     return contents
