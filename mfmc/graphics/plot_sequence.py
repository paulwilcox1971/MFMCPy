# -*- coding: utf-8 -*-
"""
Created on Wed May 10 23:39:24 2023

@author: mepdw
"""


import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, AxesWidget
from matplotlib.backend_bases import MouseButton
from matplotlib.colors import Normalize

import numpy as np
from ..read import fn_read_sequence_data, fn_read_frame, fn_read_law
from ..utils import UNITS


from ..strs import h5_keys
from ..strs import eng_keys


#Absolute sizes in mm
ctrl_mm_h = 50
map_mm_v = 30
gap_mm = 15
inch_to_mm = 25.4


def fn_plot_sequence(fig, mfmc_sequence_group):
    #Function should accept either HDF5 object or seq_data dict (latter shoudl contain at least one frame)
    
    #clear all the current axes
    for a in fig.axes:
        fig.delaxes(a)
    
    
   
    
    seq_data = fn_read_sequence_data(mfmc_sequence_group) 

    selected_tx = 0
    selected_rx = 0
    show_what = 0
    selected_ascan = 0
    selected_time = 0
    bscan_indices = 0
    
    #set up figure    
    edge_fract = 0.05
    
    
    ax_map = fig.add_axes([edge_fract, edge_fract, 0.2 - 2 * edge_fract, 0.2 - 2 * edge_fract])
    ax_map.set_axis_off()

    ax_bscan = fig.add_axes([0.2 + edge_fract, 0.2 + edge_fract, 0.8 - 2 * edge_fract, 0.8 - 2 * edge_fract])
#    ax_bscan.set_axis_off()
    
    ax_ascan = fig.add_axes([0.2 + edge_fract, edge_fract, 0.8 - 2 * edge_fract, 0.2 - 2 * edge_fract])
#    ax_ascan.set_axis_off()
    
    ax_ctrl = fig.add_axes([0.0 +edge_fract, 0.2 + edge_fract, 0.2 - 2 * edge_fract, 0.8 - 2 * edge_fract])
    ax_ctrl.set_axis_off()

 #    ax_btn = fig.add_axes([0,0,0.1,0.1])


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

    ax_map.imshow(max_vals, interpolation = 'none')
    map_lines = ax_map.plot([[0,0], [0,0]], [[1,1], [1,1]], visible = False)    
    map_lines[0].set(color = 'y', linestyle = ':')
    map_lines[1].set(color = 'r', linestyle = '-')    

    im = ax_bscan.imshow(np.ones([3,3]), aspect = 'auto', norm = Normalize(vmin = -global_max, vmax = global_max), interpolation = 'none')
    bscan_lines = ax_bscan.plot([[0,0], [0,0]], [[1,1], [1,1]], visible = False)    
    bscan_lines[0].set(color = 'y', linestyle = ':')
    bscan_lines[1].set(color = 'r', linestyle = '-')
    
    ascan_lines = ax_ascan.plot([0,1], [0,1], visible = True, color = 'r')

    
    def fn_checkbox_callback(label):
        fn_refresh_bscan()
        fn_refresh_map_lines()
        
    def fn_mouse_click_bscan(ev):
        nonlocal selected_ascan, selected_time
        if ev.inaxes == ax_bscan:
            selected_ascan = int(np.round(ev.ydata) - 1)
            fn_refresh_ascan()
            
    def fn_refresh_ascan():
        xd = np.array([time[0], time[-1]]) * UNITS['s'][1]
        yd = np.array([1,1]) * (selected_ascan + 1)
        bscan_lines[1].set(xdata = xd, ydata = yd, visible = True)
        ascan_lines[0].set(xdata = time  *UNITS['s'][1], ydata = np.real(data[bscan_indices[selected_ascan], :]), 
                           visible = True)
                           
        ax_ascan.set_xlim(np.array([time[0], time[-1]]) * UNITS['s'][1])
        ax_ascan.set_ylim([-global_max, global_max])
        ax_ascan.set_xlabel('Time ($\mu$s)')
        fig.canvas.draw_idle()

    def fn_mouse_move_bscan(ev):
        if ev.inaxes == ax_bscan:
            xd = np.array([min(time), max(time)]) * UNITS['s'][1]
            yd = np.array([1,1]) * np.round(ev.ydata)
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
        nonlocal show_what, bscan_indices
        show_what = check.value_selected
        if show_what == 'Tx gather':
            bscan_indices = np.asarray(tx_law_indices == selected_tx).nonzero()[0]
        if show_what == 'Rx gather':
            bscan_indices = np.asarray(rx_law_indices == selected_rx).nonzero()[0]
        if show_what == 'Diag':
            bscan_indices = np.asarray(tx_law_indices - rx_law_indices == selected_tx - selected_rx).nonzero()[0]
        im.set_data(np.real(data[bscan_indices,:]))
        im.set(extent = [np.min(time) * UNITS['s'][1], np.max(time) * UNITS['s'][1], len(bscan_indices) + 0.5, 0.5])
        fig.canvas.draw_idle()
        
    def fn_fig_resize(ev):
        v = fig.get_figheight() * inch_to_mm
        h = fig.get_figwidth() * inch_to_mm

        #Convert to fractions
        edge_fract_h = gap_mm / h
        edge_fract_v = gap_mm / v
        ctrl_frac_h = ctrl_mm_h / h
        map_frac_v = map_mm_v / v


        col_lefts =   [edge_fract_h, ctrl_frac_h + 2 * edge_fract_h]
        row_bottoms = [edge_fract_v, map_frac_v  + 2 * edge_fract_v]

        col_widths =  [ctrl_frac_h, 1 - 3 * edge_fract_h - ctrl_frac_h]
        row_heights = [map_frac_v,  1 - 3 * edge_fract_v - map_frac_v]
        
        if col_widths[1] < 0.1 or row_heights[1] < 0.2:
            return
        
        ax_map.set_position([ col_lefts[0],    row_bottoms[0], col_widths[0], row_heights[0]])
        ax_ctrl.set_position([col_lefts[0], row_bottoms[1], col_widths[0], row_heights[1]])
        ax_ascan.set_position([col_lefts[1], row_bottoms[0], col_widths[1], row_heights[0]])
        ax_bscan.set_position([col_lefts[1],  row_bottoms[1], col_widths[1], row_heights[1]])
        #ax_btn.set_position([col_lefts[0], row_bottoms[1]+row_heights[1] / 2, col_widths[0], row_heights[1] / 2])
    
    fig.canvas.mpl_connect('resize_event', fn_fig_resize)
    
    # def fn_btn_callback(ev):
    #     print(ev)
    
    #controls
    check = RadioButtons(
        ax = ax_ctrl,
        labels = ['Tx gather', 'Rx gather', 'Diag'],
        active = 2
        )
    check.on_clicked(fn_checkbox_callback)
    
    # btn = Button(ax = ax_btn, label ='Test')
    
    # btn.on_clicked(fn_btn_callback)
    
    

    map_widget = AxesWidget(ax_map)
    map_widget.connect_event("button_press_event", fn_mouse_click_map)
    map_widget.connect_event('motion_notify_event', fn_mouse_move_map)

    bscan_widget = AxesWidget(ax_bscan)
    bscan_widget.connect_event("button_press_event", fn_mouse_click_bscan)
    bscan_widget.connect_event('motion_notify_event', fn_mouse_move_bscan)


    fn_fig_resize([])
    fn_refresh_bscan()
    fn_refresh_ascan()
    fn_refresh_map_lines()
    return check#, btn

def fn_analyse_laws(focal_laws_for_seq):
    unique_laws, i =  np.unique(focal_laws_for_seq, return_index = True)
    unique_laws = unique_laws[np.argsort(i)]
    law_dict = {}
    for r in unique_laws:
        law_dict[r] = np.asarray(focal_laws_for_seq == r).nonzero()[0]
    law_indices = np.array([np.asarray(unique_laws == r).nonzero()[0][0] for r in focal_laws_for_seq])
    
    return unique_laws, law_dict, law_indices


    


