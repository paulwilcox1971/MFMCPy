# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:31:59 2023

@author: mepdw
"""

#The function fn_analyse_probe will test specified probe using all functions in
#this file and return the one with the highest match

import numpy as np
import sys

from .. import utils
from ..strs import eng_keys
from ..strs import h5_keys


def fn_test_for_1D_linear_probe(probe, relative_tolerance = utils.default_tolerance):
    details = {eng_keys.TYPE: eng_keys.PROBE_TYPE_1D_LINEAR, eng_keys.MATCH: 0}
    log_likelihood = 0
    
    #Analyse element positions
    (q, v, no_dims, loglikelihood_dim, pitch, loglikelihood_pitch, no_per_dim) = \
        utils.fn_estimate_params_of_point_cloud(probe[h5_keys.ELEMENT_POSITION], relative_tolerance)

    #For 1D probe, active direction (e1) is same as element major axis,
    #e2 is given by element minor axis and e3 (normal) - but is this right? What
    #if major and minor are defined the other way around? See spec - these should define probe normal unambigiously
    #so should get e1 = v[0] then e3 = maj x min and final e2 = e1 x e3
    e1 = np.mean(probe[h5_keys.ELEMENT_MINOR], axis = 0)
    e1 /= np.linalg.norm(e1)
    e2 = np.mean(probe[h5_keys.ELEMENT_MAJOR], axis = 0)
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(e2, e1)
    
    #Add the details - note numbers are not rounded at this point
    details[eng_keys.NUMBER_OF_ELEMENTS] = probe['ELEMENT_POSITION'].shape[0]
    details[eng_keys.PITCH] = pitch[0]
    details[eng_keys.ELEMENT_LENGTH] = np.mean(np.linalg.norm(probe[h5_keys.ELEMENT_MAJOR], axis = 1)) * 2
    details[eng_keys.ELEMENT_WIDTH] = np.mean(np.linalg.norm(probe[h5_keys.ELEMENT_MINOR], axis = 1)) * 2
    details[eng_keys.FIRST_ELEMENT_POSITION] = list(probe[h5_keys.ELEMENT_POSITION][0, :])
    details[eng_keys.LAST_ELEMENT_POSITION] = list(probe[h5_keys.ELEMENT_POSITION][-1, :])
    details[eng_keys.MID_POINT_POSITION] = list(np.mean(probe[h5_keys.ELEMENT_POSITION], axis = 0))
    details[eng_keys.ACTIVE_VECTOR] = e1
    details[eng_keys.PASSIVE_VECTOR] = e2
    details[eng_keys.NORMAL_VECTOR] = e3 
    
    # details[eng_keys.FIRST_VECTOR] = e1
    # details[eng_keys.SECOND_VECTOR] = e2

    details[eng_keys.MATCH] = np.exp(log_likelihood) * 100
    
    return details

def fn_test_for_2D_matrix_probe(probe, relative_tolerance = utils.default_tolerance):
    details = {eng_keys.TYPE: eng_keys.PROBE_TYPE_2D_MATRIX, eng_keys.MATCH: 0}
    log_likelihood = 0
    
    #Analyse element positions
    (q, v, no_dims, loglikelihood_dim, pitch, loglikelihood_pitch, no_per_dim) = \
        utils.fn_estimate_params_of_point_cloud(probe[h5_keys.ELEMENT_POSITION], relative_tolerance)
    
    #If number of elements can be expressed as product, do it like this otherwise
    #just return total number of elements because it's probably not a matrix probe
    if np.prod(no_per_dim) != probe[h5_keys.ELEMENT_POSITION].shape[0] or len(no_per_dim) < 2:
        no_elements = probe[h5_keys.ELEMENT_POSITION].shape[0]
    else:
        no_elements = list(no_per_dim)
    
    #Likelihood of being 2D array    
    log_likelihood += loglikelihood_dim[1] # index one because this is for 2D array
    
    #For matrix array, must be regular pitch in both dims
    log_likelihood += np.sum(loglikelihood_pitch) #must be even pitch in both dims
       
    #Check elements same
    log_likelihood += fn_check_elements_all_same(probe, relative_tolerance)
    
    #For 2D probe, first and second vectors should be from principle components. Normal vector from maj x min
    e1 = v[0]
    e2 = v[1]
    e3 = np.cross(e1, e2)

    #Add the details - note numbers are not rounded at this point
    details[eng_keys.PITCH] = pitch
    details[eng_keys.NUMBER_OF_ELEMENTS] = no_elements
    details[eng_keys.FIRST_ELEMENT_POSITION] = list(probe[h5_keys.ELEMENT_POSITION][0, :])
    details[eng_keys.LAST_ELEMENT_POSITION] = list(probe[h5_keys.ELEMENT_POSITION][-1, :])
    details[eng_keys.FIRST_VECTOR] = e1 
    details[eng_keys.SECOND_VECTOR] = e2
    details[eng_keys.NORMAL_VECTOR] = e3
    details[eng_keys.MATCH] = np.exp(log_likelihood) * 100
    
    return details


#Internal functions

def fn_vector_best_fit_line(points):
    # This came from ChatGPT!
    
    # Perform linear regression
    lineection, _, _, _ = np.linalg.lstsq(points, np.ones_like(points[:, 0]), rcond=None)
    lineection /= np.linalg.norm(lineection)
    
    # Find a point on the line by taking the mean of the coordinates
    point_on_line = np.mean(points, axis=0)
    
    return (point_on_line, lineection)

def fn_lambda_for_point(point, point_on_line, lineection):
    return np.dot(point - point_on_line, lineection)

def fn_calculate_distance_to_line(point, lineection, point_on_line):
    # Calculate the vectors from point_on_line to each point in P
    vectors_P = point - point_on_line

    # Calculate the projections of vectors_P onto lineection
    projections = np.dot(vectors_P, lineection)

    # Calculate the orthogonal components of vectors_P
    orthogonal_components = vectors_P - np.outer(projections, lineection)

    # Calculate the distances as the norms of the orthogonal components
    distances = np.linalg.norm(orthogonal_components, axis=1)
    
    return distances

def fn_check_elements_all_same(probe, relative_tolerance):
    dimensional_tolerance = relative_tolerance * utils.fn_representative_scale_of_points(probe[h5_keys.ELEMENT_POSITION])
    log_likelihood = 0
    log_likelihood += utils.fn_normal_log_likelihood_rows_are_same(probe[h5_keys.ELEMENT_MAJOR], dimensional_tolerance)
    log_likelihood += utils.fn_normal_log_likelihood_rows_are_same(probe[h5_keys.ELEMENT_MINOR], dimensional_tolerance)
    return log_likelihood
