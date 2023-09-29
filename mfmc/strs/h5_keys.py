# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 16:20:01 2023

@author: mepdw
"""

#Definitions of fieldnames in MFMC

import numpy as np
import h5py as h5

PATH_SEPARATOR = "/"

TYPE = "TYPE"
VERSION = "VERSION"
ELEMENT_POSITION = "ELEMENT_POSITION"
ELEMENT_MINOR = "ELEMENT_MINOR"
ELEMENT_MAJOR = "ELEMENT_MAJOR"
ELEMENT_SHAPE = "ELEMENT_SHAPE"
ELEMENT_RADIUS_OF_CURVATURE = "ELEMENT_RADIUS_OF_CURVATURE"
ELEMENT_AXIS_OF_CURVATURE = "ELEMENT_AXIS_OF_CURVATURE"
WEDGE_SURFACE_POINT = "WEDGE_SURFACE_POINT"
WEDGE_SURFACE_NORMAL = "WEDGE_SURFACE_NORMAL"
DEAD_ELEMENT = "DEAD_ELEMENT"
CENTRE_FREQUENCY = "CENTRE_FREQUENCY"
BANDWIDTH = "BANDWIDTH"
PROBE_MANUFACTURER = "PROBE_MANUFACTURER"
PROBE_SERIAL_NUMBER = "PROBE_SERIAL_NUMBER"
PROBE_TAG = "PROBE_TAG"
WEDGE_MANUFACTURER = "WEDGE_MANUFACTURER"
WEDGE_SERIAL_NUMBER = "WEDGE_SERIAL_NUMBER"
WEDGE_TAG = "WEDGE_TAG"
MFMC_DATA = "MFMC_DATA"
MFMC_DATA_IM = "MFMC_DATA_IM"
PROBE_PLACEMENT_INDEX = "PROBE_PLACEMENT_INDEX"
PROBE_POSITION = "PROBE_POSITION"
PROBE_X_DIRECTION = "PROBE_X_DIRECTION"
PROBE_Y_DIRECTION = "PROBE_Y_DIRECTION"
TRANSMIT_LAW = "TRANSMIT_LAW"
RECEIVE_LAW = "RECEIVE_LAW"
PROBE_LIST = "PROBE_LIST"
TIME_STEP = "TIME_STEP"
START_TIME = "START_TIME"
SPECIMEN_VELOCITY = "SPECIMEN_VELOCITY"
WEDGE_VELOCITY = "WEDGE_VELOCITY"
TAG = "TAG"
DAC_CURVE = "DAC_CURVE"
RECEIVER_AMPLIFIER_GAIN = "RECEIVER_AMPLIFIER_GAIN"
FILTER_TYPE = "FILTER_TYPE"
FILTER_PARAMETERS = "FILTER_PARAMETERS"
FILTER_DESCRIPTION = "FILTER_DESCRIPTION"
OPERATOR = "OPERATOR"
DATE_AND_TIME = "DATE_AND_TIME"
PROBE = "PROBE"
SEQUENCE = "SEQUENCE"
LAW = "LAW"
ELEMENT = "ELEMENT"
DELAY = "DELAY"
WEIGHTING = "WEIGHTING"

np_equiv_dtype = {
    'H5T_STRING': np.string_,
    'H5T_FLOAT': np.floating,
    'H5T_INTEGER': np.integer,
    'H5T_STD_REF_OBJ': h5.ref_dtype}#np.dtype('O')}

DEFAULT_PREFIX = {
    PROBE: "P",
    SEQUENCE: "S",
    LAW: "L" }


