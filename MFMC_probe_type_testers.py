# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:31:59 2023

@author: mepdw
"""

#The function fn_analyse_probe will test specified probe using all functions in
#this file and return the one with the highest match

import numpy as np

TOLERANCE = 0.001

def fn_test_for_1D_linear_probe(probe):
    print('trying 1d probe')
    details = {'type': '1D linear'}
    match = 1
    #load element positions etc as an nx3 matrices
    p = probe['ELEMENT_POSITION']
    e1 = probe['ELEMENT_MAJOR']
    e2 = probe['ELEMENT_MINOR']
    #Choose a suitable tolerance value
    tol = np.sqrt(np.sum((np.max(p, axis = 0) - np.min(p, axis = 0)) ** 2)) * TOLERANCE
    #All elements must be same size and have same normal direction so minor and major vectors should all be equal
    if np.max(np.abs(e1 - np.mean(e1, axis = 0, keepdims = True))) > tol or np.max(np.abs(e2 - np.mean(e2, axis = 0, keepdims = True))) > tol:
        match = 0
        return (details, match)
    
    return (details, match)

def fn_test_for_2d_matrix_probe(probe):
    print('trying 2d probe')
    details = {'type': '2D matrix'}
    match = 0
    return (details, match)