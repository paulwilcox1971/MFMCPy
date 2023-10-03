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
TYPE = 'Type'
MATCH = 'Match (%)'
NUMBER_OF_ELEMENTS = 'Number of elements' 
PITCH = 'Pitch (m)'
FIRST_ELEMENT_POSITION = 'First element position (m)'
LAST_ELEMENT_POSITION = 'Last element position (m)'
MID_POINT_POSITION = 'Probe mid-point (m)'
NORMAL_VECTOR ='Probe normal'
WARNINGS = 'Warnings'
ACTIVE_VECTOR = 'Probe active direction'  #Used for 1D arrays
PASSIVE_VECTOR = 'Probe passive direction'#Used for 1D arrays
ELEMENT_WIDTH = 'Element width (m)'       #size in active direction for 1D arrays
ELEMENT_LENGTH = 'Element length (m)'     #size in passive direction for 1D arrays
ELEMENT_SIZE = 'Element size (m)'         #Used for 2D arrays
FIRST_VECTOR = 'First vector direction'   #Used for 2D arrays rather than active direction
SECOND_VECTOR = 'Second vector direction' #Used for 2D arrays rather than passive direction
CENTRE_FREQUENCY = 'Centre frequency (Hz)'

#Types of probe
PROBE_TYPE_1D_LINEAR = '1D linear'
PROBE_TYPE_2D_MATRIX = '2D matrix'

