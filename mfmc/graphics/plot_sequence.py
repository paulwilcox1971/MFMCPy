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


def fn_plot_sequence(fig, mfmc_sequence_group):
    #Function should accept either HDF5 object or seq_data dict (latter shoudl contain at least one frame)
    
    #clear all the current axes
    for a in fig.axes:
        fig.delaxes(a)
    
    seq_data = fn_read_sequence_data(mfmc_sequence_group) 

    selected_tx = 0
    selected_rx = 0
    show_what = 0
    
    #set up figure    
    edge_fract = 0.02
    ax_map = fig.add_axes([edge_fract, edge_fract, 0.2 - 2 * edge_fract, 0.2 - 2 * edge_fract])
    ax_map.set_axis_off()

    ax_bscan = fig.add_axes([0.2 + edge_fract, 0.2 + edge_fract, 0.8 - 2 * edge_fract, 0.8 - 2 * edge_fract])
#    ax_bscan.set_axis_off()
    
    ax_ascan = fig.add_axes([0.2 + edge_fract, edge_fract, 0.8 - 2 * edge_fract, 0.2 - 2 * edge_fract])
    ax_ascan.set_axis_off()
    
    ax_ctrl = fig.add_axes([0.0 +edge_fract, 0.2 + edge_fract, 0.2 - 2 * edge_fract, 0.8 - 2 * edge_fract])
    ax_ctrl.set_axis_off()

    #unique laws, utx and urx, in order they appear in data for tx and rx
    unique_tx_laws, tx_law_dict, tx_law_indices = fn_analyse_laws(seq_data['TRANSMIT_LAW'])
    unique_rx_laws, rx_law_dict, rx_law_indices = fn_analyse_laws(seq_data['RECEIVE_LAW'])
    
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

    im = ax_bscan.imshow(np.ones([3,3]), aspect = 'auto', vmin = -global_max, vmax = global_max)
    bscan_lines = ax_map.plot([[0,0], [0,0]], [[1,1], [1,1]], visible = False)    
    bscan_lines[0].set(color = 'y', linestyle = ':')
    bscan_lines[1].set(color = 'r', linestyle = '-')    

    
    def fn_checkbox_callback(label):
        fn_refresh_bscan()
        fn_refresh_map_lines()
        
    def fn_mouse_click_bscan(ev):
        pass

    def fn_mouse_move_bscan(ev):
        if ev.inaxes == ax_bscan:
            xd = np.array([min(time), max(time)]) * 1e6
            yd = np.array([1,1]) * np.round(ev.ydata)
#            print(xd, yd)
            bscan_lines[0].set(xdata = xd, ydata = yd, visible = True)
        else:
            bscan_lines[0].set(visible = False)
        fig.canvas.draw_idle()

    def fn_mouse_click_map(ev):
        nonlocal selected_tx, selected_rx    
        if ev.inaxes == ax_map:
            selected_tx = int(np.round(ev.xdata))
            selected_rx = int(np.round(ev.ydata))
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
        nonlocal show_what
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
        nonlocal show_what
        show_what = check.value_selected
        if show_what == 'Tx gather':
            i = np.asarray(tx_law_indices == selected_tx).nonzero()[0]
        if show_what == 'Rx gather':
            i = np.asarray(rx_law_indices == selected_rx).nonzero()[0]
        if show_what == 'Diag':
            i = np.asarray(tx_law_indices - rx_law_indices == selected_tx - selected_rx).nonzero()[0]
        im.set_data(np.real(data[i,:]))
        im.set(extent = [np.min(time) * 1e6, np.max(time) * 1e6, 1, len(ascan_label)])
        ax_bscan.set_xlabel('Time ($\mu$s)')
        ax_bscan.set_ylabel('Ascan')
        fig.canvas.draw_idle()
    
    #controls
    check = RadioButtons(
        ax = ax_ctrl,
        labels = ['Tx gather', 'Rx gather', 'Diag'],
        active = 0
        )
    check.on_clicked(fn_checkbox_callback)

    map_widget = AxesWidget(ax_map)
    map_widget.connect_event("button_press_event", fn_mouse_click_map)
    map_widget.connect_event('motion_notify_event', fn_mouse_move_map)

    bscan_widget = AxesWidget(ax_bscan)
    bscan_widget.connect_event("button_press_event", fn_mouse_click_bscan)
    bscan_widget.connect_event('motion_notify_event', fn_mouse_move_bscan)


    
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


    


