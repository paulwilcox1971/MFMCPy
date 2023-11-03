# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 16:34:46 2023

@author: mepdw
"""

import os


import os

mfmc_path = os.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[0:-1])

#Default values
default_tolerance = 0.000001
default_spec_fname = os.sep.join([mfmc_path, 'spec', 'MFMC Specification 2.0.0.xlsx'])