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
    #Function should accept either HDF5 object or seq_data dict (latter shoudl contain at least one frame)

    seq_data = fn_read_sequence_data(mfmc_sequence_group) 
    
    #unique laws, utx and urx, in order they appear in data for tx and rx
    
    unique_tx_laws, tx_law_dict, tx_law_indices = fn_analyse_laws(seq_data['TRANSMIT_LAW'])
    unique_rx_laws, rx_law_dict, rx_law_indices = fn_analyse_laws(seq_data['RECEIVE_LAW'])
    
    
    ax_outer.clear()
    ax_outer.set_axis_off()
    
    ax_map = ax_outer.inset_axes([0.0, 0.0, 0.2, 0.2])
    #ax_map.set_axis_off()

    ax_bscan = ax_outer.inset_axes([0.2, 0.2, 0.8, 0.8])
    ax_bscan.set_axis_off()
    
    ax_ascan = ax_outer.inset_axes([0.2, 0.0, 0.8, 0.2])
    
    ax_ctrl = ax_outer.inset_axes([0.0, 0.2, 0.2, 0.8])
    ax_ctrl.set_axis_off()

    
    fi = seq_data[h5_keys.NUMBER_OF_FRAMES] - 1
    
    data = fn_read_frame(mfmc_sequence_group, fi)
    
    max_vals = np.zeros((len(unique_tx_laws), len(unique_rx_laws)))
    max_vals[tx_law_indices, rx_law_indices] = np.max(np.abs(data), axis = 1)

    time = seq_data[h5_keys.START_TIME] + np.arange(data.shape[1]) * seq_data[h5_keys.TIME_STEP]
    ascan_label = np.arange(data.shape[0])

    ax_map.imshow(max_vals, extent = [0, len(unique_tx_laws), len(unique_rx_laws), 0])
    ax_map.set_ylim([min(tx_law_indices), max(tx_law_indices)])
    ax_map.set_xlim([min(rx_law_indices), max(rx_law_indices)])
    
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
            i = np.asarray(tx_law_indices == 5).nonzero()[0]
            # i = i[np.argsort(ri[i])]
            # print(ri[i])
        if show_what == 'Rx gather':
            i = np.asarray(rx_law_indices == 3).nonzero()[0]
            # i = i[np.argsort(ti[i])]
            # print(ti[i])
        if show_what == 'Diag':
            i = np.asarray(tx_law_indices == rx_law_indices).nonzero()[0]
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

def fn_analyse_laws(focal_laws_for_seq):
    unique_laws, i =  np.unique(focal_laws_for_seq, return_index = True)
    unique_laws = unique_laws[np.argsort(i)]
    law_dict = {}
    for r in unique_laws:
        law_dict[r] = np.asarray(focal_laws_for_seq == r).nonzero()[0]
    law_indices = np.array([np.asarray(unique_laws == r).nonzero()[0][0] for r in focal_laws_for_seq])
    
    return unique_laws, law_dict, law_indices


    

