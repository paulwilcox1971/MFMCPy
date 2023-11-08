# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:39:24 2023

@author: mepdw
"""


import matplotlib.pyplot as plt
import numpy as np
from ..read import fn_read_sequence_data, fn_read_frame, fn_read_law

from ..strs import h5_keys
from ..strs import eng_keys


def fn_plot_sequence(ax_outer, sequence):

    seq = fn_read_sequence_data(sequence) #It would be better to just make all the read write functions have just the group as the argument!!
    
    #unique laws
    tx = seq[h5_keys.TRANSMIT_LAW]
    rx = seq[h5_keys.RECEIVE_LAW]
    tx_laws = np.unique(tx)
    rx_laws = np.unique(rx)
    laws_full = {l: fn_read_law(sequence.file[l]) for l in np.unique(np.concatenate((tx_laws, rx_laws)))}
    
    sorted_laws, ti, ri, fmc_map = fn_get_fmc_map(tx, rx, tx_laws, rx_laws, laws_full)

    ax_outer.clear()
    ax_outer.set_axis_off()
    
    ax_map = ax_outer.inset_axes([0.0, 0.0, 0.2, 0.2])
    #ax_map.set_axis_off()

    ax = ax_outer.inset_axes([0.2, 0.2, 0.8, 0.8])
    ax.set_axis_off()
    

    
    #data = sequence[h5_keys.MFMC_DATA][0,:,:]
    
    fi = seq[h5_keys.NUMBER_OF_FRAMES] - 1
    
    data = fn_read_frame(sequence, fi)
    
    max_vals = np.zeros(fmc_map.shape)
    max_vals[ti, ri] = np.max(np.abs(data), axis = 1)

    time = seq[h5_keys.START_TIME] + np.arange(data.shape[1]) * seq[h5_keys.TIME_STEP]
    ascan_label = np.arange(data.shape[0])

    ax.imshow(np.real(data), extent=[np.min(time) * 1e6, np.max(time) * 1e6, 1, len(ascan_label)], aspect = 'auto')
    ax.set_title('Raw data')
    ax.set_xlabel('Time ($\mu$s)')
    ax.set_ylabel('Ascan')

    ax_map.imshow(max_vals, alpha = np.array(fmc_map >= 0, dtype = float), extent = [1, len(sorted_laws) + 1, len(sorted_laws) + 1, 1])

    return 0

def fn_get_fmc_map(tx, rx, tx_laws, rx_laws, laws_full):
    
    #sort these laws by some magic method so that laws (just the names) is in this order - TOOD
    sorted_laws = fn_sort_laws(tx_laws, rx_laws, laws_full)
    
    #get the indices of the tx and rx law associated with each A-scan
    ti = [np.where(sorted_laws == t)[0][0] for t in tx]
    ri = [np.where(sorted_laws == r)[0][0] for r in rx]
    
    
    # utx, ti = np.unique(tx, return_inverse = True)
    # urx, ri = np.unique(rx, return_inverse = True)
    fmc_map = np.full([len(sorted_laws), len(sorted_laws)], -1)
    fmc_map[ti, ri] = 1
    #fmc_map[ti[ti<=ri], ri[ti<=ri]] = 1 #temp text to get hmc
    
    return sorted_laws, ti, ri, fmc_map

def fn_sort_laws(tx_laws, rx_laws, laws_full):
    #sort of 'centre of gravity' based element indices is used for sorting
    ewt = [np.sum(laws_full[t][h5_keys.ELEMENT] * laws_full[t][h5_keys.WEIGHTING]) for t in tx_laws]
    ewr = [np.sum(laws_full[r][h5_keys.ELEMENT] * laws_full[r][h5_keys.WEIGHTING]) for r in rx_laws]
    sorted_laws = np.concatenate((tx_laws[np.argsort(ewt)], rx_laws[np.argsort(ewr)]))
    return sorted_laws
    