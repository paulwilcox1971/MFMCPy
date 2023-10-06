# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 16:57:00 2023

@author: mepdw
"""

"""
Following are keys used in dictionaries describing array parameters
These are not part of the MFMC specification and can be altered to suit language etc
"""

#Probe parameters used as dictionary keys
#All array types
TYPE = 'Type'
MATCH = 'Match (%)'
NUMBER_OF_ELEMENTS = 'Number of elements' 
PITCH = 'Pitch (m)'
FIRST_ELEMENT_POSITION = 'First element position (m)'
LAST_ELEMENT_POSITION = 'Last element position (m)'
MID_POINT_POSITION = 'Probe mid-point (m)'
NORMAL_VECTOR ='Probe normal (vec)'
CENTRE_FREQUENCY = 'Centre frequency (Hz)'
ELEMENT_SHAPE = 'Element shape'
WARNINGS = 'Warnings'

#1D linear arrays
ACTIVE_VECTOR = 'Probe active direction (vec)'  #Used for 1D arrays
PASSIVE_VECTOR = 'Probe passive direction (vec)'#Used for 1D arrays
ELEMENT_WIDTH = 'Element width (m)'       #size in active direction for 1D arrays
ELEMENT_LENGTH = 'Element length (m)'     #size in passive direction for 1D arrays

#2D arrays
FIRST_VECTOR = 'First vector direction (vec)'   #Used for 2D arrays rather than active direction
SECOND_VECTOR = 'Second vector direction (vec)' #Used for 2D arrays rather than passive direction
ELEMENT_SIZE = 'Element size (m)'         #Used for 2D arrays

#Element shapes
SHAPE_RECTANGULAR = 'Rectangular'
SHAPE_ELLIPTICAL = 'Elliptical'
SHAPE_ANNULAR = 'Annular'
SHAPE_UNKNOWN = 'Unknown'

#Types of probe
PROBE_TYPE_1D_LINEAR = '1D linear'
PROBE_TYPE_2D_MATRIX = '2D matrix'
PROBE_TYPE_2D_OTHER = '2D other'

#suffix in names used to indicate vectors where only direction (not sign) matters
DIRECTION_ONLY_SUFFIX = '(vec)'
