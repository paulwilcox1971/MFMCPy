# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:28:00 2023

@author: mepdw
"""

import numpy as np

def fn_convert_to_natural_coordinates(p, relative_tolerance = 0.000001):
    #get PCs
    (q, v) = fn_pca(p, 3)
    #work out significance of variation along each axis
    dimensional_tolerance = fn_representative_scale_of_points(q) * relative_tolerance
    # if not(dimensional_tolerance):
    #     dimensional_tolerance = 1
    #only return the natural coordinates with significant variations
    
    #probabilities for of each number of dims
    probs = 1 - np.exp(-(np.sum(q ** 2, axis = 0)) / dimensional_tolerance ** 2)
    if not(any(probs)):
        probs[0] = 1
    with np.errstate(divide = 'ignore'):
        loglikelihood = np.log([probs[0] * (1 - probs[2]) * (1 - probs[1]), probs[0] * probs[1] * (1 - probs[2]), probs[0] * probs[1] * probs[2]])
    no_dims = np.argmax(loglikelihood) + 1
    q = q[:, 0:no_dims]
    v = v[0:no_dims, :]
    return (q, v, no_dims, loglikelihood)


def fn_representative_scale_of_points(p):
    ''''Returns a scalar measure of the representative scale based on a matrix of coordinates'''
    tmp = np.sqrt(np.sum(np.std(p, axis = 0) ** 2))
    if not(tmp):
        tmp = 1.0
    return tmp

def fn_normal_log_likelihood(vals, mu, sigma):
    normal_log_likelihood = -np.sum((np.sum((vals - mu) ** 2)) / sigma ** 2)
    return normal_log_likelihood

def fn_normal_log_likelihood_rows_are_same(vals, sigma):
    return fn_normal_log_likelihood(vals, np.mean(vals, axis = 0, keepdims = True), sigma) #np.sum(np.log(np.exp((np.sum((vals - np.mean(vals, axis = 0, keepdims = True)) ** 2, axis = 1)) / sigma ** 2)))

def fn_pca(p, num_components):
    if p.shape[0] < 2:
        return (p, np.eye(3))
    # Standardize the data
    p = p - np.mean(p, axis = 0)
    
    # Calculate the covariance matrix
    covariance_matrix = np.cov(p, rowvar = False)
    
    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    
    # Sort eigenvalues and corresponding eigenvectors in descending order
    sorted_indices = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sorted_indices]
    eigenvectors = eigenvectors[:, sorted_indices]
    
    # Select the top 'num_components' eigenvectors
    top_eigenvectors = eigenvectors[:, :num_components]
    
    # Project the data onto the new lower-dimensional subspace
    transformed_data = np.dot(p, top_eigenvectors)
    
    return transformed_data, top_eigenvectors

def fn_estimate_pitch(q, relative_tolerance = 0.000001):
    if q.shape[0] < 2:
        return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    dimensional_tolerance = fn_representative_scale_of_points(q) * relative_tolerance
    pitch = []
    loglikelihood = []
    #loop over columnes in q
    for qq in q.T:
        #Calculate separation between all pairs of values
        (a, b) = np.meshgrid(qq, qq)
        c = np.abs(a - b)
        #Remove the values equal or near zero
        c[c < dimensional_tolerance] = np.nan
        #Calculate minimum separation of remaining values
        seps = np.nanmin(c, axis = 0)
        #Pitch estimate is given by mean
        pt = np.mean(seps)
        pitch.append(pt)
        #Likelihood of periodicity
        loglikelihood.append(fn_normal_log_likelihood(seps, pt, dimensional_tolerance))
        
    return (pitch, loglikelihood)
    
    