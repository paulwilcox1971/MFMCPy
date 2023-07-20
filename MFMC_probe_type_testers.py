# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:31:59 2023

@author: mepdw
"""

#The function fn_analyse_probe will test specified probe using all functions in
#this file and return the one with the highest match

import numpy as np


TYPE_KEY = 'Type'
MATCH_KEY = 'Match (%)'
NUMBER_OF_ELEMENTS_KEY = 'Number of elements' 

PITCH_KEY = 'Pitch (m)'
FIRST_ELEMENT_POSITION_KEY = 'First element position (m)'
LAST_ELEMENT_POSITION_KEY = 'Last element position (m)'
MID_POINT_POSITION_KEY = 'Probe mid-point (m)'
ACTIVE_VECTOR_KEY = 'Probe active direction'
PASSIVE_VECTOR_KEY = 'Probe passive direction'
NORMAL_VECTOR_KEY ='Probe normal'
WARNINGS_KEY = 'Warnings'
ELEMENT_WIDTH_KEY = 'Element width (m)'
ELEMENT_LENGTH_KEY = 'Element length (m)'

def fn_test_for_1D_linear_probe(probe, relative_tolerance):
    details = {TYPE_KEY: '1D linear', MATCH_KEY: 0}
    log_likelihood = 0
    #Load element positions etc as an nx3 matrices
    p = probe['ELEMENT_POSITION']
    e1 = probe['ELEMENT_MAJOR']
    e2 = probe['ELEMENT_MINOR']
    #Choose a suitable dimensional tolerance value
    dimensional_tolerance = np.sqrt(np.sum((np.max(p, axis = 0) - np.min(p, axis = 0)) ** 2)) * relative_tolerance
        
    #Check elements all same size and orientation?
    log_likelihood -= fn_normal_log_likelihood_rows_are_same(e1, dimensional_tolerance)
    log_likelihood -= fn_normal_log_likelihood_rows_are_same(e2, dimensional_tolerance)
    
    #Check element positions are colinear
    (point_on_line, line_direction) = fn_vector_best_fit_line(p)
    dist_from_line = fn_calculate_distance_to_line(p, line_direction, point_on_line)
    log_likelihood -= fn_normal_log_likelihood(dist_from_line, 0, dimensional_tolerance)
        
    #Check points are evenly spaced along line
    k = fn_lambda_for_point(p, point_on_line, line_direction)
    i = np.argsort(k)
    if not(all(i == range(len(i))) or all(np.flip(i) == range(len(i)))):
       details[WARNINGS_KEY] = 'Elements not numbered in order'
       k = np.sort(k)
    dk = k[1: ] - k[0: -1]
    log_likelihood -= fn_normal_log_likelihood_rows_are_same(dk, dimensional_tolerance)
    
    #Add the details - note numbers are not rounded at this point
    details[NUMBER_OF_ELEMENTS_KEY] = p.shape[0]
    details[PITCH_KEY] = np.mean(dk)
    details[ELEMENT_LENGTH_KEY] = np.mean(np.linalg.norm(e1, axis = 1)) * 2
    details[ELEMENT_WIDTH_KEY] = np.mean(np.linalg.norm(e2, axis = 1)) * 2
    details[FIRST_ELEMENT_POSITION_KEY] = list(p[0, :])
    details[LAST_ELEMENT_POSITION_KEY] = list(p[-1, :])
    details[MID_POINT_POSITION_KEY] = list(np.mean(p, axis = 0))
    details[ACTIVE_VECTOR_KEY] = list(line_direction)
    e3 = np.cross(np.mean(e1, axis = 0), np.mean(e2, axis = 0))
    e3 /= np.linalg.norm(e3)
    details[PASSIVE_VECTOR_KEY] = np.cross(line_direction, e3)
    details[NORMAL_VECTOR_KEY] = e3 
    details[MATCH_KEY] = np.exp(log_likelihood) * 100
    
    return details

def fn_test_for_planar_2d_probe(probe, relative_tolerance):
    details = {TYPE_KEY: '2D planar', MATCH_KEY: 0}
    log_likelihood = 0
    #Load element positions etc as an nx3 matrices
    p = probe['ELEMENT_POSITION']
    e1 = probe['ELEMENT_MAJOR']
    e2 = probe['ELEMENT_MINOR']
    
    #Choose a suitable dimensional tolerance value
    dimensional_tolerance = np.sqrt(np.sum((np.max(p, axis = 0) - np.min(p, axis = 0)) ** 2)) * relative_tolerance
        
    #Check elements all same size and orientation
    log_likelihood -= fn_normal_log_likelihood_rows_are_same(e1, dimensional_tolerance)
    log_likelihood -= fn_normal_log_likelihood_rows_are_same(e2, dimensional_tolerance)
    
    #Check element positions are coplanar
    # TODO
    
    #Add the details - note numbers are not rounded at this point
    details[NUMBER_OF_ELEMENTS_KEY] = p.shape[0]
    details[FIRST_ELEMENT_POSITION_KEY] = list(p[0, :])
    e3 = np.cross(np.mean(e1, axis = 0), np.mean(e2, axis = 0))
    details[NORMAL_VECTOR_KEY] = e3 / np.linalg.norm(e3)
    details[MATCH_KEY] = np.exp(log_likelihood) * 90
    
    return details


#Internal functions

def fn_normal_log_likelihood_rows_are_same(vals, sigma):
    return fn_normal_log_likelihood(vals, np.mean(vals, axis = 0, keepdims = True), sigma) #np.sum(np.log(np.exp((np.sum((vals - np.mean(vals, axis = 0, keepdims = True)) ** 2, axis = 1)) / sigma ** 2)))

def fn_normal_log_likelihood(vals, mu, sigma):
    normal_log_likelihood = np.sum(np.log(np.exp((np.sum((vals - mu) ** 2)) / sigma ** 2)))
    #print('Log likelihood:', normal_log_likelihood)
    return normal_log_likelihood

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

