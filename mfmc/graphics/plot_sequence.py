# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:39:24 2023

@author: mepdw
"""


import matplotlib.pyplot as plt
import numpy as np

from ..strs import h5_keys
from ..strs import eng_keys


def fn_plot_sequence(ax_outer, sequence):

    ax_outer.clear()
    ax_outer.set_axis_off()
    
    rax = ax_outer.inset_axes([0.0, 0.0, 0.2, 1.0])
    rax.set_axis_off()

    ax = ax_outer.inset_axes([0.2, 0.0, 0.8, 1.0])
    ax.set_axis_off()
    

    
    data = sequence[h5_keys.MFMC_DATA][0,:,:]
    time = sequence.attrs[h5_keys.START_TIME] + np.arange(data.shape[1]) * sequence.attrs[h5_keys.TIME_STEP]
    ascan_label = np.arange(data.shape[0])

    ax.imshow(data, extent=[np.min(time) * 1e6, np.max(time) * 1e6, 1, len(ascan_label)], aspect = 'auto')
    ax.set_title('Raw data')
    ax.set_xlabel('Time ($\mu$s)')
    ax.set_ylabel('Ascan')

    return 0

