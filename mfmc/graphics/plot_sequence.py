# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:39:24 2023

@author: mepdw
"""


import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, AxesWidget
from matplotlib.backend_bases import MouseButton

import numpy as np
from ..read import fn_read_sequence_data, fn_read_frame, fn_read_law

from ..strs import h5_keys
from ..strs import eng_keys


def fn_plot_sequence(ax_outer, mfmc_sequence_group):
    #Function currently requires HDF5 object from open file - will not work on seq dict as access to laws etc. is needed.

    seq = fn_read_sequence_data(mfmc_sequence_group) 
    
    #unique laws
    tx = seq[h5_keys.TRANSMIT_LAW]
    rx = seq[h5_keys.RECEIVE_LAW]
    tx_laws = np.unique(tx)
    rx_laws = np.unique(rx)
    laws_full = {l: fn_read_law(mfmc_sequence_group.file[l]) for l in np.unique(np.concatenate((tx_laws, rx_laws)))}
    
    sorted_laws, ti, ri, fmc_map = fn_get_fmc_map(tx, rx, tx_laws, rx_laws, laws_full)

    ax_outer.clear()
    ax_outer.set_axis_off()
    
    ax_map = ax_outer.inset_axes([0.0, 0.0, 0.2, 0.2])
    #ax_map.set_axis_off()

    ax_bscan = ax_outer.inset_axes([0.2, 0.2, 0.8, 0.8])
    ax_bscan.set_axis_off()
    
    ax_ascan = ax_outer.inset_axes([0.2, 0.0, 0.8, 0.2])
    
    ax_ctrl = ax_outer.inset_axes([0.0, 0.2, 0.2, 0.8])
    ax_ctrl.set_axis_off()

    
    #data = mfmc_sequence_group[h5_keys.MFMC_DATA][0,:,:]
    
    fi = seq[h5_keys.NUMBER_OF_FRAMES] - 1
    
    data = fn_read_frame(mfmc_sequence_group, fi)
    
    max_vals = np.zeros(fmc_map.shape)
    max_vals[ti, ri] = np.max(np.abs(data), axis = 1)

    time = seq[h5_keys.START_TIME] + np.arange(data.shape[1]) * seq[h5_keys.TIME_STEP]
    ascan_label = np.arange(data.shape[0])

    ax_map.imshow(max_vals, alpha = np.array(fmc_map >= 0, dtype = float), extent = [0, len(sorted_laws), len(sorted_laws), 0])
    ax_map.set_ylim([min(ti), max(ti)])
    ax_map.set_xlim([min(ri), max(ri)])
    
    check = RadioButtons(
        ax = ax_ctrl,
        labels = ['Tx gather', 'Rx gather', 'Diag'],
        active = 0
        )
    
    def fn_callback(label):
        fn_refresh()
        
    def fn_refresh():
        show_what = check.value_selected
        print(show_what)
        if show_what == 'Tx gather':
            i = np.asarray(ti == 3).nonzero()[0]
            i = i[np.argsort(ri[i])]
            print(ri[i])
        if show_what == 'Rx gather':
            i = np.asarray(ri == 13).nonzero()[0]
            i = i[np.argsort(ti[i])]
            print(ti[i])
        if show_what == 'Diag':
            i = np.asarray(ti + 8 == ri).nonzero()[0]
        ax_bscan.imshow(np.real(data[i,:]), extent = [np.min(time) * 1e6, np.max(time) * 1e6, 1, len(ascan_label)], aspect = 'auto')
        ax_bscan.set_title('Raw data')
        ax_bscan.set_xlabel('Time ($\mu$s)')
        ax_bscan.set_ylabel('Ascan')
        plt.draw()
    
    
    def mouse_event(x):
        print(x)

    cc = AxesWidget(ax_map)
    cc.connect_event("button_press_event", mouse_event)
    
    
    # cid = ax_map.canvas.mpl_connect('button_press_event', mouse_event)
    
    # def on_move(event):
    #     if event.inaxes:
    #         print(event.inaxes)
    #         print(f'data coords {event.xdata} {event.ydata},',
    #               f'pixel coords {event.x} {event.y}')


    # def on_click(event):
    #     if event.button is MouseButton.LEFT:
    #         print('disconnecting callback')
    #         plt.disconnect(binding_id)


    # binding_id = plt.connect('motion_notify_event', on_move)
    # plt.connect('button_press_event', on_click)

    
    
    
    
    fn_refresh()
    check.on_clicked(fn_callback)
    
    
    return check

def fn_get_fmc_map(tx, rx, tx_laws, rx_laws, laws_full):
    
    #sort these laws by some magic method so that laws (just the names) is in this order - TOOD
    sorted_laws = fn_sort_laws(tx_laws, rx_laws, laws_full)
    
    #get the indices of the tx and rx law associated with each A-scan
    ti = np.array([np.where(sorted_laws == t)[0][0] for t in tx])
    ri = np.array([np.where(sorted_laws == r)[0][0] for r in rx])
    
    
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
    