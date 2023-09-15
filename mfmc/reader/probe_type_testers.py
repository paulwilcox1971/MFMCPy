# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:31:59 2023

@author: mepdw
"""

#The function fn_analyse_probe will test specified probe using all functions in
#this file and return the one with the highest match

import numpy as np
import sys
sys.path.append('..') #So mfmc can be found in parent directory
import mfmc



def fn_test_for_1D_linear_probe(probe, relative_tolerance = mfmc.default_tolerance):
    details = {mfmc.TYPE_KEY: mfmc.ARRAY_TYPE_1D_LINEAR, mfmc.MATCH_KEY: 0}
    log_likelihood = 0
    
    #Analyse element positions
    (q, v, no_dims, loglikelihood_dim, pitch, loglikelihood_pitch, no_per_dim) = \
        mfmc.fn_estimate_params_of_point_cloud(probe['ELEMENT_POSITION'], relative_tolerance)

    #For 1D probe, active direction (e1) is same as element major axis,
    #e2 is given by element minor axis and e3 (normal) - but is this right? What
    #if major and minor are defined the other way around? See spec - these should define probe normal unambigiously
    #so should get e1 = v[0] then e3 = maj x min and final e2 = e1 x e3
    e1 = np.mean(probe['ELEMENT_MINOR'], axis = 0)
    e1 /= np.linalg.norm(e1)
    e2 = np.mean(probe['ELEMENT_MAJOR'], axis = 0)
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(e2, e1)
    
    #Add the details - note numbers are not rounded at this point
    details[mfmc.NUMBER_OF_ELEMENTS_KEY] = probe['ELEMENT_POSITION'].shape[0]
    details[mfmc.PITCH_KEY] = pitch[0]
    details[mfmc.ELEMENT_LENGTH_KEY] = np.mean(np.linalg.norm(probe['ELEMENT_MAJOR'], axis = 1)) * 2
    details[mfmc.ELEMENT_WIDTH_KEY] = np.mean(np.linalg.norm(probe['ELEMENT_MINOR'], axis = 1)) * 2
    details[mfmc.FIRST_ELEMENT_POSITION_KEY] = list(probe['ELEMENT_POSITION'][0, :])
    details[mfmc.LAST_ELEMENT_POSITION_KEY] = list(probe['ELEMENT_POSITION'][-1, :])
    details[mfmc.MID_POINT_POSITION_KEY] = list(np.mean(probe['ELEMENT_POSITION'], axis = 0))
    details[mfmc.ACTIVE_VECTOR_KEY] = e1
    details[mfmc.PASSIVE_VECTOR_KEY] = e2
    details[mfmc.NORMAL_VECTOR_KEY] = e3 
    
    # details[mfmc.FIRST_VECTOR_KEY] = e1
    # details[mfmc.SECOND_VECTOR_KEY] = e2

    details[mfmc.MATCH_KEY] = np.exp(log_likelihood) * 100
    
    return details

def fn_test_for_2d_matrix_probe(probe, relative_tolerance = mfmc.default_tolerance):
    details = {mfmc.TYPE_KEY: mfmc.ARRAY_TYPE_2D_MATRIX, mfmc.MATCH_KEY: 0}
    log_likelihood = 0
    
    #Analyse element positions
    (q, v, no_dims, loglikelihood_dim, pitch, loglikelihood_pitch, no_per_dim) = \
        mfmc.fn_estimate_params_of_point_cloud(probe['ELEMENT_POSITION'], relative_tolerance)
    
    #If number of elements can be expressed as product, do it like this otherwise
    #just return total number of elements because it's probably not a matrix probe
    if np.prod(no_per_dim) != probe['ELEMENT_POSITION'].shape[0] or len(no_per_dim) < 2:
        no_elements = probe['ELEMENT_POSITION'].shape[0]
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
    details[mfmc.PITCH_KEY] = pitch
    details[mfmc.NUMBER_OF_ELEMENTS_KEY] = no_elements
    details[mfmc.FIRST_ELEMENT_POSITION_KEY] = list(probe['ELEMENT_POSITION'][0, :])
    details[mfmc.LAST_ELEMENT_POSITION_KEY] = list(probe['ELEMENT_POSITION'][-1, :])
    details[mfmc.FIRST_VECTOR_KEY] = e1 
    details[mfmc.SECOND_VECTOR_KEY] = e2
    details[mfmc.NORMAL_VECTOR_KEY] = e3
    details[mfmc.MATCH_KEY] = np.exp(log_likelihood) * 100
    
    return details


#Internal functions

def fn_vector_best_fit_line(points):
    # This came from ChatGPT!
    
    # Perform linear regression
    line_direction, _, _, _ = np.linalg.lstsq(points, np.ones_like(points[:, 0]), rcond=None)
    line_direction /= np.linalg.norm(line_direction)
    
    # Find a point on the line by taking the mean of the coordinates
    point_on_line = np.mean(points, axis=0)
    
    return (point_on_line, line_direction)

def fn_lambda_for_point(point, point_on_line, line_direction):
    return np.dot(point - point_on_line, line_direction)

def fn_calculate_distance_to_line(point, line_direction, point_on_line):
    # Calculate the vectors from point_on_line to each point in P
    vectors_P = point - point_on_line

    # Calculate the projections of vectors_P onto line_direction
    projections = np.dot(vectors_P, line_direction)

    # Calculate the orthogonal components of vectors_P
    orthogonal_components = vectors_P - np.outer(projections, line_direction)

    # Calculate the distances as the norms of the orthogonal components
    distances = np.linalg.norm(orthogonal_components, axis=1)
    
    return distances

def fn_check_elements_all_same(probe, relative_tolerance):
    dimensional_tolerance = relative_tolerance * mfmc.fn_representative_scale_of_points(probe['ELEMENT_POSITION'])
    log_likelihood = 0
    log_likelihood += mfmc.fn_normal_log_likelihood_rows_are_same(probe['ELEMENT_MAJOR'], dimensional_tolerance)
    log_likelihood += mfmc.fn_normal_log_likelihood_rows_are_same(probe['ELEMENT_MINOR'], dimensional_tolerance)
    return log_likelihood
