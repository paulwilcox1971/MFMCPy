# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 14:27:10 2023

@author: mepdw
"""

import os
import sys


path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
os.chdir(os.sep.join(dir_path.split(os.sep)[0:-2]))

import mfmc as m
from mfmc.graphics.plot_probes import fn_plot_probe


import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, Wedge
from matplotlib.collections import PatchCollection

plt.close('all')

fname = os.sep.join(['example MFMC files', 'some probes3.mfmc'])

MFMC = m.read.fn_open_file_for_reading(fname)

probe_dict = {}
for p in m.read.fn_get_probe_list(MFMC):
    probe_dict[p] = m.read.fn_read_probe(MFMC, p)
    
probe = probe_dict['/PROBE<12>']


fig, ax = plt.subplots()

check = fn_plot_probe(ax, probe)
