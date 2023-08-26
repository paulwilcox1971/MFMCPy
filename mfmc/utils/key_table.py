# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 16:57:00 2023

@author: mepdw
"""

#Following are keys used in dictionaries describing array parameters
TYPE_KEY = 'Type'
MATCH_KEY = 'Match (%)'
NUMBER_OF_ELEMENTS_KEY = 'Number of elements' 
PITCH_KEY = 'Pitch (m)'
FIRST_ELEMENT_POSITION_KEY = 'First element position (m)'
LAST_ELEMENT_POSITION_KEY = 'Last element position (m)'
MID_POINT_POSITION_KEY = 'Probe mid-point (m)'
NORMAL_VECTOR_KEY ='Probe normal'
WARNINGS_KEY = 'Warnings'
ACTIVE_VECTOR_KEY = 'Probe active direction'  #Used for 1D arrays
PASSIVE_VECTOR_KEY = 'Probe passive direction'#Used for 1D arrays
ELEMENT_WIDTH_KEY = 'Element width (m)'       #size in active direction for 1D arrays
ELEMENT_LENGTH_KEY = 'Element length (m)'     #size in passive direction for 1D arrays
ELEMENT_SIZE_KEY = 'Element size (m)'         #Used for 2D arrays
FIRST_VECTOR_KEY = 'First vector direction'   #Used for 2D arrays rather than active direction
SECOND_VECTOR_KEY = 'Second vector direction' #Used for 2D arrays rather than passive direction

#Following are strings used to defined array types
ARRAY_TYPE_1D_LINEAR = '1D linear'
ARRAY_TYPE_2D_MATRIX = '2D matrix'

default_tolerance = 0.000001