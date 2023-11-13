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

#edge_fract = 0.02
#map_lines = 0
#show_what = 0

def fn_plot_sequence(fig, mfmc_sequence_group):
    #Function should accept either HDF5 object or seq_data dict (latter shoudl contain at least one frame)
    
    for a in fig.axes:
        fig.delaxes(a)
    
    seq_data = fn_read_sequence_data(mfmc_sequence_group) 
    selected_tx = 0
    selected_rx = 0
    edge_fract = 0.02
    
    #unique laws, utx and urx, in order they appear in data for tx and rx
    unique_tx_laws, tx_law_dict, tx_law_indices = fn_analyse_laws(seq_data['TRANSMIT_LAW'])
    unique_rx_laws, rx_law_dict, rx_law_indices = fn_analyse_laws(seq_data['RECEIVE_LAW'])
    
    
    #ax_map = ax_outer.inset_axes([0.0, 0.0, 0.2, 0.2], zorder = 6)
    ax_map = fig.add_axes([edge_fract, edge_fract, 0.2 - 2 * edge_fract, 0.2 - 2 * edge_fract])
    ax_map.set_axis_off()

    #ax_bscan = ax_outer.inset_axes([0.2, 0.2, 0.8, 0.8])
    ax_bscan = fig.add_axes([0.2 + edge_fract, 0.2 + edge_fract, 0.8 - 2 * edge_fract, 0.8 - 2 * edge_fract])
    ax_bscan.set_axis_off()
    
    #ax_ascan = ax_outer.inset_axes([0.2, 0.0, 0.8, 0.2])
    ax_ascan = fig.add_axes([0.2 + edge_fract, edge_fract, 0.8 - 2 * edge_fract, 0.2 - 2 * edge_fract])
    
    #ax_ctrl = ax_outer.inset_axes([0.0, 0.2, 0.2, 0.8])
    ax_ctrl = fig.add_axes([0.0 +edge_fract, 0.2 + edge_fract, 0.2 - 2 * edge_fract, 0.8 - 2 * edge_fract])
    ax_ctrl.set_axis_off()

    
    fi = seq_data[h5_keys.NUMBER_OF_FRAMES] - 1
    
    data = fn_read_frame(mfmc_sequence_group, fi)
    global_max = np.max(np.abs(data))
    
    max_vals = np.zeros((len(unique_tx_laws), len(unique_rx_laws)))
    max_vals[tx_law_indices, rx_law_indices] = np.max(np.abs(data), axis = 1)

    time = seq_data[h5_keys.START_TIME] + np.arange(data.shape[1]) * seq_data[h5_keys.TIME_STEP]
    ascan_label = np.arange(data.shape[0])

    ax_map.imshow(max_vals)
    map_lines = ax_map.plot([[0,0], [0,0]], [[1,1], [1,1]], visible = False)    
    map_lines[0].set(color = 'y', linestyle = ':')
    map_lines[1].set(color = 'r', linestyle = '-')    
    
    def fn_callback(label):
        fn_refresh_bscan()
        fn_refresh_map_lines()
        
    def fn_mouse_click_map(ev):
        nonlocal selected_tx, selected_rx    
        if ev.inaxes == ax_map:
            selected_tx = int(np.round(ev.xdata))
            selected_rx = int(np.round(ev.ydata))
            #print(selected_tx, selected_rx)
            fn_refresh_map_lines()
            fn_refresh_bscan()
            
    def fn_mouse_move_map(ev):
        if ev.inaxes == ax_map:
            xd, yd = fn_get_map_lines(np.round(ev.xdata), np.round(ev.ydata))
            map_lines[0].set(xdata = xd, ydata = yd, visible = True)
        else:
            map_lines[0].set(visible = False)
        fig.canvas.draw_idle()
            
    def fn_refresh_map_lines():
        xd, yd = fn_get_map_lines(selected_tx, selected_rx)
        map_lines[1].set(xdata = xd, ydata = yd, visible = True)
        fig.canvas.draw_idle()

    def fn_get_map_lines(t, r):
        if show_what == 'Tx gather':
            xd = [t, t]
            yd = [min(rx_law_indices) - 0.5, max(rx_law_indices) + 0.5]
        if show_what == 'Rx gather':
            xd = [min(tx_law_indices) - 0.5, max(tx_law_indices) + 0.5]
            yd = [r, r]
        if show_what == 'Diag':
            xd = [-max(tx_law_indices) + t, max(tx_law_indices) + t]
            yd = [-max(rx_law_indices) + r, max(rx_law_indices) + r]
        return xd, yd

    def fn_refresh_bscan():
        global show_what
        show_what = check.value_selected
        if show_what == 'Tx gather':
            i = np.asarray(tx_law_indices == selected_tx).nonzero()[0]
            # i = i[np.argsort(ri[i])]
            # print(ri[i])
        if show_what == 'Rx gather':
            i = np.asarray(rx_law_indices == selected_rx).nonzero()[0]
            # i = i[np.argsort(ti[i])]
            # print(ti[i])
        if show_what == 'Diag':
            i = np.asarray(tx_law_indices - rx_law_indices == selected_tx - selected_rx).nonzero()[0]
        ax_bscan.imshow(np.real(data[i,:]), extent = [np.min(time) * 1e6, np.max(time) * 1e6, 1, len(ascan_label)], aspect = 'auto', vmin = -global_max, vmax = global_max)
        ax_bscan.set_xlabel('Time ($\mu$s)')
        ax_bscan.set_ylabel('Ascan')
        fig.canvas.draw_idle()
    
    #controls
    check = RadioButtons(
        ax = ax_ctrl,
        labels = ['Tx gather', 'Rx gather', 'Diag'],
        active = 0
        )
    check.on_clicked(fn_callback)

    map_widget = AxesWidget(ax_map)
    map_widget.connect_event("button_press_event", fn_mouse_click_map)
    map_widget.connect_event('motion_notify_event', fn_mouse_move_map)
    
    fn_refresh_bscan()
    fn_refresh_map_lines()
    return check, map_widget

def fn_analyse_laws(focal_laws_for_seq):
    unique_laws, i =  np.unique(focal_laws_for_seq, return_index = True)
    unique_laws = unique_laws[np.argsort(i)]
    law_dict = {}
    for r in unique_laws:
        law_dict[r] = np.asarray(focal_laws_for_seq == r).nonzero()[0]
    law_indices = np.array([np.asarray(unique_laws == r).nonzero()[0][0] for r in focal_laws_for_seq])
    
    return unique_laws, law_dict, law_indices


    


