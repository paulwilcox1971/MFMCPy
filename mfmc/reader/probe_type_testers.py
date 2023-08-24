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

def fn_test_for_1D_linear_probe(probe, relative_tolerance):
    details = {mfmc.TYPE_KEY: mfmc.ARRAY_TYPE_1D_LINEAR, mfmc.MATCH_KEY: 0}
    log_likelihood = 0
    #Load element positions etc as an nx3 matrices
    p = probe['ELEMENT_POSITION']
    e1 = probe['ELEMENT_MAJOR']
    e2 = probe['ELEMENT_MINOR']
    #Choose a suitable dimensional tolerance value
    dimensional_tolerance = mfmc.fn_representative_scale_of_points(p) * relative_tolerance
        
    #Check elements all same size and orientation
    log_likelihood += mfmc.fn_normal_log_likelihood_rows_are_same(e1, dimensional_tolerance)
    log_likelihood += mfmc.fn_normal_log_likelihood_rows_are_same(e2, dimensional_tolerance)
    
    
    #Convert to natural coordinates
    (q, v, no_dims, loglikelihood_dim) = mfmc.fn_convert_to_natural_coordinates(p)

    #Likelihood of being 1D array    
    log_likelihood += loglikelihood_dim[0] # index zero because this is for 1D array
    
    #Uniformity of pitch
    (pitch, loglikelihood_pitch) = mfmc.fn_estimate_pitch(q)
    log_likelihood += loglikelihood_pitch[0] # index zero because this is for 1D array
    
    #Add the details - note numbers are not rounded at this point
    details[mfmc.NUMBER_OF_ELEMENTS_KEY] = p.shape[0]
    details[mfmc.PITCH_KEY] = pitch[0]
    details[mfmc.ELEMENT_LENGTH_KEY] = np.mean(np.linalg.norm(e1, axis = 1)) * 2
    details[mfmc.ELEMENT_WIDTH_KEY] = np.mean(np.linalg.norm(e2, axis = 1)) * 2
    details[mfmc.FIRST_ELEMENT_POSITION_KEY] = list(p[0, :])
    details[mfmc.LAST_ELEMENT_POSITION_KEY] = list(p[-1, :])
    details[mfmc.MID_POINT_POSITION_KEY] = list(np.mean(p, axis = 0))
    details[mfmc.ACTIVE_VECTOR_KEY] = list(v[0])
    e3 = np.cross(np.mean(e2, axis = 0), np.mean(e1, axis = 0))
    e3 /= np.linalg.norm(e3)
    details[mfmc.PASSIVE_VECTOR_KEY] = np.cross(e3, v[0])
    details[mfmc.NORMAL_VECTOR_KEY] = e3 
    details[mfmc.MATCH_KEY] = np.exp(log_likelihood) * 100
    
    return details

def fn_test_for_2d_matrix_probe(probe, relative_tolerance):
    details = {mfmc.TYPE_KEY: mfmc.ARRAY_TYPE_2D_MATRIX, mfmc.MATCH_KEY: 0}
    log_likelihood = 0
    #Load element positions etc as an nx3 matrices
    p = probe['ELEMENT_POSITION']
    e1 = probe['ELEMENT_MAJOR']
    e2 = probe['ELEMENT_MINOR']
    
    #Choose a suitable dimensional tolerance value
    dimensional_tolerance = np.sqrt(np.sum((np.max(p, axis = 0) - np.min(p, axis = 0)) ** 2)) * relative_tolerance
        
    #Check elements all same size and orientation
    log_likelihood += mfmc.fn_normal_log_likelihood_rows_are_same(e1, dimensional_tolerance)
    log_likelihood += mfmc.fn_normal_log_likelihood_rows_are_same(e2, dimensional_tolerance)
    
    #Convert to natural coordinates
    (q, v, no_dims, loglikelihood_dim) = mfmc.fn_convert_to_natural_coordinates(p)
     
    #Likelihood of being 1D array    
    log_likelihood += loglikelihood_dim[1] # index one because this is for 2D array
    
    #Uniformity of pitch
    (pitch, loglikelihood_pitch) = mfmc.fn_estimate_pitch(q)
    log_likelihood += np.sum(loglikelihood_pitch) #must be even pitch in both dims
    
    #Add the details - note numbers are not rounded at this point
    #This needs improving to return 2 element vector for number of elements as it is a matrix array, same for pitch and el-size - rule is that it should all be exactly same as input params!
    details[mfmc.NUMBER_OF_ELEMENTS_KEY] = p.shape[0]
    details[mfmc.FIRST_ELEMENT_POSITION_KEY] = list(p[0, :])
    e3 = np.cross(np.mean(e1, axis = 0), np.mean(e2, axis = 0))
    details[mfmc.NORMAL_VECTOR_KEY] = e3 / np.linalg.norm(e3)
    details[mfmc.MATCH_KEY] = np.exp(log_likelihood) * 90
    
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

