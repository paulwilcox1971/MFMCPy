# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:39:24 2023

@author: mepdw
"""
import MFMC_Py as mfmc

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

fname = 'BRAIN example.mfmc'
fname = 'AS example.mfmc'
fname = 'new_brain_example.mfmc'

MFMC = mfmc.fn_open_file(fname)

sequence_list = mfmc.fn_get_sequence_list(MFMC)
sequence = mfmc.cl_sequence(MFMC, sequence_list[0])

#(time, ascan_label, data) = sequence.fn_return_frame(rx = 32, tmin = 5e-6, tmax = 15e-6)
(time, ascan_label, data) = sequence.fn_return_frame()


(fig, (ax)) = plt.subplots(1, 1)
ax.imshow(data, extent=[np.min(time) * 1e6, np.max(time) * 1e6, 1, len(ascan_label)], aspect = 'auto')
ax.set_title('Raw data')
ax.set_xlabel('Time ($\mu$s)')
ax.set_ylabel('Ascan')

